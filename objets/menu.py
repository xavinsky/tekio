# -*- coding: utf-8 -*-

from tekio.libtek import check_admin, check_edit
from tekio.sessions import affiche_user_openid
from tekio.objets.base import ObjBase

def get_menu(datas,socket):
    menu=None
    if check_admin(datas,socket,alerte=False):
        menu=menu_admin(datas,socket)
    elif check_edit(datas,socket,alerte=False):
        menu=menu_editor(datas,socket)
    return menu



def menu_editor(datas,socket):
    return menu_admin(datas,socket)

def menu_admin(datas,socket):
    _=datas._

    classe_actu=datas.objet_actu.__class__.__name__
    action_actu=datas.objet_actu.action.__name__

    menu=[(_('Tekio'),None,1,
           [(_('Se deconnecter'),'logout',1,None),
            (_('A propos'),'apropos',1,None),
            ]),
          ]

    if check_admin(datas,socket,alerte=False):
        menu.extend([
          (_('Site'),None,1,
           [(_('Editer Proprietes'),'editsite',1,None),
            (_('Gestion Utilisateurs'),'editusers',1,None),
            ]),
                  ])
    else:
        menu.extend([
          (_('Site'),None,1,
           [(_('Editer Proprietes'),'editsite',1,None),
            ]),
                  ])
    if check_admin(datas,socket,alerte=False):
        if (classe_actu=='Skin'):
            menu.extend([
            (_('Skin'),None,1,
             [ (_('Liste Des Skins'),'editskins',1,None),
               (_('Generation des couleurs'),'skingencolors',1,None),
               (_('Retourche des couleurs'),'skincolors',1,None),
               (_('Modification des images'),'skinimages',1,None),
               (_('Modification des styles'),'skinstyles',1,None),
               (_('Changer la disposition'),'skindisposition',1,None),
               ]),
            ])
        elif ((classe_actu=='Page') or (classe_actu=='Racine')):
            menu.extend([
            (_('Skin'),None,1,
             [ (_('Liste Des Skins'),'editskins',1,None),
               (_('Generation des couleurs'),'skingencolors_%s' % datas.skin_name,1,None),
               (_('Retourche des couleurs'),'skincolors_%s' % datas.skin_name,1,None),
               (_('Modification des images'),'skinimages_%s' % datas.skin_name,1,None),
               (_('Modification des styles'),'skinstyles_%s' % datas.skin_name,1,None),
               (_('Changer la disposition'),'skindisposition_%s' % datas.skin_name,1,None),
               ]),
            ])
        else:
            menu.extend([
            (_('Skin'),None,1,
             [ (_('Liste Des Skins'),'editskins',1,None),
               ]),
                ])


    if (classe_actu=='Page'):
            ## TODO Externaliser le menu d'un type d'objet dans sa classe
            #PAGE
        menu.extend([
                  (_('Page'),None,1,
                   [(_('Ajouter une page'),'addpage',1,None),
                    (_('Editer page'),'editpage',1,None),
                    (_('Deplacer page'),'movepage',1,None),
                    (_('Detruire page'),'delpage',1,None),
                  ]),
                  (_('Contenu'),None,1,
                   [(_('Activer edition de contenu'),'wikion',1,None),
                    (_('Ajouter Texte'),'addtext',1,None),
                    (_('Ajouter Image'),'addimage',1,None),
                    (_('Ajouter Fichier'),'addfile',1,None),
                  ]),
                  ])
    elif ((classe_actu=='Racine') and (action_actu=='affiche')):
            #RACINE
        menu.extend([
                  (_('Page'),None,1,
                   [(_('Ajouter une page'),'addpage',1,None),
                    (_('Editer page'),'editpage',1,None),
                  ]),
                  (_('Contenu'),None,1,
                   [(_('Activer edition de contenu'),'wikion',1,None),
                    (_('Ajouter Texte'),'addtext',1,None),
                    (_('Ajouter Image'),'addimage',1,None),
                    (_('Ajouter Fichier'),'addfile',1,None),
                  ]),
                  ])

    else:
        #AUTRE
        pass

    return menu


"""
TODO

1 Tekio
  parametre logiciel.
    Preference d'Interface (par personne)
      Presentation
        Couleurs
        Typos et styles

2 Affichage
  Cacher les fenetres
  liste de fenetres a a fichier...
  Afficher/masquer la grille. 
  Reperes.
  Sauvegarder/restaurer des Vue 
   (liste de vues type)

3 Edition
  Undo
  Redo
  Selectionner multiple
  Selectionner special
  Deselectionner
  Deselectionner Tout.
  Editer la selection...

4 Page
  Propriete de la page. ( Changer Meta / tags.)
  Liste des objets

5 Site
   Propriete
      Changer Meta. 
      Title. 
      Webmaster....
      Domaine
   Arborescence.
   Droit.
   Utilisateurs. 
   Workflow.
   Habillage

6 Aide
"""

