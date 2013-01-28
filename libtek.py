# -*- coding: utf-8 -*-
import string 
import datetime
import time
import os
import threading
import traceback
import re

from tekio.utils import PseudoSemaphore
from tekio.utils import slash_to_list_int

#mettre a jour regulierement...
names_classes={
    0  : 'Racine',
    1  : 'Admin',
    2  : 'Page',
    3  : 'Folder',
    4  : 'Galerie',
    5  : 'Menu',
    6  : 'Palette',
    7  : 'Login',
   11  : 'Texte',
   12  : 'Image',
   13  : 'File',
   20  : 'Navigation',
   30  : 'Skin',
   31  : 'SkinPart',
   32  : 'Skins',
   40  : 'Utilisateur',
   41  : 'Groupe',
   50  : 'Forge',
   51  : 'Moule',
   52  : 'Piece',
  100  : 'ImageAleatoire',
}


##########################
## logs
##########################

class log:

    file_default='logs.txt'
    
    def __init__(self,config,fichier=None,clean=False):
        self.ERR=1
        self.WARN=3
        self.INFO=5
        self.DEBUG=7
        self.TRACE=9
        self.config=config
        if config.flags_semaphores['logs']:
            self.semaphore_log=threading.Semaphore()
        else:
            self.semaphore_log=PseudoSemaphore()
        if fichier:
            self.file_default=fichier
        self.clean=clean


    def verif(self,fichier,niv):
        if not fichier:
            fichier=self.file_default
        if not niv:
            niv=self.ERR
        fichier=self.config.logs_redirect.get(fichier,fichier)
        level_max=self.config.logs_levels.get(fichier,self.config.logs_levels.get('default',10))
        if niv > level_max:
            return None
        return fichier

    def traceback(self,file=None,niv=None):
        file=self.verif(file,niv)
        if file:
            self.semaphore_log.acquire()
            try:
                f=open('%s/%s' % (self.config.path['logs'],file) , 'a' )
                f.write('[%s]%s : %s\n' % (niv,datetime.datetime.now(),"==== TRACEBACK START ===="))
                traceback.print_exc(file=f)
                f.write('[%s]%s : %s\n' % (niv,datetime.datetime.now(),"===== TRACEBACK END ====="))
                f.close()
            except:
                pass
            self.semaphore_log.release()

    def L(self,niv,text,file=None):
        file=self.verif(file,niv)
        if file:
            self.semaphore_log.acquire()
            try:
                f=open('%s/%s' % (self.config.path['logs'],file) , 'a' )
                if self.clean:
                    f.write('%s\n' % text)
                else:
                    f.write('[%s]%s : %s\n' % (niv,datetime.datetime.now(),text))
                f.close()
            except:
                pass
            self.semaphore_log.release()

    def err(self,text,file=None):
        self.L(self.ERR,text,file)
    def warn(self,text,file=None):
        self.L(self.WARN,text,file)
    def info(self,text,file=None):
        self.L(self.INFO,text,file)
    def debug(self,text,file=None):
        self.L(self.DEBUG,text,file)
    def trace(self,text,file=None):
        self.L(self.TRACE,text,file)


##########################
## languages
##########################

def get_langues(datas,config):
    try:
        return datas.my_session.langues
    except:
        return config.langues
        
def get_langue(datas,config):
    return get_langues(datas,config)[0]


##########################
## droits
##########################

def check_admin(datas,socket,alerte=True):
    if datas.my_session.is_admin:
        return True
    elif alerte:
        _=datas._
        socket.send_datas(_(" Vous n'etes pas administrateur ou non connecte "))
    return False

def check_edit(datas,socket,alerte=True):
    if datas.my_session.is_edit:
        return True
    elif alerte:
        _=datas._
        socket.send_datas(_(" Vous n'etes pas editeur ou non connecte "))
    return False

##########################
## redirection
##########################

def redirect_ok(socket,datas):
    socket.redirection_http('%s%s' % (datas.url_base,datas.my_session.get_new_url()), "Action Ok")

