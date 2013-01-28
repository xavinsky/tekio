# -*- coding: utf-8 -*-

import gettext
from tekio.utils import surcharge_unicode

def get_traducteurs(config):
    table_traducteurs={}
    for lg in config.langues_interface:
        langue_code="fr_FR"
        if lg=="es":
            langue_code="es_MX"
        elif lg=="fr":
            langue_code="fr_FR"
        elif lg=='en':
            langue_code="en_US"

        file_trad=open('%s/locale/%s/LC_MESSAGES/internationalisation.mo' % ( config.path['instance'],
                                                                              langue_code), 'r')
        Trad=gettext.GNUTranslations(file_trad)
        table_traducteurs[lg]=surcharge_unicode(Trad.gettext)
        file_trad.close()
        file_trad=None
        Trad=None
    return table_traducteurs
