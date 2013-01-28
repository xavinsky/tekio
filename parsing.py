# -*- coding: utf-8 -*-

import re
from tekio.listclasses import get_info_id_class, disposition_niveau
from tekio.libtek import get_instance_from_infos, get_classe
from tekio.libtek import action_for_url


########################################
# Parsing de l'url dans glob
########################################

def check_action(datas,cl_f,path_r,log):
    listea4u=get_info_id_class(cl_f,'a4u',[])
    action_for_url(datas,listea4u,path_r,log)

def ids_path(datas,glob,socket,log):
    path_entier=socket.path
    lang=datas.my_session.langue
    fragments=path_entier.split('/')
    path_f=''
    path_r=path_entier
    
    #Parcours de l'url pour chercher l'objet cible.
    datas.ids_path=[(0,0,path_f,path_r),]
    datas.action=False
    datas.action_params=[]
    datas.non_objet=[]

    id_p=0
    while len(fragments)!=0 and not datas.action:
        f=fragments.pop(0)
        if f:
            path_f += '/%s' % f
            path_r = path_entier[len(path_f):]
            id_f=glob.objets[id_p]['urls'][lang].get(f,None) 
            if not id_f:
                datas.non_objet.append(f)
                continue

            cl_f=glob.objets[id_f].get('type',None)
            if not cl_f:
                datas.non_objet.append(f)
                continue
            infos=(id_f,cl_f,path_f,path_r)
            datas.ids_path.append(infos)
            if path_r:
                check_action(datas,cl_f,path_r,log)
            id_p=id_f

    if len(datas.ids_path)==1:
        if datas.ids_path[0][3]:
            check_action(datas,0,datas.ids_path[0][3],log)

    datas.infos_objet_actu=datas.ids_path[-1]
    datas.infos_chemin=datas.ids_path[:-1]


def get_dispo_dispo_niveau(glob,id_o,cl_o):
    return glob.objets[id_o]['proprietes'].get('dispo_niveau',
            disposition_niveau.get(cl_o,6))

def get_objets_actifs(glob,datas):
    datas.objets_actifs=[]
    idpos=-1
    for infos in datas.infos_chemin:
        (id_o,cl_o,path,path_r)=infos

        pos=get_dispo_dispo_niveau(glob,id_o,cl_o)
        if pos==idpos:
            datas.objets_actifs.pop()
        if pos>=idpos:
            idpos=pos
            datas.objets_actifs.append(infos)
            obj_prs=glob.objets[id_o]['proprietes']
            sk= obj_prs.get('skin',None)
            if sk:
                datas.skin=int(sk)
                name_skin=glob.objets[int(sk)]['names'].values()[0]
                datas.skin_path='/skins/'+name_skin
                datas.skin_header=int(obj_prs.get('skin_header',None))
                datas.skin_footer=int(obj_prs.get('skin_footer',None))

    infos=datas.infos_objet_actu
    (id_f,cl_f,path_f,path_r)=infos
    pos=get_dispo_dispo_niveau(glob,id_f,cl_f)
    if pos==idpos:
        datas.objets_actifs.pop()
    datas.objets_actifs.append(infos)
    obj_prs=glob.objets[id_f]['proprietes']
    sk= obj_prs.get('skin',None)
    if sk:
        datas.skin=int(sk)
        name_skin=glob.objets[int(sk)]['names'].values()[0]
        datas.skin_path='/skins/'+name_skin
        datas.skin_header=int(obj_prs.get('skin_header',None))
        datas.skin_footer=int(obj_prs.get('skin_footer',None))

    sk= obj_prs.get('skin_specifique',None)
    if sk:
        datas.skin=int(sk)
        name_skin=glob.objets[int(sk)]['names'].values()[0]
        datas.skin_path='/skins/'+name_skin
        datas.skin_header=int(obj_prs.get('skin_specifique_header',None))
        datas.skin_footer=int(obj_prs.get('skin_specifique_footer',None))

    datas.skin_name=name_skin



