# -*- coding: utf-8 -*-

import string 
import datetime
import time
import cgi
import os
import popen2
import tempfile
import sys

from threading import Thread
from htmlentitydefs import codepoint2name

###########################
## dicos, listes et tuples
###########################
def list_to_dic(l):
    d={}
    for (k,v) in l:
        d[k]=v
    return d

def to_tuple(params):
    if type(params)==type(u''):
        params=utos(params)
    if type(params)==type(''):
        return (params,)
    if type(params)==type(1):
        return (params,)
    if type(params)==type(1L):
        return (params,)
    if type(params)==type(1.0):
        return (params,)
    if type(params)==type([]):
        return tuple(params)
    if type(params)==type(()):
        return params
    return ()

def slash_to_list_int(chaine):
    liste=[]
    dec=chaine.split('/')
    for i in dec:
        if i!=u'' and i!='':
            liste.append(int(i))
    return liste


##########################
## structures api sql
##########################

def py_to_apisql(chaine):
    return chaine.replace("'%s'",'?').replace('"%s"','?').replace("%s",'?')

def check_params_sql(params):
    """ check les params pour sql pour eviter les injections avec '
        ne pas utiliser si les params sont passe par le driver 
        le check est alors fait par le driver.
    """
    if type(params)==type([]) or type(params)==type(()):
        ret=[]
        for p in params:
            if type(p)==type(u''):
                p=utos(p)
            if type(p)==type(''):
                p=p.replace("'","''").replace('"','""')
            ret.append(p)
        return tuple(ret)
    if type(params)==type(1) or type(params)==type(1L) or type(params)==type(1.0) or type(params)==type(''):
        if type(params)==type(u''):
            params=utos(params)
        if type(params)==type(''):
            params=params.replace("'","''").replace('"','""')
        return (params,)
    return ()


##########################
## chaines de caracteres
##########################

charurlok=string.ascii_letters+string.digits+'.'+'/'+'_'+'-'

# pour les urls
def check_char_idpage(chaine):
    res=""
    for c in chaine:
        if c in string.lowercase:
            res+=c
        elif c in string.uppercase:
            res+=c.lower()
        else:
            res+='_'
    return res


def check_char(chaine,charok=string.ascii_letters+string.digits):
    res=""
    for c in chaine:
        if c in charok:
            res+=c
    return res

def check_char_url(chaine):
    r=check_char(chaine,charurlok)
    r=r.replace(' ','_')
    return r.replace('..','')

# pour l'unicode

def stou(chaine):
    if type(chaine)==type(u''):
        return chaine
    else:
        return unicode(str(chaine),'utf-8',errors='ignore')
    
def utos(uni):
    if type(uni)==type(''):
        return uni
    elif type(uni)==type(u''):
        return uni.encode('utf-8')
    else:
        return str(uni).encode('utf-8')

def surcharge_unicode(fn):
    def newfn(txt):
        r=fn(txt)
        if type(r)==type(''):
            return unicode(r,'utf-8',errors='ignore')
        return r
    return newfn

# pour le html
def utoh(u):
    htmlentities = list()
    for c in u:
        if c=='"': 
            htmlentities.append("&quot;")
        elif c=="'": 
            htmlentities.append("&apos;")
        elif ord(c) < 128:
            htmlentities.append(c)
        else:
            htmlentities.append('&%s;' % codepoint2name[ord(c)])
    return ''.join(htmlentities)


def quote_html(html):
    """remplace les '&<>' par leurs entités html."""
    if not html:
        return ''
    return html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def quoteattr(s):
    qs = cgi.escape(s, 1)
    return '"%s"' % (qs,)

def balise_utf8(datas_includes=[]):
    includes=""
    for (typ,file) in datas_includes:
        if typ=="css":
	    includes+='<link rel="stylesheet" type="text/css" href="/includes/css/%s.css" />\n' % file
        elif typ=="js":
	    includes+='<script type="text/javascript" src="/includes/js/%s"></script>\n' % file
	elif typ=="jsl":
	    includes+='<script type="text/javascript" src="%s"></script>\n' % file
	else:
	    includes+=file

    return ("""<html>
<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<base id="baseurl" href="/" />%s
</head><body>""" % includes,"""</body></html>""")

##########################
## path
##########################

def name_from_path(chaine):
    chaine=utos(chaine)
    plist=chaine.split('/')
    plist=remove_all('',plist)
    if len(plist)>0:
        return plist[-1]
    else:
        return ''

def remove_all(elem,list):
    for i in range(list.count(elem)):
        list.remove(elem)
    return list

def path_to_liste(chaine):
    chaine=utos(chaine)
    plist=chaine.split('/')
    plist=remove_all('',plist)
    return plist

def format_path_list(l):
    if len(l)>0:
        return '/'+'/'.join(l)
    else:
        return ''

def format_path(chaine):
    chaine=utos(chaine)
    l=path_to_liste(chaine)
    return format_path_list(l)

def path_pere(chaine):
    chaine=utos(chaine)
    l=path_to_liste(chaine)
    if len(l)==0:
        return None
    return format_path_list(l[:-1])


##########################
## fichiers.
##########################

