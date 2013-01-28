# -*- coding: utf-8 -*-

from threading import Semaphore
from tekio.utils import list_to_dic
from tekio.libtek import get_instance_from_id, utilise_interface
from tekio.libtek import drop_id

def set_propriete_all(reqset,reqadd,glob,database,id_obj,name,value):
    old=glob.objets[id_obj]['proprietes'].get(name,None)
    if old:
        database.write(reqset,(value,id_obj,name))
    else:
        database.write(reqadd,(id_obj,name,value))
    glob.objets[id_obj]['proprietes'][name]=value

def set_propriete(glob,database,id_obj,name,value):
    return set_propriete_all('set_propriete','add_propriete',
                             glob,database,id_obj,name,value)
def set_propriete_i(glob,database,id_obj,name,value):
    return set_propriete_all('set_propriete_i','add_propriete_i',
                             glob,database,id_obj,name,value)

def del_propriete_all(reqdel,glob,database,id_obj,name):
    database.write(reqdel,(id_obj,name))
    if glob.objets[id_obj]['proprietes'].has_key(name):
        del(glob.objets[id_obj]['proprietes'][name])

def del_propriete(glob,database,id_obj,name):
    return del_propriete_all('del_propriete',glob,database,id_obj,name)

def del_propriete_i(glob,database,id_obj,name):
    return del_propriete_all('del_propriete_i',glob,database,id_obj,name)

def get_propriete(glob,id_obj,name,default=None):
    return glob.objets[id_obj]['proprietes'].get(name,default)
def get_propriete_i(glob,id_obj,name,default=None):
    return get_propriete(glob,id_obj,name,default)

def get_proprietes(glob,id_obj):
    return glob.objets[id_obj]['proprietes']

def put_in_pr_dico(dico,k,v,limit,log):
    if limit==1:
        dico[k]=v
        return
        
    s=k.split('.',1)
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
    put_in_pr_dico(sub,s[1],v,limit-1,log)
            
def get_dico_proprietes(glob,id_obj,name,limit,log):
    prs=glob.objets[id_obj]['proprietes']
    dico={}
    for (k,v) in prs.items():
        s=k.split(name+'.',1)
        if s[0]=="" and len(s)>1:
            put_in_pr_dico(dico,s[1],v, limit,log)
    return dico

def create_element(glob,database,id_classe,id_pere,names,proprietes={}):
    #database id
    database.semaphore_idmax.acquire()
    id_obj=1+database.read1('get_max',())[0]
    database.write('add_type',(id_obj,id_classe))
    database.semaphore_idmax.release()

    for (lang,name) in names.items():
        if name.find('%s')!=-1:
            names[lang]=name % id_obj

    #glob.objets
    glob.ajoute_obj(id_obj,id_pere,id_classe,names)

    #database
    database.write('add_liaison',(id_pere,id_obj,1))

    #proprietes
    for (k,v) in proprietes.items():
        if type(v)==type(1L) or type(v)==type(1):
            set_propriete_i(glob,database,id_obj,k,v)
        else:
            set_propriete(glob,database,id_obj,k,v)
    for (lang,name) in names.items():
        set_propriete(glob,database,id_obj,'name_%s' % lang,name)

    if id_classe==2 or id_classe==4:
        for l in glob.langues:
            glob.get_infos_sous_pages(l,id_pere,recursif=False)

    #fs nada !
    return id_obj

def rename_element(interfaces,id_obj,new_names,only_list=False):
    database = interfaces[3]
    fs_svn   = interfaces[4]
    log      = interfaces[5]
    glob     = interfaces[8]

    obj_instance=get_instance_from_id(interfaces,id_obj)

    old_names=glob.objets[id_obj]['names']
    old_files=obj_instance.listfiles()
    
    glob.set_names(id_obj, new_names)
    # TODO verif nombre de names identique ?!
    for (k,v) in new_names.items():
        obj_instance.set_propriete('name_%s' % k,v)
    new_files=obj_instance.listfiles()
    id_pere=glob.objets[id_obj]['pere']
    obj_pere=glob.objets[id_pere]
    path_pere=obj_pere['path'].values()[0]
    #TODO verif nombre de fichier identique ?!
    for i in range(len(new_files)):
        if old_files[i]!=new_files[i]:
            old_file='%s/%s' % (path_pere,old_files[i])
            new_file='%s/%s' % (path_pere,new_files[i])
            fs_svn.move(old_file,new_file)

    if glob.objets[id_obj]['type']==2:
        for l in glob.langues:
            glob.get_infos_sous_pages(l,id_pere)

def drop_dispo_in_instance(pere_instance,id):
    dispo=pere_instance.get_propriete("dispo_normal",'=')
    new_dispo=drop_id(id,dispo)
    pere_instance.set_propriete("dispo_normal",new_dispo)
    dispo=pere_instance.get_propriete("dispo_parent",'#')
    new_dispo=drop_id(id,dispo)
    pere_instance.set_propriete("dispo_parent",new_dispo)

