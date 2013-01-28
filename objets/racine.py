# -*- coding: utf-8 -*-

from tekio.libtek import check_admin, check_edit
from tekio.libtek import redirect_ok

from tekio.objets.base import ObjBase
from tekio.objets.base import get_propriete
from tekio.objets.base import create_element

from tekio.objets.page import ajoute_page_form, ajoute_page
from tekio.objets.page import edit_page_form, edit_page

from tekio.objets.site import edit_site_form, edit_site
from tekio.objets.image import ajoute_image_form, ajoute_image
from tekio.objets.file import ajoute_file_form, ajoute_file
from tekio.objets.texte import ajoute_text_form, ajoute_text
from tekio.objets.galerie import ajoute_galerie_form, ajoute_galerie

from tekio.objets.wiki import element_delete_confirm, enleve_element
from tekio.objets.wiki import element_move
from tekio.objets.wiki import element_edit_form

class Racine(ObjBase):
    ajoute_page_form=ajoute_page_form
    ajoute_page=ajoute_page
    edit_page_form=edit_page_form
    edit_page=edit_page
    edit_site_form=edit_site_form
    edit_site=edit_site
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
        self.datas.site_title=self.get_propriete('site_titre_%s' % l,"")
        self.datas.site_description=self.get_propriete('site_description_%s' % l,"")
        self.datas.site_keywords=self.get_propriete('site_keywords_%s' % l,"")
        self.datas.title=self.get_propriete('titre_%s' % l,"")
        self.datas.description=self.get_propriete('description_%s' % l,"")
        self.datas.keywords=self.get_propriete('keywords_%s' % l,"")
                                

    def affiche(self):
        """
        self.socket.send_datas('<h1>HOME</h1>\n')
        self.socket.send_datas("URL : %s <br /> " % self.pathr)
        self.socket.send_datas("SUBPATH : %s <br />" % self.subpath)
        """
        pass

    def admin(self):
	    if not check_admin(self.datas,self.socket):
		    return
	    _=self.datas._
	    self.socket.send_datas(_('<h1>Administration </h1>\n'))
	    self.socket.send_datas('<a href="%s/admin/users">%s</a><br />' % (self.datas.url_base,_('Gestion des utilisateurs')))
	    self.socket.send_datas('<a href="%s/admin/globs">%s</a><br />' % (self.datas.url_base,_('Vue technique des objets')))


    def admin_users(self):
	    if not check_admin(self.datas,self.socket):
		    return
	    _=self.datas._
	    self.socket.send_datas('<h1>%s</h1>\n' % _('Gestion des utilisateurs'))
            
	    users=self.glob.utilisateurs

	    self.socket.send_datas('<br /><br /><ul class="liste">')
	    for (id,user) in users.items():
                listgroups="(%s)" % ', '.join(user.groupes)
                self.socket.send_datas('<li>[<a href="%s/admin/users/edit/%s">E</a>] [<a href="%s/admin/users/delete/%s">D</a>]%s %s</li>\n' % (self.datas.url_base,id,self.datas.url_base,id,listgroups,user['proprietes']['openid']))
	    self.socket.send_datas('</ul>')
	    self.socket.send_datas('<form action="%s/admin/users/new" method="post">' % self.datas.url_base)
	    self.socket.send_datas('%s <input type="text" name="newopenid" value="" />' % _('Nouvel utilisateur : openid'))
	    self.socket.send_datas('<input type="submit" value="%s" />' % _('Valider'))
	    self.socket.send_datas('</form>')

    def admin_users_new(self):
	    if not check_admin(self.datas,self.socket):
		    return
	    _=self.datas._
	    newuser=self.socket.input_text_value('newopenid')  
	    self.datas.my_session.set_new_url('/admin/users/')
            if newuser in self.glob.openids.keys():
                redirect_ok(self.socket,self.datas)
            
            create_element(self.glob,self.database,40,0,{},{'openid':newuser,})

	    redirect_ok(self.socket,self.datas)

    def admin_users_edit(self):
	    if not check_admin(self.datas,self.socket):
		    return
	    _=self.datas._
            elem=self.datas.action_params[0]
	    self.socket.send_datas('<h1>%s %s</h1>\n' % (_('Edition Utilisateur'),elem))
	    allgroups=self.glob.groupes
	    self.socket.send_datas('<form action="%s/admin/users/valid/edit" method="post">' % self.datas.url_base)
	    self.socket.send_datas('<input type="hidden" name="iduser" value="%s" />' % elem)
	    self.socket.send_datas('%s' % _('Liste des groupes :<br />'))
	    for (idg,groupe) in allgroups.items():
                nameg=groupe['proprietes']['nom']
                if idg in self.glob.utilisateurs[elem].groupes:
                    checked=' checked '
                else:
                    checked=' '
                self.socket.send_datas('<input type="checkbox" name="groupe_%s" %s /> %s <br />' % (idg,checked,nameg))
	    self.socket.send_datas('<input type="submit" value="%s" />' % _('Valider'))
	    self.socket.send_datas('</form>')

    def admin_users_delete(self):
	    if not check_admin(self.datas,self.socket):
		    return
	    _=self.datas._
            elem=self.datas.action_params[0]
	    iduser=int(elem)
	    self.datas.my_session.set_new_url('/admin/users/')
            openid=self.glob.utilisateurs[elem]['proprietes']['openid']
            del(self.glob.openids[openid])
            del(self.glob.utilisateurs[elem])
	    for (idg,groupe) in self.glob.groupes.items():
                if elem in groupe.responsables:
                    groupe.responsable.remove(elem)
                if elem in groupe.membres:
                    groupe.membres.remove(elem)
            
            detruire_element(self.interfaces,iduser)
	    redirect_ok(self.socket,self.datas)

    def admin_users_valid_edit(self):
        if not check_admin(self.datas,self.socket):
            return
        iduser=int(self.socket.input_text_value('iduser'))

        for g in self.glob.utilisateurs[iduser].groupes:
            self.glob.groupes[g].membres.remove(iduser)
        self.glob.utilisateurs[iduser].groupes=[]
        self.database.write('del_my_groupes',(iduser,))

        listgr=[]
        for k in self.socket.input_text_value:
            if k.find('groupe_')!=-1:
                listgr.append(int(k.split('groupe_')[1]))
                
        for gr in listgr:
            self.database.write('add_liaison',(int(gr),iduser,3))
            self.glob.groupes[gr].membres.append(iduser)
            self.glob.utilisateurs[iduser].groupes.append(gr)

        self.datas.my_session.set_new_url('/admin/users/')
        redirect_ok(self.socket,self.datas)


    def includes(self):
	    if check_edit(self.datas,self.socket, False):
		    return [('js','base.js'),
			    ('js','config.js'),
			    ('js','editeurtext.js'),
                            ('js','events.js'),
                            ('js','colors.js'),
                            ('js','iefix.js'),
                            ('js','interraction.js'),
                            ('js','editskindispo.js'),
                            ('js','selectorcolor.js'),
			    ('css','editeurtext'),
                            ('css','selectorcolor'),]

	    else:
		    return [('js','base.js'),
			    ('js','config.js'),]
	    

    def action_apropos(self):
	_=self.datas._    
        self.socket.send_datas('<h1>%s V0.2 beta</h1>\n' % _('Tekio version '))
        self.socket.send_datas('<h1>%s <a href="mailto:xav@tekio.org">xav@tekio.org</a>.</h1>\n' % _('En cas de probleme contacter'))


    def admin_stop(self):
	if not check_admin(self.datas,self.socket):
	    return
        _=self.datas._
        self.socket.send_datas('<h1>FIN</h1>\n')
	self.glob.stop_flag=True
	self.socket.newsoc()


    def affiche_arbre_pages_glob(self,idobj,niv):
        self.vuglob.append(idobj)
        espace='&nbsp;'*niv*2
        page=self.glob.objets[idobj]
        self.socket.send_datas("<br /> <b>%s</b> : %s" % ('sous_pages',str(page['sous_pages'][self.glob.langues[0]])))
        self.socket.send_datas("<br /> <b>ordre sous pages</b> : %s" % (page['proprietes']['ordre_sous_pages']) )

    def affiche_arbre_glob(self,idobj,niv):
        self.vuglob.append(idobj)
        espace='&nbsp;'*niv*2
        obj=self.glob.objets.get(idobj,None)
        if not obj:
            self.socket.send_datas("%s%s : MANQUANT<br />" % (espace,str(idobj)))
        else:
            names=obj.get('names',{})
            if len(names.values())==0:
                name=''
            else:
                name=names.values()[0]
            ltype=obj.get('type','??')
            self.socket.send_datas("%s<a href='/admin/glob/%s'>%s(%s)[%s]</a><br />" % ( espace,
                                                                                         str(idobj),
                                                                                         name,
                                                                                         str(idobj),
                                                                                         ltype))
            subs=obj.get('subs',[])
            for sub in subs:
                if not sub in self.vuglob:
                    self.affiche_arbre_glob(sub,niv+1)
                else:
                    self.socket.send_datas("%sDOUBLON (pere %s fils %s)<br />" % (espace,str(idobj),str(sub)))
                

    def admin_check_globs(self):
        self.vuglob=[]
        self.socket.send_datas("<br /><br />users : %s " % str(self.glob.utilisateurs))
        self.socket.send_datas("<br /><br />groupes : %s " % str(self.glob.groupes))
        self.socket.send_datas("<br /><br />openids : %s " % str(self.glob.openids))
        self.socket.send_datas("<br /><br />langues : %s " % str(self.glob.langues))

        self.socket.send_datas("<br /><br />objets : <br />")
        self.affiche_arbre_glob(0,0)
        nonlies=[]
        for o in self.glob.objets.keys():
            if not o in self.vuglob:
                nonlies.append(o)
        self.socket.send_datas("<br /><br />objets non lies : %s" % str(nonlies))
        
    def admin_check_globps(self):
        self.vuglob=[]
        self.affiche_arbre_pages_glob(0,0)

    def admin_check_glob(self):
        elem=self.datas.action_params[0]
        self.socket.send_datas('<a href="/admin/globs/">retour objets</a> <br />')
        self.socket.send_datas("objet %s <br />" % elem)
        for (k,v) in self.glob.objets[int(elem)].items():
            self.socket.send_datas("<br /> <b>%s</b> : %s" % (str(k),str(v)))

	
    a4u=[(action_apropos,            'action/apropos'),
	 
	 (ajoute_page_form,    'ajoute_page/form'),
	 (ajoute_page,         'ajoute_page'),
	 (edit_page_form,      'edit_page/form'),
	 (edit_page,           'edit_page'),
	 (edit_site_form,      'edit_site/form'),
	 (edit_site,           'edit_site'),
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
    
    f_direct = [admin_users_new,admin_users_valid_edit,admin_users_delete,
		ajoute_page_form, ajoute_page,
		edit_page_form, edit_page,
		edit_site_form, edit_site,
		ajoute_text_form, ajoute_text, 
		ajoute_image_form, ajoute_image,
		ajoute_file_form, ajoute_file,
		ajoute_galerie_form, ajoute_galerie,
		element_edit_form,
		element_move, 
		admin_stop, 
		element_delete_confirm,  
		enleve_element, action_apropos]



