# -*- coding: utf-8 -*-

# TODO, tester HTTP/1.1 avec keep alive

################################################################################
# Serveur http multithread avec objet socket en thread separer et son handler.
################################################################################

NAME_SERVER = "Tekio_serverhandler_Beta[0.02]"

import socket
import sys
import urllib
import datetime
import cgi
import Cookie
import mimetypes
import time
import mimetools
import random
import traceback
import StringIO
from threading import Thread, Semaphore
from Queue import Queue

from tekio.utils import check_char_url
from tekio.utils import quote_html
from tekio.utils import date_time_string_header
from tekio.utils import responses_http, error_message_http
from tekio.utils import split_requestline_http
from tekio.utils import Action_Thread
from tekio.utils import format_path
from tekio.utils import stou


from tekio.libtek import log

################################################################################
# Objet socket en thread separer pour eviter sa non fermeture.
################################################################################

class Socket_Thread(Thread):

    def get_host_client(self):
        if self.FORGET_ERRORS:
            try:
                if not self._host_client:
                    h, p = self.client_address[:2]
                    self._host_client=socket.getfqdn(h)
            except:
                self.err("error get_host_client")
                return None
        else:
            if not self._host_client:
                h, p = self.client_address[:2]
                self._host_client=socket.getfqdn(h)
        return self._host_client
    _host_client = None
    host_client = property(get_host_client)

    def __init__ (self,idsoc,client_address, socket_thread, queue_in, queue_out, mylog, config, server_address):
        Thread.__init__(self)
        self.idsoc=idsoc
        self.server_address=server_address
        self.client_address=client_address
        self.socket_thread=socket_thread
        self.queue_in=queue_in
        self.queue_out=queue_out
        self.log=mylog
        self.config=config

        self.rfile = None
        self.wfile = None

        #surchage possible par config :
        self.rbufsize = -1
        self.wbufsize = 0
        self.protocol_version = "HTTP/1.0"

        self.NAME_SERVER = NAME_SERVER
        self.sys_version = "Python/" + sys.version.split()[0]
        self.server_version = self.NAME_SERVER
        self.version_string = self.server_version + ' ' + self.sys_version

        self.timer_init=None

        
        if self.config.flag_server['TIMER_REQUESTS']:
            self.log_ts=log(config,fichier="timer_requests.txt",clean=True)
            self.timer_init=time.time()
        if self.config.flag_server['TIMER_REQUEST']:
            self.log_t=log(config,fichier="req-%s.txt" % idsoc)
            self.trace("start")


    def trace(self,txt):
        if self.config.flag_server['TIMER_REQUEST']:
            self.log_t.trace(txt)

    def run(self):
        while 1:
            as=self.queue_in.get()
            ret=None
            if as.action=='initialise':
                ret=self.initialise()
            elif as.action=='trace':
                ret=self.trace(as.values)
            elif as.action=='handle':
                ret=self.handle()
            elif as.action=='is_keep_alive':
                ret=self.is_keep_alive()
            elif as.action=='content_type':
                ret=self.content_type(as.values)
            elif as.action=='add_header':
                ret=self.add_header(as.values[0],as.values[1])
            elif as.action=='send_datas':
                ret=self.send_datas(as.values)
            elif as.action=='send_error':
                ret=self.send_error(as.values)
            elif as.action=='send_binary_file':
                ret=self.send_binary_file(as.values)
            elif as.action=='send_binary_datas':
                ret=self.send_binary_datas(as.values[0],as.values[1])
            elif as.action=='redirection_http':
                ret=self.redirection_http(as.values[0],as.values[1])
            elif as.action=='redirection_html':
                ret=self.redirection_html(as.values)
            elif as.action=='form_keys':
                ret=self.form_keys()
            elif as.action=='input_text_value':
                ret=self.input_text_value(as.values[0],as.values[1])
            elif as.action=='input_dico_text_value':
                ret=self.input_dico_text_value(as.values[0],as.values[1])
            elif as.action=='checkbox_value':
                ret=self.checkbox_value(as.values[0],as.values[1])
            elif as.action=='input_file_item':
                ret=self.input_file_item(as.values)
            elif as.action=='get_datas_file_form':
                ret=self.get_datas_file_form(as.values)
            elif as.action=='get_path':
                ret=self.path
            elif as.action=='get_args':
                ret=self.args
            elif as.action=='finish':
                self.finish()
                self.queue_out.put(None)
                return
            elif as.action=='get_cookies':
                ret=self.cookies
            elif as.action=='newsoc':
                #pour fermer le server !
                socket.socket(socket.AF_INET,socket.SOCK_STREAM).connect(self.server_address)
                ret=None
            self.queue_out.put(ret)

                
    def initialise(self):

        for (k,v) in self.config.socket_thread.items():
            setattr(self,k,v)
 
        self.flag_init_response = False
        self.keep_alive = False
        self.response_headers = []
        self.response_code = 200
        self.response_message = None
        self.response_content_type='text/html'
        if self.FORGET_ERRORS:
            try:
                self.rfile = self.socket_thread.makefile('rb', self.rbufsize)
                self.wfile = self.socket_thread.makefile('wb', self.wbufsize)
            except:
                self.err("error makefile socket_thread")
                return False
        else:
            self.rfile = self.socket_thread.makefile('rb', self.rbufsize)
            self.wfile = self.socket_thread.makefile('wb', self.wbufsize)
        return True


    def finish(self):
        try:
            self.send_datas(None)
        except:
            pass
        try:
            if not self.wfile.closed:
                self.wfile.flush()
        except:
            pass
        try:
            self.wfile.close()
        except:
            pass
        try:
            self.rfile.close()
        except:
            pass
        try:
            self.socket_thread.shutdown(2)
        except:
            pass
        try:
            self.socket_thread.close()
        except:
            pass
        try:
            del(self.socket_thread)
        except:
            pass
        self.socket_thread=None
        if self.config.flag_server['TIMER_REQUESTS']:
            nt=time.time()
            dt=nt-self.timer_init
            self.log_ts.trace(" time=%s (%s) : %s " % (dt,self.idsoc,self.path) )
        if self.config.flag_server['TIMER_REQUEST']:
            self.trace("end")

    def check_url(self):
        self.path=check_char_url(self.path)
        return True

    def handle(self):
        """ Handle a single HTTP request. GET et POST seulement """
        self.command = None 

        # recuperation de la ligne de requete.
        try:
            line = self.rfile.readline()
        except:
            self.err("error get requestline ")
            self.http_error(400,'No requestline')
            return False

        (ok,values)=split_requestline_http(line,self.protocol_version)
        if not ok:
            self.err(values[1])
            self.http_error(values[0],values[1])
            return False

        (self.command, self.path, self.request_version, self.keep_alive) = values

        #get headers with mimetools.Message RFC 2822
        self.headers = mimetools.Message(self.rfile, 0)

        #check Connection keep-alive
        if self.keep_alive:
            conntype = self.headers.get('Connection', "")
            if conntype.lower() != 'keep-alive':
                self.keep_alive=False

        #get form
        if self.command=="POST":
            storage = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                         }
                )
            self.form = storage
        elif self.command=="GET":
            self.form = None

        #get path / query_string
        if self.path.find('?') != -1:
            self.path, self.query_string = self.path.split('?', 1)
        else:
            self.query_string = ''

        #unquote path
        try:
            self.path=urllib.unquote(self.path)
        except:
            self.dbg('error unquote path %s ' % self.path)

        self.path=format_path(self.path)
        
        #get args query_string
        self.args = dict(cgi.parse_qsl(self.query_string))
        for k in self.args.keys():
            self.args[k] = stou(self.args[k])

        #get cookies
        self.cookies=None
        if 'cookie' in self.headers.keys() or 'Cookie' in self.headers.keys() :
            self.cookies=Cookie.SimpleCookie()
            self.cookies.load(self.headers['Cookie'])

        if not self.check_url():
            self.err("error get requestline ")
            self.http_error(400,'URL incorrecte %s ' % self.path)
            return False
            
        return True


    def form_keys(self):
        if self.form:
            return self.form.keys()
        else:
            return []

    def http_error(self, code, message=None):
        self.response_code=code
        self.response_message=message
        self.add_header('Connection', 'close')
        try:
            short, explain = responses_http[code]
        except KeyError:
            short, explain = '???', '???'
        if message is None:
            message = short
        content = (error_message_http %
                   {'code': code, 'message': quote_html(message), 'explain': explain})
        self.send_datas(content)

    def init_response(self):
        """Send the response & header and log the response code."""
        self.keep_alive=False
        code=self.response_code
        message=self.response_message            
        path4log=getattr(self,'path','NOPATH')
        self.log_request(" (%s) %s" %  (str(code), path4log) )
        if message is None:
            if code in responses_http.keys():
                message = responses_http[code][0]
            else:
                message = ''
            
        if self.request_version != 'HTTP/0.9':
            self.add_header('Server', self.version_string)
            self.add_header('Date', date_time_string_header())
            if self.response_content_type:
                self.add_header("Content-Type", self.response_content_type)

            self.wfile.write("%s %d %s\r\n" %
                           (self.protocol_version, code, message))

            for (keyword, value) in self.response_headers:
                """Send a MIME header."""
                if self.request_version != 'HTTP/0.9':
                    self.wfile.write("%s: %s\r\n" % (keyword, value))
                
                if keyword.lower() == 'connection':
                    if value.lower() == 'close':
                        self.keep_alive=False

            self.wfile.write("\r\n")

        return 

    def content_type(self, value):
        self.response_content_type=value

    def add_header(self,k,v):
        if not self.flag_init_response:
            self.response_headers.append((k,v))
        else:
            raise ('Header impossible, contenu deja envoye')

    def send_error(self,datas):
        self.send_datas('Erreur : %s' % datas)

    def send_datas(self,datas):
        try:
            if not self.flag_init_response:
                self.init_response()
                self.flag_init_response=True
            if datas:
                if self.response_code not in (100,101,204, 304):
                    if type(datas)==type(u''):
                        datas=datas.encode('ascii', 'xmlcharrefreplace')
                    self.wfile.write(datas)
        except socket.error:
            self.err('socket erreur...')
        self.wfile.flush()

    def send_binary_datas(self,typemime,datas):
        self.content_type(typemime)
        self.add_header('Content-Length', len(datas))
        try: 
            self.send_datas(datas)
        except: 
            self.log.debug('erreur send datas')
        return

    def send_binary_file(self,pathfile):
        typemime=mimetypes.guess_type(pathfile)[0]
        self.content_type(typemime)
        f=open(pathfile,'rb')
        datas=f.read()
        f.close()
        self.send_binary_datas(typemime,datas)

    def is_keep_alive(self):
        return self.keep_alive

    def redirection_http(self,redirect_url,msg=''):
        """ redirection http """
        self.response_code=302
        self.add_header('Location', redirect_url)

    def redirection_html(self, form, nameform):
        """ redirection html : 
            envoie une page avec un formulaire qui s'auto execute."""
        response = """\
<html><head><title>Transaction in progress</title></head>
<body onload='document.getElementById("%s").submit()'>
%s
</body></html>
""" % (nameform, form)
        self.send_datas(response)

    def input_text_value(self,champ,nulvalue):
        return self.form.getvalue(champ,nulvalue)

    def put_in_ch_dico(self,dico,k,v,limit):
        if limit==1:
            dico[k]=v
            return
        
        s=k.split('_',1)
        if len(s)==1:
            dico[k]=v
            return
        if dico.has_key(s[0]):
            sub=dico[s[0]]
            if type(sub)!=type({}):
                sub={}
        else:
            sub={}
        dico[s[0]]=sub
        self.put_in_ch_dico(sub,s[1],v,limit-1)

    def input_dico_text_value(self,champ,limit):
        dico={}
        for k in self.form.keys():
            s=k.split(champ+'_',1)
            if s[0]=='' and len(s)==2:
                self.put_in_ch_dico(dico,s[1],self.form.getvalue(k,''), limit)
        return dico
    
    def checkbox_value(self,champ,nulvalue):
        return self.form.getvalue(champ,nulvalue)

    def input_file_item(self,champ):
        return self.form[champ]

    def dbg(self,msg):
        self.log.debug(msg,'socket_thread.txt')

    def err(self,msg):
        self.log.err(msg)
        self.log.err("%s" % sys.exc_info()[0])
        self.log.traceback()

    def log_request(self,msg):
        self.log.debug(msg,'request.txt')

    def get_datas_file_form(self,fileitem):
        datas_binary=''
        while 1:
            chunk = fileitem.file.read(100000)
            if not chunk: break
            datas_binary+=chunk
        return datas_binary
            
