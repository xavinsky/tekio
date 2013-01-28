# -*- coding: utf-8 -*-

from tekio.libtek import check_admin, check_edit
from tekio.objets.base import ObjBase
from tekio.objets.base import get_propriete, set_propriete

def get_palette(datas,socket,t):
    palette=None
    if check_admin(datas,socket,alerte=False):
        palette=palette_admin(datas,socket,t)
    elif check_edit(datas,socket,alerte=False):
        palette=palette_editor(datas,socket,t)
    return palette

def palette_editor(datas,socket,t):
    return palette_admin(datas,socket,t)

def palette_admin(datas,socket,t):
    _=datas._
    palette=[
           [(_('Se deconnecter'),'logout',1,None),
            (_('A propos'),'apropos',1,None),
            ],
          ]

    if check_admin(datas,socket,alerte=False):
        palette.extend([
           [(_('Editer Proprietes'),'editsite',1,None),
            (_('Editer Skins'),'editskins',1,None),
            (_('Gestion Utilisateurs'),'editusers',1,None),
            ],
                  ])
    else:
        palette.extend([
           [(_('Editer Proprietes'),'editsite',1,None),
            (_('Editer Skins'),'editskins',1,None),
            ],
                  ])


    if t=='2':
            ## TODO Externaliser le palette d'un type d'objet dans sa classe
            #PAGE
        palette.extend([
                   [(_('Ajouter une page'),'addpage',1,None),
                    (_('Editer page'),'editpage',1,None),
                    (_('Deplacer page'),'movepage',1,None),
                    (_('Detruire page'),'delpage',1,None),
                  ],
                   [(_('Ajouter Texte'),'addtext',1,None),
                    (_('Ajouter Image'),'addimage',1,None),
                    (_('Ajouter Fichier'),'addfile',1,None),
                    (_('Ajouter Galerie'),'addgalerie',1,None),
                  ],
                  ])
    elif t=='0':
            #RACINE
        palette.extend([
                   [(_('Ajouter une page'),'addpage',1,None),
                    (_('Editer page'),'editpage',1,None),
                  ],
                   [(_('Ajouter Texte'),'addtext',1,None),
                    (_('Ajouter Image'),'addimage',1,None),
                    (_('Ajouter Fichier'),'addfile',1,None),
                    (_('Ajouter Galerie'),'addgalerie',1,None),
                  ],
                  ])
    elif t=='4':
            #GALERIE
        palette.extend([
                   [(_('Editer propriete'),'editgalinfo',1,None),
                    (_('Ajouter Element'),'addelemgal',1,None),
                  ],
                  ])

    else:
            #AUTRE
        pass


    return palette


def get_palette_modes(datas,t):
    _=datas._
    palette_modes=[]
    if t=='0' or t=='2' :
        palette_modes.extend([(_('Activer edition de contenu'),'wikion',1,None),])

    return palette_modes

class Palette(ObjBase):

    def affiche(self):
        if not check_admin(self.datas,self.socket,False):
            return
	typeactu=self.datas.objet_actu.name_class
	if (typeactu==0) and (self.datas.objet_actu.action.__name__!='affiche'):
		typeactu=-1

        active=self.get_propriete('active','false')
        posx=self.get_propriete('initx','0')
        posy=self.get_propriete('inity','30')

        id_user=self.datas.my_session.id_user
        if id_user>-1:
            active=get_propriete(self.glob,id_user,'pal_active',active)
            posx=get_propriete(self.glob,id_user,'pal_initx',posx)
            posy=get_propriete(self.glob,id_user,'pal_inity',posy)

        if active!="false":
            self.socket.send_datas("""<div class="pere_palette">
<div id="palette" class="palette" alt="palette">
  Palette
</div>
<script language="javascript">
jsbox_init_box("palette",%s,%s,120,100,'white');
http_url_datas_to_fct("/%s/in/%s",load_palette);
</script>
</div>
""" % ( posx,posy,self.get_name(), typeactu ) )

    def palette(self):
        if not check_edit(self.datas,self.socket,False):
            return
        _=self.datas._
        param=self.datas.action_params[0]
        pal=get_palette(self.datas,self.socket,param)
        self.socket.send_datas("""<div class="icones_palette">""")
        for l in pal:
            for (m2_name, m2_id, m2_aff, m2_subs) in l:
                if m2_aff!=0:
                    self.socket.send_datas("""<a href="#" onclick="javascript:pal_click(event,'%s');"><img class="img_pal_base" src="/includes/images/interface/iconsmenu/%s.png"><img class="img_pal_hover" src="/includes/images/interface/iconsmenu/%s_r.png"></a>""" % (m2_id,m2_id,m2_id)) 
            self.socket.send_datas("""<br />""")
        self.socket.send_datas("""</div>""")
        self.socket.send_datas("""<div class="pal_modes">""")
        mpal=get_palette_modes(self.datas,param)
        for (m2_name, m2_id, m2_aff, m2_subs) in mpal:
            if m2_aff!=0:
                self.socket.send_datas("""<a href="#" onclick="javascript:pal_click(event,'%s');"><img class="img_pal_base" src="/includes/images/interface/iconsmenu/%s.png"><img class="img_pal_hover" src="/includes/images/interface/iconsmenu/%s_r.png"></a>""" % (m2_id,m2_id,m2_id)) #
        self.socket.send_datas("""</div>""")

    def position(self):
        _=self.datas._
        posx=int(self.datas.action_params[0])
        posy=int(self.datas.action_params[1])
        id_user=self.datas.my_session.id_user
        set_propriete(self.glob,self.database,id_user,'pal_initx',posx)
        set_propriete(self.glob,self.database,id_user,'pal_inity',posy)
        self.socket.send_datas("""alert:%s %s %s""" % (_('nouvelle position palette : '),posx,posy))
        

    def includes(self):
        if check_edit(self.datas,self.socket,False):
            return [('js','palette.js'),
		    ('css','palette'),]
        else:
            return []

    a4u=[(palette,            'in/*'),
         (position,           'position/*/*'),]

    f_direct = [palette,position]
