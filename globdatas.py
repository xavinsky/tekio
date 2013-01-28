# -*- coding: utf-8 -*-

from tekio.utils import slash_to_list_int

##########################
## path
##########################
def get_dico_lang(obj,lang):
    if not obj:
        return ''
    if lang and obj.has_key(lang):
        return obj[lang]
    if obj.has_key('all'):
        return obj['all']
    return obj.values()[0]


class GlobTekio:
    stop_flag=False

    def initialisation(self,database):
        self.objets={}
        self.reinit(database,0)

        self.orphelins=[]
        ks=self.objets.keys()
        alls_objs=database.read('get_alls' , ())
        for obj,objclass in alls_objs:
            if not obj in ks:
                self.orphelins.append(obj)

        self.get_population(database)

    def reinit(self, database, id_obj,recursif=True):
        if id_obj==0:
            id_pere=0
            path_pere=None
        else:
            id_pere=self.objets[id_obj]['pere']
            path_pere=self.objets[id_pere]['path']

        self.get_branche(database, id_obj, id_pere, path_pere, recursif)
        self.ordre_sous_pages(database,id_obj,recursif)
        for langue in self.langues:
            self.get_infos_sous_pages(langue,id_obj,recursif)
        if id_obj!=0:
            self.ajoute_obj_ref_pere(id_obj,id_pere)

    def get_name_by_id(self,id,lang=None):
        return get_dico_lang(self.objets[id]['names'],lang)

    def get_path_by_id(self,id,lang=None):
        return get_dico_lang(self.objets[id]['path'],lang)

    def new_path_from_pere(self,id_o,id_p,names,path_pere):
        if not names:
            return path_pere
        path_fils={}
        for (k,v) in names.items():
            if k=='all':
                if v!='':
                    for l in self.langues:
                        slash=''
                        try:
                            if path_pere[l]!='/':
                                slash='/'
                            path_fils[l]=path_pere[l]+slash+v
                        except:
                            path_fils[l]='/'+v

                else:
                    for l in self.langues:
                        try:
                            path_fils[l]=path_pere[l]
                        except:
                            path_fils[l]='/'
            else:
                if k in self.langues:
                    slash=''
                    try:
                        if path_pere[k]!='/':
                            slash='/'
                        path_fils[k]=path_pere[k]+slash+v
                    except:
                        path_fils[k]='/'+v

        return path_fils

    def new_path(self,id_o,id_p,names):
        if id_o==0:
            path_pere={}
            for l in self.langues:
                path_pere[l]='/'
        else:
            path_pere=self.objets[id_p]['path']

        return self.new_path_from_pere(id_o,id_p,names,path_pere)
        
    def get_branche(self, database, id_o, id_p, path_pere=None, recursif=True):
        #type
        if not path_pere:
            if id_o==0:
                path_pere={}
                for l in self.langues:
                    path_pere[l]='/'
            else:
                for l in self.langues:
                    try:
                        path_pere[l]=self.objets[id_p]['path']
                    except:
                        path_pere[l]='/'
        
        r_types=database.read('get_classe' , (id_o,))
        if r_types:
            typeo=r_types[0][0]
            #proprietes
            r_pr_i_s=database.read('get_proprietes', (id_o,))
            r_pr_t_s=database.read('get_proprietes_i', (id_o,))
            proprietes={}
            for (name, value) in r_pr_i_s:
                proprietes[name]=value
            for (name, value) in r_pr_t_s:
                proprietes[name]=value

            names={}
            for pr_key in proprietes.keys():
                if pr_key[:5]=="name_":
                    lang=pr_key[5:]
                    name=proprietes[pr_key]
                    names[lang]=name

            path_fils=self.new_path_from_pere(id_o,id_p,names,path_pere)

            #sous objets
            r_lies=database.read('get_fils', (id_o,))
            subs=[]
            for r_lie in r_lies:
                lie=r_lie[0]
                if recursif:
                    idnew=self.get_branche(database, lie,id_o ,path_fils)
                    if idnew!=None:
                        subs.append(idnew)
                else:
                    subs.append(lie)

            #prepare urls
            urls={}
            for l in self.langues:
                urls[l]={}

            for subid in subs:
                if not subid in self.objets.keys():
                    print "subid %s n'existe plus " % subid
                    return None
                sub=self.objets[subid]
                for (lang,name) in sub['names'].items():
                    if lang=='all':
                        for l in self.langues:
                            urls[l][name]=subid
                    elif lang in self.langues:
                        urls[lang][name]=subid
            
            obj= {'id'         : id_o,
                  'type'       : typeo,
                  'proprietes' : proprietes,
                  'names'      : names,
                  'path'       : path_fils,
                  'subs'       : subs,
                  'urls'       : urls,
                  'pere'       : id_p}
            self.objets[id_o]=obj
            return id_o
        else:
            print 'pas de type pour %s ???' % id_o
            return None

    def change_path_subs(self,id_o):
        for idf in self.objets[id_o]['subs']:
            self.objets[idf]['path']=self.new_path(idf,id_o,self.objets[idf]['names'])
            self.change_path_subs(idf)

    def get_population(self,database):
        subs=self.objets[0]['subs']

        self.utilisateurs=[]
        self.openids={}
        self.groupes={}
        for sub in subs:
            o=self.objets[sub]
            if o['type']==40:
                self.utilisateurs.append(sub)
                openid=o['proprietes'].get('openid','')
                self.openids[openid]=sub
                o['responsabilites']=[]
                o['groupes']=[]
            if o['type']==41:
                nom=o['proprietes'].get('nom','')
                self.groupes[nom]=sub
                o['responsables']=[]
                o['membres']=[]
    
        r_membres=database.read('get_membres')
        for (groupe,utilisateur) in r_membres:
            g=self.objets[groupe]
            u=self.objets[utilisateur]
            g['membres'].append(utilisateur)
            u['groupes'].append(groupe)

        r_responsables=database.read('get_responsables')
        for (groupe,utilisateur) in r_responsables:
            g=self.objets[groupe]
            u=self.objets[utilisateur]
            g['responsables'].append(utilisateur)
            u['responsabilites'].append(groupe)

	
        id_gr_admin=self.groupes.get('admin',None)
        if id_gr_admin:
		self.users_indestructibles=self.objets[id_gr_admin]['responsables']
            

    def ordre_sous_pages(self,database,id=0,recursif=True):
        page=self.objets[id]
        page['sous_pages']={}
        for langue in self.langues:
            page['sous_pages'][langue]=[]
        sous_pages_tmp=[]
        for sub in page['subs']:
            o=self.objets[sub]
            if o['type']==2 or o['type']==4:
                if recursif:
                    self.ordre_sous_pages(database,sub)
                sous_pages_tmp.append(sub)
        sous_pages=[]
        str_ordre=page['proprietes'].get('ordre_sous_pages',None)
        if str_ordre==None:
            database.write('add_propriete',(id,'ordre_sous_pages',''))
            str_ordre=''
        if not type(str_ordre)==type([]):
            ordre=slash_to_list_int(str_ordre)
        else:
            ordre=str_ordre
        for i in ordre:
            if i in sous_pages_tmp:
                sous_pages.append(int(i))
        for i in sous_pages_tmp:
            if not i in sous_pages:
                sous_pages.append(int(i))
        page['proprietes']['ordre_sous_pages']=sous_pages
    
    def get_infos_sous_pages(self,lang,id=0,recursif=True):
        infos=[]
        page=self.objets[id]
        page['sous_pages'][lang]=[]
        for idsub in page['proprietes']['ordre_sous_pages']:
            subpage=self.objets[idsub]
            name=self.get_name_by_id(idsub,lang)
            textnav=subpage['proprietes'].get('textnav_%s' % lang, None)
            if not textnav:
                textnav=subpage['proprietes'].get('textnav' , None)
            if not textnav:
                textnav=name
            try:
                path=subpage['path'][lang]
            except:
                path=''
            page['sous_pages'][lang].append((idsub,textnav,path,name))
            if recursif:
                self.get_infos_sous_pages(lang,idsub)
        return 


    def modif_url_pere(self,id_o,id_p,new_names,old_names=None):
        urls_pere=self.objets[id_p]['urls']
        for (k,v_n) in new_names.items():
            if old_names:
                try:
                    v_o=old_names[k]
                except:
                    v_o=None
            else:
                v_o=None
            if v_o==None or v_o!=v_n:
                if k=='all':
                    for l in self.langues:
                        if v_o and v_o in urls_pere[l].keys():
                                del(urls_pere[l][v_o])
                        urls_pere[l][v_n]=id_o
                else:
                    if v_o and v_o in urls_pere[k].keys():
                        del(urls_pere[k][v_o])
                    urls_pere[k][v_n]=id_o
        self.objets[id_p]['urls']=urls_pere

    def set_names(self,id_o, new_names):
        my_obj=self.objets[id_o]
        my_type=my_obj['type']
        id_pere=my_obj['pere']
        obj_pere=self.objets[id_pere]
        old_names=my_obj['names']
        self.objets[id_o]['names']=new_names


        if old_names.keys()!=new_names.keys():
            # TODO
            pass
            #ATTENTION DIFFERENCE ENTRE LANGUES old et new !!!
            # ne devrai pas arriver mais a faire au cas ou..

        if id_o!=0:
            self.objets[id_o]['path']=self.new_path(id_o,id_pere,new_names)
            self.change_path_subs(id_o)
            self.modif_url_pere(id_o,id_pere,new_names,old_names)

        if my_type==2 or my_type==4:
            for l in self.langues:
                self.get_infos_sous_pages(l,id_pere)

    def ajoute_obj_ref_pere(self,id_o,id_p):
        if not id_o in self.objets[id_p]['subs']:
            self.objets[id_p]['subs'].append(id_o)
        self.modif_url_pere(id_o,id_p,self.objets[id_o]['names'])
        if self.objets[id_o]['type']==2 or self.objets[id_o]['type']==4:
            if not id_o in self.objets[id_p]['proprietes']['ordre_sous_pages']:
                self.objets[id_p]['proprietes']['ordre_sous_pages'].append(id_o)
            for l in self.langues:
                self.get_infos_sous_pages(l,id_p,recursif=False)

    def ajoute_obj(self,id_o,id_p,type_o,names):
        proprietes={}
        path_fils=self.new_path(id_o,id_p,names)

        if type_o==2 or type_o==4:
            proprietes['ordre_sous_pages']=[]


        subs=[]
        urls={}
        for l in self.langues:
            urls[l]={}
            
        obj= {'id'         : id_o,
              'type'       : type_o,
              'proprietes' : proprietes,
              'names'      : names,
              'path'       : path_fils,
              'subs'       : subs,
              'urls'       : urls,
              'pere'       : id_p}


        if type_o==2 or type_o==4:
            sous_pages={}
            for l in self.langues:
                sous_pages[l]=[]
            obj['sous_pages']=sous_pages
            
        self.objets[id_o]=obj
        self.ajoute_obj_ref_pere(id_o,id_p)


    def delete_obj_ref_pere(self,id_o,id_pere):
        my_obj=self.objets[id_o]
        my_type=my_obj['type']
        obj_pere=self.objets[id_pere]
        old_names=my_obj['names']

        try:
            self.objets[id_pere]['subs'].remove(id_o)
        except:
            pass

        if my_type==2 or my_type==4:
            try:
                self.objets[id_pere]['proprietes']['ordre_sous_pages'].remove(id_o)
            except:
                pass
            for l in self.langues:
                self.get_infos_sous_pages(l,id_pere)

        for (k,v) in old_names.items():
            if k=='all':
                for l in self.langues:
                    if v in obj_pere['urls'][l].keys():
                        del(obj_pere['urls'][l][v])
            else:
                try:
                    if v in obj_pere['urls'][k].keys():
                        del(obj_pere['urls'][k][v])
                except:
                    pass
    def delete_obj(self,id_o):
        try:
            my_obj=self.objets[id_o]
        except: 
            return
        id_pere=my_obj['pere']
        self.delete_obj_ref_pere(id_o,id_pere)
        del(self.objets[id_o])
        
    def deplace_obj(self,id_o,id_old_p,id_new_p):
        my_obj=self.objets[id_o]
        self.delete_obj_ref_pere(id_o,id_old_p)
        my_obj['pere']=id_new_p
        my_obj['path']=self.new_path(id_o,id_new_p,my_obj['names'])
        self.ajoute_obj_ref_pere(id_o,id_new_p)