class Socket_Interface:
    def get_args(self):
        return self.action('get_args',None)
    args=property(get_args)

    def get_path2(self):
        if self._path==None:
            self._path=self.get_path()
        return self._path
    _path=None
    path=property(get_path2)

    def __init__(self, idsoc, client_address, queue_in, queue_out, log, config,server_address):

        self.server_address=server_address
        self.client_address=client_address
        self.queue_in=queue_in
        self.queue_out=queue_out
        self.log=log
        self.config=config
        self.idsoc=idsoc

    def action(self,action,valeurs):
        self.queue_in.put(Action_Thread(action,valeurs))
        r=self.queue_out.get()
        return r
        
    def initialise(self):
        return self.action('initialise',None)

    def newsoc(self):
        return self.action('newsoc',None)

    def handle(self):
        return self.action('handle',None)

    def finish(self):
        return self.action('finish',None)

    def is_keep_alive(self):
        return self.action('is_keep_alive',None)

    def content_type(self,type):
        return self.action('content_type',type)

    def add_header(self,v,k):
        return self.action('add_header',(v,k))

    def send_datas(self,datas):
        return self.action('send_datas',datas)

    def send_error(self,datas):
        return self.action('send_error',datas)

    def send_binary_file(self,pathfile):
        return self.action('send_binary_file',pathfile)

    def send_binary_datas(self,mimetype,datas):
        return self.action('send_binary_datas',(mimetype,datas))

    def redirection_http(self,url,msg=''):
        return self.action('redirection_http',(url,msg))

    def redirection_html(self,form,nameform):
        return self.action('redirection_html',(form,nameform))

    def get_cookies(self):
        return self.action('get_cookies',None)

    def input_text_value(self,champ,nulvalue=''):
        return self.action('input_text_value',(champ,nulvalue))

    def input_dico_text_value(self,champ,limit=-1):
        return self.action('input_dico_text_value',(champ,limit))

    def checkbox_value(self,champ,nulvalue=''):
        return self.action('checkbox_value',(champ,nulvalue))

    def input_file_item(self,champ):
        return self.action('input_file_item',champ)

    def get_datas_file_form(self,champ):
        return self.action('get_datas_file_form',champ)

    def form_keys(self):
        return self.action('form_keys',None)

    def get_path(self):
        return self.action('get_path',None)

    def trace(self,txt):
        return self.action('trace',txt)