def analyse_instance(interfaces,id_i,cl_i,path,path_r,branche_actu=0):
    log   = interfaces[5]
    datas = interfaces[7]
    glob  = interfaces[8]
    lang=datas.my_session.langue

    ouvre_div='<div %s%s>'
    ferme_div='</div>'
    
    infos=(id_i,cl_i,path,path_r)
    instance=get_instance_from_infos(infos,interfaces)

    actu=instance.is_actu
    parent=False
    if branche_actu>-1 and not actu:
        parent=True

    proprietes=glob.objets[id_i]['proprietes']
    
    if parent:
        dispo=proprietes.get('dispo_parent','#')
    else:
        dispo=proprietes.get('dispo_normal','=')

    include_css=proprietes.get('include_css',None)
    if include_css:
        add_include=('css',include_css)
        if not add_include in datas.includes:
            datas.includes.append(add_include)

    includes_css=proprietes.get('includes_css',None)
    if includes_css:
        for include_css in includes_css.split(','):
            add_include=('css',include_css.strip())
            if not add_include in datas.includes:
                datas.includes.append(add_include)

    include_js=proprietes.get('include_js',None)
    if include_js:
        add_include=('js',include_js)
        if not add_include in datas.includes:
            datas.includes.append(add_include)

    includes_js=proprietes.get('includes_js',None)
    if includes_js:
        for include_js in includes_js.split(','):
            add_include=('js',include_js.strip())
            if not add_include in datas.includes:
                datas.includes.append(add_include)

    for i in instance.includes():
        if not i in datas.includes:
            datas.includes.append(i)

    instance.pre_execution()

    dispo=dispo.replace(']',',]')
    decdispo=dispo.split('[')
    initdec=True
    idec=0
    for dec in decdispo:
        idec+=1
        if initdec:
            initdec=False
        else:
            idname=""
            classename=""
            if ':' in dec:
                (classename,dec)=dec.split(':',1)
                if '+' in classename:
                    (classename,idname)=classename.split('+',1)
            strclass=''
            if classename:
                strclass=' class="%s"' % classename
            if idname=='' and classename=="elem":
                dectmp=dec.split(',',1)
                if len(dectmp)>0:
                    idname='elemid_'+dectmp[0]
            if idname!='':
                strid=' id="%s"' % idname
            else:
                strid=''
            datas.to_exec.append((None,ouvre_div % (strclass,strid)))
            datas.inbalises.append(classename+'+'+idname)

        dec2=dec.split(',')
        for subdec in dec2:
            if subdec:
                if subdec=="]":
                    datas.to_exec.append((None,ferme_div))
                    try:
                        pass
                        datas.inbalises.pop()
                    except:
                        pass
                elif subdec=="=":
                    if actu:
                        datas.to_exec.append((instance.action,[]))
                    else:
                        datas.to_exec.append((instance.affiche,[]))
                elif subdec=="#":
                    if branche_actu<len(datas.objets_actifs):
                        (id_a,cl_a,a_path,a_path_r)=datas.objets_actifs[branche_actu+1]
                        analyse_instance(interfaces,id_a,cl_a,a_path,a_path_r,branche_actu+1)
                else:
                    try:
                        idsub=int(subdec)
                    except:
                        idsub=-1
                    if idsub>=0:
                        namefils=glob.get_name_by_id(idsub,lang)
                        if namefils:
                            newpath=path+'/'+namefils
                            newpath_r=path_r[len(namefils)+1:]
                        else:
                            newpath=path
                            newpath_r=path_r

                        clsub=get_classe(glob,idsub)
                        analyse_instance(interfaces,idsub,clsub,newpath,newpath_r,-1)


def get_instances_includes_exec(interfaces):
    datas    = interfaces[7]
    (id_start,cl_start,path,path_r)=datas.objets_actifs[0]
    datas.inbalises=[]
    analyse_instance(interfaces,datas.skin_header,31,datas.skin_path,path_r,branche_actu=-1)
    analyse_instance(interfaces,id_start,cl_start,path,path_r,branche_actu=0)
    analyse_instance(interfaces,datas.skin_footer,31,datas.skin_path,path_r,branche_actu=-1)

