# -*- coding: utf-8 -*-
import os
import random

from tekio.libtek import redirect_ok
from tekio.libtek import check_edit
from tekio.libtek import get_langue
from tekio.utils import new_name_file

from tekio.utils import list_to_dic
from tekio.utils import path_pere, name_from_path

from tekio.objets.base import ObjBase
from tekio.objets.base import create_element , get_proprietes, set_propriete
from tekio.objets.base import get_dico_proprietes

from tekio.objets.wiki import dispo_add_elem, tpl_placement

import Image

cpr=Image.ANTIALIAS
# Image.ANTIALIAS)    # best down-sizing filter
# Image.NEAREST)      # use nearest neighbour
# Image.BILINEAR)     # linear interpolation in a 2x2 environment
# Image.BICUBIC)      # cubic spline interpolation in a 4x4 environment

def dimentions(fs_svn,path,old_name,new_x):
    i=fs_svn.get_image('%s/%s' % (path,old_name))
    (initx,inity)=i.size
    new_y=int(int(new_x)*inity/initx)
    return (new_x,new_y)

def redimentionne(fs_svn,path,old_name,new_x):
    di=old_name.split('.')
    tplname='.'.join(di[:-1])+'-%spx.'+di[-1]
    name=tplname % new_x

    if fs_svn.exist('%s/%s' % (path,name)):
        return name

    i=fs_svn.get_image('%s/%s' % (path,old_name))
    (initx,inity)=i.size
    new_y=int(int(new_x)*inity/initx)
    new_i = i.resize((int(new_x), int(new_y)), cpr)

    fs_svn.set_image(new_i,'%s/%s' % (path,name))

    return name


def add_Image_Form(datas):
    _=datas._
    return """
<div class="label">%s</div> : <input type="texte" name="titre" /><br />
<div class="label">%s</div> : <input type="texte" name="lien" /> <br />
<div class="label">%s</div> : <input type="texte" name="css" /> <br />
<div class="label">%s</div> : <input type="file" name="image" /><br />""" %(_("Titre image"),
                                                                            _("Lien image"),
                                                                            _("Classe css"),
                                                                            _('Fichier Image'))

def edit_Image_Form(datas,path,titre,lien,cl_css):
    _=datas._
    return """
<img src="%s%s" class="vignette" /><br />
<div class="label">%s</div> : <input type="texte" name="titre" value="%s" /><br />
<div class="label">%s</div> : <input type="texte" name="lien" value="%s" /> <br />
<div class="label">%s</div> : <input type="texte" name="css" value="%s" /> <br />
<div class="label">%s</div> : <input type="file" name="image" /><br />""" %( datas.url_base,
                                                                             path,
                                                                            _("Titre image"),
                                                                             titre,
                                                                            _("Lien image"),
                                                                             lien,
                                                                            _("Classe css"),
                                                                             cl_css,
                                                                            _("Changer l'image"))