##########################
## interfaces
##########################
def utilise_interface(obj,interfaces):
    obj.socket   = interfaces[0]
    obj.sessions = interfaces[1]
    obj.traduct  = interfaces[2]
    obj.database = interfaces[3]
    obj.fs_svn   = interfaces[4]
    obj.log      = interfaces[5]
    obj.config   = interfaces[6]
    obj.datas    = interfaces[7]
    obj.glob     = interfaces[8]

##########################
## parsing
##########################
def action_for_url(datas,listea4u,path_r,log):
    if path_r=="":
        path_r='/'
    finish=False
    for (a,u) in listea4u:
        if not finish:
            u='/'+u
            if u.find('*')!=-1:
                ur='^'+u.replace('*','[\w_\-.]+')+'$'
                if re.match(ur,path_r):
                    datas.action=a.__name__
                    ut=u.split('*')
                    tmp_u=path_r
                    while ut:
                        elem=ut.pop(0)
                        if elem:
                            (p,tmp_u)=tmp_u.split(elem,1)
                        else:
                            p=tmp_u
                            tmp_u=''
                        datas.action_params.append(p)
                    datas.action_params.pop(0)
                    finish=True
            else:
                if u==path_r :
                    datas.action=a.__name__
                    finish=True


##########################
## instance
##########################

def get_classe(glob,id_o):
    return glob.objets[id_o].get("type",None)

def get_instance_from_infos(infos,interfaces):
    (id_i,cl_i,path_f,path_r)=infos
    datas    = interfaces[7]
    o=datas.instances.get(id_i,None)
    if o :
        return o
    c=datas.classes[cl_i]
    o=c(id_i,interfaces,path_f,path_r)
    datas.instances[id_i]=o
    return o

def get_instance_from_id(interfaces,id_i):
    log      = interfaces[5]
    datas    = interfaces[7]
    glob     = interfaces[8]

    cl_i=get_classe(glob,id_i)
    if cl_i==None:
        return None
    path=glob.get_path_by_id(id_i,datas.my_session.langue)
    infos=(id_i,cl_i,path,'')
    return get_instance_from_infos(infos,interfaces)


##########################
## dispositions 
##########################

    
def drop_id(id,dispo=''):
    newdispo=False
    try:  
        newdispo=drop_id_wiki(id,dispo)
    except:
        pass
    if not newdispo:
        newdispo=drop_id_normal(id,dispo)
    return newdispo

def drop_id_normal(id,dispo):
        newdispo=[]
        dispo2=dispo.replace(']',',]')
        decdispo=dispo2.split('[')

        for dec1 in  decdispo:
            dec2=dec1.split(':',1)
            if len(dec2)>1:
                base=dec2[0]+':'
                listedec=dec2[1]
            else:
                base='' 
                listedec=dec2[0]

            if listedec.find(str(id)+',')==0:
                listedec=listedec.replace(str(id)+',','')
                base=''

            newelems=[]
            elems=listedec.split(',')
            for elem in elems:
                drop=False
                if elem<>str(id):
                    newelems.append(elem)

            newdispo.append(base+','.join(newelems))

        tmp='['.join(newdispo)
        tmp=tmp.replace(',,',',')
        tmp=tmp.replace(',,',',')
        tmp=tmp.replace(',]',']')
        tmp=tmp.replace('[]','')
        tmp=tmp.replace('[]','')
        tmp=tmp.replace(',,',',') 
        tmp=tmp.replace(",[line:[col1:]]",'')
        value=tmp.replace(',,',',')
        return value

def drop_id_wiki(id,dispo):

        flagmodif=False 
        sep="="
        (h,wikitmp2)=dispo.split('=',1) 


        linesbruts=wikitmp2.split(',[line:')
        if linesbruts[0]=='':
            linesbruts=linesbruts[1:]

        lines=[]
        for line in linesbruts:

            colsbruts=line.split(',[col')
            cols=[]
            for colbrut in colsbruts:
                if colbrut!='':
                
                    col=colbrut.replace('[col','').split(":",1)[1][:-1]
                    verifcol=col.split(':')[1][:-1]

                    if int(id)!=int(col):
                        cols.append(col)
                    else: 
                        flagmodif=True

            nbcols=len(cols)
            if nbcols>0:
                col4join=[]
                for c in cols:
                    col4join.append('[col%s:%s]' % (nbcols,c))

                line=','.join(col4join)
                lines.append(line)

        line4join=[]
        for l in lines:
            line4join.append('[line:%s]' % l)

        newdispo=h+sep+","+','.join(line4join)
        if flagmodif:
            return newdispo

        return False