def detruire_element(interfaces,id,prems=True):
    database = interfaces[3]
    fs_svn   = interfaces[4]
    log      = interfaces[5]
    datas    = interfaces[7]
    glob     = interfaces[8]

    # racine indestructible.
    if id==0:
        return

    # get instance
    datas.detruit.append(id)
    elem_instance=get_instance_from_id(interfaces,id)
    if not elem_instance:
        print 'pas possible de detruire %s : no instance ' % id
        return

    id_pere=glob.objets[id]['pere']
    pere_instance=get_instance_from_id(interfaces,id_pere)
    if prems:
        drop_dispo_in_instance(pere_instance,id)

    #detruire les enfants.
    # TODO detruire les fils seulement si unique reference
    # lorsque l'on fera des liens symboliques...
    subs=glob.objets[id]['subs']
    for sub in subs:
        if not sub in datas.detruit:
            detruire_element(interfaces,sub,prems=False)

    # destruction fichier (vers poubelle)
    files=elem_instance.listfiles()
    for f in files:
        filepath=pere_instance.path+'/'+f
        if fs_svn.exist(filepath):
            fs_svn.trash(filepath)

    # destruction objet dans glob
    glob.delete_obj(id)

    purge_db_element(interfaces,id)

def purge_db_element(interfaces,id):
    database = interfaces[3]

    # racine indestructible.
    if id==0:
        return

    database.write('del_classe',id)
    database.write('del_proprietes',id)
    database.write('del_proprietes_i',id)
    database.write('del_liaisons',(id,id))


def deplace_element(interfaces,id,id_new_pere):
    database = interfaces[3]
    fs_svn   = interfaces[4]
    log      = interfaces[5]
    datas    = interfaces[7]
    glob     = interfaces[8]

    if id==0:
        #pas de deplacement de la racine
        return
    id_old_pere=glob.objets[id]['pere']
    if id_old_pere==id_new_pere:
        # pas de deplacement (meme endroit)
        return

    obj_instance=get_instance_from_id(interfaces,id)
    pere_instance=get_instance_from_id(interfaces,id_old_pere)

    files_names=obj_instance.listfiles()
    old_path=pere_instance.path
    new_path=glob.objets[id_new_pere]['path'].values()[0]
    for file_name in files_names:
        old_file='%s/%s' % (old_path,file_name)
        new_file='%s/%s' % (new_path,file_name)
        fs_svn.move(old_file,new_file)

    drop_dispo_in_instance(pere_instance,id)
    database.write('del_liaison',(id_old_pere,id))
    database.write('add_liaison',(id_new_pere,id,1))

    glob.deplace_obj(id,id_old_pere,id_new_pere)

def id_get_fils_by_name(glob,id_pere,name):
    urls_dicos=glob.objets[id_pere]['urls']
    for (lang,urls_dico) in urls_dicos.items():
        for (name_e,id_e) in urls_dico.items():
            if name==name_e:
                return id_e
    return -1

class ObjBase:

    def __init__(self,ido,interfaces,path_f,path_r):
        self.id=ido

        self.path_entier=path_f+path_r
        self.path=path_f
        self.path_r=path_r

        self.interfaces=interfaces
        utilise_interface(self,interfaces)
        self.is_actu = False
        self.initialise()


    def initialise(self):
        pass

    def init_actu(self):
        if self.datas.action:
            self.action=getattr(self,self.datas.action)
        else:
            self.action=self.action_default

    def is_direct(self):
        namesdirect=[]
        for f in self.f_direct:
            namesdirect.append(f.__name__)
        return self.action.__name__ in namesdirect

    def includes(self):
        return []

    def pre_execution(self):
        return

    def affiche(self):
        return 

    def confirm_detruire(self):
        self.pre_execution()
        self.affiche()
        

    def sendbinary(self,path=None):
        if not path:
            path=self.path_entier
        fileinfiles=self.config.path['files']+path

        self.socket.send_binary_file(fileinfiles)


    def action_element_edit_form(self):
        self.socket.send_error("Cet element n'a pas de formulaire d'edition.")

    def get_propriete(self,name,default=None):
        return get_propriete(self.glob,self.id,name,default)

    def get_proprietes(self):
        return get_proprietes(self.glob,self.id)
    proprietes=property(get_proprietes)

    def get_dico_proprietes(self,name,limit=-1):
        return get_dico_proprietes(self.glob,self.id,name,limit,self.log)
            
    def set_propriete(self,name,value):
        set_propriete(self.glob,self.database,self.id,name,value)

    def del_propriete(self,name):
        del_propriete(self.glob,self.database,self.id,name)

    def rename(self,new_names,only_list=False):
        rename_element(self.interfaces,self.id,new_names,only_list)

    def get_parent(self):
        return self.glob.objets[self.id]['pere']

    def get_name(self):
        lang=self.datas.my_session.langue
        return self.glob.get_name_by_id(self.id,lang)

    def get_names(self):
        try:
            return self.glob.objets[self.id]['names'].values()
        except:
            return []

    def get_fils_by_name(self,name):
        return id_get_fils_by_name(self.glob,self.id,name)

    def listfiles(self):
        return self.get_names()
    
    def se_deplacer(self,id_new_pere):
        deplace_element(self.interfaces,self.id,id_new_pere)

    a4u=[]
    f_direct=[]
    action_default=affiche