def new_name_file(origin):
    s1=origin.split('.',1)
    s2=s1[0].split('-',1)
    try:
        ext=int(s2[1])+1
    except:
        ext=2
    name=s2[0]+'-'+str(ext)
    if len(s1)>1:
        name+='.'+s1[1]
    sinpath=name.split('/')[-1]
    return (name,sinpath)


def format_3mini(nb):
    if nb>=100:
        return str(nb)
    if nb>=10:
        return "%0.1f" % nb
    return "%0.2f" % nb

def size_human_file(file):
    try:
        size_machine=os.stat(file)[6]
        if size_machine<1024 :
            return str(size_machine)+' c'
        size_ko=size_machine/1024.0
        if size_ko<1024:
            return format_3mini(size_ko)+' ko'
        size_mo=size_ko/1024.0
        if size_mo<1024:
            return format_3mini(size_mo)+' Mo'
        size_go=size_mo/1024.0
        return format_3mini(size_go)+' Go'
    except:
        return 'Fichier Vide !'


##########################
## dates
##########################
# TODO : version multilangue pour header des weekdayname et monthname
# avec langue du navigateur a detecter.

weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def date_time_string_header():
    """Return the current date and time formatted for a message header."""
    now = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(now)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        weekdayname[wd], day, monthname[month], year, hh, mm, ss)
    return s

##########################
## commandes systemes
##########################
# TODO eliminer au maximum pour des modules pythons
# pour ameliorer les perfs.

def system_no_ret(cmd,check=True):
    r=os.system(cmd) 
    if check and r!=0:
        raise("Cmd retour (%s) : %s" % (utos(r),utos(cmd)))

def system_ret(cmd):
    fd1, filename1 = tempfile.mkstemp()
    f1 = os.fdopen(fd1, 'wb')
    fd2, filename2 = tempfile.mkstemp()
    f2 = os.fdopen(fd2, 'wb')
    (f1,f2)=popen2.popen2(cmd)
    ret=f1.read()
    f1.close()
    f2.close()
    system_no_ret('rm -Rf %s' % filename1,check=False)
    system_no_ret('rm -Rf %s' % filename2,check=False)
    return ret

##########################
## Threading
##########################

class Action_Thread:
    def __init__(self,action,values):
        self.action=action
        self.values=values

class PseudoSemaphore:
    def acquire(self):
        pass
    def release(self):
        pass

##########################
## Except
##########################

def get_code_erreur():
    return sys.exc_info()[0]
    
##########################
## HTTP
##########################
# Table mapping response codes to messages; entries have the
# form {code: (shortmessage, longmessage)}.
# See http://www.w3.org/hypertext/WWW/Protocols/HTTP/HTRESP.html

responses_http = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No response', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this server.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
              'this proxy before proceeding.'),
        408: ('Request Time-out', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service temporarily overloaded',
              'The server cannot process the request due to a high load'),
        504: ('Gateway timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version not supported', 'Cannot fulfill request.'),
        }

error_message_http = """\
<head>
<title>Error HTTP : code %(code)d</title>
</head>
<body>
<h1>Error HTTP response</h1>
<p>Error code : %(code)d.
<p>Error code explanation : %(code)s = %(explain)s.
<p>Message : %(message)s.
</body>
"""

def split_requestline_http(requestline, protocol_version):
    if not requestline:
        msg='No requestline'
        return (False,(400,msg))   
    if requestline[-2:] == '\r\n':
        requestline = requestline[:-2]
    elif requestline[-1:] == '\n':
        requestline = requestline[:-1]
    words = requestline.split()
    nbwords=len(words)
    if nbwords>3 or nbwords<2:
        msg="Incorrect requestline %s " % requestline
        return (False,(400,msg))

    if nbwords == 2:
        (command, path) = words
        keep_alive=False
        version = "HTTP/0.9" 
        if command != 'GET':
            msg="Bad HTTP/0.9 request type (%r)" % command
            return (False,(400,msg))
        return (True,(command,path,version,keep_alive))

    (command, path, version) = words
    if command not in ['GET','POST']:
            msg="Unsupported method (%r)" % self.command
            return (False,(501, msg))

    if version[:5] != 'HTTP/':
        msg="Bad request version (%r)" % version
        return (False,(400,msg))
    try:
        base_version_number = version.split('/', 1)[1]
        version_number = base_version_number.split(".")
        version_number = int(version_number[0]), int(version_number[1])
    except :
        msg="Bad request version (%r)" % version
        return (False,(400,msg))
    if version_number >= (2, 0):
        msg="Invalid HTTP Version (%r)" % base_version_number
        return (False,(505,msg))

    if version_number >= (1, 1) and protocol_version >= "HTTP/1.1":
        keep_alive=True
    else:
        keep_alive=False

    return (True,(command,path,version,keep_alive))

#### COOKIES

def tuple_cookie(name,value,date=None,path=None,domain=None,secure=None):
        """ creation d'un tuple cookie """
        s='%s=%s' % (name,value)
        if date:
            s+='; Expires=%s' % time.strftime("%a, %d-%b-%Y %T GMT",date.timetuple()) 
        if path:
            s+='; Path=%s' % path
        if domain:
            s+='; Domain=%s' % domain
        if secure:
            s+='; Secure'
        return ('Set-Cookie', s)
