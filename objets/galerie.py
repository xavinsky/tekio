# -*- coding: utf-8 -*-

import os
import random

from tekio.utils import check_char_url
from tekio.utils import name_from_path

from tekio.libtek import redirect_ok
from tekio.libtek import check_edit
from tekio.libtek import get_langue

from tekio.objets.base import create_element
from tekio.objets.base import ObjBase 

from tekio.objets.wiki import dispo_add_elem, tpl_placement

def ajoute_galerie_form(self):
    _=self.datas._
    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path
    template="""
%s :
<form action="%s/ajoute_galerie" method="POST">
%s : <input type="text" name="urlgalerie" value=""/><br />
%s : <input type="text" name="titregalerie" value=""/><br />
%s : <input type="text" name="textnav" value=""/><br />
%s : <textarea name="description" class="petit"></textarea><br />
%s <input type="submit" value="%s" />
</form>
""" % (_('Ajouter une Galerie'), baseurl, _('Url'),_('Titre'),_('Texte Navigation'),_('Description'),tpl_placement(self.datas),_('Valider'))
    self.socket.send_datas(template)




def ajoute_galerie(self):
    if not check_edit(self.datas,self.socket):
        return

    url=self.socket.input_text_value('urlgalerie')
    url=check_char_url(url)
    titre=self.socket.input_text_value('titregalerie','')
    textnav=self.socket.input_text_value('textnav','')
    description=self.socket.input_text_value('description','')
    titre=titre.replace("'", "&#39;")
    titre=titre.replace('"', '&#34;')
    textnav=textnav.replace("'", "&#39;")
    textnav=textnav.replace('"', '&#34;')
    description=description.replace("'", "&#39;")
    description=description.replace('"', '&#34;')
    placement=self.socket.input_text_value('placement')

    lang=get_langue(self.datas,self.config)
    pere_id=self.datas.objet_actu.id
    pere_path=self.datas.objet_actu.path


    new_Galerie(self.glob,self.database,self.datas,self.socket,pere_id,pere_path,
              name=url,titre=titre,textnav=textnav,description=description,
              placement_wiki=placement,lang=lang)


def new_Galerie(glob,database,datas,socket,pere_id,pere_path,
                name=None,titre='Galerie',textnav='Galerie',description='',
                placement_wiki=None,lang='all'):

    if not check_edit(datas,socket):
        return

    pathgalerie=config.path['files']+pere_path+'/'+name
    os.system('mkdir -p "%s"' % pathgalerie)
    os.system('mkdir -p "%s/mini"' % pathgalerie)
    os.system('mkdir -p "%s/normal"' % pathgalerie)
    os.system('mkdir -p "%s/info"' % pathgalerie)
    os.system('mkdir -p "%s/download"' % pathgalerie)

    proprietes={
        'titre' : titre.strip(),
        'textnav' : textnav.strip(),
        'description' : description.strip(),
        }

    obj_id=create_element(glob,database,4,pere_id,{'all':name,},proprietes)

    if placement_wiki:
        dispo_add_elem(glob,database,pere_id,obj_id, placement_wiki)

    redirect_ok(socket,datas)


def ajoute_galerie_element_form(self):
    _=self.datas._
    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path
    template="""
%s :
<form action="%s/ajoute/ok" method="POST" enctype="multipart/form-data">
%s : <input type="text" name="titre" value=""/><br />
%s : <textarea name="description" class="petit"></textarea><br />
%s <input type="file" name="image" /><br />
%s <input type="file" name="mini" /><br />
%s <input type="file" name="download" /><br />
<input type="submit" value="%s" /><br />
</form>
""" % (_('Ajouter un element à la galerie'), baseurl, 
       _('Titre'),_('Description'),
       _('Image a afficher'),_('Vignette (mini)'),_('Fichier a telecharger'),
       _('Valider'))
    self.socket.send_datas(template)

def ajoute_galerie_element(self):

    if not check_edit(self.datas,self.socket):
        return

    pere_id=self.datas.objet_actu.id
    pere_path=self.datas.objet_actu.path

    titre = self.socket.input_text_value('titre','')
    description = self.socket.input_text_value('description','')
    fileitem_image = self.socket.input_file_item('image')
    fileitem_mini = self.socket.input_file_item('mini')
    fileitem_download = self.socket.input_file_item('download')

    if fileitem_image == None:
        self.socket.send_error(" Pas d'image ")

    new_ElementGalerie(self.fs_svn,self.socket,pere_id,pere_path,
    titre=titre,description=description,fileitem_image=fileitem_image,
    fileitem_mini=fileitem_mini,fileitem_download=fileitem_download)


