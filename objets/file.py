# -*- coding: utf-8 -*-
import os
import random

from tekio.libtek import redirect_ok
from tekio.libtek import check_edit
from tekio.libtek import get_langue

from tekio.utils import new_name_file
from tekio.utils import list_to_dic
from tekio.utils import path_pere
from tekio.utils import name_from_path

from tekio.objets.base import ObjBase
from tekio.objets.base import create_element

from tekio.objets.wiki import dispo_add_elem, tpl_placement

def add_File_Form(datas):
    _=datas._
    return _('Fichier')+""" : <input type="file" name="file" />"""

def ajoute_file_form(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        self.socket.send_datas(_('connectez vous...'))
        return

    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path
    template="""
%s :
<form action="%s/ajoute_file" method="POST" enctype="multipart/form-data" id="panneauform">
%s
%s
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
""" % (_('Ajouter un File'),baseurl,
       add_File_Form(self.datas),
       tpl_placement(self.datas),
       _('Valider'))
    self.socket.send_datas(template)
    

def ajoute_file(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        self.socket.send_datas(_('connectez vous...'))
        return

    pere_id=self.datas.objet_actu.id
    pere_path=self.datas.objet_actu.path
    fileitem = self.socket.input_file_item('file')
    placement=self.socket.input_text_value('placement')

    new_File(self.glob,self.database,self.fs_svn,self.socket,pere_id,pere_path,
              fileitem=fileitem,placement_wiki=placement)

    self.datas.my_session.set_new_url(self.path)
    redirect_ok(self.socket,self.datas)


def new_File(glob,database,fs_svn,socket,pere_id,pere_path,
              name=None,datas_binary=None,fileitem=None,
              placement_wiki=None,lang='all'):

    
    if not name and fileitem==None:
        socket.send_error(" Pas de nom de file ")
        return False
    if not name:
        name=fileitem.filename

    if fileitem!=None:
        datas_binary=socket.get_datas_file_form(fileitem)

    pathfile=pere_path+'/'+name
    while fs_svn.exist(pathfile):
        (pathfile,name)=new_name_file(pathfile)

    msg='new fichier %s' % (pathfile)
    fs_svn.add(pathfile,datas_binary,msg,binary=True)
    
    names={'all': name ,}
    obj_id=create_element(glob,database,13,pere_id,names)

    if placement_wiki:
        dispo_add_elem(glob,database,pere_id,obj_id, placement_wiki)

    return obj_id

class File(ObjBase):

    def binary(self):
        if self.fs_svn.exist(self.path):
            self.action=self.sendbinary
        else:
            self.error=(404,"Le fichier n'existe pas ou vous est interdit")
        self.sendbinary()

    def affiche(self):
        name=self.path.split('/')[-1]
        icone_file='<img src="%s/includes/images/interface/icons/telechargement.png" border="0" alt="telecharger" />' % self.datas.url_base
        # TODO DELOC size_human_file dans fssvn !!!
        size_human= self.fs_svn.size_human_file(self.path)
        html='%s <a href="%s%s" >%s (%s)</a>' % (icone_file,self.datas.url_base, self.path, name,size_human)
        self.socket.send_datas(html)

    def action_element_edit_form(self):
        _=self.datas._
        if not check_edit(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        txt=u"""
%s :
<form action="%s/edit/ok" method="POST" enctype="multipart/form-data" id="panneauform">
%s : <input type="file" name="file" />
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
""" % (_('Edition du Fichier'),self.path,
       _('Changer le fichier'),_('Valider'))

        self.socket.send_datas(txt)


    def edit_ok(self):
        _=self.datas._
        if not check_edit(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        urlparent=path_pere(self.path)
        self.datas.my_session.set_new_url(urlparent)

        fileitem = self.socket.input_file_item('file')

        if fileitem.filename=="":
            self.socket.send_error(_(" Pas de fichier !!! "))
            redirect_ok(self.socket,self.datas)
            return
        

        if fileitem.filename!=name_from_path:
            #TODO fichier a renommer !!!
            pass
        
        datas_binary=self.socket.get_datas_file_form(fileitem)
        self.fs_svn.modif(self.path,datas_binary)

        redirect_ok(self.socket,self.datas)

    a4u=[(edit_ok,  'edit/ok'),
         ]
    f_direct=[edit_ok,binary,]
    action_default=binary
