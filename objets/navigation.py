# -*- coding: utf-8 -*-

from tekio.objets.base import ObjBase 
from tekio.objets.base import create_element
from tekio.objets.base import set_propriete, get_propriete
from tekio.utils import name_from_path, stou, check_char

types_nav=[('normales','Standard'),
          ('subnavigation','enleve 1 niveau'),
          ('horizontal','Horizontal'),
          ('horizontal-open','avec open/close')]

def add_Navigation_Form(datas):
    _=datas._
    options=""
    for (type_nav,nom_nav) in types_nav:
        options+="""<option value="%s">%s</option>""" % (type_nav,_(nom_nav))

    return """
%s : <input type="text" name="name" value="" />    
%s : <select name="direction">
%s
</select>
""" % (_('Id de la navigation (dont derive les css) '),_('Type de navigation'), options )


def edit_Navigation_Form(datas,direction):
    _=datas._
    options=""
    for (type_nav,nom_nav) in types_nav:
        sel=''
        if type_nav==direction:
            sel=' selected'
        options+="""<option value="%s" %s >%s</option>""" % (type_nav,sel,nom_nav)
    return """
%s : <select  name="direction">
%s
</select>
""" % (_('Type de navigation'), options )



def new_Navigation(glob,database,fs_svn,socket,
                   pere_id,pere_path,name,direction=''):

    name=check_char(name)
    if not name:
        name="navigation"
    
    proprietes={'direction':direction}
    obj_id=create_element(glob,database,20,pere_id,{'all':name,},proprietes)

    return obj_id


def change_Navigation(glob,database,fs_svn,socket, id_obj, direction):

    set_propriete(glob,database,id_obj,'direction',direction)
    