def ajoute_image_form(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        self.socket.send_datas(_('connectez vous...'))
        return

    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path
    template="""
%s :
<form action="%s/ajoute_image" method="POST" enctype="multipart/form-data" id="panneauform">
%s
<br />
<br />
%s
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
""" % (_('Ajouter une Image'),baseurl,
       add_Image_Form(self.datas),tpl_placement(self.datas),
       _('Valider'))
    self.socket.send_datas(template)

def ajoute_image(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        self.socket.send_datas(_('connectez vous...'))
        return
    #lang=get_langue(self.datas,self.config)

    titre=self.socket.input_text_value('titre')
    lien=self.socket.input_text_value('lien')
    cl_css=self.socket.input_text_value('css')

    pere_id=self.datas.objet_actu.id
    pere_path=self.datas.objet_actu.path
    fileitem = self.socket.input_file_item('image')
    placement=self.socket.input_text_value('placement')

    new_Image(self.glob,self.database,self.fs_svn,self.socket,pere_id,pere_path,
              fileitem=fileitem,titre=titre,lien=lien,cl_css=cl_css,placement_wiki=placement)

    self.datas.my_session.set_new_url(self.path)
    redirect_ok(self.socket,self.datas)


def new_Image(glob,database,fs_svn,socket,pere_id,pere_path,
              name=None,datas_binary=None,fileitem=None,
              titre="",lien="",cl_css="",
              placement_wiki=None,lang='all'):

    if not name and fileitem==None:
        socket.send_error(" Pas de nom d'image ")
        return False
    if not name:
        name=fileitem.filename

    if fileitem!=None:
        datas_binary=socket.get_datas_file_form(fileitem)

    pathfile=pere_path+'/'+name
    while (fs_svn.exist(pathfile)):
        (pathfile,name)=new_name_file(pathfile)
    
    msg='new image %s' % (pathfile)
    fs_svn.add(pathfile,datas_binary,msg,binary=True)
            
    proprietes={'titre' : titre,
                'lien'  : lien,
                'cl_css': cl_css }
    obj_id=create_element(glob,database,12,pere_id,{'all':name,},proprietes)

    if placement_wiki:
        dispo_add_elem(glob,database,pere_id,obj_id, placement_wiki)

    return obj_id

def change_Image(glob,database,fs_svn,socket,id_obj,fileitem,titre,lien,cl_css):

    set_propriete(glob,database,id_obj,'titre',titre)
    set_propriete(glob,database,id_obj,'lien',lien)
    set_propriete(glob,database,id_obj,'cl_css',cl_css)
    path=glob.objets[id_obj]['path'][glob.langues[0]]
            
    if fileitem.filename!="":
        #TODO change name !
        datas_binary=socket.get_datas_file_form(fileitem)
        fs_svn.modif(path,datas_binary)


class Image(ObjBase):

    def binary(self):
        self.sendbinary()

    def pre_execution(self):
        nbcol=None
        inb=getattr(self.datas,"inbalises",[])
        for nd in inb:
            if nd and nd[:3]=='col':
                try:
                    nbcol=int(nd[3])
                except:
                    pass
        self.nbcol=nbcol

    def affiche(self):
        kp=self.proprietes.keys()
        titre=''
        ht_css=""
        cl_css=""
        lien=""
        l1=""
        l2=""
        if 'titre' in kp:
            titre=self.proprietes['titre']
        if 'cl_css' in kp:
            cl_css=self.proprietes['cl_css'].strip()
            if cl_css:
                ht_css=' class="%s" ' % cl_css
        if 'lien' in kp:
            lien=self.proprietes['lien'].strip()
            if lien:
                if ht_css:
                    l1='<a href="%s" %s>' % (lien,ht_css)
                else:
                    l1='<a href="%s">' % lien
                l2="</a>"

        path=path_pere(self.path)
        name=name_from_path(self.path)

        if self.nbcol:
            info_dispo=get_dico_proprietes(self.glob,self.datas.skin,'idispo',0,self.log)
            size=info_dispo.get('COL%s' % self.nbcol,None)
            if size:
                pass
                # veritable compression...
                # mais necessite gerer l'acces a l'image !!
                # name=redimentionne(self.fs_svn,path,name,size)
                (new_x,new_y)=dimentions(self.fs_svn,path,name,size)
                html='%s<img src="%s%s/%s" alt="%s" title="%s" %s width="%spx" height="%spx" />%s' % (l1,
                        self.datas.url_base, 
                        path,name, titre,titre,ht_css,new_x,new_y,l2)

                self.socket.send_datas(html)
                return

        html='%s<img src="%s%s/%s" alt="%s" title="%s" %s />%s' % (l1,
                     self.datas.url_base, path,name,
                     titre,titre,ht_css,l2)
        self.socket.send_datas(html)
        
    def action_element_edit_form(self):
        _=self.datas._
        if not check_edit(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        kp=self.proprietes.keys()

        titre=""
        lien=""
        cl_css=""

        if 'titre' in kp:
            titre=self.proprietes['titre']
        if 'lien' in kp:
            lien=self.proprietes['lien'] 
        if 'cl_css' in kp:
            cl_css=self.proprietes['cl_css']

        tpl_form=edit_Image_Form(self.datas,self.path,titre,lien,cl_css)

        txt=u"""
%s :<br />
<form action="%s/edit/ok" method="POST" enctype="multipart/form-data" id="panneauform">
%s
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
""" % (_("Edition de l'Image"),self.path,tpl_form,_('Valider'))

        self.socket.send_datas(txt)


    def edit_ok(self): 
        _=self.datas._
        if not check_edit(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        fileitem = self.socket.input_file_item('image')
        titre=self.socket.input_text_value('titre')
        lien=self.socket.input_text_value('lien')
        cl_css=self.socket.input_text_value('css')

        change_Image(self.glob,self.database,self.fs_svn,self.socket,
                     self.id,fileitem,titre,lien,cl_css)

        urlparent='/'.join(self.datas.objet_actu.path.split('/')[:-1])
        self.datas.my_session.set_new_url(urlparent)
        redirect_ok(self.socket,self.datas)




    a4u=[(edit_ok,  'edit/ok'),
         ]
    f_direct = [edit_ok,binary,]   
    action_default=binary


class ImageAleatoire(Image):
    def binary(self):
        pere=path_pere(self.path)
        name=name_from_path(self.path)
        obj='.'.join(name.split('.')[:-1])
        rep=pere+'/'+obj
        if self.fs_svn.isdir(rep):
            lf=self.fs_svn.listdir(rep)
            fs=[]
            for f in lf:
                if f.find(obj)<>-1:
                    fs.append(f)
            r=random.choice(fs)
            filepath=rep+'/'+r
            self.sendbinary(filepath)
        else:
            self.error=(404,"Le repertoire n'existe pas ou est interdit")

    def action_element_edit_form(self):
        _=self.datas._
        self.socket.send_datas(_('non implemente...'))
        
    def edit_ok(self):
        self.error=(500,_('non implemente...'))
    action_default=binary
