# -*- coding: utf-8 -*-

from tekio.objets.racine import Racine
from tekio.objets.login import Login
from tekio.objets.page import Page
from tekio.objets.folder import Folder
from tekio.objets.texte import Texte
from tekio.objets.image import Image, ImageAleatoire
from tekio.objets.file import File
from tekio.objets.galerie import Galerie
from tekio.objets.navigation import Navigation
from tekio.objets.skin import Skins, Skin, SkinPart
from tekio.objets.utilisateurs import Utilisateur, Groupe
from tekio.objets.admin import Admin
from tekio.objets.palette import Palette
from tekio.objets.menu import Menu
from tekio.objets.forge import Forge, Moule, Piece

# TODOBEST : include liste libtek et getattr 
classes={
    0  : Racine,
    1  : Admin,
    2  : Page,
    3  : Folder,
    4  : Galerie,
    5  : Menu,
    6  : Palette,
    7  : Login,
   11  : Texte,
   12  : Image,
   13  : File,
   20  : Navigation,
   30  : Skin,
   31  : SkinPart,
   32  : Skins,
   40  : Utilisateur,
   41  : Groupe,
   50  : Forge,
   51  : Moule,
   52  : Piece,
  100  : ImageAleatoire,
}

disposition_niveau={
    0  : 1,
    1  : 2,
    2  : 4,
    3  : 4,
    4  : 4,
    5  : 7,
    6  : 7,
    7  : 4,
   11  : 6,
   12  : 6,
   13  : 6,
   20  : 6,
   30  : 2,
   31  : 2,
   32  : 4,
   40  : 6,
   41  : 6,
   50  : 4,
   51  : 4,
   52  : 4,
  100  : 6,
}

def get_info_id_class(id_class,propriete,default=None):
    return getattr(classes[id_class],propriete,default)
