# -*- coding: utf-8 -*-

######## TODO

###### DANGER INSTALL : NECCESSTE SVN FRANCAIS
###### certain de grep fonctionne avec du svn Francais !!!
###### faire patch pour que cela fonctionne dans les autres langues...

###### LOGS 
###### sortie des commande svn du nohup vers les logs

###### change auteur de la modification ??!! si possible avec openid !
###### remarque, il semble possible gerer l'authentification par pam
###### et de regler un truc specifique pour ca !!

###### Le semaphore devrai englober l'action svn en plus du commit et du get revision.
###### la on peux avoir une action qui se deplace dans un autre commit par erreur...

import os
import popen2
import tempfile
import threading
import datetime
import Image
from tekio.utils import system_ret, system_no_ret
from tekio.utils import format_path, path_to_liste
from tekio.utils import name_from_path, path_pere
from tekio.utils import utos
from tekio.utils import size_human_file

class FS_SVN:
    def __init__(self,reposvn,dataread,log):
        self.reposvn=reposvn
        self.dataread=format_path(dataread)
        self.semaphore_svn=threading.Semaphore()
        self.log=log

    def prepare_fstmp(self,repref=None):
        fsreptmp = tempfile.mkdtemp()
        if repref!=None:
            system_no_ret("""cp -r "%s%s/.svn" "%s" """  % (self.dataread,repref,fsreptmp))
        return fsreptmp

    def creation(self,initdata,create_server=True,delete_trash=True):
        if create_server:
            system_no_ret("""rm -Rf "%s" """ % self.reposvn )
            system_no_ret("""mkdir -p "%s" """ % self.reposvn )
            system_no_ret("""svnadmin create "%s" """ % self.reposvn) 
        if initdata:
            msg='import initial'
            if delete_trash:
                system_no_ret("""rm -Rf "%s/trash" """ % initdata )
            system_no_ret("""mkdir -p "%s/trash" """ % initdata )
            system_no_ret("""cd "%s" && recursif "rm -Rf .svn" """ % initdata)
            system_no_ret("""svn import "%s" "file://%s" -m "%s" """ % (initdata,self.reposvn,msg))

        system_no_ret("""rm -Rf "%s" """ % self.dataread)
        system_no_ret("""mkdir -p "%s" """ % self.dataread)
        system_no_ret("""svn checkout "file://%s" "%s" """ % (self.reposvn,self.dataread))

    def get_rev(self,path):
        path=format_path(path)
        ret=system_ret("""svn info  "%s%s" |grep vision| grep difica""" % (self.dataread,path))
        #grep francophone !!!
        try:
            r=int(ret.split(':',1)[1].split('/n')[0].strip())
        except:
            self.log.debug(path)
            self.log.debug(ret)
            r=0
        return r

    def date(self,path,rev=None):
        path=format_path(path)
        if rev:
            txtrev="-r %s " % rev
        else:
            txtrev=""
        filename='%s%s' % (self.dataread,path)
        ret=system_ret("""svn info %s "%s" |grep Date| grep difica""" % (txtrev,filename))
        #grep francophone !!!
        datestr=ret.split(':',1)[1].split('(')[0].strip()
        return datestr

    def get_revs(self,path):
        path=format_path(path)
        filename='%s%s' % (self.dataread,path)
        ret=system_ret("""svn log  "%s" """ % filename )
        mods=ret.split('------------------------------------------------------------------------')
        ids=[]
        for m in mods:
            try:
                v=int(m.split('|',1)[0].strip()[1:])
                ids.append(v)
            except:
                pass
        return ids

    def diff(self,path,r1,r2):
        path=format_path(path)
        if r1>r2:
            r3=r1
            r1=r2
            r2=r3
        try:
            filename='%s/%s' % (self.dataread,path)
            ret=system_ret("""svn diff -r %s:%s "%s" """ % (r1,r2,filename) )
            diff=ret.split('\n',4)[4]
            return diff
        except:
            return None

    def commit(self,actions,message,tmpcommit,tmpbase):
        self.semaphore_svn.acquire()
        new_rev=None
        #test

        #try:
        if 1:
            for action in actions:
                self.log.debug(action)
                system_no_ret(action)

            if not message:
                message="commit %s " % str((actions,message,tmpcommit)).replace('"',"%")

            if type(tmpcommit)==type(u''):
                tmpcommit=utos(tmpcommit)

            if type(tmpcommit)==type(''):
                cmd=""" svn commit -m "%s" "%s" """  % (message,tmpcommit)
                self.log.debug(cmd)
                system_no_ret(cmd)

            elif type(tmpcommit)==type([]):
                for tc in tmpcommit:
                    cmd="""svn commit -m "%s" "%s" """  % (message,tc)
                    self.log.debug(cmd)
                    system_no_ret(cmd)
                
            cmd="""svn update "%s" """  % self.dataread
            self.log.debug(cmd)
            system_no_ret(cmd)
            new_rev=self.get_rev("")

        #except:
        #    message=""
        #    try:
        #        message="ERROR commit %s " % str((actions,message,tmpcommit)).replace('"',"%")
        #    except:
        #        message='ERROR COMMIT'
        #    new_rev=None
        #    self.semaphore_svn.release()
        #    raise(message)
        
        
        self.semaphore_svn.release()
        #system_no_ret('rm -Rf %s' % tmpbase, check=False)
        return new_rev


    def get(self,path,rev=None):
        path=format_path(path)
        if not rev:
            try:
                f=open("%s%s" % (self.dataread,path))

                ret=f.read()
                f.close()
                return ret
            except:
                return None
        else:
            fsreptmp = tempfile.mkdtemp()
            system_no_ret("""svn export -r %s "%s%s" "%s/file" """ % (rev,self.dataread,path,fsreptmp))
            f=open("%s/file" % (fsreptmp))
            ret=f.read()
            f.close()
            return ret

    def get_image(self,path):
        f=Image.open("%s%s" % (self.dataread,path))
        return f

    def set_image(self,obj_img,path):
        #l'image n'est pas dans le svn !!
        obj_img.save("%s%s" % (self.dataread,path))
   
    def modif(self,path,data,msg=None,binary=False):
        self.log.debug("MODIF")
        path=format_path(path)
        if path=='':
            #la racine n'est pas un fichier.
            return
        pere=path_pere(path)
        name=name_from_path(path)

        fsreptmp=self.prepare_fstmp(pere)

        if binary:
            acces='wb'
        else:
            acces='w'

        f=open('%s/%s' % (fsreptmp,name),acces)
        f.write(data)
        f.close()

        actions=[]
        message=msg
        if not message:
            message = "Modifie fichier %s " % path
        tmpcommit=fsreptmp+'/'+name
        new_rev=self.commit(actions,message,tmpcommit,fsreptmp)

        return new_rev

    def add_folder(self,path,msg=None):
        self.log.debug("ADDFOLDER")
        path=format_path(path)
        if path=='':
            #on ne peux creer la racine (elle existe deja)
            return
        pere=path_pere(path)
        name=name_from_path(path)

        fsreptmp=self.prepare_fstmp(pere)

        system_no_ret("""mkdir "%s/%s" """  %  (fsreptmp,name))
        
        actions=[("""svn add "%s/%s" """  %  (fsreptmp,name)),]
        message=msg
        if not message:
            message = "Ajouter Repertoire %s " % path
        tmpcommit=fsreptmp+'/'+name
        new_rev=self.commit(actions,message,tmpcommit,fsreptmp)

        return new_rev

    def add_link(self,pathlinkinit,pathlinkfinal,msg=None):
        self.log.debug("ADDLINK")
        pathlinkinit=format_path(pathlinkinit)
        pathlinkfinal=format_path(pathlinkfinal)

        perefinal=path_pere(pathlinkfinal)
        namefinal=name_from_path(pathlinkfinal)

        fsreptmp = self.prepare_fstmp(perefinal)

        #TODO BEST : lien en relatif et pas en absolu
        # pour permettre le deplacement dans un autre repertoire du contenu.
        system_no_ret("""ln -s "%s/%s" "%s/%s" """  %  (self.dataread,pathlinkinit,fsreptmp,namefinal))

        actions=[("""svn add "%s/%s" """  %  (fsreptmp,namefinal)),]
        message=msg
        if not message:
            message="Ajout lien symbolique %s => %s " % (pathlinkinit,pathlinkfinal)
        tmpcommit=fsreptmp+'/'+namefinal
        new_rev=self.commit(actions,message,tmpcommit,fsreptmp)

        return new_rev


    def add(self,path,data,msg=None,binary=False):
        path=format_path(path)
        if path=='':
            return
        pere=path_pere(path)
        name=name_from_path(path)
        fsreptmp=self.prepare_fstmp(pere)
        if binary:
            acces='wb'
        else:
            acces='w'
        f=open('%s/%s' % (fsreptmp,name),acces)
        f.write(data)
        f.close()

        actions=[("""svn add "%s/%s" """  %  (fsreptmp,name)),]
        message=msg
        if not message:
            message="Ajouter fichier %s " % path
        tmpcommit=fsreptmp+'/'+name
        new_rev=self.commit(actions,message,tmpcommit,fsreptmp)

        return new_rev

    def delete(self,path,msg=None):
        self.log.debug("DELETE")
        ### Ne pas appeler directemer dans les modules,
        ### prefere appeler trash pour garder le contenu.
        path=format_path(path)
        if path=='':
            #on ne peux detruire la racine
            return
        pere=path_pere(path)
        name=name_from_path(path)

        fsreptmp=self.prepare_fstmp(pere)

        system_no_ret("""cp -r "%s%s" "%s" """  % (self.dataread,path,fsreptmp))

        actions=[("""svn del "%s/%s" """   %  (fsreptmp,name)),]
        message=msg
        if not message:
            message="Detruit fichier %s " % path
        tmpcommit=fsreptmp+'/'+name
        new_rev=self.commit(actions,message,tmpcommit,fsreptmp)

        return new_rev

    def move(self,pathinit,pathfinal,msg=None):
        self.log.debug("MOVE")
        pathinit=format_path(pathinit)
        pathfinal=format_path(pathfinal)
        if (pathinit==pathfinal):
            # destination = arrive !! pas de deplacement
            return
        if not self.exist(pathinit):
            # l'objet a deplacer n existe pas dans le fs.
            return 
        if (pathinit==''):
            # on ne peux deplacer la racine
            return

        li=path_to_liste(pathinit)   #liste path init
        lf=path_to_liste(pathfinal)  #liste path final

        lc=[] # liste path commun
        acontinuer=True
        while acontinuer:
            if len(li)>0 and len(lf)>0 and li[0]==lf[0]:
                lc.append(li.pop(0))
                lf.pop(0)
            else:
                acontinuer=False
                
        ri=format_path('/'.join(li))   # path repertoire initial sans le commun.
        rf=format_path('/'.join(lf))   # path repertoire final sans le commun.
        rc=format_path('/'.join(lc))   # path repertoire commun 

        if ri=='':
            #ne peux pas deplacer un repertoire dans lui meme....
            return

        fscommun='%s%s' % (self.dataread,rc)

        # cree la structure temporaire svn dans 
        fsreptmp=self.prepare_fstmp(rc)

        # cree la structure temportaire des repertoire initaux
        for i in range(len(li)-1):
            rep=format_path('/'.join(li[:i+1]))
            if rep!='':
                self.log.debug("prepare inital %s " % rep)
                system_no_ret("""mkdir "%s%s" """  % (fsreptmp,rep))
                system_no_ret("""cp -r "%s%s/.svn" "%s%s" """  % (fscommun,rep,fsreptmp,rep))
                
        # copie le repertoire ou le fichier a deplacer
        if self.isdir(pathinit):
            self.log.debug("copie dir %s  " % ri)
            system_no_ret("""cp -r "%s%s" "%s%s" """  % (fscommun,ri,fsreptmp,ri))
        else:
            self.log.debug("copie file %s  " % ri)
            system_no_ret("""cp "%s%s" "%s%s" """  % (fscommun,ri,fsreptmp,ri))

        # cree la structure temportaire des repertoire finaux

        for i in range(len(lf)-1):
            rep=format_path('/'.join(lf[:i+1]))
            if rep!='':
                self.log.debug("prepare final  %s " % rep)
                if not self.exist(rep):
                    self.add_folder(rep)
                system_no_ret("""mkdir "%s%s" """  % (fsreptmp,rep))
                system_no_ret("""cp -r "%s%s/.svn" "%s%s" """  % (fscommun,rep,fsreptmp,rep))
            else:
                system_no_ret("""cp -r "%s/.svn" "%s" """  % (fscommun,fsreptmp))


        # si la destination est un repertoire, preparation structure.
        if self.exist(pathfinal):
            if self.isdir(pathfinal):
                self.log.debug("prepare final folder %s " % rf)
                system_no_ret("""mkdir "%s%s" """  % (fsreptmp,rf))
                system_no_ret("""cp -r "%s%s/.svn" "%s%s" """  % (fscommun,rf,fsreptmp,rf))


        #definition svn move et commit

        actions=[("""svn move "%s%s" "%s%s" """  %  (fsreptmp,ri,fsreptmp,rf)),]
        self.log.debug(str(actions))
        message=msg
        if not message:
            message="move %s => %s" % (pathinit,pathfinal)
        tmpcommit=[fsreptmp+ri,fsreptmp+rf]
        self.log.debug('commits')
        self.log.debug(str(tmpcommit))
        new_rev=self.commit(actions,message,tmpcommit,fsreptmp)

        # returne la revision actuelle.
        return new_rev

    def trash(self,path,msg=None): 
        self.log.debug("TRASH")
        path=format_path(path)
        if path=='':
            #on ne peux pas mettre la racine dans trash
            return
        pere=path_pere(path)
        name=name_from_path(path)

        dt=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pathtrash="/trash/%s" % dt

        self.log.debug('create  %s' % pathtrash)
        new_rev=self.add_folder(pathtrash)

        pathtrashobj="%s/%s" % (pathtrash,name)
        message="Trash : %s => %s " % (path,pathtrashobj)
        self.log.debug(message)

        new_rev=self.move(path,pathtrashobj)
        
        return (new_rev,dt)


    def listdir(self,path):
        path=format_path(path)
        filename='%s%s' % (self.dataread,path)
        return os.listdir(filename)

    def exist(self,path):
        path=format_path(path)
        filename='%s%s' % (self.dataread,path)
        return os.path.lexists(filename) and os.access(filename,os.F_OK) and os.access(filename,os.R_OK) 

    def isdir(self,path):
        path=format_path(path)
        filename='%s%s' % (self.dataread,path)
        return os.path.isdir(filename)

    def size_human_file(self,path):
        filename='%s%s' % (self.dataread,path)
        return size_human_file(filename)

