# -*- coding: utf-8 -*-

import time
import datetime
import random
import cgi

from openid.store import memstore
import openid.store.filestore
import openid.fetchers

from tekio.utils import quoteattr
from tekio.utils import tuple_cookie
from tekio.objets.base import create_element


class My_Session():
    def __init__(self, log, config, expire, glob, database):
        self.config=config
        self.log=log
        self.expire=expire
        self.initdatas()

        if config.flag_server.has_key('ACTIVE_USER'):
            if config.flag_server['ACTIVE_USER']:
                self.set_user(config.flag_server['ACTIVE_USER'],glob,database)
                

    def initdatas(self):
        self.user=""
        self.id_user=-1
        self.openid=None
        self.action_openid=None

        self.dico={}
        #todo add : preference user.
        self.groupes=[]
        self.responsabilites=[]
        self.is_admin=False
        self.is_edit=False
        self.new_url=''
        self.futur_new_url=''

        self.langues=self.config.langues
        self.langues_interface=self.config.langues_interface
        self.langue=self.langues[0]
        self.langue_interface=self.langues_interface[0]

    def set_new_url(self,u):
        self.new_url=u
    def set_futur_new_url(self,u):
        self.new_url=u


    def expired(self):
        """ verifie la date d'expiration de la session. """
        if datetime.datetime.now()>self.expire:
            return True
        return False

    def set_expire(self,d):
        self.expire=d

    def deconnecte(self):
        self.initdatas()

    def set_user(self,user,glob,database):
        self.openidinit=user
        self.openidtekiolang=None
        for l in ['fr','es','en']:
            if user.find('http://%s.openid.tekio.org/id/' % l)==0:
                dec=user.split('http://%s.openid.tekio.org/id/' % l,1)
                user='http://openid.tekio.org/id/%s' % dec[1]
                self.openidtekiolang=l
                
        self.user=user

        self.groupes=[]
        self.responsabilites=[]
                                
        self.is_admin=False
        self.is_edit=False
        
        if self.user=='':
            # ?? cas possible ??
            return

        self.id_user=glob.openids.get(self.user,-2)

        if self.id_user==-2:
            #TODO option pour activer/desactiver autocreate user 
            create_element(glob,database,40,0,{},{'openid':self.user,})
            glob.get_population(database)

            self.id_user=glob.openids.get(self.user,-2)
        

        self.infos_utilisateur=glob.objets[self.id_user]

        self.groupes=self.infos_utilisateur['groupes']
        self.responsabilites=self.infos_utilisateur['responsabilites']

        if glob.groupes["admin"] in self.groupes:
            self.is_admin=True
        if glob.groupes["editor"] in self.groupes:
            self.is_edit=True

        self.proprietes=self.infos_utilisateur['proprietes']
        
        l=self.proprietes.get('langue',None)
        self.change_langue_interface(l)
        return

    def change_langue_interface(self,l):
        if l:
            if l in self.langues_interface:
                self.langue_interface=l
                self.langues_interface.remove(l)
                self.langues_interface.insert(0,l)
        return self.action_openid


    def get_action_openid(self):
        return self.action_openid

    def get_process_openid_url(self):
        return self.process_openid_url

    def get_openid(self):
        return self.openid

    def get_user(self):
        return self.user

    def get_new_url(self):
        return self.new_url

    def get_futur_new_url(self):
        return self.futur_new_url

    def get_langue_interface(self):
        return self.langue_interface

    def get_langue(self):
        return self.langue

    def set_action_openid(self,value):
        self.action_openid=value

    def set_process_openid_url(self,value):
        self.process_openid_url=value

    def set_openid(self,value):
        self.openid=value