def extract_objets_ids(self):
            
        dispo=self.dispo.replace(']',',]')
        decdispo=dispo.split('[')
        resultats=[]
        for dec1 in  decdispo:
            dec2=dec1.split(':',1)
            if len(dec2)>1:
                listedec=dec2[1]
            else:
                listedec=dec2[0]
            elems=listedec.split(',')
            for elem in elems:
                try:
                    resultats.append(int(elem))
                except:
                    pass
        return resultats

def move_id_wiki(dispo,idelem,posline,poscol,solo):

        (h,str_lines)=dispo.split('=')

        tab_lines=str_lines.split(',[line')
        if tab_lines[0]=='':
            tab_lines=tab_lines[1:]

        poslineactu=1
        addflag=False
        lines=[]
        class_elem_actu=""
        
        for line in tab_lines:
            if solo and posline==poslineactu:
                lines.append(('','[col1:ELEMMOVESP]'))
                addflag=True

            
            (line_info,str_cols)=line.split(':',1)
            str_cols=str_cols[:-1]

            if str_cols!='':
                str_cols=','+str_cols
                tab_cols=str_cols.split(',[col')
                if tab_cols[0]=='':
                    tab_cols=tab_cols[1:]

                cols=[]
                
                for col in tab_cols:
                    (col_info,str_elems)=col.split(':',1)
                    str_elems=str_elems[:-1]
                    if str_elems!='':
                        str_elems=','+str_elems


                        dec_col_info=col_info.split(' ',1)
                        if len(dec_col_info)==1:
                            class_col=''
                        else:
                            (col_info,class_col)=dec_col_info
                            class_col=' '+class_col
                        dec_col_info=col_info.split('_',1)
                        if len(dec_col_info)==1:
                            largeur_col=1
                        else:
                            largeur_col=int(dec_col_info[1])
                        
                        if str_elems!='':
                            tab_elems=str_elems.split(',[elem')
                            if tab_elems[0]=='':
                                tab_elems=tab_elems[1:]

                            elems=[]
                            for elem in tab_elems:
                                (elem_info,str_id)=elem.split(':',1)
                                str_id=str_id[:-1]

                                dec_elem_info=elem_info.split(' ',1)
                                if len(dec_elem_info)<2:
                                    class_elem=''
                                else:
                                    class_elem=' '+dec_elem_info[1]

                                int_id=None
                                try:
                                    int_id=int(str_id)
                                except:
                                    print "erreur conversion str_id ?? : %s"  % str_id

                                if int_id and int(idelem)!=int_id:
                                    elems.append('[elem%s:%s]' % (class_elem,str_id))
                                else:
                                    class_elem_actu=class_elem
                                
                            if len(elems)>0:
                                cols.append(  ( class_col,largeur_col,','.join(elems) )  )

                if len(cols)>0:
                    nbcols=0
                    for (cl,largeur,elems) in cols:
                        nbcols+=largeur
                    if not solo and posline==poslineactu :
                        nbcols+=1

                    col4join=[]
                    for (cl,largeur,elems) in cols:
                        str_largeur=''
                        if largeur!=1:
                            str_largeur='_%s' % largeur
                        col4join.append('[col%s%s%s:%s]' % (nbcols,str_largeur,cl,elems) )
                    if not solo and posline==poslineactu:
                        col4join.insert(poscol,'[col%s:ELEMMOVESP]' % nbcols)
                        addflag=True

                    if len(col4join)!=0:
                        lines.append(  ( line_info,','.join(col4join) )  )

            poslineactu+=1

        if not addflag:
            lines.append(('','[col1:ELEMMOVESP]'))

        line4join=[]
        for (cl,line) in lines:
            line4join.append('[line%s:%s]' % (cl,line))

        newdispo=h+"=,"+','.join(line4join)

        newdispo=newdispo.replace('ELEMMOVESP','[elem%s:%s]' % (class_elem_actu,str(idelem)) )

        return newdispo
