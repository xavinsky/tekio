#!/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
import time

mytracefile=open("logs/mytrace.txt","w")

import tekio.database
import tekio.editeurtext
import tekio.fssvn
import tekio.HTTP
import tekio.langues
import tekio.libtek
import tekio.listclasses
import tekio.parsing
import tekio.sessions
import tekio.sqlliste
import tekio.tekiod
import tekio.traductions
import tekio.utils
import tekio.globdatas
import tekio.objets.base
import tekio.objets.file
import tekio.objets.folder
import tekio.objets.galerie
import tekio.objets.image
import tekio.objets.navigation
import tekio.objets.page
import tekio.objets.racine
import tekio.objets.site
import tekio.objets.skin
import tekio.objets.texte
import tekio.objets.utilisateurs
import tekio.objets.wiki
import tekio.objets.menu
import tekio.objets.palette
import tekio.rendus.HTML

modules_tekio=[tekio.database,
               tekio.editeurtext,
               tekio.fssvn,
               tekio.HTTP,
               tekio.langues,
               tekio.libtek,
               tekio.listclasses,
               tekio.menu,
               tekio.palette,
               tekio.parsing,
               tekio.sessions,
               tekio.sqlliste,
               tekio.tekiod,
               tekio.traductions,
               tekio.utils,
               tekio.globdatas,
               tekio.rendus.HTML,
               tekio.objets.base,
               tekio.objets.file,
               tekio.objets.folder,
               tekio.objets.galerie,
               tekio.objets.image,
               tekio.objets.navigation,
               tekio.objets.page,
               tekio.objets.racine,
               tekio.objets.site,
               tekio.objets.skin,
               tekio.objets.texte,
               tekio.objets.utilisateurs,
               tekio.objets.wiki]

classes_tekio=[]
fonctions_tekio={}


from Queue import Queue
classes_interdites=[Queue,]

def add_fonction(myobjet,myfonction):
    global fonctions_tekio
    fonctions_tekio[myfonction]=myobjet

def check_classe(myclasse):
    global classes_tekio
    classes_tekio.append(myclasse)
    inspect_membres(myclasse)

def check_module(mymodule):
    inspect_membres(mymodule)

def inspect_membres(myobjet):
    global classes_tekio
    global fonctions_tekio
    membres=inspect.getmembers(myobjet)
    for (name,value) in membres:
        if inspect.isclass(value):
            if not value in classes_tekio:
                if not value in classes_interdites:
                    check_classe(value)
        elif inspect.ismethod(value):
            if not value in fonctions_tekio.keys():
                add_fonction(myobjet,value)
        elif inspect.isfunction(value):
            if not value in fonctions_tekio.keys():
                add_fonction(myobjet,value)

def crea_surcharge(f,name):
    def surcharge(*elem,**dico):
        add_trace(f,name)
        return f(*elem,**dico)
    return surcharge


def surcharge_tout():
    global fonctions_tekio
    global modules_tekio
    for mymodule in modules_tekio:
        check_module(mymodule)

    for f in fonctions_tekio.keys():
        c=fonctions_tekio[f]
        newf=crea_surcharge(f,c.__name__)
        setattr(c,f.__name__,newf)
        print '%s => %s' % (c,f)


import time
time_actu=time.time()
info_actu="start"

def add_trace(f,name):
    import tekio.tracetout
    import time
    info_actu='%s.%s' % (name,f.__name__)
    nt=time.time()
    dt=nt-tekio.tracetout.time_actu
    tekio.tracetout.mytracefile.write('%2.6f : %s \n' % (dt,tekio.tracetout.info_actu))
    tekio.tracetout.info_actu=info_actu
    tekio.tracetout.time_actu=nt
    
