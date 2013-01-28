# -*- coding: utf-8 -*-
import random
import openid.consumer.consumer
import openid.cryptutil
import cgi

from tekio.sessions import tuple_cookie, affiche_user_openid

from tekio.utils import quoteattr
from tekio.libtek import get_langue, get_langues
from tekio.libtek import redirect_ok

from tekio.objets.base import ObjBase
from tekio.objets.base import get_proprietes

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

from tekio.langues import tablang

def header(interfaces):
    socket   = interfaces[0]
    datas    = interfaces[7]
    glob     = interfaces[8]
    
    lang=datas.my_session.langue
    title=datas.site_title+" "+datas.title
    description=datas.site_description+" "+datas.description
    keywords=datas.site_keywords+" "+datas.keywords

    includes=""
    includes+='<script type="text/javascript" src="/includes/js/%s.js"></script>\n' % lang
    
    for (typ,file) in datas.includes:
        if typ=="css":
	    includes+='<link rel="stylesheet" type="text/css" href="/includes/css/%s.css" />\n' % file
        elif typ=="js":
	    includes+='<script type="text/javascript" src="/includes/js/%s"></script>\n' % file
	elif typ=="jsl":
	    includes+='<script type="text/javascript" src="%s"></script>\n' % file
	else:
	    includes+=file
                
    includes+='<link rel="stylesheet" type="text/css" href="/includes/css/%s.css" />\n' % lang

    #TODO :
    # multilang keyword/description.
    # keyword/description par url.
    # favicon <link rel="shortcut icon" href="favicon_animated.gif" type="image/gif"/>

    socket.send_datas("""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="%s">
<head>""" % lang)

    baseurl=datas.url_base
    path=socket.get_path()
    if path!='/':
        baseurl+=path
    socket.send_datas("""  <title>%s</title> """ % title)
    socket.send_datas("""  <base id="baseurl" href="%s" />""" % baseurl)
    socket.send_datas("""  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />""")
    socket.send_datas("""  <meta http-equiv="keywords" lang="%s" content="%s" /> """ % (lang,keywords))
    socket.send_datas("""  <meta name="description" lang="%s" content="%s" /> """ % (lang,description))
    socket.send_datas("""<link type="image/png" href="/includes/images/favicon.gif" rel="shortcut icon"/>""")
    socket.send_datas(includes)
    socket.send_datas("""</head>\n<body>""")
    

def footer(interfaces):
    socket   = interfaces[0]
    socket.send_datas('</body></html>')

