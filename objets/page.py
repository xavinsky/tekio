# -*- coding: utf-8 -*-
import os

from tekio.utils import check_char_url, check_char_idpage
from tekio.utils import new_name_file
from tekio.utils import name_from_path
from tekio.utils import path_pere
from tekio.utils import format_path, format_path_list
from tekio.utils import stou

from tekio.libtek import redirect_ok
from tekio.libtek import check_edit
from tekio.libtek import get_langue

from tekio.objets.base import create_element
from tekio.objets.base import ObjBase 
from tekio.objets.base import set_propriete
from tekio.objets.base import get_propriete

from tekio.objets.site import edit_site_form, edit_site 
from tekio.objets.image import ajoute_image_form, ajoute_image
from tekio.objets.texte import ajoute_text_form, ajoute_text
from tekio.objets.file import ajoute_file_form, ajoute_file
from tekio.objets.galerie import ajoute_galerie_form, ajoute_galerie

from tekio.objets.wiki import element_delete_confirm, enleve_element
from tekio.objets.wiki import element_move
from tekio.objets.wiki import element_edit_form

from tekio.langues import tablangtrad

def ajoute_page_form(self):
    _=self.datas._
    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path

    inputslang=""
    first=True
    for code in self.config.langues:
        l=tablangtrad[code][self.datas.my_session.langue]
        inputslang+="<br /><br />%s %s : <br />" % (_('Information en '),l)
        if first:
            classmore='sur'
            first=False
        else:
            classmore=""
        inputslang+="""
<span class="label%s">%s</span> : <input type="text" name="urlpage_%s" value=""/><br />
<span class="label">%s</span> : <input type="text" name="textnav_%s" value=""/><br />
<span class="label">%s</span> : <input type="text" name="titrepage_%s" value=""/><br />
""" % (classmore,_('Identifiant pour url'),code,_('Text Navigation'),code,_('Titre'),code)

    template="""
%s :
<form action="%s/ajoute_page" method="POST" id="panneauform" >
%s
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
""" % (_('Ajouter une Page'), baseurl, inputslang, _('Valider'))
    self.socket.send_datas(template)