def create_socket_thread(idsoc, client_address, socket, queue_in, queue_out, log, config, server_address):

    socket_thread=Socket_Thread(idsoc,client_address, socket, queue_in, queue_out, log, config, server_address)
    socket_interface=Socket_Interface(idsoc, client_address,queue_in, queue_out, log, config, server_address)
    ret=(socket_thread,socket_interface)
    return ret

class HTTP_Server:

    def __init__(self, server_address, Request_Handler_Class, Glob_Class):
        """
          Parametres par default et initialisation.
        """
        self.FORGET_ERRORS = False
        self.SHOW_ERRORS = False
        self.THREADING = True

        self.server_address = server_address
        self.Request_Handler_Class = Request_Handler_Class
        self.socket_blocking = True
        self.SOCKET_TIMEOUT = 10

        self.daemon_threads = False
        self.request_queue_size = 30
        self.allow_reuse_address = 1

        self.idsoc_actu = 0
        self.dico_queue_in={} 
        self.dico_queue_out={} 
        self.dico_thread={}
        self.dico_finish={}
        self.semaphore_idsoc=Semaphore()

        self.glob=Glob_Class()

    def start(self):
        """
          action apres parametrage.
        """
        
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.allow_reuse_address:
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(self.server_address)
        (self.server_name,self.server_port)=self.server_address
        self.listener.listen(self.request_queue_size)
        #self.listener.setdefaulttimeout(self.SOCKET_TIMEOUT)
        if self.FORGET_ERRORS:
            try:
                self.ecoute()
                
                pass
            except:
                self.dbg("erreur ecoute %s " % sys.exc_info()[0])
                self.dbgtr()
        else:
            self.ecoute()
            pass
        self.stop_server()

    def ecoute(self):
        """
          boucle d ecoute.
        """
        while not self.glob.stop_flag:

            # clean objet finished not closed !!

            """
            for idsoc in self.dico_finish.keys():
                th=self.dico_thread[idsoc]
                if th:
                    th.join()
                self.dico_thread[idsoc]=None
                self.dico_finish[idsoc]=None
            """
            # create new socket_fils

            socket_fils, client_address = self.listener.accept()


            if self.socket_blocking:
                socket_fils.setblocking(1)
                socket_fils.settimeout(self.SOCKET_TIMEOUT) 
            else:
                socket_fils.setblocking(0)

            # check si serveur eteint
            if self.glob.stop_flag:
                try:
                    socket_fils.shutdown(2)
                except:
                    pass
                socket_fils.close()
                return

            # create isreq
            self.semaphore_idsoc.acquire()
            self.idsoc_actu+=1
            idsoc=self.idsoc_actu+0
            self.semaphore_idsoc.release()


            # thread the socket objet
            queue_in=Queue()
            queue_out=Queue()
            self.dico_queue_in[idsoc]=queue_in
            self.dico_queue_out[idsoc]=queue_out
            socket_thread=None
            ret=create_socket_thread(idsoc, client_address,
                                     socket_fils,
                                     queue_in, queue_out,
                                     self.log, self.config,
                                     self.server_address)
            (socket_thread,socket_interface)=ret
            socket_thread.start()

            if self.THREADING:
                t = Thread(target = self.active_handler,
                           args = (socket_interface,))
                if self.daemon_threads:
                    t.setDaemon (1)
                t.start()
                self.dico_thread[idsoc]=t
            else:
                self.active_handler(socket_interface)
            

    def do_active_handler(self, socket_interface):
        my_objs=self.my_objets()
        RH=self.Request_Handler_Class(socket_interface,my_objs)
        if self.THREADING:
            self.dico_finish[socket_interface.idsoc]=True
        del(RH)
        return

    def active_handler(self, socket_interface):
        """
            lance le handler.
        """

        if self.FORGET_ERRORS:
            try:
                self.do_active_handler(socket_interface)
            except:
                self.dbg("erreur handler %s " % sys.exc_info()[0])
                self.dbgtr()
                
        elif self.SHOW_ERRORS:
            try:
                self.do_active_handler(socket_interface)
            except:
                socket_interface.send_datas("<br /><br />\n\n show error  %s \n\n<br /><br />" % sys.exc_info()[0])
                fp = StringIO.StringIO()
                traceback.print_exc(file=fp)
                message = fp.getvalue()
                print message
                message=message.replace('<','&lt;')
                message=message.replace('\n','<br />')
                socket_interface.send_datas(message)
                socket_interface.finish()
        else:
            self.do_active_handler(socket_interface)
            

    def stop_server(self):
        if self.THREADING:
            for th in self.dico_thread.values():
                if th:
                    th.join()
        try:
            self.listener.shutdown(2)
        except:
            pass
        self.listener.close()
        self.my_stop_server()

    def dbg(self,msg,file='server.txt'):
        
        self.log.debug(msg,file)

    def dbgtr(self,file='server.txt'):
        self.log.traceback(file)


