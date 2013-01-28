# -*- coding: utf-8 -*-

from tekio.libtek import check_admin
from tekio.libtek import redirect_ok
from tekio.libtek import get_instance_from_id
from tekio.libtek import names_classes
from tekio.objets.base import ObjBase
from tekio.objets.base import purge_db_element
from tekio.objets.base import create_element, detruire_element
from tekio.objets.base import get_propriete, set_propriete, del_propriete
from tekio.objets.base import id_get_fils_by_name
from tekio.objets.page import new_Page
from tekio.objets.texte  import new_Text
from tekio.utils  import stou, utoh, balise_utf8

import os

class Admin(ObjBase):
                  
    def affiche(self):
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
            
	    users=self.glob.openids

	    self.socket.send_datas('<br /><br /><ul class="liste">')
	    for (openid,idu) in users.items():
                user=self.glob.objets[idu]
                ids_groups=user['groupes']
                names_groups=[]
                for idg in ids_groups:
                    names_groups.append(self.glob.objets[idg]['proprietes']['nom'])

                listgroups="(%s)" % ', '.join(names_groups)
                self.socket.send_datas('<li>[<a href="%s/admin/users/edit/%s">E</a>] [<a href="%s/admin/users/delete/%s">D</a>]%s %s</li>\n' % (self.datas.url_base,idu,self.datas.url_base,idu,listgroups,user['proprietes']['openid']))
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
            self.glob.get_population(self.database)

	    redirect_ok(self.socket,self.datas)

    def admin_users_edit(self):
	    if not check_admin(self.datas,self.socket):
		    return
	    _=self.datas._
            elem=self.datas.action_params[0]
            iduser=int(elem)
	    self.socket.send_datas('<h1>%s %s</h1>\n' % (_('Edition Utilisateur'),elem))
	    allgroups=self.glob.groupes
	    self.socket.send_datas('<form action="%s/admin/users/valid/edit" method="post">' % self.datas.url_base)
	    self.socket.send_datas('<input type="hidden" name="iduser" value="%s" />' % elem)
	    self.socket.send_datas('%s' % _('Liste des groupes :<br />'))
	    for (nameg,idg) in allgroups.items():
                groupe=self.glob.objets[idg]
                if iduser in groupe['membres']:
                    checked=' checked '
                else:
                    checked=' '
                self.socket.send_datas('<input type="checkbox" name="groupe_%s" %s value="OK" /> %s <br />' % (idg,checked,nameg))
	    self.socket.send_datas('<input type="submit" value="%s" />' % _('Valider'))
	    self.socket.send_datas('</form>')

    def admin_users_delete(self):
	    if not check_admin(self.datas,self.socket):
		    return
	    _=self.datas._
            elem=self.datas.action_params[0]
	    iduser=int(elem)
            if iduser in self.glob.users_indestructibles:
                self.socket.send_datas('Le premier administrateur du site est indestructible ')
                return
            
	    self.datas.my_session.set_new_url('/admin/users/')
            openid=self.glob.objets[iduser]['proprietes']['openid']
            del(self.glob.openids[openid])
            self.glob.utilisateurs.remove(iduser)
	    for (nomgroupe,idg) in self.glob.groupes.items():
                groupe=self.glob.objets[idg]
                if iduser in groupe['responsables']:
                    groupe['responsable'].remove(iduser)
                if iduser in groupe['membres']:
                    groupe['membres'].remove(iduser)
            
            detruire_element(self.interfaces,iduser)
	    redirect_ok(self.socket,self.datas)

    def admin_users_valid_edit(self):
        if not check_admin(self.datas,self.socket):
            return
        iduser=int(self.socket.input_text_value('iduser'))
        user=self.glob.objets[iduser]
        for g in user['groupes']:
            groupe=self.glob.objets[g]
            if iduser in groupe['membres']:
                groupe['membres'].remove(iduser)

        user['groupes']=[]
        self.database.write('del_my_groupes',(iduser,))

        listgr=[]
        form_keys=self.socket.form_keys()
        for k in form_keys:
            if k.find('groupe_')!=-1:
                idg=int(k.split('groupe_')[1])
                res=self.socket.input_text_value(k)
                if res:
                    listgr.append(idg)

                
        for gr in listgr:
            self.database.write('add_liaison',(int(gr),iduser,3))
            self.glob.objets[gr]['membres'].append(iduser)
            self.glob.objets[iduser]['groupes'].append(gr)

        self.datas.my_session.set_new_url('/admin/users/')
        redirect_ok(self.socket,self.datas)


    def admin_stop(self):
	if not check_admin(self.datas,self.socket):
	    return
        _=self.datas._
        self.socket.send_datas('<h1>FIN</h1>\n')
	self.glob.stop_flag=True
	self.socket.newsoc()


    def affiche_arbre_pages_glob(self,idobj,niv):
        if not check_admin(self.datas,self.socket):
            return
        self.vuglob.append(idobj)
        espace='&nbsp;'*niv*2
        page=self.glob.objets[idobj]
        self.socket.send_datas("<br /> <b>%s</b> : %s" % ('sous_pages',str(page['sous_pages'][self.glob.langues[0]])))
        self.socket.send_datas("<br /> <b>ordre sous pages</b> : %s" % (page['proprietes']['ordre_sous_pages']) )

    def affiche_arbre_glob(self,idobj,niv,flag_del=False):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
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
            txtdel=''
            if flag_del:
                if idobj!=0:
                    path_pere=''
                    idpere=self.glob.objets[idobj]['pere']
                    paths=self.glob.objets[idpere]['path']
                    path_pere=paths.get(self.glob.langues[0],'') 

                    txtdel='[<a href="/enleve_element?id=%s">%s</a>]' % (idobj,_('!!DETRUIRE!!'))
            self.socket.send_datas("%s<a href='/admin/glob/%s'>%s(%s)[%s]</a> %s <br />" % ( espace,
                                                                                         str(idobj),
                                                                                         name,
                                                                                         str(idobj),
                                                                                         ltype,txtdel))
            subs=obj.get('subs',[])
            subs.sort()
            for sub in subs:
                if not sub in self.vuglob:
                    self.affiche_arbre_glob(sub,niv+1,flag_del)
                else:
                    self.socket.send_datas("%sDOUBLON (pere %s fils %s)<br />" % (espace,str(idobj),str(sub)))




    def admin_globs_del(self):
        if not check_admin(self.datas,self.socket):
            return
        self.admin_check_globs(flag_del=True)

    def admin_check_globs(self,flag_del=False):
        if not check_admin(self.datas,self.socket):
            return

        _=self.datas._
        self.vuglob=[]
        if flag_del:
            self.socket.send_datas("""<br /><a href="/admin/globs">Retour MODE NORMAL</a>]""")
        else:
            self.socket.send_datas("<br />users : %s " % str(self.glob.utilisateurs))
            self.socket.send_datas("<br />groupes : %s " % str(self.glob.groupes))
            self.socket.send_datas("<br />openids : %s " % str(self.glob.openids))
            self.socket.send_datas("<br />langues : %s " % str(self.glob.langues))

        self.socket.send_datas("<br /><br />objets : <br />")
        self.affiche_arbre_glob(0,0,flag_del)
        nonlies=[]
        for o in self.glob.objets.keys():
            if not o in self.vuglob:
                nonlies.append(o)
        if not flag_del:
            self.socket.send_datas("<br /><br />objets non lies : %s" % str(nonlies))
            self.socket.send_datas("<br /><br />orphelin : %s" % str(self.glob.orphelins))
            self.socket.send_datas("""<br /><br />[<a href="/admin/globs/purge">PURGE ORPHELINS</a>]""")
            self.socket.send_datas("""<br />[<a href="/admin/globs/delete">MODE DESTRUCTION OBJETS</a>]""")

    def admin_globs_purge(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        for i in self.glob.orphelins:
            purge_db_element(self.interfaces,i)
            self.socket.send_datas("""<br />purge %s """ % i)
        self.socket.send_datas("""<br />FIN PURGE """)
        self.glob.orphelins=[]


    def admin_check_glob(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        elem=self.datas.action_params[0]
        gobj=self.glob.objets[int(elem)]
        self.socket.send_datas('<a href="/admin/globs/">liste objets</a> <br />')
        self.socket.send_datas("""<br /> Objet %s  """ % elem)
        self.socket.send_datas("""(%s:%s)  <br />""" % (gobj['type'],names_classes.get(gobj['type'],'') ) )

        names=gobj.get('names',{})
        if len(names)==0:
            self.socket.send_datas(""" Pas de name !!! <br />""")
        else:
            self.socket.send_datas(""" names : %s <br />""" % names)
        paths=gobj.get('path',{})
        if len(paths)==0:
            self.socket.send_datas(""" Pas de path !!! <br />""")
        else:
            self.socket.send_datas(""" paths : %s <br /><br />""" % paths)

        if elem!='0':
            self.socket.send_datas("""[<a href="/admin/glob/%s">Voir Pere %s</a>]<br /> """ % (gobj['pere'],gobj['pere']) )
        subs=gobj.get('subs',[])
        subs.sort()
        if len(subs)>0:
            self.socket.send_datas("""Fils : """)
            for sub in subs:
                self.socket.send_datas(""" [<a href="/admin/glob/%s">%s</a>] """ % (sub,sub) )
        urls=gobj.get('urls',[])
        self.socket.send_datas("""<br />Urls : %s<br /> """ % urls)
        sous_pages=gobj.get('sous_pages',[])
        self.socket.send_datas("""Sous pages : %s<br /> """ % sous_pages)
        self.socket.send_datas("""[<a href="/admin/glob/add/%s">Ajouter un fils</a>] <br /><br />""" % elem)
        

        proprietes = gobj.get('proprietes',{})
        ks=proprietes.keys()
        ks.sort()
        if len(proprietes)>0:
            self.socket.send_datas("""Proprietes : <br /> """)
            for k in ks:
                v=proprietes[k]
                if type(v)!=type('') and type(v)!=type(u''):
                    v=str(v)
                self.socket.send_datas(u" <b>%s</b> : %s<br />" % (k,stou(v)) )

        self.socket.send_datas("""[<a href="/admin/glob/edit/%s">Editer les proprietes</a>]<br /><br /> """ % elem)

        first=True
        for (k,v) in gobj.items():
            if k not in ['id','type','pere','names','path','subs','urls','sous_pages','proprietes']:
                if first:
                    self.socket.send_datas("<br /><br /> Autres infos :<br />")
                    first=False
                self.socket.send_datas(" <b>%s</b> : %s<br />" % (str(k),str(v)))


    def admin_glob_pr_edit(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        elem=self.datas.action_params[0]
        (hutf8,futf8)=balise_utf8()
        self.socket.send_datas(hutf8)
        self.socket.send_datas('<a href="/admin/globs/">liste objets</a> <br />')
        self.socket.send_datas('<a href="/admin/glob/%s">retour %s</a> <br />' % (elem,elem))
        self.socket.send_datas("proprietes de l'objet %s <br />" % elem)
        pr=self.glob.objets[int(elem)]['proprietes']
        self.socket.send_datas("""<Modifier l'objet <form action="/admin/glob/prmodif/%s" method="POST">""" % elem)
        proprietes=pr.items()
        proprietes.sort()
        for (k,v) in proprietes:
            v=stou(v) 
            v=utoh(v)
            self.socket.send_datas(u""" %s : <input type="text" name="%s" value="%s"> """ % (k,k,v) )
            self.socket.send_datas("""&nbsp;&nbsp; <a href="/admin/glob/prdel/%s/%s">DETRUIRE</a><br /> """ % (elem,k) )
        self.socket.send_datas('<input type="submit" value="%s" />' % _('Modifier'))
        self.socket.send_datas("""</form><br /><br />""")

        self.socket.send_datas("""<hr />Ajout de propriete :<form action="/admin/glob/pradd/%s" method="POST">""" % elem)
        self.socket.send_datas(""" nom : <input type="text" name="nom" > """ )
        self.socket.send_datas(""" valeur : <input type="text" name="valeur" > """ )
        self.socket.send_datas('<input type="submit" value="%s" />' % _('Ajouter'))
        self.socket.send_datas("""</form>""")
        self.socket.send_datas(futf8)


    def admin_glob_add(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        elem=self.datas.action_params[0]
        (hutf8,futf8)=balise_utf8()
        self.socket.send_datas(hutf8)
        self.socket.send_datas('<a href="/admin/globs/">retour objets</a> <br />')
        self.socket.send_datas("Ajout d'un fils a l'objet %s <br />" % elem)
        self.socket.send_datas("""<Modifier l'objet <form action="/admin/glob/addvalid/%s" method="POST">""" % elem)
        self.socket.send_datas(""" Nom : <input type="text" name="nom" value=""> """  )
        self.socket.send_datas(""" Type : <input type="text" name="type" value=""> """  )
        self.socket.send_datas('<input type="submit" value="%s" />' % _('Ajouter'))
        self.socket.send_datas("""</form>""")
        self.socket.send_datas(futf8)


    def admin_glob_add_valid(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        elem=self.datas.action_params[0]

        id_pere=int(elem)
        nom=self.socket.input_text_value("nom")
        t=int(self.socket.input_text_value("type"))

        obj_id=create_element(self.glob,self.database,t,id_pere,{'all':nom,})


        self.socket.send_datas('FAIT!!! <br />')
        self.socket.send_datas('<a href="/admin/globs/">retour objets</a> <br />')

    def admin_glob_pr_modif(self):
        if not check_admin(self.datas,self.socket):
            return
        form_keys=self.socket.form_keys()
        elem=self.datas.action_params[0]
        id_obj=int(elem)
        for k in form_keys:
            v=self.socket.input_text_value(k)  
            oldv=get_propriete(self.glob,id_obj,k)
            if type(oldv)==type('') or  type(oldv)==type(u''):
                if v!=oldv:
                    set_propriete(self.glob,self.database,id_obj,k,v)
        self.datas.my_session.set_new_url('/admin/glob/edit/%s' % elem)
        redirect_ok(self.socket,self.datas)

    def admin_glob_pr_add(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        elem=self.datas.action_params[0]
        id_obj=int(elem)

        name=self.socket.input_text_value('nom')  
        value=self.socket.input_text_value('valeur')  

        set_propriete(self.glob,self.database,id_obj,name,value)

        self.datas.my_session.set_new_url('/admin/glob/edit/%s' % elem)
        redirect_ok(self.socket,self.datas)

    def admin_glob_pr_del(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        elem=self.datas.action_params[0]
        name=self.datas.action_params[1]
        id_obj=int(elem)
        del_propriete(self.glob,self.database,id_obj,name)

        self.datas.my_session.set_new_url('/admin/glob/edit/%s' % elem)
        redirect_ok(self.socket,self.datas)


    def file_is_exist(self,file):
        if os.path.lexists(file) and os.access(file,os.F_OK) and os.access(file,os.R_OK):
            return True
        return False

    def file_is_dir(self,name):
        return os.path.isdir(name)

    def rep_list(self,rep):
        return os.listdir(rep)

    def insert_filetext(self,idpage,filetext,pseudo):
        self.socket.send_datas('<br />Ajout text %s dans page %s ' % (filetext,str(idpage)))  
        f=open(filetext)
        txt=f.read()
        f.close()
        while txt.find('<body>')!=-1:
            txt=txt.split('<body>',1)[1]
        while txt.find('<BODY>')!=-1:
            txt=txt.split('<BODY>',1)[1]
        while txt.find('</body>')!=-1:
            txt=txt.split('</body>',1)[0]
        while txt.find('</BODY>')!=-1:
            txt=txt.split('</BODY>',1)[0]
        
        pere_path=self.glob.objets[idpage]['path']['es']
        if pseudo:
            pass
        else:
            new_Text(self.glob,self.database,self.fs_svn,self.socket,self.config,
                     idpage,pere_path,text={'es':txt},name='initext',file=None, placement_wiki='bottom')
                

    def recursif_insert_datas(self,repdisk,idfolderpere,pseudo):
        self.socket.send_datas('<br /><br />Recursif sur page (%s) : %s ' % (str(idfolderpere),repdisk) )  
        page_pere=get_instance_from_id(self.interfaces,idfolderpere)
        elems=self.rep_list(repdisk)
        reps=[]
        files=[]
        alls=[]
        for elem in elems:
            if elem not in ['noms.txt','NODISPO']:
                efile='%s/%s' % (repdisk,elem)
                if self.file_is_exist(efile):
                    if self.file_is_dir(efile):
                        reps.append(elem)
                    else:
                        files.append(elem)
                    alls.append(elem)
        alls.sort()

        file_noms='%s/noms.txt' % repdisk
        if self.file_is_exist(file_noms):
            f=open(file_noms)
            lines=f.readlines()
            f.close()
            for line in lines:
                line=line.strip()
                try:
                    subs=line.split('/',2)
                except:
                    subs=[]
                if len(subs)==3:
                    if len(alls)==0: 
                        self.socket.send_datas('<br /><b>Erreur , plus de correspondance pour (dans noms.txt) : </b>')  
                        self.socket.send_datas(str(subs))
                    else:
                        nameelem=alls.pop(0)
                        init_datas={'es':{'url':subs[0],
                                          'textnav':subs[2],
                                          'titre':subs[1],
                                          'description':''}}
                        if nameelem in reps:
                            self.socket.send_datas('<br />New page :')  
                        else:
                            self.socket.send_datas('<br />New page* :')  
                        self.socket.send_datas('%s ' % str([nameelem,subs[0]]))

                        if pseudo:
                            idpage=0
                        else:

                            idpage=new_Page(page_pere,init_datas)
                                 
                        newpath='%s/%s' % (repdisk,nameelem)

                        if nameelem in reps:
                            self.recursif_insert_datas(newpath,idpage,pseudo)
                        else:
                            self.insert_filetext(idpage,newpath,pseudo)
                       
                    
        for nameelem in alls:
            if nameelem in reps:
                self.socket.send_datas('<br /><b>Erreur : Repertoire sans infos.</b>')  
                self.socket.send_datas(str(nameelem))
            else:
                filetext='%s/%s' % (repdisk,nameelem)
                self.insert_filetext(idfolderpere,filetext,pseudo)

    def admin_insert_datas_pseudo(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        self.admin_insert_datas(pseudo=True)
                    
    def admin_insert_datas(self,pseudo=False):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        repdisk='%s/datas/filestoinsert' % self.config.path['instance']

        self.recursif_insert_datas(repdisk,0,pseudo)
        self.socket.send_datas('<br />fin insert')

    def admin_migre(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        
        pere_id=0
        id_forge=id_get_fils_by_name(self.glob,pere_id,'forge')
        if id_forge==-1:
            id_type=50 
            name='forge'
            proprietes={}
            id_forge=create_element(self.glob,self.database,
                                    id_type,pere_id,
                                    {'all':name,},proprietes)

            self.socket.send_datas('<br />create forge')
        
        self.socket.send_datas('<br />fin migre')


    def admin_debug(self):
        if not check_admin(self.datas,self.socket):
            return
        _=self.datas._
        
        page_pere=get_instance_from_id(self.interfaces,0)
        init_datas={"es": { "url" : "testaccent2",
                            "textnav" : "ñoño",
                            "titre" : "ñoño ñoño",
                            "description" : ""}}

        idpage=new_Page(page_pere,init_datas)
        self.socket.send_datas('<br />fin debug')


    a4u=[(admin_users,            'users'),
	 (admin_users_new,        'users/new'),
	 (admin_users_edit,       'users/edit/*'),
	 (admin_users_delete,     'users/delete/*'),
	 (admin_users_valid_edit, 'users/valid/edit'),
	 (admin_stop,             'stop'),
	 (admin_check_globs,      'globs'),
	 (admin_globs_del,        'globs/delete'),
	 (admin_globs_purge,      'globs/purge'),
	 (admin_check_glob ,      'glob/*'),
	 (admin_glob_pr_edit ,    'glob/edit/*'),
	 (admin_glob_add ,        'glob/add/*'),
	 (admin_glob_add_valid ,  'glob/addvalid/*'),
	 (admin_glob_pr_modif ,   'glob/prmodif/*'),
	 (admin_glob_pr_del ,     'glob/prdel/*/*'),
	 (admin_glob_pr_add ,     'glob/pradd/*'),
	 (admin_insert_datas ,        'insertdatas/go'),
	 (admin_insert_datas_pseudo , 'insertdatas/pseudo'),
	 (admin_debug,            'debug'),
	 (admin_migre,            'migre'),
	 ]
    
    f_direct = [admin_users_new,admin_users_valid_edit,admin_users_delete,admin_stop,
                admin_check_globs,admin_globs_del,
                admin_check_glob,admin_glob_pr_edit,
                admin_glob_pr_modif,admin_glob_pr_del,admin_glob_pr_add,
                admin_glob_add, admin_glob_add_valid]

    action_default=affiche