def fileitem_to_pathfire(pathfile,fileitem):
    fout = open (pathfile, 'wb')
    while 1:
        chunk = fileitem.file.read(100000)
        if not chunk: break
        fout.write (chunk)
    fout.close()

def copy_file(pathinit,fileend):
    fout = open (pathend, 'wb')
    fin = open (pathinit, 'rb')
    fout.write(fin.read())
    fin.close()
    fout.close()

def new_ElementGalerie(fs_svn,socket,pere_id,pere_path,
                       titre,description,fileitem_image,
                       fileitem_mini=None,fileitem_download=None,
                       lang='all'):

    pathpage=config.path['files']+pere_path

    name=fileitem_image.filename
    if not name:
        name=fileitem_image.name

    pathfile_image=pathpage+'/normal/'+name
    pathfile_mini=pathpage+'/mini/mini_'+name
    pathfile_download=pathpage+'/download/download_'+name
    pathfile_info=pathpage+'/info/'+name+'.info'

    fileitem_to_pathfire(pathfile_image,fileitem_image)
    if fileitem_mini != None:
        fileitem_to_pathfire(pathfile_mini,fileitem_mini)
    else:
        copy_file(pathfile_image,pathfile_mini)
    if fileitem_download != None:
        fileitem_to_pathfire(pathfile_download,fileitem_download)
    else:
        copy_file(pathfile_image,pathfile_download)

    f= open (pathfile_info, 'wb')
    f.write(titre+'\n'+description)
    f.close()

    redirect_ok(socket,datas)


def delete_galerie_confirm(self):
    _=self.datas._
    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path

    parenturl='/'.join(baseurl.split('/')[:-1])

    template="""%s :<br />
    <h1>%s</h1>
    <a href="%s/enleve_element?id=%s">%s</a> &nbsp;&nbsp;&nbsp;&nbsp;
    """ % (_('Etes vous sur que vous voulez detruire cette galerie'),
           baseurl,parenturl,self.id,
           _('Destruction GALERIE'))
    template+="""<a href="#" onclick="javascript:hide('div_bande_alerte');">%s</a></br>""" % _('Annuler')
    self.socket.send_datas(template)