class Menu(ObjBase):

    def affiche(self):
        self.datas.menu=get_menu(self.datas,self.socket)
        if not self.datas.menu:
            return

        actions_menu=""
        
        for (m_name, m_id, m_aff, m_subs) in self.datas.menu:
            nodisplay=""
            if m_aff==0:
                nodisplay=" nodisplay"
            divid=""
            if m_id:
                divid=""" id="menu_%s" onclick="menu_click('%s')" """ % (m_id,m_id)
            if m_subs:
                subs=""
                first=" first"
		for (m2_name, m2_id, m2_aff, m2_subs) in m_subs:
                    m2_id_c=m2_id.split('_',1)[0]
		    divid2=""" id="menu_%s" onclick="menu2_click(event,'%s')" """ % (m2_id,m2_id)
		    nodisplay2=""
		    if m2_aff==0:
                        nodisplay2=" nodisplay"
		    subs+="""<div class="menu_niv2%s %s" %s
><img class="img_menu_base" src="/includes/images/interface/iconsmenu/%s.png" style="vertical-align:middle"
><img class="img_menu_hover" src="/includes/images/interface/iconsmenu/%s_r.png" style="vertical-align:middle"
>&nbsp;&nbsp;&nbsp;&nbsp;%s</div>""" % (nodisplay2,first,divid2,m2_id_c,m2_id_c,m2_name)
		    first=""

                niv2="""
<div
class="menu_niv2_ombre"><div
  class="ombre_menu_niv2_gauche"><div
    class="ombre_menu_niv2_droite"><div
      class="menu_niv2_interieur">
%s
</div></div></div><div class="ombre_menu_niv2_bas"><div
    class="ombre_menu_niv2_bas_gauche"></div><div
    class="ombre_menu_niv2_bas_droite"></div><div
    class="ombre_menu_niv2_bas_centre"></div></div></div>
""" % subs

                    
            actions_menu+="""<div class="menu_niv1 %s" %s>%s%s\n</div>""" % (nodisplay,divid,niv2,m_name)

        affiche_user=affiche_user_openid(self.datas.my_session.user)

        tpl="""
<div class="invisible" style="position: absolute; z-index: 800;" id="retour_menu" onclick="show('menu_tekio');show('ombre_menu_1');hide('retour_menu');" ><img src="/includes/images/interface/iconetekio.png" />\n</div>
<div class="menu_line_niv1" id="menu_tekio">
<div class="menu_logo" ><a name="top" onclick="hide('ombre_menu_1');show('retour_menu');hide('menu_tekio');"><img src="/includes/images/interface/iconetekio.png" /></a>\n</div>%s
%s
</div>
<div class="ombre_menu_1" id="ombre_menu_1">&nbsp;</div>
<div class="panneau_base" id="div_panneau_base">
  <div class="panneau_ombre">
    <div class="panneau_base_contenu" id="div_panneau_base_contenu"></div>
  </div>
  <div class="panneau_valid_base" id="div_panneau_valid"></div>
  <div class="panneau_annule"
    onclick="hide('div_panneau_base');vide('div_panneau_base_contenu');">
    <img class="img_div_base" src="/includes/images/interface/annuler.png" />
    <img class="img_div_hover" src="/includes/images/interface/annuler_r.png" />
  </div>
</div>
<div class="panneau_alerte" id="div_panneau_alerte">
  <div class="panneau_ombre">
    <div class="panneau_alerte_contenu" id="div_panneau_alerte_contenu"></div>
  </div>
  <div class="panneau_valid_alerte" id="div_panneau_valid_alerte"></div>
  <div class="panneau_annule"
    onclick="hide('div_panneau_alerte');vide('div_panneau_alerte_contenu');">
    <img class="img_div_base" src="/includes/images/interface/annuler.png" />
    <img class="img_div_hover" src="/includes/images/interface/annuler_r.png" />
  </div>
</div>
<div class="accesskeylist">
  <a href="javascript:menu_click('wikion');" accesskey="1" >wikion</a>
</div>
""" % (actions_menu,affiche_user)

        self.socket.send_datas(tpl)

        
                
    def includes(self):
        if check_edit(self.datas,self.socket,False):
            return [('css','menu'),
		    ('js','menu.js'),]
        else:
            return []

