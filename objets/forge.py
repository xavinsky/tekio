# -*- coding: utf-8 -*-
import os

from tekio.libtek import redirect_ok
from tekio.libtek import check_edit
from tekio.libtek import get_langue, get_langues
from tekio.libtek import action_for_url
from tekio.libtek import utilise_interface
from tekio.libtek import get_instance_from_id
from tekio.objets.base import create_element
from tekio.objets.base import ObjBase
from tekio.objets.base import get_propriete, set_propriete, del_propriete
from tekio.objets.base import id_get_fils_by_name
from tekio.objets.wiki import dispo_add_elem, tpl_placement
from tekio.langues import tablangtrad

"""
format des proprietes

  Format workflow
workflow.<groupe>.<nivel>.<methode>=url
groupe : all / user / myuser

  Format propriete
struct.<name>.type=<type>
struct.<name>.title=<title>
struct.<name>.value=<default>
# facultatif... 


Format propriete dans moule :
struct.<name>.type=<type>
struct.<name>.default=<default>
# facultatif... 
struct.<name>.title=<title>


Format des templates :

/*+<nompropriere>:<methodes>[:<param>[:<param>[:<param>etc...]]]*/


"""

#TYPES
class type_base:
    def __init__(self,interfaces,piece,name,value=None,title=None):
        self.interfaces=interfaces
        self.piece=piece
        self.name=name
        if not title:
            self.title=name
        else: 
            self.title=title
        self.value=value
        self.obj=None

    def create(self,value):
        self.piece.set_propriete('struct.%s.type' % self.name, self.etype)
        self.piece.set_propriete('struct.%s.value' % self.name, value)

    def get_value(self):
        self.value=self.piece.get_propriete('struct.%s.value' % self.name,None)
        return self.value

    def get_obj(self):
        if self.obj:
            return
        self.get_value()
        glob=self.interfaces[8]
        self.id_obj=id_get_fils_by_name(glob,self.piece.id,self.value)
        self.obj=get_instance_from_id(self.interfaces,self.id_obj)

    def affiche(self):
        return "%s : %s <br />" % (self.title,self.value)

    def form(self):
        if not self.value:
            self.value=""
        return """%s : <input type="text" name="%s" value="%s" /><br />""" % (self.title,self.name,self.value)


class type_text(type_base):
    etype='text'

class type_text_r(type_base):
    etype='text_r'
    def form(self):
        return "%s : %s <br />" % (self.title,self.value)


class type_liste(type_base):
    etype='liste'
    def create(self,value):
        self.piece.set_propriete('struct.%s.type' % self.name, self.etype)
        self.piece.set_propriete('struct.%s.value' % self.name, value)

        name_moule_liste=value
        id_moule_liste=create_piece(self.interfaces,self.piece.id,name_moule_liste,name_moule_liste,{})
         
    def get_liste_subs(self):
        self.get_obj()
        glob=self.interfaces[8]
        self.list_subs=glob.objets[self.id_obj]['subs']
        return self.list_subs

    def liste(self,max=None):
        self.get_liste_subs()
        if len(self.list_subs)>0:
            self.obj.affiche_template('headerliste')
            for id_sub in self.list_subs:
                obj_sub=get_instance_from_id(self.interfaces,id_sub)
                self.obj_sub.affiche_template('lineliste')
            self.obj.affiche_template('footerliste')
        else:
            self.obj.affiche_template('listevide')

    def link_new(self,param=None):
        self.get_obj()
        self.obj.affiche_template('linknew')


dico_type_classe={
    'text' : type_text,
    'text_r' : type_text_r,
    'liste' : type_liste,
}


def check_action_workflow(datas,glob,log,workflow,path_r,piece,id_user_p=-10):
    listworkflow=[]
    for (name_group,obj) in workflow.items():
        if name_group in ['all','user','myuser'] or name_group in glob.groupes.keys():
            validsp=False
            interditsp=False
            id_group=False
            if name_group=='all':
                validsp=True
            elif name_group=='user':
                if datas.my_session.id_user!=-1:
                    validsp=True
            elif name_group=='myuser':
                log.debug('myuser')
                log.debug(id_user_p)
                if datas.my_session.id_user!=id_user_p:
                    interditsp=True
                else:
                    validsp=True
                    log.debug("validmyuser")
            else:
                id_group=glob.groupes.get(name_groupe,0)

            if not interditsp and (validsp or (
                    id_group and id_group in datas.my_session.groupes)):
                for (nivel,obj2) in obj.items():
                    for (methode,url) in obj2.items():
                        listworkflow.append((int(nivel),methode,url))

    listworkflow.sort()
    listea4u=[]
    for (nivel,astr,u) in listworkflow:
        amet=getattr(piece,astr)
        listea4u.append((amet,u))
    log.debug(str(listea4u))
    action_for_url(datas,listea4u,path_r,log)


class Forge(ObjBase):
    pass


