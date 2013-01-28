# -*- coding: utf-8 -*-
import os
import mimetypes
import urllib

from tekio.utils import path_pere, name_from_path
from tekio.libtek import redirect_ok
from tekio.objets.base import ObjBase
from tekio.libtek import check_edit, check_admin

class Folder(ObjBase):
    def init_actu(self):
        self.action=self.affiche
        if self.fs_svn.exist(self.path_entier):
            if not self.fs_svn.isdir(self.path_entier):
                self.action=self.sendbinary

    def affiche(self):
        _=self.datas._
        self.socket.send_datas('<body><h1>'+_('SERVEUR HTTPDtekio : Repertoires et Fichiers Publics')+'</h1>\n')
        pathpere=path_pere(self.path_entier)
        parent=name_from_path(pathpere)
        if not parent:
            parent='Racine'
        self.socket.send_datas(_('Retour')+' : <a href="%s">%s</a> <br />' % (pathpere,parent))
        self.socket.send_datas('<br />')
        self.socket.send_datas(_("Contenu du Repertoire Actuel")+" : %s <br />" % self.path_entier)
        for elem in self.fs_svn.listdir(self.path_entier):
            path_obj="%s/%s" % (self.path_entier,elem)
            urlobj="%s/%s" % (self.datas.url_base,path_obj)
            admins_action=''
            if check_admin(self.datas,self.socket):
                typemime=mimetypes.guess_type(path_obj)[0]
                if typemime in self.type_edit:
                    admins_action='[<a href="http://%s/edit">E</a>] [<a href="http://%s/delete">D</a>]' % (urlobj,urlobj)
            self.socket.send_datas('<a href="http://%s">%s</a> %s<br />' % (urlobj,elem,admins_action))           
        return

    def edit(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        self.path_obj=self.path_entier.split('/edit')[0]
        typemime=mimetypes.guess_type(self.path_obj)[0]

        if typemime in self.type_edit:
            if typemime=='text/css':
                self.edit_text()
        else:
            self.socket.send_datas(_("Type non pris en compte")+" : %s <br />" % typemime)

    def edit_ok(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        self.path_obj=self.path_entier.split('/edit/ok')[0]

        typemime=mimetypes.guess_type(self.path_obj)[0]

        if typemime in self.type_edit:
            if typemime=='text/css':
                self.edit_text_ok()
        else:
            self.socket.send_datas(_("Type non pris en compte")+" : %s <br />" % typemime)

        return


    def edit_text(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        
        txt=self.fssvn.get(self.path_obj)

        urlobj="%s/%s" % (self.datas.url_base,self.path_obj)

        html="""
<form class="edittext" action="%s/edit/ok" method="POST">
<textarea name="text">
%s
</textarea>
<input type="submit" value="%s">
</form>
        """ % (urlobj,txt,_('Valider'))

        self.socket.send_datas(html)

    def edit_text_ok(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        
        urlobj="%s/%s" % (self.datas.url_base,self.path_obj)

        text=self.socket.input_text_value('text')
        if text:
            self.fs_svn.trash(self.path_obj)
            self.fssvn.modif(self.path_obj)

        pathpere=path_pere(self.path_obj)
        self.datas.my_session.set_new_url(pathpere)
        redirect_ok(self.socket,self.datas)


    def delete(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        self.path_obj=self.path_entier.split('/delete')[0]
        pathpere=path_pere(self.path_obj)

        self.fs_svn.trash(self.path_obj)
        self.datas.my_session.set_new_url(pathpere)
        redirect_ok(self.socket,self.datas)

    type_edit=['text/css',]
    a4u=[(edit,                 '*/edit'),
         (edit_ok,              '*/edit/ok'),
         (delete,                '*/delete'),
         ]
    sendbinary=ObjBase.sendbinary
    f_direct=[edit_ok,delete,sendbinary]
    
