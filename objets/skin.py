# -*- coding: utf-8 -*-
import os

from tekio.libtek import redirect_ok
from tekio.libtek import get_instance_from_id
from tekio.utils import utoh, quote_html
from tekio.utils import name_from_path
from tekio.utils  import stou, balise_utf8
from tekio.libtek import check_admin

from tekio.objets.base import create_element
from tekio.objets.base import ObjBase
from tekio.objets.base import set_propriete, get_propriete, del_propriete
from tekio.objets.base import detruire_element, create_element
from tekio.objets.folder import Folder

from tekio.objets.image import new_Image, add_Image_Form, edit_Image_Form, change_Image
from tekio.objets.texte import new_Text, add_Text_Form, change_Text, get_text_lang_by_path
from tekio.objets.navigation import new_Navigation, add_Navigation_Form
from tekio.objets.navigation import change_Navigation, edit_Navigation_Form
from tekio.editeurtext import get_js_prepare_submit

"""
Proprietes du skin_header
  dispoheader / include(s)_css
Proprietes du skin_footer
  dispofooter
Proprietes du skin

afin de generer la css
Les couleurs.    : liste couleurs / valeurs
  color.1S (S=sombre) : /*+COL:1S+*/
  color.1N (N=normal) : /*+COL:1N+*/
  color.1C (C=claire) : /*+COL:1C+*/
  color.2S (S=sombre) : /*+COL:2S+*/
  color.2N (N=normal) : /*+COL:2N+*/
  color.2C (C=claire) : /*+COL:2C+*/
  color.3A (A=alerte) : /*+COL:3A+*/
  color.4N (N=nois)   : /*+COL:4N+*/
  color.4G (G=gris)   : /*+COL:4G+*/
  color.4B (B=blanc)  : /*+COL:4B+*/

Les images.      : fils. (penser a liér les images des css)
  image.<nomimg> : /*+IMG:<nomimg>+*/


Infos fonts.       : infos styles.
  css.<balise>.<propriete> <valeur> xxx : /*+CSS:<balise>+*/


      
"""

balises=['body','a','a:hover','p','h1','h2','h3','h4','h5','h6',
                 'small','sup','sub','acronym','DOTrecadre1','DOTrecadre2']

proprietes={
            'font-family' : ['Georgia', 'Trebuchet MS', 'Verdana', 'Arial',
                             'Times New Roman', 'Impact' ],
            'font-weight' : ['bold','100', '200', '300', '400', '500', '600', '700', '800', '900'],
            'text-align' : ['left','right', 'center', 'justify'],
            'text-transform' : ['capitalize', 'uppercase', 'lowercase'],
            'font-variant' : ['small-caps',],
            'border-style' : ['solid', 'dotted', 'dashed', 'double',
                              'groove', 'ridge', 'inset', 'outset'],
            }

proprietes_size={
            'font-size-line-height' : ['7/9','10/12','12/15','15/18','21/24','24/30','36/42','48/60'],
            'padding-top' : [ '0', '1', '2', '3', '4', '5', '6', '9', '12', '15', '18', '24'],
            'padding-bottom' : [ '0', '1', '2', '3', '4', '5', '6', '9', '12', '15', '18', '24'],
            'padding-left' : [ '0', '1', '2', '3', '4', '5', '6', '9', '12', '15', '18', '24'],
            'padding-right' : [ '0', '1', '2', '3', '4', '5', '6', '9', '12', '15', '18', '24'],
            'border-top-width' : ['1', '2', '3', '4', '5', '6' ],
            'border-bottom-width' : ['1', '2', '3', '4', '5', '6' ],
            'border-left-width' : ['1', '2', '3', '4', '5', '6' ],
            'border-right-width' : ['1', '2', '3', '4', '5', '6' ],
            'letter-spacing' : ['1', '2', '3', '4', '5', '6' ],

            }

proprietes_colors=['color','background-color',
                   'border-top-color', 'border-bottom-color',
                   'border-left-color', 'border-right-color']

