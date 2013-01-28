# -*- coding: utf-8 -*-

from tekio.libtek import check_admin
from tekio.langues import tablangtrad

def edit_site_form(self):
    _=self.datas._
    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path

    inputslang=""
    for code in self.config.langues:
        l=tablangtrad[code][self.datas.my_session.langue]

        titre=self.get_propriete('site_titre_%s' % code)
        keywords=self.get_propriete('site_keywords_%s' % code)
        description=self.get_propriete('site_description_%s' % code)

        inputslang+="<br /><br />%s %s : <br />" % (_('Information en '),l) 
        inputslang+="""
%s : <input type="text" name="titre_%s" value="%s"/><br />
%s : <input type="text" name="keywords_%s" value="%s"/><br />
%s : <textarea name="description_%s" class="petit">%s</textarea>
""" % ( _('Titre'),       code, titre,
        _('Meta : Mots clefs'),  code, keywords,
        _('Meta : Description'), code, description )

    template=u"""
%s :
<form action="%s/edit_site" method="POST" id="panneauform" >
%s
<div id="div_valid" class="invisible">
<input type="button" value="%s" onClick="document.forms.panneauform.submit();">
</div>
</form>
""" % (_(u'Editer les proprietes du site'),baseurl,inputslang,_('Valider'))
    self.socket.send_datas(template)

def edit_site(self):
    if not check_admin(self.datas,self.socket):
        return

    baseurl=self.datas.url_base
    if self.path!='/':
        baseurl+=self.path
            
    inputslang=""
    for code in self.config.langues:

        titre=self.socket.input_text_value('titre_%s' % code)
        if not titre:
            titre=''
        self.set_propriete("site_titre_%s" % code,titre)

        keywords=self.socket.input_text_value('keywords_%s' % code)
        if not keywords:
            keywords=''
        self.set_propriete("site_keywords_%s" % code,keywords)

        description=self.socket.input_text_value('description_%s' % code)
        if not description:
            description=''
        self.set_propriete("site_description_%s" % code,description)

    self.socket.redirection_http(baseurl, "Action Ok")

