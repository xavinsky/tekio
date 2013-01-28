# -*- coding: utf-8 -*-
from tekio.HTTP import HTTP_Handler, HTTP_Server
from globdatas import GlobTekio

from tekio.sessions import Sessions
from tekio.libtek import log
from tekio.database import Database
from tekio.fssvn import FS_SVN
from tekio.traductions import get_traducteurs

from tekio.parsing import ids_path, get_objets_actifs, get_instances_includes_exec

from tekio.libtek import get_instance_from_infos, utilise_interface

from tekio.listclasses import classes

from tekio.rendus import HTML

class Tekiod(HTTP_Server):

    def __init__(self,config):
        # Chargement config

        self.config=config 

        # Chargement Systeme de log
        self.log=log(config)

        #initialise les sessions (normal et openid)
        self.sessions=Sessions(self.log,config)

        # Database
        self.database=Database(self.log,self.config,config.path['sql'])
                                
        # FS SVN Interface
        #travail dans une base svn pour l'ecriture des modifs du fs.
        self.fs_svn=FS_SVN(config.path['svn'],config.path['files'],self.log)
        #self.fs_svn.creation(repertoiredesdatasinitiales)

        self.traducteurs=get_traducteurs(self.config)

        #Calcul de la base url :
        #TODO check ssl
        port=config.http['port']
        domain=config.http['domain']

        #Creation du serveur et demarrage :
        HTTP_Server.__init__(self, (domain,port), Tekio_Handler, GlobTekio)

        for (k,v) in config.flag_server.items():
            setattr(self,k,v)

        self.glob.langues=self.config.langues
        self.glob.langue=self.config.langues[0]

        self.glob.initialisation(self.database)
        
        print 'Serveur pret' 
        self.start()

    def my_objets(self):
        return((
         self.log,
         self.config,
         self.sessions,
         self.database,
         self.fs_svn,
         self.traducteurs,
         self.glob))

    def my_stop_server(self):
        self.sessions.stop_sessions()
        self.database.stop_database()
        for k in self.traducteurs.keys():
            self.traducteurs[k]=None

        return


class Datas_Handler:
    pass

class Tekio_Handler(HTTP_Handler):

    def my_get_interfaces(self, socket_interface,objs):
        self.interfaces=self.my_interfaces(socket_interface,objs)
        utilise_interface(self,self.interfaces)

    def my_init(self):
        return True

    def my_interfaces(self,socket_interface,objs):

        (log,
         config,
         sessions,
         database,
         fs_svn,
         traducteurs,
         glob)=objs

        datas=Datas_Handler()
        
        return (socket_interface,
                sessions,
                traducteurs,
                database,
                fs_svn,
                log,
                config,
                datas,
                glob)

    def my_handler(self):
        
        self.socket.trace("start my handler")
        
        self.datas.url_base=self.config.http['url_base']
        self.datas.url_proxy=self.config.http['url_proxy']

        self.datas.my_session=self.sessions.get_session(self.interfaces)
        if self.datas.my_session==None:
            # operation open Id => interupt affichage pour redirection open id.
            return False

        self.datas._=self.traduct[self.datas.my_session.get_langue_interface()]


        self.datas.actions_backup=[]
        self.datas.actions_fssvn=[]

        self.datas.my_session.set_new_url(self.socket.path)

        self.datas.classes=classes

        self.datas.rendus={}
        self.datas.templates={}
        self.datas.id_cl={}
        self.datas.instances={}
        self.datas.includes=[]
        self.datas.to_exec=[]
        self.datas.dispos_normals={}
        self.datas.dispos_parents={}
        self.datas.detruit=[]

        self.socket.trace("session ok")

        ids_path(self.datas,self.glob,self.socket,self.log)

        self.datas.objet_actu=get_instance_from_infos(self.datas.infos_objet_actu,
                                                       self.interfaces)
        self.datas.objet_actu.is_actu=True
        self.datas.objet_actu.init_actu()
        self.datas.objet_actu.name_class=self.datas.ids_path[-1][1]

        self.socket.trace("id_path ok")

        #self.log.debug("IDACTU : %s" % self.datas.objet_actu.id )

        if self.datas.objet_actu.is_direct():
            self.socket.trace("action directe")
            self.datas.objet_actu.pre_execution()
            self.datas.objet_actu.action()
        else:
            get_objets_actifs(self.glob,self.datas)

            # on considere ici que le rendu doit etre un rendu HTML
            # on pourra eventuelement ajouter d'autre style
            # genre comme pour direct pour d'autre type d'affichage
            # par exemple, pour pda / xml / rss ou autres...

            self.socket.trace("objets actifs ok")
            get_instances_includes_exec(self.interfaces)
            self.socket.trace("get instance exec ok")

            self.socket.trace("debut header HTML")
            HTML.header(self.interfaces)
            self.socket.trace("fin header HTML")

            for (fct,params) in self.datas.to_exec:
                if fct:
                    self.socket.trace("lance %s(%s)" % (fct,params))
                    if params:
                        fct(params)
                    else:
                        fct()
                else:
                    self.socket.send_datas(params)

            self.socket.trace("debut footer HTML")
            HTML.footer(self.interfaces)

        self.socket.trace("fin action")


        #TODO : enregistrement des svn et sqlbackup pour revert possible.
        if self.datas.actions_backup or self.datas.actions_fssvn:
            for action_backup in self.datas.actions_backup:
                pass
            for action_fssvn in self.datas.actions_fssvn:
                pass
        return True
        self.dbg('fin my_handler HTTP_Handler_Tekio')

    def my_finish(self):
        pass
    