class Moule(ObjBase):

    def create_piece(self,interfaces,id_piece_pere,name,proprietes={}):
        utilise_interface(self,interfaces)
        self.structure=self.get_dico_proprietes('struct')
        self.workflows=self.get_dico_proprietes('workflow',limit=1)
        self.log.debug("workflows moule %s" % self.id  )
        self.log.debug(str(self.workflows))

        id_type=52

        id_piece=create_element(self.glob,self.database,
                                id_type,id_piece_pere,
                                {'all':name,},proprietes)
        
        piece=get_instance_from_id(interfaces,id_piece)

        self.fs_svn.add_folder(piece.path)

        for (name,dico) in self.structure.items():
            etype=dico['type']
            title=dico.get('title',None)
            default=dico['default']
            cl=dico_type_classe[etype]
            obj=cl(interfaces,piece,name,title=title)
            if name=="id_user":
                default=self.datas.my_session.id_user
            obj.create(default)

        self.log.debug("workflows %s "% id_piece)
        self.log.debug(str(self.workflows))

        for (name,w) in self.workflows.items():
            piece.set_propriete('workflow.%s' % name,w)

        piece.set_propriete('modele', self.get_name())

        listfiles=self.fs_svn.listdir(self.path)
        listfiles.remove('.svn')


        for i in listfiles:
            fi=self.path+'/'+i
            ff=piece.path+'/'+i
            self.fs_svn.add_link(fi,ff)

        return id_piece


def create_piece(interfaces,id_piece_pere,name_moule,name,proprietes={}):
    glob=interfaces[8]
    id_forge=id_get_fils_by_name(glob,0,'forge')
    id_moule=id_get_fils_by_name(glob,id_forge,name_moule)
    moule=get_instance_from_id(interfaces,id_moule)
    id_piece=moule.create_piece(interfaces,id_piece_pere,name,proprietes)
    return id_piece


class Piece(ObjBase):
    def init_actu(self): 
        workflow=self.get_dico_proprietes('workflow')
        id_user_p=int(self.get_propriete('struct.id_user.value',-10))
        check_action_workflow(self.datas,self.glob,self.log,workflow,self.path_r,self,id_user_p)
        ObjBase.init_actu(self)

    def manque_action(self):
        _=self.datas._ 
        self.socket.send_datas(_('Action non definie'))

    def todo(self):
        _=self.datas._ 
        self.socket.send_datas(_('TODO'))
 
    def get_structure(self):  
        self.structure=self.get_dico_proprietes('struct')
        return self.structure
                   
    def need_connect(self):
        _=self.datas._ 
        self.socket.send_datas(_('Vous devez etre connecter pour voir cette page'))
        return


    def user_affiche(self): 
        _=self.datas._ 
        self.get_structure() 
        id_user=int(self.structure.get('id_user',{}).get('value',-10))
        if id_user!=int(self.datas.my_session.id_user):
            self.socket.send_datas(_('Donnee Privee'))
            return
        self.affiche()

    def affiche_template(self,tpl):
        template=self.fs_svn.get(self.path+'/template.%s' % tpl)
        self.get_structure()
        dec=template.split('/*+')
        self.socket.send_datas(dec[0])
        for dec1 in dec[1:]:
            dec2=dec1.split('+*/')
            (name,action)=dec2[0].split(':',1)
            if name=='path':
                self.socket.send_datas(self.path)
            else:
                dec3=action.split(':')
                action=dec3[0]
                params=dec3[1:]
                element=self.structure.get(name,None)
                if element:
                    etype=element.get('type',None)
                    if etype: 
                        cl=dico_type_classe[etype]
                        obj=cl(self.interfaces,self,name)
                        methode=getattr(obj,action)
                        methode(params)

            self.socket.send_datas(dec2[1])

    def affiche(self): 
        self.affiche_template('affiche')


    def affiche_user(self):
        name_moule_user=self.get_propriete('moule_user','')
        id_user=self.datas.my_session.id_user
        id_user_piece=self.get_fils_by_name('user_%s' % id_user)
        
        if id_user_piece==-1:
            id_user_piece=create_piece(self.interfaces,self.id,name_moule_user,'user_%s' % id_user,{})
        user_piece=get_instance_from_id(self.interfaces,id_user_piece)

        self.datas.my_session.set_new_url(self.path+'/user_'+str(id_user)+self.path_r)
        redirect_ok(self.socket,self.datas)

    def admin_affiche_users(self):
        pass
        #TODO user template liste et elem liste
        #Foncions admin : delete / edit / new
        
    def todo(self):
        _=self.datas._ 
        self.socket.send_datas(_('TODO'))

    def form_new(self):
        _=self.datas._ 
        self.affiche_template('form_new')

    def valid_new(self):
        _=self.datas._ 
        self.socket.send_datas(_('VALID'))


    a4u=[]
    f_direct=[affiche_user,]
    action_default=manque_action
