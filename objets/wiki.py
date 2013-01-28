# -*- coding: utf-8 -*-

from tekio.libtek import get_instance_from_id
from tekio.libtek import redirect_ok
from tekio.libtek import check_edit
from tekio.libtek import move_id_wiki
from tekio.utils import path_pere

from tekio.objets.base import detruire_element
from tekio.objets.base import set_propriete, get_propriete, get_proprietes

def tpl_placement(datas):
    _=datas._
    return """
%s : <select name="placement">
  <option value="top">%s</option>
  <option value="topleft">%s</option>
  <option value="topright">%s</option>
  <option value="bottomleft">%s</option>
  <option value="bottomright">%s</option>
  <option value="bottom" selected>%s</option>
</select>
""" % (_('Placer'),_('En haut de la page'),_('En haut a gauche'),
       _('En haut a droite'),_('En bas a gauche'),_('En bas a droite'),
       _('En bas de la page') )

def enleve_element(self):
    # BUG lors de enleve element Page au niveau de la racine !!!! 
    if not check_edit(self.datas,self.socket):
        return
    i=int(self.socket.args["id"])
    if i==0:
        return
    url_ret=self.path
    if self.id==i:
        url_ret=path_pere(url_ret)
    self.datas.my_session.set_new_url(url_ret)
    if i!=0:
        detruire_element(self.interfaces,i)
    redirect_ok(self.socket,self.datas)

def element_edit_form(self):
    ido=int(self.datas.action_params[0])
    instance=get_instance_from_id(self.interfaces,ido)
    if instance:
        instance.action_element_edit_form()

def element_delete_confirm(self):
    _=self.datas._
    ido=int(self.datas.action_params[0])
    instance=get_instance_from_id(self.interfaces,ido)
    if instance:

        baseurl=self.datas.url_base
        if self.path!='/':
            baseurl+=self.path

    tpl="""
%s : <br />
%s : %s <br />
""" % (_('Etes vous sur que vous voulez detruire cette element'),
       instance.id, instance.path)

    tpl+="""

<div id="div_valid" class="invisible">
<center>
<a href="%s/enleve_element?id=%s"><h3>%s</h3></a>
</center>
</div>

<br />
""" % (baseurl,instance.id,_('Destruction'))

    self.socket.send_datas(tpl)
    instance.confirm_detruire()


def element_move(self):
    idelem=int(self.socket.args["id"])
    posline=int(self.socket.args["line"])
    poscol=int(self.socket.args["col"])
    solostr=self.socket.args["solo"]
    solo=False
    if solostr=='y':
        solo=True
    dispo_normal=self.get_propriete('dispo_normal','=')
    print "MOVE"
    print dispo_normal
    print (idelem,posline,poscol,solo)
    new_dispo=move_id_wiki(dispo_normal,idelem,posline,poscol,solo)
    print new_dispo
    self.set_propriete('dispo_normal',new_dispo)
    self.datas.my_session.set_new_url(self.path)
    redirect_ok(self.socket,self.datas)

def dispo_add_elem(glob,database,idp,id,placement):

    colonne_max=4

    dispo_normal=get_propriete(glob,idp,'dispo_normal','=')

    ## recuperation du contenu de la page (entre = et -) 
    wikitmp2=dispo_normal
    h=''
    if dispo_normal.find('=')!=-1:
        (h,wikitmp2)=dispo_normal.split('=',1)
        if len(wikitmp2)>0 and wikitmp2[0]==',':
            wikitmp2=wikitmp2[1:]

    # decoupe les ligne mais reste la ligne init !att: reste le premier [line: sans la ','
    linesbruts=wikitmp2.split(',[line:') 
    lines=[]   
    for linebrut in linesbruts:
        # on vire le [line: restant et les ] qui leur correspondaient
        line=linebrut.replace('[line:','')[:-1].strip()
        if line:
            lines.append(line)

    if placement not in ["top","topleft","topright",
                         "bottomleft","bottomright","bottom"]:
        placement="bottom"

    # baseline pour : 0 => avant le tableau
    # baseline pour : X => dans la ligne X (notation humaine qui commence par 1)
    # baseline pour : -1 => apres le tableau

    if len(lines)==0:
        baseline=0
    elif placement=="top":
        baseline=0
    elif placement=="bottom":
        baseline=-1
    elif placement in ["topleft","topright"]:
        baseline=1
    elif placement in ["bottomleft","bottomright"]:
        baseline=len(lines)


    if baseline < 1 :
        #inser une nouvelle ligne au debut ou a la fin.
        newline="[col1:[elem:%s]]" % id
        if baseline==0:
            lines.insert(0,newline)
        else:
            lines.append(newline)

    else:
        varline=lines[baseline-1]
        colsbruts=varline.split(',[col')
        cols=[]   
        for colbrut in colsbruts:
            if colbrut:
                try:
                    col=colbrut.replace('[col','').split(":",1)[1][:-1]
                    cols.append(col)
                except:
                    log.err("erreur colbrut %s " % colbrut)
        newcol="[elem:%s]" % id
        if placement in ["topleft","bottomleft"]:
            cols.insert(0,newcol)
        if placement in ["topright","bottomright"]:
            cols.append(newcol)

        nbcols=len(cols)
        col4join=[]
        for c in cols:
            col4join.append('[col%s:%s]' % (nbcols,c))
        
        lines[baseline-1]=','.join(col4join)


    # recolage des lignes
    line4join=[]
    for l in lines:
        line4join.append('[line:%s]' % l)
    newdispo=h+'=,'+','.join(line4join)

    # ecriture nouvelle disppo
    set_propriete(glob,database,idp,'dispo_normal',newdispo)

    
