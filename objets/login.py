# -*- coding: utf-8 -*-

from tekio.objets.base import ObjBase
from tekio.objets.base import get_propriete
from tekio.objets.base import set_propriete

from tekio.langues import tablang
from tekio.libtek import check_admin, check_edit

import urllib

class Login(ObjBase):


    def affiche(self):
	    _=self.datas._
	    if self.datas.my_session.user:
                    self.socket.send_datas('<h1>%s</h1>\n' % _('Compte utilisateur'))
		    self.socket.send_datas('<br /> %s : %s [<a href="%s/user/logout">%s</a>]<br />' % (_('Utilisateur'),self.datas.my_session.user,self.datas.url_base,_('Deconnection')))

                    pl=self.datas.my_session.langue

		    options_langues=''
		    for l in self.config.langues_interface:
			    selected=""
			    if l==pl:
				    selected=" SELECTED"
			    options_langues+='<option value="%s"%s>%s</option>' % (l,selected,tablang[l])

                    options_palette=""

                    if check_admin(self.datas,self.socket,alerte=False):

                        id_pal=self.glob.objets[0]['urls'][pl].get('palette')
                        id_user=self.datas.my_session.id_user
                        active=get_propriete(self.glob,id_pal,'active',"false")
                        posx=get_propriete(self.glob,id_pal,'initx','0')
                        posy=get_propriete(self.glob,id_pal,'inity',"30")
                        active=get_propriete(self.glob,id_user,'pal_active',active)
                        posx=get_propriete(self.glob,id_user,'pal_initx',posx)
                        posy=get_propriete(self.glob,id_user,'pal_inity',posy)
                        s1=""
                        s2=""
                        if active=='false':
                            s2=" SELECTED"
                        else:
                            s1=" SELECTED"
                        options_palette="""
<li>
<br />
                    %s <select name="pal_active">
                    <option value="true" %s>%s</option>
                    <option value="false" %s>%s</option>
                    </select>
                    / %s
                    X : <input type="text" name="pal_initx" value="%s" size="4" />
                    Y : <input type="text" name="pal_inity" value="%s" size="4" /><br />
</li>
                    """ % (_('Activation de la palette'),s1,_('Activer'),s2,_('Desactiver'),
                           _('Coordonees'),posx,posy)


                    ordre_infos=self.get_propriete('ordre_infos','').split(',')

                    infos=self.get_dico_proprietes('infos')

                    for k in infos.keys():
                        if not k in  ordre_infos:
                            ordre_infos.append(k)
                    
                    infos_html=""
                    pl=self.datas.my_session.langue
                    id_user=self.datas.my_session.id_user
                    for elem in ordre_infos:
                        if elem in infos.keys():
                            info=infos[elem]
                            type_info=""
                            if type(info)==type({}):
                                type_info=info.keys()[0]
                                info=info[type_info]
                            else:
                                type_info='textr'
                              
                            if type(info)==type({}):
                                langs=info.keys()
                                if 'all' in langs:
                                    value=info['all']
                                elif pl in langs:
                                    value=info[pl]
                                elif len(langs)>0:
                                    value=info[langs[0]]
                                else:                               
                                    value=''
                            else:
                                value=str(info)
                               
                            if type_info=='textr':
                                if value:
                                    infos_html+="<li><br /><p>%s</p></li>" % value
                            if type_info=='textu':
                                uservalue=get_propriete(self.glob,id_user,elem,"")
                                if uservalue:
                                    infos_html+="<li><br />"
                                    if value:
                                        infos_html+=value+" : "
                                    infos_html+=uservalue+"</li>"
                            elif type_info=="textw":
                                uservalue=get_propriete(self.glob,id_user,elem,"")
                                infos_html+="""<li><br />
%s : <input type="text" name="%s" value="%s" /></li>""" % (value,elem,uservalue)
                            

                    self.socket.send_datas("""
<form action="%s/user/edit" method="post">
<ul>
<li>
<br />%s : 
<select name="monlanguage">
%s
</select>
</li>
%s
%s
<li>
<br /><input type="submit" value="%s">
</li>
</ul>
</form>
""" % (       self.datas.url_base,_("Votre language"),options_langues,options_palette,infos_html,_("Valider"))) 

	    else:
		    self.socket.send_datas ( """
<h1>%s</h1>
<form action="%s/user/verify" method="post">
<input type="hidden" name="ie" value="e">
<ul>
<li>
<br />%s : <input type="text" name="openid" value="">
</li>
<li>
<li>
<br /><input type="checkbox" name="autoconnect" value="yes"> %s
</li>
<br /><input type="submit" value="%s">
</li>
</ul>
</form>
""" % (_('Connection'),
       self.datas.url_base, _('Identifiant tekio ou Open ID'),
       _('Se connecter automatiquement la prochaine fois'),
       _('se connecter'))
)

    def user_login_db(self):
        pass

    def user_edit(self):
        id_user=self.datas.my_session.id_user
        if id_user<0:
            return
            
        monlanguage=self.socket.input_text_value('monlanguage')  
        set_propriete(self.glob,self.database,id_user,'langue',monlanguage)
        self.datas.my_session.langue=monlanguage
        self.datas.my_session.change_langue_interface(monlanguage)
        pal_active=self.socket.input_text_value('pal_active')  
        pal_initx=self.socket.input_text_value('pal_initx')  
        pal_inity=self.socket.input_text_value('pal_inity')  
        set_propriete(self.glob,self.database,id_user,'pal_active',pal_active)
        set_propriete(self.glob,self.database,id_user,'pal_initx',pal_initx)
        set_propriete(self.glob,self.database,id_user,'pal_inity',pal_inity)


        ordre_infos=self.get_propriete('ordre_infos','').split(',')
        
        infos=self.get_dico_proprietes('infos')

        for k in infos.keys():
            if not k in  ordre_infos:
                ordre_infos.append(k)

        for elem in ordre_infos:
            if elem in infos.keys():
                info=infos[elem]
                type_info=""
                if type(info)==type({}):
                    if info.has_key('textw'):
                        uservalue=self.socket.input_text_value(elem)  
                        set_propriete(self.glob,self.database,id_user,elem,uservalue)
                            
        self.socket.redirection_http("%s/user" % self.datas.url_base)

    def user_verify(self,openid_url=None):
        
        return self.sessions.openid_step_init_verify(self.interfaces,openid_url,self.datas.my_session)

    def user_logout(self):
        redirect=None
        rettek='%s/user' % self.datas.url_base
        retteku=urllib.quote(rettek,'')
        oid=self.datas.my_session.openidinit
        for l in ['fr','es','en']:
            if oid.find('http://%s.openid.tekio.org/id/' % l)==0:
                redirect='http://%s.openid.tekio.org/logout?redirect=%s' % (l,retteku)
        if oid.find('http://getopenid.com/' )==0:
                redirect='http://getopenid.com/action/signoff' 

        if not redirect:
            redirect=rettek

        self.datas.my_session.deconnecte()

        self.socket.redirection_http(redirect)

	
    a4u=[(user_verify,           'verify'),
	 (user_edit,             'edit'),
	 (user_logout,           'logout'),
	 (user_login_db,          'logindb'),
	 ]
    
    f_direct = [user_verify,user_logout,user_edit]

    action_default=affiche