class Sessions:
    def __init__(self, log, config):
        #intialisation des sessions
        # TODO BEST stoquer dans une base sql pour ne pas perdre les sessions au redemarrage
        self.config=config
        self.log=log
        self.sessions={}
        self.sessions_openid={}
        #intialisation base de donnee open id
        #TEST CON MEMORY STORE..
        self.openid_store = openid.store.filestore.FileOpenIDStore(config.path["openid_consumer"])
        #self.openid_store = memstore.MemoryStore()

        # je ne sais pas a quoi correspond les fetchers, lie a weakssl !?!
        #openid.fetchers.setDefaultFetcher(openid.fetchers.Urllib2Fetcher())
        
    def get_session(self,interfaces):
        """ recupere la session courrant dans la base de session du serveur, 
            crée un session, si pas de session courrante """

        socket   = interfaces[0]
        sessions = interfaces[1]
        traduct  = interfaces[2]
        database = interfaces[3]
        fs_svn   = interfaces[4]
        log      = interfaces[5]
        config   = interfaces[6]
        datas    = interfaces[7]
        glob     = interfaces[8]
        cookies=socket.get_cookies()

        # date previsionnelle d'expiration du cookie
        d=datetime.datetime.now()+datetime.timedelta(0,self.config.params['session_secondes'])

        cs=None
        if cookies:
            #recuperation du cookie
            cs=cookies.get(self.config.cookies['session'],None)

        my_session=None

        if cs:
            alea=cs.value
            if self.sessions.has_key(alea):
                my_session=self.sessions[alea]
                if my_session.expired():
                    #detruit la session si elle a expiré.
                    self.sessions[alea]=None
                else:
                    my_session.set_expire(d)


        # Si pas de session actuelement, creation d'une session.
        if not my_session:
            alea=str(random.randrange(1000000000))
            alea+=str(random.randrange(1000000000))

            my_session=My_Session(self.log,self.config,d,glob,database)
            self.sessions[alea]=my_session

            if my_session.user=='':
                if cookies:
                    cs=cookies.get(self.config.cookies['session_auto_openid'],None)
                    if cs:
                        userautoopenid=cs.value
                        if userautoopenid!='':
                            self.envoie_cookie_session(socket,alea,d)
                            self.openid_step_init_verify(interfaces,userautoopenid,my_session)
                            my_session.set_futur_new_url(socket.path)
                            return None

        action_openid=my_session.get_action_openid()

        if action_openid=='process':
            self.openid_step_process(interfaces,my_session)
        else:
            self.envoie_cookie_session(socket,alea,d)
        return my_session

    def envoie_cookie_session(self,socket,value,date):
        # Actualisation du cookie de session. 
        (k,v)=tuple_cookie(self.config.cookies['session'],
                           value,
                           date=date,
                           path='/')
        socket.add_header(k,v)


    def getConsumer(self,my_session,socket,cookies):
        return openid.consumer.consumer.Consumer(self.getSessionOpenId(my_session,socket,cookies), self.openid_store)

    def getSessionOpenId(self,my_session,socket,cookies):
        myopenid=my_session.get_openid()
        if myopenid is not None:
            return myopenid

        name_cookie=self.config.cookies['session_openid']
        sid=None
        if cookies:
            cmsid=cookies.get(name_cookie,None)
            if cmsid:
                sid=cmsid.value

        # If a session id was not set, create a new one
        if sid is None:
            sid = openid.cryptutil.randomString(16, '0123456789abcdef')
            session = None
        else:
            try:
                session = self.sessions_openid.get(sid)
            except:
                session = None

        # If no session exists for this session ID, create one
        if session is None:
            session = {'id': sid }
            my_session.set_openid (session)
            (k,v)=tuple_cookie(name_cookie,
                               sid,
                               path='/')
            socket.add_header(k,v)
            self.sessions_openid[sid] = session
        return session

    def crea_autoconnect(self,socket,value):
        (k,v)=tuple_cookie(self.config.cookies['session_auto_openid'],
                           value,
                           path='/')
        socket.add_header(k,v)

    def annule_autoconnect(self,socket,config):
        (k,v)=tuple_cookie(config.cookies['session_auto_openid'],
                           '',
                           path='/')
        socket.add_header(k,v)

    def openid_step_init_verify(self,interfaces,userautoopenid,my_session):
        socket   = interfaces[0]
        sessions = interfaces[1]
        traduct  = interfaces[2]
        database = interfaces[3]
        fs_svn   = interfaces[4]
        log      = interfaces[5]
        config   = interfaces[6]
        datas    = interfaces[7]
        glob     = interfaces[8]
        cookies=socket.get_cookies()

        oidconsumer = self.getConsumer(my_session,socket,cookies)

        auto=True

        if userautoopenid:
            openid_url=userautoopenid
        else:
            #passage par le formulaire de connexion !
            auto=False
            openid_url = socket.input_text_value('openid')
            if openid_url.find('/')==-1:
                lang=config.langues[0]
                openid_url='http://%s.openid.tekio.org/id/%s' % (lang,openid_url)
            if openid_url.find('//')==-1:
                openid_url='http://'+openid_url
            autoconnect = socket.checkbox_value('autoconnect')
            if autoconnect=='yes':
                self.crea_autoconnect(socket,openid_url)
            my_session.set_futur_new_url('')

        try:
            requestoid = oidconsumer.begin(openid_url)

        except openid.consumer.consumer.DiscoveryFailure, exc:
            self.annule_autoconnect(socket,config)
            socket.send_datas('Erreur de connexion sur openid 1 : %s ' % openid_url)
            socket.send_datas('Autoconnect openid detruit. ')
            return


        if not requestoid:
            if userautoopenid:
                self.annule_autoconnect(socket,config)
                socket.send_datas('Erreur de connexion sur openid 2 : %s ' % openid_url)
                socket.send_datas('Autoconnect openid detruit. ' % openid_url)
                return
            else:
                self.annule_autoconnect(socket,config)
                socket.send_datas('Identifiant openid invalide ou inactif : %s ' % openid_url)
                socket.send_datas('Autoconnect openid detruit. ' % openid_url)
                return

        # ?? DATA ? PAPE
        #self.requestRegistrationData(requestoid)
        #self.requestPAPEDetails(requestoid)

        #immediate=True
        immediate=False

        my_session.set_action_openid('process')
        my_session.set_process_openid_url(openid_url)
        trust_root = self.config.http['url_base']+'/'
        return_to = datas.url_base+my_session.get_futur_new_url()+'/'

        if not requestoid.shouldSendRedirect():
            print 'NE DOIT PAS REDURECTURL !!! je le fait quand meme ?!!'

        direct_url = requestoid.redirectURL(trust_root, return_to, immediate=immediate)
        
        socket.redirection_http(direct_url)

    def openid_step_process(self,interfaces,my_session):
        socket   = interfaces[0]
        sessions = interfaces[1]
        traduct  = interfaces[2]
        database = interfaces[3]
        fs_svn   = interfaces[4]
        log      = interfaces[5]
        config   = interfaces[6]
        datas    = interfaces[7]
        glob     = interfaces[8]
        cookies=socket.get_cookies()

        my_session.set_action_openid(None)
        oidconsumer = self.getConsumer(my_session,socket,cookies)

        url = datas.url_base+my_session.get_futur_new_url()+'/'
        
        info = oidconsumer.complete(socket.get_args(), url)
        
        if info.status == openid.consumer.consumer.FAILURE and info.identity_url:

            self.annule_autoconnect(socket,config)
            fmt = "Verification of %s failed: %s"
            message = fmt % (cgi.escape(info.identity_url),
                             info.message)

            
        elif info.status == openid.consumer.consumer.SUCCESS:

            openidfromform=my_session.get_process_openid_url()
            if cgi.escape(info.identity_url)!=openidfromform:
                self.annule_autoconnect(socket,config)
                message = "retour id incorrectu du server !!!"
                return

            fmt = "You have successfully verified %s as your identity."
            message = fmt % (cgi.escape(info.identity_url),)
            if info.endpoint.canonicalID:
                message += ("  This is an i-name, and its persistent ID is %s"
                            % (cgi.escape(info.endpoint.canonicalID),))

            my_session.set_user(openidfromform,glob,database)

            return

        elif info.status == openid.consumer.consumer.CANCEL:
            # cancelled
            self.annule_autoconnect(socket,config)
            message = 'Verification cancelled'

        elif info.status == openid.consumer.consumer.SETUP_NEEDED:
            my_session.set_action_openid('process')
            OK=2
            if info.setup_url:
                message = '<a href=%s>%s</a>' % ( quoteattr(info.setup_url),
                                                  'Vous devez faire aller sur le serveur d\'identification')
                socket.redirection_http(info.setup_url, message)
                return
            else:
                # todo non-immediate mode.
                message = 'Setup needed'
        else:
            self.annule_autoconnect(socket,config)
            message = 'Verification failed. Dont know why.'

        socket.redirection_http("/" , message)

    def deconnecte(self,my_session,socket,config):
        my_session.deconnecte()
        self.annule_autoconnect(socket,config)

    def stop_sessions(self):
        for alea in self.sessions.keys():
            self.sessions[alea]=None


#TODO CLEAN SESSION pour virer toutes les sessions trop vielles...

def affiche_user_openid(useropenid):
    tmp=useropenid.split('/')
    site='/'.join(tmp[:-1])
    name=tmp[-1]
    return '<div class="papabull"><div class="infobull">%s</div><a href="/user" >%s</a></div>' % (site,name)