################################################################################
#
# #### HTTP_Handler
#
################################################################################


class HTTP_Handler:
    def __init__(self, interfaces,objs):
        self.my_get_interfaces(interfaces,objs)
        if not self.socket.initialise():
            self.socket.finish()
            return
        if not self.my_init():
            self.socket.finish()
            return
        ok=self.handle()
        while ok and self.socket.is_keep_alive():
            ok=self.handle()
        self.finish()
        
    def handle(self):
        ok=self.socket.handle()
        if not ok:
            return False

        if self.config.flag_server['FORGET_ERRORS']:
            try:
                return self.my_handler()
            except:
                self.log.err('my handler erreur...')
                self.log.err('%s' % sys.exc_info()[0])
                self.log.traceback()
                return False
        else:
            return self.my_handler()

    def finish(self):
        self.my_finish()
        self.socket.finish()

    def my_get_interfaces(self, interfaces):
        """ A SURCHARGER """
        self.socket = interfaces[0]
        self.log    = interfaces[1]
        self.config = interfaces[2]
        self.glob   = interfaces[3]
        self.log.err('my_get_interfaces manquant')

    def my_init(self):
        """ METHODE A SURCHARGER """
        self.log.err('my_init manquant')

    def my_handler(self):
        """ METHODE A SURCHARGER """
        self.log.err('my_handler manquant')

    def my_finish(self):
        """ METHODE A SURCHARGER """
        self.log.err('my_finish manquant')

    def my_interfaces(self,socket_interface,objs):
        """
          A SURCHARGE
        """
        return (socket_interface,socket_interface.log,socket_interface.config,self.glob)