def ajoute_page(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        return


    init_datas={}
    
    for code in self.config.langues:
        init_datas[code]={}
        init_datas[code]['url']=check_char_idpage(self.socket.input_text_value('urlpage_%s' % code))
        init_datas[code]['textnav']=self.socket.input_text_value('textnav_%s' % code)
        init_datas[code]['titre']=self.socket.input_text_value('titrepage_%s' % code)

    new_Page(self,init_datas)
    
    self.datas.my_session.set_new_url(self.path)
    redirect_ok(self.socket,self.datas)

def new_Page(self,init_datas):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        return

    
    pid=self.id
    lang=get_langue(self.datas,self.config)

    names={}
    proprietes={}

    linkdest=None
    nameslistactu=[]
    for code in self.config.langues:
        url=init_datas[code]['url']
        url=check_char_url(url)
        pathpage=self.glob.objets[self.id]['path'][self.glob.langues[0]]
        name=url
        if name=="":
            if nameslistactu==[]:
                self.socket.send_datas(_("Erreur : Pas de nom d'url"))
                return
            else:
                name=nameslistactu[0]
        if not name in nameslistactu:
            pathfile=pathpage+'/'+name
            while (self.fs_svn.exist(pathfile)):
                (pathfile,name)=new_name_file(pathfile)
            nameslistactu.append(name)
            if not linkdest:
                self.fs_svn.add_folder(pathfile)
                linkdest=pathfile
            else:
                self.fs_svn.add_link(linkdest,pathfile)

        names[code]=name
 
    for code in self.config.langues:
        textnav=init_datas[code]['textnav']
        if textnav=="":
            textnav=nameslistactu[0]
        titre=init_datas[code]['titre']
        titre=titre.replace("'", "&#39;")
        titre=titre.replace('"', '&#34;')
        textnav=textnav.replace("'", "&#39;")
        textnav=textnav.replace('"', '&#34;')
        titre=titre.strip()
        textnav=textnav.strip()
        proprietes['titre_%s' % code]=titre
        proprietes['textnav_%s' % code]=textnav

    obj_id=create_element(self.glob,self.database,2,pid,names,proprietes)
    return obj_id


def delete_page_confirm(self):
    _=self.datas._
    ido=self.id
    path_retour=path_pere(self.path)

    tpl="""
%s : <br />
%s : %s <br />
""" % (_('Etes vous sur que vous voulez detruire cette page'),
       self.id, self.path)

    tpl+="""

<div id="div_valid" class="invisible">
<center>
<a href="%s/enleve_element?id=%s"><h3>%s</h3></a>
</center>
</div>

<br />
""" % (path_retour,ido,_('Destruction de la page'))

    self.socket.send_datas(tpl)
    self.confirm_detruire()


def niv_arbo_mov(glob,datas,niv,id,decal):
    page=glob.objets[id]

    lang=datas.my_session.langue
    url=page['path'].get(lang,'')
    pages=page['sous_pages'][lang]
    

    pathin=False
    if datas.objet_actu.path.find(url)!=-1:
        pathin=True

    tpl=''
    if niv>0:
        tpl+='<div class="arbo_move_indic">'
        if len(pages)==0 and pathin:
            tpl+='<div class="arbo_move_indic1">'
        if len(pages)>0 and pathin:
            tpl+='<div class="arbo_move_indic2">'
        if len(pages)==0 and not pathin:
            tpl+='<div class="arbo_move_indic3">'
        if len(pages)>0 and not pathin:
            tpl+='<div class="arbo_move_indic4">'
            
        tpl+='<div class="arbo_indic_over" onmouseover="arbo_ouvre_page(event);">'
        tpl+='<img src=/includes/images/interface/util/pixel.gif" width="20px" heigh="20px" />'
        tpl+='</div>'

    if pathin:
        inv=''
    else:
        inv=' invisible'

    tpl+='<div class="arbo_move_niv%s" id="arbo_menu__%s__%s">' % (inv,url.replace('/','__'),id)

    max=len(pages)+decal

    positionelem=0
    for (idsub,textsub,pathsub,namesub) in pages:
        max2=0
        tpl2=''
        if datas.objet_actu.path==pathsub:
            tpl+=u"""<div class="arbo_move_elem actu"
            id="arbo_move_elem_actu"
            onclick="javascript:go_move_page(event)" ><div
            class="arbo_move_elem_titre">%s</div></div>""" % stou(textsub)
        else:
            mouseover=' onmouseover="arbo_move_page(event,%s);" ' % positionelem
            if datas.objet_actu.path.find(pathsub)!=-1:
                tpl+='<div class="arbo_move_elem actif">'
            else:
                tpl+='<div class="arbo_move_elem inactif">'
            tpl+='<div class="arbo_move_over" %s >' % mouseover
            tpl+='<div class="arbo_move_elem_titre">%s</div>' % textsub
            tpl+='</div>'
            (max2,tpl2)=niv_arbo_mov(glob,datas,niv+1,idsub,decal)
            positionelem+=1
            if max2>max:
                max=max2
            tpl+=tpl2
            tpl+='</div>'
        decal+=1

    tpl+='</div>'
    if niv>0:
        tpl+='</div>'
        tpl+='</div>'

    return (max,tpl)

            
def move_page_form(self):
    _=self.datas._

    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path

    listurls=self.path.split('/')[1:]

    (max,arbomove)=niv_arbo_mov(self.glob,self.datas,0,0,0)
     
    sizearbo=str(20*(max))
    template=u"""
%s
<div class="arbo_indice_niveau">
  <div class="arbo_indice_niveau_0">0</div>
  <div class="arbo_indice_niveau_1">1</div>
  <div class="arbo_indice_niveau_2">2</div>
  <div class="arbo_indice_niveau_3">3</div>
  <div class="arbo_indice_niveau_4">4</div>
</div>
<div class="arbo_move" style="height: %spx;">
%s
</div>
<div id="div_valid" class="invisible">
</div>

""" % (_('La zone verte indique la page a deplacer. Vous pouvez survoler les autres pages pour vous intercaller. Vous pouvez survoler les fleches pour entrer dans une sous page. Cliquer dans la zone verte pour valider le deplacement de la page.'), sizearbo,arbomove)

    self.socket.send_datas(template)
           

def move_page(self):
    if not check_edit(self.datas,self.socket):
        return

    chemin=format_path_list(self.socket.args["pere"].split('__')[1:-1])
    
    idpere=int(self.socket.args["pere"].split('__')[-1])
    pos=int(self.socket.args["pos"])

    my_obj=self.glob.objets[self.id]
    oldpere=my_obj['pere']
    oldpere_obj=self.glob.objets[oldpere]
    newpere_obj=self.glob.objets[idpere]


    if (oldpere!=idpere):
        self.se_deplacer(idpere)
        self.datas.my_session.set_new_url(oldpere_obj['path'][self.glob.langues[0]])
    else:
        self.datas.my_session.set_new_url(self.path)


    # reordoner les sous pages 
    pages=newpere_obj['proprietes']['ordre_sous_pages']
    newordre=[]
    j=0
    posok=False
    for (idpage) in pages:
        if j==pos:
            newordre.append(self.id)
            j+=1
            posok=True
        if idpage!=self.id:
            newordre.append(idpage)
            j+=1
    if not posok:
        newordre.append(self.id)

    newordrestr='/'.join(map(str,newordre))
    set_propriete(self.glob,self.database,idpere,'ordre_sous_pages',newordrestr)
    newpere_obj['proprietes']['ordre_sous_pages']=newordre
    for lang in self.glob.langues:
        self.glob.get_infos_sous_pages(lang,idpere)
        
    redirect_ok(self.socket,self.datas)

def edit_page_form(self):
    _=self.datas._
    if not check_edit(self.datas,self.socket):
        return

    inputslang=u''
    name=name_from_path(self.path)
    urllangdefault=name

    for code in self.config.langues:
        l=tablangtrad[code][self.datas.my_session.langue]
    
        inputslang+=u"<br /><br />%s %s : <br />" % (_('Information en '),l) 

        if self.id!=0:
            try:
                urllang=self.glob.objets[self.id]['names'][code]
            except:
                urllang=''
            inputslang+=u"""<div class="label">%s</div> : <input type="text" name="urlpage_%s" value="%s"/>
                            <br />""" % (_('Identifiant pour url '), code, urllang )
            textnav=self.get_propriete('textnav_%s' % code,'')
            if type(textnav)==type(''):
                textnav=stou(textnav)
            inputslang+=u"""<div class="label">%s</div> : <input type="text" name="textnav_%s" value="%s"/>
                            <br />""" % (_('Text Navigation'),code,textnav )


        titre=stou(self.get_propriete('titre_%s' % code,''))

        inputslang+=u"""
              <div class="label">%s</div> : <input type="text" name="titrepage_%s" value="%s"/><br />
              """ % ( _('Titre'),code,titre)

    template=u"""
%s :
<form action="%s/edit_page" method="POST" id="panneauform" >
%s 
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
""" % (_('Editer les proprietes de la page'), self.path,inputslang,_('Valider'))
    self.socket.send_datas(template)

def edit_page(self):
    if not check_edit(self.datas,self.socket):
        return

    if self.id!=0:
        pereurl=path_pere(self.path)+'/%s'
        firstname=""
        oldnames=self.glob.objets[self.id]['names']
        newnames={}
        i=0
        for code in self.glob.langues:
            newnames[code]=check_char_idpage(self.socket.input_text_value('urlpage_%s' % code,'').strip())
            
            if i==0:
                if newnames[code]=='':
                    self.socket.send_datas('necessite url pour la page !!!')
                    return
                else:
                    namebase=newnames[code]
            else:
                if newnames[code]=='':
                    newnames[code]=namebase
        names=[]

        flagmodifbase=False
        for code in self.config.langues:
            pathpageold=pereurl % oldnames[code]
            pathpagenew=pereurl % newnames[code]
            if len(names)==0:
                if oldnames[code]!=newnames[code]: 
                    flagmodifbase=True
                    if newnames[code] in oldnames.values():
                        for c in oldnames:
                            if oldnames[c]==newnames[code]:
                                oldnames[c]=None
                                pass
                                #self.fs_svn.trash(pathpagenew)
                    else:
                        while (self.fs_svn.exist(pathpagenew)):
                            (pathpagenew,newnames[code])=new_name_file(pathpagenew)
                    pass
                    #self.fs_svn.move(pathpageold,pathpagenew)
            else:
                if flagmodifbase or oldnames[code]!=newnames[code]:
                    if pathpageold!=None and not oldnames[code] in names:
                        pass
                        #self.fs_svn.trash(pathpageold)
                    if not newnames[code] in names:
                        newlink=pereurl % names[0]
                        while (self.fs_svn.exist(pathpagenew)):
                            (pathpagenew,newnames[code])=new_name_file(pathpagenew)
                        pass
                        #self.fs_svn.add_link(newlink,pathpagenew)
                
            names.append(newnames[code])

        self.rename(newnames)


        newlink=pereurl % names[0]
        

        self.datas.my_session.set_new_url(newlink)
    else:
        self.datas.my_session.set_new_url('')

        
    for code in self.config.langues:
        if self.id!=0:
            textnav=self.socket.input_text_value('textnav_%s' % code,'').strip()
            if textnav=='':
                textnav=newnames[code]
            self.set_propriete('textnav_%s' % code,textnav)
        titre=self.socket.input_text_value('titrepage_%s' % code,'').strip()
        self.set_propriete('titre_%s' % code,titre)

    self.glob.reinit(self.database,self.id)

    redirect_ok(self.socket,self.datas)


class Page(ObjBase):
    ajoute_page_form=ajoute_page_form
    ajoute_page=ajoute_page
    edit_page_form=edit_page_form
    edit_page=edit_page
    move_page_form=move_page_form
    move_page=move_page
    edit_site_form=edit_site_form
    edit_site=edit_site
    delete_page_confirm=delete_page_confirm
    ajoute_text_form=ajoute_text_form
    ajoute_text=ajoute_text
    ajoute_image_form=ajoute_image_form
    ajoute_image=ajoute_image
    ajoute_file_form=ajoute_file_form
    ajoute_file=ajoute_file
    ajoute_galerie_form=ajoute_galerie_form
    ajoute_galerie=ajoute_galerie
    enleve_element=enleve_element

    element_edit_form=element_edit_form
    element_move=element_move
    element_delete_confirm=element_delete_confirm
    
    def pre_execution(self):
        l=self.datas.my_session.langue
        self.datas.title=self.get_propriete('titre_%s' % l,"")
        self.datas.description=self.get_propriete('description_%s' % l,"")
        self.datas.keyworks=self.get_propriete('keywords_%s' % l,"")

    def affiche(self):
        return

    def confirm_detruire(self):
        _=self.datas._
        tpl="""
        <center>
<h2>%s</h2>
<h1>%s</h1>
<h3>%s</h3>
        </center>
        """ % (_("Attention vous detruisez"),_("!!! UNE PAGE !!!"),_("et tous ses elements"))
        self.socket.send_datas(tpl)


    a4u=[(ajoute_page_form,    'ajoute_page/form'),
         (ajoute_page,         'ajoute_page'),
         (edit_page_form,    'edit_page/form'),
         (edit_page,         'edit_page'),
         (edit_site_form,      'edit_site/form'),
         (edit_site,           'edit_site'),
         (move_page_form,      'move_page/form'),
         (move_page,           'move_page'),
         (delete_page_confirm, 'delete_page/confirm'),
         (ajoute_text_form,    'ajoute_text/form'),
         (ajoute_text,         'ajoute_text'),
         (ajoute_image_form,   'ajoute_image/form'),
         (ajoute_image,        'ajoute_image'),
         (ajoute_file_form,   'ajoute_file/form'),
         (ajoute_file,        'ajoute_file'),
         (ajoute_galerie_form,   'ajoute_galerie/form'),
         (ajoute_galerie,        'ajoute_galerie'),
         (enleve_element,      'enleve_element'),
         
         (element_edit_form,      'element_edit_form/*'),
         (element_move,           'element_move'),
         (element_delete_confirm, 'element_delete_confirm/*'),
         
         ]
    f_direct = [ajoute_page_form, ajoute_page, delete_page_confirm,
                edit_page_form, edit_page,
                move_page_form, move_page,
                edit_site_form, edit_site,
                ajoute_text_form, ajoute_text, 
                ajoute_image_form, ajoute_image, 
                ajoute_file_form, ajoute_file,
                ajoute_galerie_form, ajoute_galerie,
                element_edit_form,
                element_edit_form,
                element_move, 
                element_delete_confirm, 
                enleve_element]