class Galerie(ObjBase):
    ajoute_galerie_form=ajoute_galerie_form
    ajoute_galerie=ajoute_galerie
    ajoute_galerie_element_form=ajoute_galerie_element_form
    ajoute_galerie_element=ajoute_galerie_element
    delete_galerie_confirm=delete_galerie_confirm
    
    def edit_form(self):
        _=self.datas._
        baseurl=self.datas.url_base
        if self.path!='/':
            baseurl+=self.path
        #todo multilangue.
        titre=self.get_propriete('titre','')
        textnav=self.get_propriete('textnav','')
        description=self.get_propriete('description','')

        name=name_from_path(self.path)
        urlgalerie=""
        if self.id!=0:
            urlgalerie="""%s : <input type="text" name="urlgalerie" value="%s"/><br />""" % (_('Url'),name)
        template=u"""
%s :
<form action="%s/edit/ok" method="POST">
%s 
%s : <input type="text" name="titre" value="%s"/><br />
%s : <input type="text" name="textnav" value="%s"/><br />
%s : <textarea name="description" class="petit">%s</textarea>
<input type="submit" value="%s" />
</form>
""" % (_('Editer les proprietes de la galerie'),baseurl,urlgalerie,_('Titre'),titre,_('Text Nav'),textnav,_('Description'),description,_('Valider'))
        self.socket.send_datas(template)


    def edit_ok(self):

        if not check_edit(self.datas,self.socket):
            return
        baseurl=self.datas.url_base
        if self.path!='/':
            baseurl+=self.path

        url=self.socket.input_text_value('urlgalerie')
        titre=self.socket.input_text_value('titre')
        textnav=self.socket.input_text_value('textnav')
        description=self.socket.input_text_value('description')

        name=name_from_path(self.path)

        if self.id!=0:
            redirecturl=baseurl
            if url!=name:
                self.path='/'.join(baseurl.split('/')[:-1])+'/'+url
                redirecturl=self.path
                self.rename({"all":name})
                
        self.set_propriete("titre",titre)
        self.set_propriete("textnav",textnav)
        self.set_propriete("description",description)

        self.socket.redirection_http(redirecturl, "Action Ok")

    def affiche_image(self):

        self.pathfiles=self.config.path['files']
        self.filepath=self.pathfiles+self.path

        self.sendbinary()

    def affiche(self):

        _=self.datas._
        name=name_from_path(self.path)
        if self.id!=self.datas.objet_actu.id:

            titre=self.get_propriete('titre','')
            description=self.get_propriete('description','')
            pathpage=self.config.path['files']+self.path
            pathlist=pathpage+'/normal/'
            elems=os.listdir(pathlist)
            images_elems=""
            if len(elems)>6:
                alea_elem=[]
                while len(alea_elem)<4:
                    e=random.choice(elems)
                    if e[0]!='.' and e not in alea_elem:
                        alea_elem.append(e)
                        images_elems+="""&nbsp;<img src="%s/%s/mini/mini_%s" border="0" />&nbsp;""" % (self.datas.objet_actu.path,name,e)
            self.socket.send_datas( u"""<div class="galerie_extrait"><a href="%s/%s" title="%s" alt="%s"><p class="bottom5">%s %s</p>%s</a></div>""" % (
                    self.datas.objet_actu.path,name,description,description,_('voir la galerie'),titre,images_elems))
            return

        self.page()
            
    def page(self):
        
        titre=self.get_propriete('titre','')
        description=self.get_propriete('description','')
        
        self.socket.send_datas( "<h1>%s</h1>" % titre)
        self.socket.send_datas( "%s<br />" % description)

        pathpage=self.config.path['files']+self.path

        pathlist=pathpage+'/normal/'
        elems=os.listdir(pathlist)
        elems.sort()
        try:
            elems.remove('.svn')
        except:
            pass

        for elem in elems:
            f=open(pathpage+'/info/'+elem+'.info')
            d=f.read()
            f.close()
            (titre,description)=d.split('\n',1)
            template="""<div class="galerie_elem"><a href="%s/voir/%s"><p class="bottom5">%s</p>
            <img src="%s/mini/mini_%s" alt="%s" title="%s" border="0" />
            </a>
            </div>
            """ % (self.path,elem,titre,self.path,elem,titre,description)
            self.socket.send_datas(template)

    def voir(self):
        _=self.datas._
        elem=self.datas.action_params[0]
        pathpage=self.config.path['files']+self.path

        pathlist=pathpage+'/normal/'
        elems=os.listdir(pathlist)
        elems.sort()
        indexelem=elems.index(elem)
        precedent=''
        if indexelem>0:
            precedent='&lt;&lt; <a href="%s/voir/%s">%s</a> &lt;&lt;' % (
                self.path,elems[indexelem-1],_('Precedent')
                )
        suivant=''
        if indexelem<len(elems)-1:
            suivant='&gt;&gt; <a href="%s/voir/%s">%s</a> &gt;&gt;' % (
                self.path,elems[indexelem+1],_('Suivant')
                )

        f=open(pathpage+'/info/'+elem+'.info')
        d=unicode(f.read(),'utf-8')
        f.close()
        (titre,description)=d.split('\n',1)
        template=u"""%s <a href='%s'>%s</a> %s <br /><br /><h3>%s</h3>
            <img src="%s/normal/%s" alt="%s" title="%s" border="0" /><br />
            %s<br /><br /><a href="%s/download/download_%s">%s</a>
            """ % (precedent,self.path,_('Retour galerie'),suivant,titre,self.path,elem,titre,titre,description,self.path,elem,_('Version Detail'))
        self.socket.send_datas(template)

    action_default=affiche

    a4u=[(edit_form,     'edit/form'),
         (edit_ok,       'edit/ok'),
         (voir,          'voir/*'),
         (page,          'page/*'),
         (affiche_image, 'mini/*'),
         (affiche_image, 'normal/*'),
         (affiche_image, 'download/*'),
         (ajoute_galerie_element_form, 'ajoute/form'),
         (ajoute_galerie_element,     'ajoute/ok'),
         ]
    f_direct = [edit_form,edit_ok, 
                ajoute_galerie_element_form,ajoute_galerie_element, 
                affiche_image]
    