class Navigation(ObjBase):

    def affiche_niveau(self,styles,id_obj=0,niv=1,text='',path='',pere_actif=True):

        if type(text)==type(""):
            text=stou(text)

        if len(styles)<niv:
            print 'niveau trop grand'
            return

        lang=self.datas.my_session.langue
        infos=self.glob.objets[id_obj]['sous_pages'][lang]
        actif=""
        new_pere_actif=False
        if (self.datas.objet_actu.path+'/').find(self.glob.get_path_by_id(id_obj,lang=lang)+'/')!=-1:
            actif=" actif"
            new_pere_actif=True

        my_style=styles[niv-1]
        if type(my_style)==type(()):
            if pere_actif:
                my_style=my_style[0]
            else:
                my_style=my_style[1]

        if my_style=='popup':
            my_style='element'


        sub_style=None
        if len(styles)>niv and len(infos)>0:
            sub_style=styles[niv]
            if type(sub_style)==type(()):
                if new_pere_actif:
                    sub_style=sub_style[0]
                else:
                    sub_style=sub_style[1]

        if my_style==None:
            #cas impossible ? ne sert plus ?
            if actif!='':
                if sub_style:
                    for (idsub,textnav,newpath,nom) in infos:
                        self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
            return

        if my_style.find('conteneur')!=-1:
            #conteneur premier niveau.
            cl_c='class="nav_conteneur_%s_%s%s"' % (self.name,niv,actif)
            self.socket.send_datas('<ul %s>' % (cl_c))
            if sub_style:
                for (idsub,textnav,newpath,nom) in infos:
                    self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
            self.socket.send_datas('</ul>')
            return

        path_j=path.replace('/','_')

        if my_style=='element':
            cl_e='class="nav_element_%s_%s%s"' % (self.name,niv,actif)
            js_e="""onclick="document.location.href='%s';" """ % (path)
            self.socket.send_datas('<li %s %s>' % (cl_e,js_e))

            if sub_style and sub_style=='popup':
                cl_p='class="nav_popup_%s_%s%s"' % (self.name,niv,actif)
                self.socket.send_datas("""<div %s>""" % cl_p )

                self.socket.send_datas("""<ul>""")
                for (idsub,textnav,newpath,nom) in infos:
                    self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
                self.socket.send_datas("""</ul>""")


            self.socket.send_datas(text)

            if sub_style:
                if sub_style=='popup':
                    self.socket.send_datas("""</div>""")
                else:
                    cl_c='class="nav_conteneur_%s_%s%s"' % (self.name,niv,actif)
                    self.socket.send_datas("""<ul %s>""" % cl_c )
                    for (idsub,textnav,newpath,nom) in infos:
                        self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
                    self.socket.send_datas("""</ul>""")
                    
                        
            self.socket.send_datas('</li>')

        if my_style=='element-list':
            cl_e='class="nav_element_%s_%s%s"' % (self.name,niv,actif)
            self.socket.send_datas('<li %s >' % cl_e)

            if sub_style and sub_style=='popup':
                cl_p='class="nav_popup_%s_%s%s"' % (self.name,niv,actif)
                self.socket.send_datas("""<div %s>""" % cl_p )
                self.socket.send_datas("""<ul>""")
                for (idsub,textnav,newpath,nom) in infos:
                    self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
                self.socket.send_datas("""</ul>""")
                self.socket.send_datas("""</div>""")

            js_e="""onclick="document.location.href='%s';" """% (path)
            self.socket.send_datas(u"""<div class="link" %s>%s</div>""" % (js_e,text))
            self.socket.send_datas('</li>')

            if sub_style and sub_style!='popup':
                for (idsub,textnav,newpath,nom) in infos:
                    self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
                        

        if my_style=='element-open':
            cl_e='class="nav_element_%s_%s%s"' % (self.name,niv,actif)
            self.socket.send_datas('<li %s>' % cl_e)

            idul='nav_contoleur_opener__'+path.replace('/','_')

            if new_pere_actif==True:
                v="visible"
            else:
                v="invisible"
            button="""<a href="javascript:swapvisu('%s')" class="boutton_nav_%s %s" 
><img src="/includes/images/interface/util/pixel.gif" height="18px" width="18px" 
/></a><img src="/includes/images/interface/util/pixel.gif" height="18px" width="3px" class="pixdec" 
/>""" % (idul,niv,actif) 

            self.socket.send_datas(u'%s<a href="%s" %s>%s</a>' % (button,path,cl_e,text))

            if sub_style and len(infos)>0:
                cl_c='class="nav_conteneur_%s_%s%s %s" id="%s"' % (self.name,niv,actif,v,idul)
                self.socket.send_datas("""<ul %s>""" % cl_c )
                for (idsub,textnav,newpath,nom) in infos:
                    self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
                self.socket.send_datas("""</ul>""")
            self.socket.send_datas('</li>')

            
        if my_style=='element-puce':
            cl_e='class="nav_element_%s_%s%s"' % (self.name,niv,actif)
            self.socket.send_datas('<li %s>' % cl_e)

            button="""<a class="boutton_nav_%s %s" 
><img src="/includes/images/interface/util/pixel.gif" height="18px" width="30px" 
/></a><img src="/includes/images/interface/util/pixel.gif" height="18px" width="1px"  class="pixdec"
/>""" % (niv,actif)
            

            self.socket.send_datas(u'%s<a href="%s" %s>%s</a>' % (button,path,cl_e,text))

            if sub_style and len(infos)>0:
                cl_c='class="nav_conteneur_%s_%s%s %s" id="%s"' % (self.name,niv,actif,v,idul)
                self.socket.send_datas("""<ul %s>""" % cl_c )
                for (idsub,textnav,newpath,nom) in infos:
                    self.affiche_niveau(styles,idsub,niv+1,textnav,newpath,new_pere_actif)
                self.socket.send_datas("""</ul>""")

            self.socket.send_datas('</li>')

    def affiche(self):
        tpl=self.get_propriete('direction')
        if not tpl:
            tpl='normale'
        self.name=tpl
        if tpl==u'subnavigation':
            styles=[None,'conteneur','element',('element','popup')]
        elif tpl==u'horizontal':
            styles=['conteneur','element','popup']
        elif tpl==u'horizontal-open':
            styles=['conteneur','element-open','element-puce']
        else:
            styles=['conteneur','element-list',('element','popup')]

        self.affiche_niveau(styles)

    def includes(self):
        name_nav=self.glob.objets[self.id]["names"]['all']
        id_skin=self.glob.objets[self.id]["pere"]
        skin_name=self.glob.objets[id_skin]['names']['all']
        
        return [('css','nav_%s_%s' % (skin_name,name_nav)),]