class Skin(Folder):
    def init_actu(self):
        if self.datas.action:
            self.action=getattr(self,self.datas.action)
        else:
            self.action=self.action_default
            if self.fs_svn.exist(self.path_entier):
                if not self.fs_svn.isdir(self.path_entier):
                    self.action=self.sendbinary

    def initialise(self):
        self.nameskin = name_from_path(self.path)

        self.datas.my_session.new_url_skin = '/skins/'+self.nameskin+'/edition'

    def edition(self):
        if not check_admin(self.datas,self.socket):
		return
        _=self.datas._
        baseurl=self.datas.url_base
        if baseurl[-1]=='/':
            baseurl=baseurl[:-1]
        baseurl=self.datas.url_base
        
        baseurl=self.datas.url_base
        if self.path!='/':
            baseurl+=self.path
        urlbase='/'.join(baseurl.split('/')[:-1])

        (hutf8,futf8)=balise_utf8([('js','base.js')])
        self.socket.send_datas(hutf8)
        self.socket.send_datas('<h1> Skin %s </h1>' % self.nameskin )
        self.socket.send_datas("""
<style>
textarea {
height: 200px;
width: 400px;
}

textarea.mini {
height: 40px;
width: 200px;
}

textarea.grand {
height: 300px;
width: 600px;
}

</style>

""" )

        # formulaire edit skin.
        # formulaire edit placement header / footer
        # liste des objets (delete/modif) + ajout :  Textes / Images / Navigation.

        my_obj=self.glob.objets[self.id]
        id_header=my_obj['urls'][self.glob.langues[0]]['header']
        tpl_h=get_propriete(self.glob,id_header,'dispo_normal','')
        id_footer=my_obj['urls'][self.glob.langues[0]]['footer']
        tpl_f=get_propriete(self.glob,id_footer,'dispo_normal','')

        v_include_css=get_propriete(self.glob,id_header,'include_css',None)
        v_includes_css=get_propriete(self.glob,id_header,'includes_css','').strip().split(',')
        if v_include_css and v_include_css.strip():
            v_includes_css.append(v_include_css.strip())
        v_templates_css=get_propriete(self.glob,id_header,'templates_css','').strip().split(',')
        for tpl in v_templates_css:
            if not tpl in v_includes_css:
                v_includes_css.append(tpl)

        del_propriete(self.glob,self.database,id_header,'include_css')
        set_propriete(self.glob,self.database,id_header,'includes_css',','.join(v_includes_css))
        set_propriete(self.glob,self.database,id_header,'templates_css',','.join(v_templates_css))

        self.socket.send_datas("""<form action="/skins/%s/change_includes" method="POST" style="border: 1px solid black;">
<h2>%s</h2>
<div class="label">%s : </div> : <input name="includes_css" type="text" value="%s"> <br /><br />
<div class="label">%s : </div> : <input name="templates_css" type="text" value="%s"> <br /><br />
<input type="submit" value="%s" ><br /></form> 
""" %  (self.nameskin,_('Liste des templates et includes css'),
        _('Includes css'),','.join(v_includes_css),
        _('Templates css'),','.join(v_templates_css),
        _('Valider la modification des deux liste') ) )

        
        self.socket.send_datas('<h2>%s</h2>' % _('Edition des fichier template et css'))
        
        for i in v_includes_css:
            if i in v_templates_css:
                name_file=i+'.tpl'

                text_file=quote_html(self.fs_svn.get('/includes/css/%s.tpl' % i))

                form_edit_file="""
<form action="/skins/%s/change_tpl/%s" method="POST">
<textarea class="grand" name="tpl">%s</textarea><br />
<input type="submit" value="%s" >
</form>
<br />""" % (self.nameskin,i,text_file,_('Valider'))

                self.socket.send_datas("""
                <div class="edit_tpl" style="border: 1px solid black;">
                <h3>%s %s </h3>
<span id="show_edit_file_%s" onclick="show('edit_file_%s');hide('show_edit_file_%s');">[%s]</span>
<div id="edit_file_%s" style="display: none;">
<span onclick="hide('edit_file_%s');show('show_edit_file_%s');">[%s]</span>
%s
</div>
</div>
                """ % ( _('fichier template : '),name_file,i,i,i,
                        _('Editer'),i,i,i,_('ANNULER'),form_edit_file) )


        self.socket.send_datas('<h2> Objets </h2>')
        id_objets=my_obj['subs']
        objets=[]
        for id_objet in id_objets:
            objets.append(self.glob.objets[id_objet])

        self.socket.send_datas('<h3> Images </h3>')
        self.socket.send_datas('<ul>')
        for o in objets:
            if o['type']==12:
                names=o.get('names',{})
                if len(names.values())==0:
                    name=''
                else:
                    name=names.values()[0]
                self.socket.send_datas('<li> %s:%s ' % (o['id'],name))
                self.socket.send_datas('[<a href="%s/edit/image/form/%s">%s</a> ]' % (self.path,o['id'],_('Editer')) )
                self.socket.send_datas('[<a href="/enleve_element?id=%s">%s</a> ]' % (o['id'],_('Detruire')))
                self.socket.send_datas('</li>')
        self.socket.send_datas('</ul>')
                
        tpl="""
<h4>%s</h4>        
<form action="%s/add/image" method="post"  enctype="multipart/form-data">
%s
<input type="submit" value="%s" /><br />
</form>""" % (_('Nouvelle Image'),self.path, add_Image_Form(self.datas), _('Ajouter cette image'))
                                                                                                            
        self.socket.send_datas(tpl)

        self.socket.send_datas('<hr />')
        self.socket.send_datas('<h3> Navigations </h3>')
        self.socket.send_datas('<ul>')
        for o in objets:
            if o['type']==20:
                names=o.get('names',{})
                if len(names.values())==0:
                    name=''
                else:
                    name=names.values()[0]
                self.socket.send_datas('<li> %s:%s ' % (o['id'],name))
                self.socket.send_datas('[<a href="%s/edit/nav/form/%s">%s</a> ]' % (self.path,o['id'],_('Editer')) )
                self.socket.send_datas('[<a href="/enleve_element?id=%s">%s</a> ]' % (o['id'],_('Detruire')))
                self.socket.send_datas('</li>')
        self.socket.send_datas('</ul>')

        tpl="""
<h4>%s</h4>        
<form action="%s/add/nav" method="post">
%s
<input type="submit" value="%s" /><br />
</form>""" % (_('Nouvelle Navigation'),self.path, add_Navigation_Form(self.datas), _('Ajouter une navigation'))

        self.socket.send_datas(tpl)
        self.socket.send_datas('<hr />')

        self.socket.send_datas('<h3> Textes </h3>')
        self.socket.send_datas('<ul>')
        for o in objets:
            if o['type']==11:
                names=o.get('names',{})
                if len(names.values())==0:
                    name=''
                else:
                    name=names.values()[0]
                self.socket.send_datas('<li> %s:%s ' % (o['id'],name))
                self.socket.send_datas('[<a href="%s/edit/text/form/%s">%s</a> ]' % (self.path,o['id'],_('Editer')) )
                self.socket.send_datas('[<a href="/enleve_element?id=%s">%s</a> ]' % (o['id'],_('Detruire')))
                self.socket.send_datas('</li>')
        self.socket.send_datas('</ul>')
        self.socket.send_datas('[<a href="%s/add/text/form">%s</a> ]' % (self.path,_('Editer un nouveau texte')) )
                

        self.socket.send_datas('<h2> Code template </h2>')
        self.socket.send_datas("""<form action="/skins/%s/change_template" method="POST">""" % self.nameskin)
        self.socket.send_datas('<br />%s : <textarea name="tplh" >%s</textarea>' % (_('Header'),tpl_h) )
        self.socket.send_datas('<br />%s : <textarea name="tplf" >%s</textarea>' % (_('Footer'),tpl_f) )
        self.socket.send_datas('<br /><input type="submit" value="%s" ></form><br />' % _('Changer les codes template') )
 
        # TODO LIST OBJET DELETE / MODIF / ADD.
        self.socket.send_datas(futf8)



    def change_template(self):
        if not check_admin(self.datas,self.socket):
		return
        _=self.datas._
        new_tplh=self.socket.input_text_value('tplh')
        new_tplf=self.socket.input_text_value('tplf')
        my_obj=self.glob.objets[self.id]
        id_obj_header=my_obj['urls'][self.glob.langues[0]]['header']
        id_obj_footer=my_obj['urls'][self.glob.langues[0]]['footer']
        set_propriete(self.glob,self.database,id_obj_header,'dispo_parent',new_tplh)
        set_propriete(self.glob,self.database,id_obj_header,'dispo_normal',new_tplh)
        set_propriete(self.glob,self.database,id_obj_footer,'dispo_parent',new_tplf)
        set_propriete(self.glob,self.database,id_obj_footer,'dispo_normal',new_tplf)
            
        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)

    def change_includes(self):
        if not check_admin(self.datas,self.socket):
		return
        _=self.datas._
 
        new_includes=self.socket.input_text_value('includes_css')
        new_templates=self.socket.input_text_value('templates_css')
        my_obj=self.glob.objets[self.id]
        id_obj_header=my_obj['urls'][self.glob.langues[0]]['header']
        set_propriete(self.glob,self.database,id_obj_header,'includes_css',new_includes)
        set_propriete(self.glob,self.database,id_obj_header,'templates_css',new_templates)
            
        self.regenere_css()

        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)
        
    def change_tpl(self):
        if not check_admin(self.datas,self.socket):
		return
        _=self.datas._
        id_tpl=self.datas.action_params[0]

        text_tpl=self.socket.input_text_value('tpl')
        self.fs_svn.modif('/includes/css/%s.tpl' % id_tpl, text_tpl)

        self.regenere_css()
        
        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)
    
    def add_image(self):
        if not check_admin(self.datas,self.socket):
		return
        _=self.datas._
        fileitem = self.socket.input_file_item('image')
        titre=self.socket.input_text_value('titre')
        lien=self.socket.input_text_value('lien')
        cl_css=self.socket.input_text_value('css')
    
        name_obj=fileitem.filename
        id_obj=new_Image(self.glob,self.database,self.fs_svn,self.socket,
                         self.id,self.path,fileitem=fileitem,titre=titre,lien=lien,cl_css=cl_css)
        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)

    def edit_image_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        id_obj=int(self.datas.action_params[0])
        titre=get_propriete(self.glob,id_obj,'titre','')
        lien=get_propriete(self.glob,id_obj,'lien','')
        cl_css=get_propriete(self.glob,id_obj,'cl_css','')
        path=self.glob.objets[id_obj]['path'][self.glob.langues[0]]

        tpl_form=edit_Image_Form(self.datas,path,titre,lien,cl_css)

        (hutf8,futf8)=balise_utf8()
        txt=u"""%s 
        %s :<br />
        <form action="%s/edit/image/valid/%s" method="POST" enctype="multipart/form-data">
        %s
        <input type="submit" value="%s" >
        </form>
        %s""" % (hutf8,_("Edition de l'Image"),self.path,id_obj,tpl_form,_('Valider'),futf8)
                    
        self.socket.send_datas(txt)


    def change_image_valid(self):
        fileitem = self.socket.input_file_item('image')
        titre=self.socket.input_text_value('titre')
        lien=self.socket.input_text_value('lien')
        cl_css=self.socket.input_text_value('css')
        id_obj=int(self.datas.action_params[0])
        
        change_Image(self.glob,self.database,self.fs_svn,self.socket,
                     id_obj,fileitem,titre,lien,cl_css)

    def edit_image_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        
        self.change_image_valid()
        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)

    def add_nav(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        name=self.socket.input_text_value('name')
        direction=self.socket.input_text_value('direction')
    
        id_obj=new_Navigation(self.glob,self.database,self.fs_svn,self.socket,
                         self.id,self.path,name,direction)
        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)

    def edit_nav_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        id_obj=int(self.datas.action_params[0])
        direction=get_propriete(self.glob,id_obj,'direction','')

        tpl_form=edit_Navigation_Form(self.datas,direction)

        (hutf8,futf8)=balise_utf8()

        txt=u"""%s
        %s :<br />
        <form action="%s/edit/nav/valid/%s" method="POST" >
        %s
        <input type="submit" value="%s" >
        </form>
        %s""" % (hutf8,_("Edition de la Navigation"),self.path,id_obj,tpl_form,_('Valider'),futf8)
                    
        self.socket.send_datas(txt)

    def edit_nav_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        
        id_obj=int(self.datas.action_params[0])
        direction=self.socket.input_text_value('direction')

        change_Navigation(self.glob,self.database,self.fs_svn,self.socket,
                     id_obj,direction)
        
        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)


    def add_text_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        ft=add_Text_Form(self.datas,self.config) % ''


        data_includes=[('js','editeurtext.js'),
                       ('css','editeurtext',
                        )]
        (hutf8,futf8)=balise_utf8(data_includes)

        j=get_js_prepare_submit()
        tpl="""%s
<h4>%s</h4>        
<form action="%s/add/text/valid" method="POST" name="form4skin">
%s
<input type="button" value="%s" onClick="%s;document.forms.form4skin.submit();">
</form>
<script>
StartEditeurText();
</script>
%s"""  % (hutf8,_('Nouveau Text'),self.path, ft, _('Ajouter un text'),j,futf8)

        self.socket.send_datas(tpl)
        self.socket.send_datas('<hr />')

    def add_text_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        text={}
        for code in self.config.langues:
            try:
                text[code]=self.socket.input_text_value('text_%s' % code)
            except:
                text[code]=''
                                        
        print 'addtext...'
        print text
        id_obj=new_Text(self.glob,self.database,self.fs_svn,self.socket,
                               self.config, self.id,self.path,text)

        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)

    def edit_text_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        id_obj=int(self.datas.action_params[0])
        path=self.glob.objets[id_obj]['path'][self.glob.langues[0]]
        direction=get_propriete(self.glob,id_obj,'direction','')

        self.datas.old_textes={}
        for code in self.config.langues:
            txt=get_text_lang_by_path(self.fs_svn,path,code)
            if not txt:
                txt=''
            self.datas.old_textes[code]=txt
                
        ft=add_Text_Form(self.datas,self.config) % ''

        data_includes=[('js','editeurtext.js'),
                       ('css','editeurtext',
                        )]
        (hutf8,futf8)=balise_utf8(data_includes)

        j=get_js_prepare_submit()
                
        txt=u"""%s
        %s :<br />
        <form action="%s/edit/text/valid/%s" method="POST" name="form4skin">
        %s
        <input type="button" value="%s" onClick="%s;document.forms.form4skin.submit();">
        </form>
        <script>
        StartEditeurText();
        </script>
        %s""" % (hutf8,_("Edition de la Textigation"),self.path,id_obj,ft,_('Valider'),j,futf8)
                
        self.socket.send_datas(txt)

    def edit_text_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        
        id_obj=int(self.datas.action_params[0])
        path=self.glob.objets[id_obj]['path'][self.glob.langues[0]]

        text_modif={}
        for code in self.config.langues:
            namefile = self.path+'.%s.txt' % code
            text=self.socket.input_text_value('text_%s' % code)
            oldtext=get_text_lang_by_path(self.fs_svn,path,code)
            if text!=oldtext:
                text_modif[code]=text
                
        change_Text(self.glob,self.fs_svn,id_obj,text_modif)

        self.datas.my_session.set_new_url(self.path+'/edition')
        redirect_ok(self.socket,self.datas)


    #TODO 3x

    def delete(self):
        pass
    def duplique(self):
        pass
    def applique(self):
        pass

                                                
    def gencolors_form(self):
        _=self.datas._
        css_colors=self.get_dico_proprietes('color')

        if not css_colors.has_key('1N'):
            css_colors['1N']="#0000FF"
        if not css_colors.has_key('2N'):
            css_colors['2N']="#00FF00"
        if not css_colors.has_key('3A'):
            css_colors['3A']="#FF0000"
        if not css_colors.has_key('4G'):
            css_colors['4G']="#606060"

        name_skin=self.glob.objets[self.id]['names']['all']
           

        tpl="""<h1>%s %s</h1>
<form action="%s/gencolors/valid" method="POST" id="panneauform">
<div class="label">%s</div> : <input name="color_1" type="text" class="color3_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_2" type="text" class="color3_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_3A" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_4G" type="text" class="color_down" value="%s"> <br /><br />
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>

""" % ( _('Generation de couleurs'),name_skin,self.path,
        _('Couleur Primaire et ses degrades sombre et clair.'),css_colors["1N"],
        _('Couleur Secondaire et ses degrades sombre et clair.'),css_colors["2N"],
        _("Couleur d alerte."),css_colors["3A"],
        _('Gris pour texte'),css_colors["4G"],
        _('Generer les couleurs') )

        self.socket.send_datas(tpl)


    def gencolors_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        css_colors=self.socket.input_dico_text_value('color')
        for (k,v) in css_colors.items():
            self.set_propriete("color."+k,v)
        self.set_propriete("color.4N","#000000")
        self.set_propriete("color.4B","#FFFFFF")

        self.regenere_css()

        self.datas.my_session.set_new_url(self.path)
        redirect_ok(self.socket,self.datas)

        

    def colors_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        css_colors=self.get_dico_proprietes('color')

        if not css_colors.has_key('1S'):
            css_colors['1S']="#000088"
        if not css_colors.has_key('1N'):
            css_colors['1N']="#0000FF"
        if not css_colors.has_key('1C'):
            css_colors['1C']="#8888FF"
        if not css_colors.has_key('2S'):
            css_colors['2S']="#008800"
        if not css_colors.has_key('2N'):
            css_colors['2N']="#00FF00"
        if not css_colors.has_key('2C'):
            css_colors['2C']="#88FF88"
        if not css_colors.has_key('3A'):
            css_colors['3A']="#FF0000"
        if not css_colors.has_key('4N'):
            css_colors['4N']="#000000"
        if not css_colors.has_key('4G'):
            css_colors['4G']="#606060"
        if not css_colors.has_key('4B'):
            css_colors['4B']="#FFFFFF"

        name_skin=self.glob.objets[self.id]['names']['all']

        tpl="""
<h1>%s %s</h1>
<form action="%s/colors/valid" method="POST" id="panneauform">
<div class="label">%s</div> : <input name="color_1S" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_1N" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_1C" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_2S" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_2N" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_2C" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_3A" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_4N" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_4G" type="text" class="color_down" value="%s"> <br /><br />
<div class="label">%s</div> : <input name="color_4B" type="text" class="color_down" value="%s"> <br /><br />
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>

""" % ( _('Couleurs utilisés'),name_skin,self.path,
        _('Couleur Primaire Sombre'),css_colors["1S"],
        _('Couleur Primaire Normale'),css_colors["1N"],
        _('Couleur Primaire Claire'),css_colors["1C"],
        _('Couleur Secondaire Sombre'),css_colors["2S"],
        _('Couleur Secondaire Normale'),css_colors["2N"],
        _('Couleur Secondaire Claire'),css_colors["2C"],
        _("Couleur d alerte."),css_colors["3A"],
        _('Noir'),css_colors["4N"],
        _('Gris pour texte'),css_colors["4G"],
        _('Blanc'),css_colors["4B"],
        _('Modifier les couleurs') )

        self.socket.send_datas(tpl)

    def colors_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
        css_colors=self.socket.input_dico_text_value('color')
        for (k,v) in css_colors.items():
            self.set_propriete("color."+k,v)

        self.datas.my_session.set_new_url(self.path)
        redirect_ok(self.socket,self.datas)


    def images_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        my_obj=self.glob.objets[self.id]
        id_objets=my_obj['subs']
        objets=[]
        for id_objet in id_objets:
            objets.append(self.glob.objets[id_objet])

        name_skin=self.glob.objets[self.id]['names']['all']


        self.socket.send_datas('<h1> %s %s </h1>' % (_('Images du skin'),name_skin))
        for o in objets:
            if o['type']==12:
                names=o.get('names',{})
                if len(names.values())==0:
                    name=''
                else:
                    name=names.values()[0]

                if name:
                    
                    self.set_propriete('image.%s' % name ,'/includes/skins/%s/%s' % (name_skin,name))
                    id_obj=o['id']
                    titre=get_propriete(self.glob,id_obj,'titre','')
                    lien=get_propriete(self.glob,id_obj,'lien','')
                    cl_css=get_propriete(self.glob,id_obj,'cl_css','')
                    path=self.glob.objets[id_obj]['path'][self.glob.langues[0]]

                    input_form=edit_Image_Form(self.datas,path,titre,lien,cl_css)

                    tpl_form=u"""
                %s :<br />
                <form action="%s/images/valid/%s" method="POST" enctype="multipart/form-data">
                %s
                <input type="submit" value="%s" >
                </form>
                """ % (_("Modification de l'Image"),self.path,id_obj,input_form,_('Valider la modification de cette image'))

                self.socket.send_datas("""
           %s [<span id="bt_edit_image_%s" onclick="show('edit_image_%s');hide('bt_edit_image_%s');">%s </span>]
<div id="edit_image_%s" class="invisible">
%s
</div><br />
                """ % (name, o['id'], o['id'], o['id'],_('Editer'),o['id'],tpl_form)
                       )
                self.socket.send_datas('<br />')
        self.regenere_css()


    def images_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        self.change_image_valid()
        self.datas.my_session.set_new_url(self.path)
        redirect_ok(self.socket,self.datas)


    def styles_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        css=self.get_dico_proprietes('css')

        css_colors=self.get_dico_proprietes('color')


        #initialisation super dico css.
        for balise in balises:
            if not css.has_key(balise):
                css[balise]={}
            prs=css[balise]
            for (propriete,choix) in proprietes.items():
                if not prs.has_key(propriete):
                    prs[propriete]=None
            for (propriete,choix) in proprietes_size.items():
                if not prs.has_key(propriete):
                    prs[propriete]=None
            for propriete in proprietes_colors:
                if not prs.has_key(propriete):
                    prs[propriete]=None

        tpl_balises=""
        tpl_propriete="""
        <div class="balise_css_propriete">
        <div class="label">%s :</div>
        %s
        </div>"""
        tpl_select="""<select name="css_%s_%s">%s</select>"""
        tpl_option="""<option value="%s" %s>%s</option>"""
        tpl_option_color="""<option value="%s" style="background-color: %s;"  %s>%s</option>"""
        # Affichage formulaire :
        for balise in balises:
            tpl_from_proprietes=""
            prs=css[balise]
            for (propriete,choix) in proprietes.items():
                selected=""
                if prs[propriete]==None:
                    selected=" selected"
                tpl_options=tpl_option % ("null",selected,_("Aucune"))
                for choi in choix:
                    selected=""
                    if prs[propriete]==choi:
                        selected=" selected"
                    tpl_options+=tpl_option % (choi,selected,choi)
                tpl_select_pr=tpl_select % (balise,propriete,tpl_options)
                tpl_from_proprietes+=tpl_propriete % (propriete,tpl_select_pr)
                    
            for (propriete,choix) in proprietes_size.items():
                selected=""
                if prs[propriete]==None:
                    selected=" selected"
                tpl_options=tpl_option % ("null",selected,_("Aucune"))
                for choi in choix:
                    selected=""
                    if prs[propriete]==choi:
                        selected=" selected"
                    tpl_options+=tpl_option % (choi,selected,choi)
                tpl_select_pr=tpl_select % (balise,propriete,tpl_options)
                tpl_from_proprietes+=tpl_propriete % (propriete,tpl_select_pr)

            for propriete in proprietes_colors:
                selected=""
                if prs[propriete]==None:
                    selected=" selected"
                tpl_options=tpl_option % ("null",selected,_("Aucune"))

                for (col_id,col_val) in css_colors.items():
                    selected=""
                    if prs[propriete]==col_id:
                        selected=" selected"
                    tpl_options+=tpl_option_color % (col_id,col_val,selected,col_id)

                tpl_select_pr=tpl_select % (balise,propriete,tpl_options)
                tpl_from_proprietes+=tpl_propriete % (propriete,tpl_select_pr)

            
            tpl_balises+="""
<div class="balise_css">
<h2>%s</h2>
<span id="show_css_balise_%s" onclick="show('css_balise_%s');hide('show_css_balise_%s');">[%s]</span>
<div id="css_balise_%s" class="invisible proprietes_css">
<span onclick="hide('css_balise_%s');show('show_css_balise_%s');">[ %s <b>%s</b> ]</span>
%s
</div>
</div>
                """ % (balise,balise,balise,balise,_('Montrer les proprietes'),
                       balise,balise,balise,_('Cacher les proprietes de la balise '),
                       balise,tpl_from_proprietes)

        name_skin=self.glob.objets[self.id]['names']['all']

        tpl="""<h1>%s %s</h1>
<form action="%s/styles/valid" method="POST" id="panneauform">
<div class="css_balises">
%s
</div>
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
<div class="stopmid" ></div>
""" % ( _('Gestion des styles'),name_skin,self.path,tpl_balises,
        _('Valider les styles') )

        self.socket.send_datas(tpl)
                
    def styles_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        css=self.socket.input_dico_text_value('css')
        for (balise,proprietes) in css.items():
            for (propriete,valeur) in proprietes.items():
                p='css.%s.%s' % (balise,propriete)
                if valeur=="null":
                    self.del_propriete(p)
                else: 
                    self.set_propriete(p,valeur)
                   
        self.regenere_css()

        self.datas.my_session.set_new_url(self.path)
        redirect_ok(self.socket,self.datas)

    def dispo_form(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return

        info_dispo=self.get_dico_proprietes('idispo')

        list_pos_site=[('left',_('A gauche')),
                       ('center',_('Au centre')),
                       ]

        if not info_dispo.has_key('pos_site'):
            pos_site='center'
            self.set_propriete('idispo.pos_site',pos_site)
        else:
            pos_site=info_dispo['pos_site']
        
        options_pos_site=""
        for (id,txt) in list_pos_site:
            selected=''
            if pos_site==id:
                selected=" selected"
            options_pos_site+="""<option value="%s"%s>%s</option>""" % (id,selected,txt)



        list_pos_menu=[('left',_('A gauche')), 
                       ('right',_('A droite')),
                       ]

        if not info_dispo.has_key('pos_menu'):
            pos_menu='left'
            self.set_propriete('idispo.pos_menu',pos_menu)
        else:
            pos_menu=info_dispo['pos_menu']

        if pos_menu in ['top',]:
            is_menu=False
        else:
            is_menu=True
            
        options_pos_menu=""
        for (id,txt) in list_pos_menu:
            selected=''
            if pos_menu==id:
                selected=" selected"
            options_pos_menu+="""<option value="%s"%s>%s</option>""" % (id,selected,txt)


        if not info_dispo.has_key('width_site'):
            width_site='765'
            self.set_propriete('idispo.width_site',width_site)
        else:
            width_site=info_dispo['width_site']


        list_marge_editor=['0', '6', '9', '12', '15', '18', '24', '30']

        if not info_dispo.has_key('marge_editor'):
            marge_editor='9'
            self.set_propriete('idispo.marge_editor',marge_editor)
        else:
            marge_editor=info_dispo['marge_editor']
        
        options_marge_editor=""
        for id in list_marge_editor:
            selected=''
            if marge_editor==id:
                selected=" selected"
            options_marge_editor+="""<option value="%s"%s>%s</option>""" % (id,selected,id)


        list_marge_elements=['0', '3', '6', '9', '12', '15', '18']

        if not info_dispo.has_key('marge_elements'):
            marge_elements='6'
            self.set_propriete('idispo.marge_elements',marge_elements)
        else:
            marge_elements=info_dispo['marge_elements']
        
        options_marge_elements=""
        for id in list_marge_elements:
            selected=''
            if marge_elements==id:
                selected=" selected"
            options_marge_elements+="""<option value="%s"%s>%s</option>""" % (id,selected,id)



        list_nb_cols=['1', '2', '3', '4', '5']

        if not info_dispo.has_key('nb_cols'):
            nb_cols='3'
            self.set_propriete('idispo.nb_cols',nb_cols)
        else:
            nb_cols=info_dispo['nb_cols']
        
        options_nb_cols=""
        for id in list_nb_cols:
            selected=''
            if nb_cols==id:
                selected=" selected"
            options_nb_cols+="""<option value="%s"%s>%s</option>""" % (id,selected,id)

        divisor=1  
        if (nb_cols=="1"):
            divisor=6 
        if (nb_cols=="2"):
            divisor=6 
        if (nb_cols=="3"):
            divisor=6 
        if (nb_cols=="4"):
            divisor=12 
        if (nb_cols=="5"):
            divisor=60 

        if not info_dispo.has_key('width_editor'):
            width_editor='516'
            self.set_propriete('idispo.width_editor',width_editor)
        else:
            width_editor=info_dispo['width_editor']

        if not info_dispo.has_key('width_nav'):
            width_nav='231'
            self.set_propriete('idispo.width_nav',width_nav)
        else:
            width_nav=info_dispo['width_nav']

        wbase=int(width_site)-2*int(marge_editor)
        if is_menu:
            mini=int(wbase*0.66/divisor)*divisor; 
            maxi=int(wbase*0.75/divisor)*divisor; 

        options_w_editor = "";
        i=mini
        while i<=maxi:
            selected=""
            if i==int(width_editor):
                selected=" selected"
            options_w_editor+="""<option value="%s" %s>%s</option>""" % (i,selected,i)
            i=i+divisor


        w_nav=int(width_site)-2*int(marge_editor)-int(width_editor)
        options_w_nav="""<option value="%s">%s</option>""" % (w_nav,w_nav)

        tpl="""
<form action="%s/disposition/valid" method="POST" id="panneauform">

%s : <select name="pos_site">%s</select> &nbsp;&nbsp;&nbsp;
%s : <select name="pos_menu" id="pos_menu" onchange='calculpossibilite();'>
%s </select><br />
<br />
%s : 
<input type="text" name="width_site" size="5" id="width_site" value="%s" onchange='calculpossibilite();' />px. <small>%s %s</small><br />
%s :
<select name="marge_editor" id="marge_editor" onchange='calculpossibilite();'>%s</select>
<small>%s</small><br />

%s :
<select name="marge_elements" id="marge_elements">%s</select>
<small>%s</small><br />

%s :
<select name="nb_cols" id="nb_cols" onchange='calculpossibilite();' >
%s</select>
<br />
%s
<select name="width_editor" id="width_editor" onchange='calcnav();'>
%s</select><small>%s %s</small> 
%s :
<select name="width_nav" id="width_nav" >%s</select>
<br />

<div id="cols">
</div>

<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>

</form>
""" 
        tpl_datas=( self.path,
                _('Site'), options_pos_site,
                _('Navigation'), options_pos_menu,
                _('Largeur Maxi'), width_site,
                _('765 pour que 99% des PC puisses voir ton site sans scroll'),
                _('ou 990 pour que 80% des PC puisses voir ton site sans scroll'),
                _('Marge zone edition'), options_marge_editor,
                _('12 pour un site en 765 / 18 pour un site en 990'),
                _('Marge des elements'), options_marge_elements,
                _('6 pour un site en 765 / 9 pour un site en 990'),
                _("Nombre colonnes maxi dans la zone d'edition"), options_nb_cols,
                _('Largeurs possible de la zone edition'), options_w_editor,
                _('pour un site en 765 environ 500'),
                _('pour un site en 990 environ 620'),
                _('Calcul taille Navigation'), options_w_nav ,
                _('Valider la disposition'))

        self.socket.send_datas(tpl  % tpl_datas )

    def dispo_valid(self):
        _=self.datas._
        if not check_admin(self.datas,self.socket):
            self.socket.send_datas(_('connectez vous...'))
            return
    
        pos_site=self.socket.input_text_value('pos_site')
        self.set_propriete('idispo.pos_site',pos_site)
        pos_menu=self.socket.input_text_value('pos_menu')
        self.set_propriete('idispo.pos_menu',pos_menu)
        width_site=self.socket.input_text_value('width_site')
        self.set_propriete('idispo.width_site',width_site)
        marge_editor=self.socket.input_text_value('marge_editor')
        self.set_propriete('idispo.marge_editor',marge_editor)
        marge_elements=self.socket.input_text_value('marge_elements')
        self.set_propriete('idispo.marge_elements',marge_elements)
        nb_cols=self.socket.input_text_value('nb_cols')
        self.set_propriete('idispo.nb_cols',nb_cols)
        width_editor=self.socket.input_text_value('width_editor')
        self.set_propriete('idispo.width_editor',width_editor)
        width_nav=self.socket.input_text_value('width_nav')
        self.set_propriete('idispo.width_nav',width_nav)
        COL1=str(int(width_editor)-2*int(marge_elements))
        COL2=str(int(width_editor)/2-2*int(marge_elements))
        COL3=str(int(width_editor)/3-2*int(marge_elements))
        COL4=str(int(width_editor)/4-2*int(marge_elements))
        COL5=str(int(width_editor)/5-2*int(marge_elements))
        self.set_propriete('idispo.COL1',COL1)
        self.set_propriete('idispo.COL2',COL2)
        self.set_propriete('idispo.COL3',COL3)
        self.set_propriete('idispo.COL4',COL4)
        self.set_propriete('idispo.COL5',COL5)

        #/* Patch crado pour la dispo site et menu */
        #/* Ecrase les ids des objets */
        #/* A refaire lorsque l on pourra editer les zones */
        txtdispo=self.fs_svn.get('/includes/dispos/%s-%s.dispo' % (pos_site,pos_menu))
        dec=txtdispo.split('\n') 
        my_obj=self.glob.objets[self.id]
        id_obj_header=my_obj['urls'][self.glob.langues[0]]['header']
        id_obj_footer=my_obj['urls'][self.glob.langues[0]]['footer']
        set_propriete(self.glob,self.database,id_obj_footer,'dispo_parent',dec[1])
        set_propriete(self.glob,self.database,id_obj_footer,'dispo_normal',dec[1])
        set_propriete(self.glob,self.database,id_obj_header,'dispo_parent',dec[0])
        set_propriete(self.glob,self.database,id_obj_header,'dispo_normal',dec[0])
        #/* Fin Patch crado */

        self.regenere_css()

        self.datas.my_session.set_new_url(self.path)
        redirect_ok(self.socket,self.datas)



    def split_tpl(self,text_tpl,tpl):
        if not text_tpl:
            return ''
        tab1=text_tpl.split('/*+')
        tab2=[(None,None,tab1[0]),]
        for elem in tab1[1:]:
            l=elem.split('+*/',1)
            if len(l)!=2:
                self.log.debug('Erreur (1) tpl %s : %s ' % (tpl,elem))
                tab2.append((None,None,elem))
            else:
                l2=l[0].split(':',1)
                if len(l)!=2:
                    self.log.debug('Erreur (2) tpl %s : %s ' % (tpl,elem))
                    tab2.append((None,None,elem))
                else:
                    tab2.append((l2[0],l2[1],l[1]))
        return tab2


    def get_tpl_css(self,balise):
        all_css=self.get_dico_proprietes('css')
        if all_css.has_key(balise):
            dico_balise_css=all_css[balise]
            tpl_prs=""
            for (k,v) in dico_balise_css.items():
                if k=='font-size-line-height':
                    (s,h)=v.split('/',1)
                    tpl_prs+="  font-size: %spx;\n\r" % s
                    tpl_prs+="  line-height: %spx;\n\r" % h
                elif k in proprietes_size.keys():
                    tpl_prs+="  %s: %spx;\n\r" % (k,v)
                elif k in proprietes_colors:
                    tpl_prs+="  %s: /*+COL:%s+*/;\n\r" % (k,v)
                else:
                    tpl_prs+="  %s: %s;\n\r" % (k,v)
            name=balise.replace("DOT",'.')
            return """
%s {
%s
}
""" % (name,tpl_prs)

        return ''
    
    def get_tpl_img(self,idimg):
        path_imgs=self.get_dico_proprietes('image',1)
        if path_imgs.has_key(idimg):
            return path_imgs[idimg]
        else:
            self.log.debug('get_tpl_img manquant %s  : %s ' % (self.nameskin,idimg))
            return '/includes/skins/%s/%s' % (self.nameskin,idimg)
    
    def get_tpl_col(self,idcol):
        css_colors=self.get_dico_proprietes('color')
        if css_colors.has_key(idcol):
            return css_colors[idcol]
        else:
            self.log.debug('get_tpl_col manquant %s  : %s ' % (self.nameskin,idcol))
            return 'none'

    def get_tpl_dispo(self,idcol):
        info_dispo=self.get_dico_proprietes('idispo')

        if idcol=="WSITE":
            return info_dispo['width_site']
        elif idcol=="WNAV":
            return info_dispo['width_nav']
        elif idcol=="WNAVL":
            if info_dispo['pos_menu']=='left':
                return info_dispo['width_nav']
            else:
                return '0'
        elif idcol=="WNAVR":
            if info_dispo['pos_menu']=='right':
                return info_dispo['width_nav']
            else:
                return '0'
        elif idcol=="MED":
            return info_dispo['marge_editor']
        elif idcol=="2MED":
            return str(2*int(info_dispo['marge_editor']))
        elif idcol=="MEL":
            return info_dispo['marge_elements']
        elif idcol=="WED2M":
            return str(int(info_dispo['width_editor'])+2*int(info_dispo['marge_editor']))
        elif idcol=="COL1":
            return str(int(info_dispo['width_editor'])-2*int(info_dispo['marge_elements']))
        elif idcol=="COL2":
            return str(int(info_dispo['width_editor'])/2-2*int(info_dispo['marge_elements']))
        elif idcol=="COL3":
            return str(int(info_dispo['width_editor'])/3-2*int(info_dispo['marge_elements']))
        elif idcol=="COL4":
            return str(int(info_dispo['width_editor'])/4-2*int(info_dispo['marge_elements']))
        elif idcol=="COL5":
            return str(int(info_dispo['width_editor'])/5-2*int(info_dispo['marge_elements']))
        else:
            self.log.debug('get_tpl_col manquant %s  : %s ' % (self.nameskin,idcol))
            return 'none'

    def regenere_css(self):
        my_obj=self.glob.objets[self.id]
        id_header=my_obj['urls'][self.glob.langues[0]]['header']
        v_templates_css=get_propriete(self.glob,id_header,'templates_css','').strip().split(',')

        self.log.debug('regenere css %s  ' % self.nameskin)

        for tpl in v_templates_css:
            if tpl:
                self.log.debug('lecture %s.tpl ' % tpl)
                text_tpl=self.fs_svn.get('/includes/css/%s.tpl' % tpl)

                #transfo css
                tab_tpl=self.split_tpl(text_tpl,tpl)
                text_tpl=""
                for (type,value,txt) in tab_tpl:
                    if type=="CSS":
                        text_tpl+=self.get_tpl_css(value)
                    else:
                        text_tpl+='/*+%s:%s+*/' % (type,value)
                    text_tpl+=txt

                self.log.debug('cssok')

                tab_tpl=self.split_tpl(text_tpl,tpl)
                text_tpl=""
                for (type,value,txt) in tab_tpl:
                    if type=="IMG":
                        text_tpl+=self.get_tpl_img(value)
                    else:
                        text_tpl+='/*+%s:%s+*/' % (type,value)
                    text_tpl+=txt

                self.log.debug('imgok')

                tab_tpl=self.split_tpl(text_tpl,tpl)
                text_tpl=""
                for (type,value,txt) in tab_tpl:
                    if type=="COL":
                        text_tpl+=self.get_tpl_col(value)
                    else:
                        text_tpl+='/*+%s:%s+*/' % (type,value)
                    text_tpl+=txt

                self.log.debug('colok')

                tab_tpl=self.split_tpl(text_tpl,tpl)
                text_tpl=""
                for (type,value,txt) in tab_tpl:
                    if type=="DISPO":
                        text_tpl+=self.get_tpl_dispo(value)
                    else:
                        text_tpl+='/*+%s:%s+*/' % (type,value)
                    text_tpl+=txt

                self.log.debug('dispo')

                self.log.debug('ecriture %s.css ' % tpl)
                self.fs_svn.modif('/includes/css/%s.css' % tpl, text_tpl)
            

    
    a4u=[(edition,              'edition'),

         (change_includes,      'change_includes'),

         (change_template,      'change_template'),
         (change_tpl,           'change_tpl/*'),


         (add_image,            'add/image'),
         (edit_image_form,      'edit/image/form/*'), 
         (edit_image_valid,     'edit/image/valid/*'), 

         (add_nav,              'add/nav'),
         (edit_nav_form,        'edit/nav/form/*'), 
         (edit_nav_valid,       'edit/nav/valid/*'), 

         (add_text_form,        'add/text/form'),
         (add_text_valid,       'add/text/valid'),
         (edit_text_form,       'edit/text/form/*'), 
         (edit_text_valid,      'edit/text/valid/*'), 

         (gencolors_form,       'gencolors'), 
         (gencolors_valid,      'gencolors/valid'), 
         (colors_form,          'colors'), 
         (colors_valid,         'colors/valid'), 
         (images_form,          'images'), 
         (images_valid,         'images/valid/*'), 
         (styles_form,          'styles'), 
         (styles_valid,         'styles/valid'), 
         (dispo_form,           'disposition'), 
         (dispo_valid,          'disposition/valid'), 

         (delete,               'delete'),   # TODO
         (duplique,             'duplique'), # TODO
         (applique,             'applique'), # TODO


         ]
    sendbinary=Folder.sendbinary
    f_direct=[sendbinary,change_template,change_includes,change_tpl,edition,
              add_image,edit_image_form,edit_image_valid,
              add_nav,edit_nav_form,edit_nav_valid,
              add_text_valid,edit_text_valid,
              gencolors_form,colors_form, gencolors_valid,colors_valid,
              images_form, images_valid,
              dispo_form, dispo_valid,
              styles_form, styles_valid,]


class Skins(ObjBase):
    
    def affiche(self):
        if not check_admin(self.datas,self.socket):
		return
        _=self.datas._
        les_skins=self.glob.objets[self.id]['subs']

        (hutf8,futf8)=balise_utf8()
        self.socket.send_datas(hutf8)
        self.socket.send_datas("""<h2>%s : </h2> """ % _('Skins existants') )


        for id_skin in les_skins:
            skin_obj=self.glob.objets[id_skin]
            name=skin_obj['names'].values()[0]
            
            self.socket.send_datas("""<li> %s """ % name)
            self.socket.send_datas("""[<a href="/skins/%s">%s</a>] """ % (name,_('Activer Menu')))
            self.socket.send_datas("""[<a href="/skins/%s/edition">%s</a>] """ % (name,_('Technique')))
            # TODO
            #self.socket.send_datas("""[<a href="/skins/%s/applique">%s</a>] """ % (name,_('Appliquer ce skin ')))
            #self.socket.send_datas("""[<a href="/skins/%s/delete">%s</a>] """ % (name,_('Detruire')))
            self.socket.send_datas("""</li>\n""")
            
        # TODO A refaire.
	"""
        self.socket.send_datas(""<h2>%s</h2>"" % _('Creer un nouveau skin') )
        self.socket.send_datas(""<form action="/skins/new_skin" method="POST">"" )
        self.socket.send_datas(""%s <input type="text" name="nom">"" % _('Nom du nouveau skin') )
        self.socket.send_datas('<br /><input type="submit" value="%s" ></form><br />' % _('Creer nouveau skin') )
        self.socket.send_datas(""</form>"" )
	"""
        self.socket.send_datas(futf8)

    #TODO
    def new_skin(self):
        if not check_admin(self.datas,self.socket):
		return
        _=self.datas._
        nom=self.socket.input_text_value('nom')
        names={'all':nom,}
        propritetes={'dispo_parent': '#', 
                     'dispo_normal': '=' ,
                     'name_all': nom }
        skin_id=create_element(self.glob,self.database,30,self.id,names,propritetes)
        self.fs_svn.add('/includes/css/skin_%s.css' % nom,"/* css %s */" % nom)
        names={'all':'header',}
        propritetes={'dispo_parent': '#', 
                     'dispo_normal': '=',
                     'include_css': 'skin_%s' % nom }
        header_id=create_element(self.glob,self.database,31,skin_id,names,propritetes)
        names={'all':'footer',}
        propritetes={'dispo_parent': '#', 
                     'dispo_normal': '='}
        footer_id=create_element(self.glob,self.database,31,skin_id,names,propritetes)
     
        self.fs_svn.add_folder(self.path+'/'+nom)
        self.datas.my_session.set_new_url(self.path+'/%s/edition' % nom)
        redirect_ok(self.socket,self.datas)

    a4u=[(new_skin, 'new_skin')]
    f_direct=[new_skin,affiche]
    action_default=affiche


class SkinPart(ObjBase):
    pass

