# -*- coding: utf-8 -*-
import os

from tekio.libtek import redirect_ok
from tekio.libtek import check_edit
from tekio.libtek import get_langue, get_langues

from tekio.objets.base import create_element
from tekio.objets.base import ObjBase

from tekio.objets.wiki import dispo_add_elem, tpl_placement
from tekio.langues import tablangtrad

from tekio.editeurtext import get_toolbar, zone_saisie, get_js_swap_zones_edit, get_js_prepare_submit

def add_Text_Form(datas,config):
    _=datas._

    nomvar="text"
    
    textareas="""
%s : 
<div class="twbaraction">
%s
%s
</div>""" % (_('Editer un Text '),get_toolbar(datas),'%s')

    old_textes=getattr(datas,'old_textes',{})
    nblangues=len(config.langues)
    visu="visu%s_%s" % (nblangues,nblangues)

    for code in config.langues:
        old_texte=old_textes.get(code,'')
        l=tablangtrad[code][datas.my_session.langue]
        info="..."
        j=get_js_swap_zones_edit(nomvar+"_"+code)
        textareas+="""<div class="twbarlang"><span class="twnamelang" >%s</span>
                      <a href="#" onclick="%s">+++</a>%s</div>""" % (l ,j,info)
        textareas+=zone_saisie(nomvar,datas,code,old_texte.replace("%","%%"),visu) 

    return textareas

def ajoute_text_form(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        self.socket.send_datas(_('connectez vous...'))
        return
    baseurl=self.datas.url_base+self.path

    f=add_Text_Form(self.datas,self.config) % tpl_placement(self.datas)
    j=get_js_prepare_submit()
    template="""
<form action="%s/ajoute_text" id="panneauform" method="POST">
%s
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="%s;document.forms.panneauform.submit();">

</div>
</form>
""" % (baseurl,f, _('Ajouter ce texte'),j)
    self.socket.send_datas(template)

def ajoute_text(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        self.socket.send_datas(_('connectez vous...'))
        return

    pere_id=self.datas.objet_actu.id
    pere_path=self.datas.objet_actu.path
    text={}
    placement=self.socket.input_text_value('placement')

    for code in self.config.langues:
        try:
            text[code]=self.socket.input_text_value('text_%s' % code)
        except:
            text[code]=''
       

    new_Text(self.glob,self.database,self.fs_svn,self.socket,self.config,pere_id,pere_path,
              text=text,placement_wiki=placement)

    self.datas.my_session.set_new_url(self.path)
    redirect_ok(self.socket,self.datas)

def new_Text(glob,database,fs_svn,socket,config,pere_id,pere_path,
              text=None,name=None,file=None,
              placement_wiki=None):

    #TODO NAME choisi par user !!!
    name="text%s"
        
    obj_id=create_element(glob,database,11,pere_id,{'all':name,})

    name=name % obj_id
    
    names={}
    for code in config.langues:
        txt=text[code]
        file='%s.%s.txt' % (name,code)
        path='%s/%s' % (pere_path,file)
        comment='new text %s (%s)' % (name,code)
        fs_svn.add(path,txt,comment)
        names[code]=name

    if placement_wiki:
        dispo_add_elem(glob,database,pere_id,obj_id, placement_wiki)

    return obj_id

def change_Text(glob,fs_svn, id_obj, text_modif):
    path=glob.objets[id_obj]['path'][glob.langues[0]]
    for (k,v) in text_modif.items():
        print (k,v)
        namefile = '%s.%s.txt' % (path,k)
        fs_svn.modif(namefile,v)
        

def get_text_lang_by_path(fs_svn,path,langue):
    namefile = path+'.%s.txt' % langue
    if fs_svn.exist(namefile):
        try:
            txt=fs_svn.get(namefile)
        except:
            return None
        return txt
    return None


class Texte(ObjBase):

    def get_text_lang(self,langue):
        namefile = self.path+'.%s.txt' % langue
        if self.fs_svn.exist(namefile):
            try:
                txt=self.fs_svn.get(namefile)
            except:
                return None
            return txt
        return None

    def get_text_my_lang(self):
        langue=self.datas.my_session.langue
        txt=self.get_text_lang(langue)
        if type(txt)==type('') or type(txt)==type(u''):
            return txt
        for langue in get_langues(self.datas,self.config):
            txt=self.get_text_lang(langue)
            if type(txt)==type('') or type(txt)==type(u''):
                return txt
        txt=self.get_text_lang('all')
        if not txt:
            txt=''
        return txt

    def affiche(self):
        self.socket.send_datas(self.get_text_my_lang())
                
    def action_element_edit_form(self):
        _=self.datas._

        if not check_edit(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        self.datas.old_textes={}
        for code in self.config.langues:
            txt=self.get_text_lang(code)
            if not txt:
                txt=''
            self.datas.old_textes[code]=txt


        f=add_Text_Form(self.datas,self.config) % tpl_placement(self.datas)

        j=get_js_prepare_submit()
        template="""
        <form action="%s/edit/ok" id="panneauform" method="POST">
        %s
        <div id="div_valid" class="invisible">
        <input type="button" value="%s" onClick="%s;document.forms.panneauform.submit();">
        
        </div>
        </form>
        """ % (self.path,f, _('Modifier ce texte'),j)
        self.socket.send_datas(template)

    def edit_ok(self):
        _=self.datas._
        if not check_edit(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        text_modif={}
        for code in self.config.langues:
            namefile = self.path+'.%s.txt' % code
            text=self.socket.input_text_value('text_%s' % code)
            oldtext=self.get_text_lang(code)
            if text!=oldtext:
                text_modif[code]=text

        change_Text(self.glob,self.fs_svn,self.id,text_modif)
                    
        urlparent='/'.join(self.path.split('/')[:-1])
        self.datas.my_session.set_new_url(urlparent)
        redirect_ok(self.socket,self.datas)


    def includes(self):
        if check_edit(self.datas,self.socket,False):
            return [('js','editeurtext.js'),
                    ('css','editeurtext')]
        else:
            return []

    def listfiles(self):
        try:
            nom=self.glob.objets[self.id]['names'].values()[0]
        except:
            return []
        ret=[]
        for l in self.glob.langues:
            ret.append('%s.%s.txt' % (nom,l))
        return ret
        
    a4u=[(edit_ok,  'edit/ok'),
              ]
    f_direct=[edit_ok,]
