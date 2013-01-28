# -*- coding: utf-8 -*-

# TODO 

# get_types_skin_current()
# afin de recuperer le css interne et l'appliquer a la zone d'edition...

# taille de la zone d'edition, largeur variable selon existant.
# hauteur variable selon nombre de langues...

css="editeurtext.css"
js="editeurtext.js"

def select_styles(datas):
    _=datas._

    # get_types_skin_current(datas)
    styles_skin=['testxav',]

    addoptions=""
    for s in styles_skin:
        addoptions+='<option value="0 c %s">%s</option>\n' % (s,s)

    return """<select id="selectstyle" onchange="SelectStyle(this.id);">
  <option value="">%s</option>
  <option value="none">%s</option>
%s  <option value="1 h1">H1 </option>
  <option value="1 h2">H2 </option>
  <option value="1 h3">H3 </option>
  <option value="1 h4">H4 </option>
  <option value="1 h5">H5 </option>
  <option value="1 h6">H6 </option>
  <option value="1 h7">H7 </option>
  <option value="1 p">p</option>
  <option value="0 pre">pre</option>
</select>
    """ % (_('Appliquer un style'),_('Normal'),addoptions)

def get_toolbar(datas):
    _=datas._
    return """<div class="imagebutton" style='width: 90px;' id="source">%s</div>
<div class="imagebutton" id="bold"><b>B</b></div>
<div class="imagebutton" id="italic"><b><i>I</i></b></div>
<div class="imagebutton" id="underline"><span class="underline">U</span></div>
<div class="imagebutton" id="textbarre"><span class="textbarre">M</span></div>
<div class="imagebutton" id="sup">x<sup><span style="color: blue;">2</font></sup></div>
<div class="imagebutton" id="sub">x<sub><span style="color: blue;">i</font></sub></div>
<div class="imagebutton" id="createlink"><img class="image" src="/includes/images/interface/editeurtext/link.gif"></div>
<div class="imagebutton" id="unlink"><img class="image" src="/includes/images/interface/editeurtext/unlink.gif"></div>
%s
""" % (_('HTML'),select_styles(datas))

def zone_saisie(name,datas,codelang,txtinit,visu='visu3_3'): 
    _=datas._
    return u"""<iframe id="ftext_%s_%s" class="%s" src="/includes/iframe/editeurtext.html"></iframe> 
<textarea id="%s_%s" name="%s_%s" class="novisible">%s</textarea
>""" % (name,codelang,visu,name,codelang,name,codelang,unicode(txtinit,'utf-8'))

def get_js_prepare_submit(): 
    return 'prepare_value_editeurtext();'

def get_js_swap_zones_edit(zone_edit): 
    return "swap_zones_edit('%s');" % zone_edit


