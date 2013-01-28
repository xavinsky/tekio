# -*- coding: utf-8 -*-

# TODO reparer le backup casse.

# TODO le revert backup (id_backup):

# cheker dans action_backup la table modifier et le type d'action

# si insert,
# recuperation des valeurs avec un select pour chaque
# puis count pour ne detruire qu'une instance 
# delete de tout , puis recreation de insert count-1 au cas ou

# si update,
# select de la table backup pour recup les values (count des doublons)
# select * avec new value pour verifier si etat actu est celui prevu
# et verification d'eventuel doublon
# delete puis recreation d'eventuel doublon
# puis insert des ancienes values.

# si delete,
# recuperation dans la table puis insert 

# Performance ... :
# possibilite annuler le systeme svn.
# ameliorer svn avec module svn qui evite les chargement de os.system ou popen..

import apsw  # sqlite3 plus rapide que pysqlite! old : #import pysqlite2.dbapi2 as sqlite

from Queue import Queue
from string import strip
from threading import Semaphore

from tekio.utils import system_ret
from tekio.utils import to_tuple
from tekio.utils import py_to_apisql
from tekio.utils import check_params_sql
from tekio.utils import stou
from tekio.sqlliste import rq

# avec sqlite, seul 1 connection ecriture possible
NB_CONNECTIONS_LECTURE = 10
NB_CONNECTIONS_ECRITURE = 1
NB_CONNECTIONS_LECTURE_BACKUP = 3
NB_CONNECTIONS_ECRITURE_BACKUP = 1

class Connections_SQL:
    def __init__(self, log, db):
        self.log=log
        file_db_objs='%s/objs.sqlite3' % db
        file_db_backup='%s/backup.sqlite3' % db
        self.pool_lecture=self.remplir_pool(file_db_objs,NB_CONNECTIONS_LECTURE)
        self.pool_ecriture=self.remplir_pool(file_db_objs,NB_CONNECTIONS_ECRITURE)
        self.pool_lecture_backup=self.remplir_pool(file_db_backup,NB_CONNECTIONS_LECTURE_BACKUP)
        self.pool_ecriture_backup=self.remplir_pool(file_db_backup,NB_CONNECTIONS_ECRITURE_BACKUP)

    def remplir_pool(self,dbfile,nbconnections):
        queue = Queue()
        semaphores=[]
        acces=[]
        for i in range(nbconnections):
            semaphore=Semaphore()
            con = apsw.Connection(dbfile)
            cur = con.cursor()
            semaphores.append(semaphore)
            acces.append((con,cur))
            queue.put(1)
        return (queue,semaphores,acces)
    
    def detruire_pool(self,pool):
        queue=pool[0]
        for (connection,cursor) in pool[2]:
            cursor.close()
            connection.close()
            queue.get()
            
    def detruire_connections(self):
        self.detruire_pool(self.pool_lecture)
        self.detruire_pool(self.pool_ecriture)
        self.detruire_pool(self.pool_lecture_backup)
        self.detruire_pool(self.pool_ecriture_backup)

    def check_free(self,semaphores,nb):
        j=0
        while j<nb:
            if semaphores[j].acquire(False):
                return j
            j+=1

    def requete(self,pool,commande,parametres):
        commande = py_to_apisql(commande)
        new_params=[]
        if type(parametres)==(type(())) or type(parametres)==(type([])):
            pass
        else:
            parametres = to_tuple(parametres)

        for p in parametres:
            if type(p)==type(""):
                new_params.append(stou(p))
            else:
                new_params.append(p)
        parametres = to_tuple(new_params)

        queue=pool[0]
        queue.get()
        semaphores=pool[1]
        nb=len(semaphores)
        id_connection=self.check_free(semaphores,nb)

        semaphore=pool[1][id_connection]
        acces=pool[2][id_connection]
        connection=acces[0]
        cursor=acces[1]
        res=[]
        try:
            #self.log.debug('execute : %s /// %s' % (commande,parametres))
            for row in cursor.execute(commande,parametres):
                res.append(row)
            #self.log.debug(res)
            # no commit with apsw ?
            #if not commande.upper().strip().startswith("SELECT"):
            #    connection.commit()
        except Exception, err:
            err="""Requete : %s / Params : %s / Type : %s / Err : %s""" % (
                commande,parametres,str(Exception),str(err))
            self.log.traceback()
            self.log.err(err)
        semaphore.release()
        queue.put(1)
        return res

    def lecture(self,commande,parametres):
        return self.requete(self.pool_lecture,commande,parametres)

    def ecriture(self,commande,parametres):
        return self.requete(self.pool_ecriture,commande,parametres)

    def lecture_backup(self,commande,parametres):
        return self.requete(self.pool_lecture_backup,commande,parametres)

    def ecriture_backup(self,commande,parametres):
        return self.requete(self.pool_ecriture_backup,commande,parametres)

def get_structure_db_sqlite3(file_db,log,read):
    ret=system_ret('sqlite3 %s .tables' % file_db)
    ret=ret.replace('\n',' ')
    liste_tables=ret.split(' ')
    try:
        while 1:
            liste_tables.remove('')
    except:
        pass
    structure={}
    for tableid in liste_tables:
        st=read('PRAGMA table_info(%s);' % tableid)
        t={}
        for l in st:
            t[l[1]]=l[2]
        structure[tableid]=t
    return structure

class Database:

    def __init__(self, log, config, db):
        self.connections=Connections_SQL(log,db)
        self.semaphore_id_backup=Semaphore()
        file_db_objs='%s/objs.sqlite3' % db
        file_db_backup='%s/backup.sqlite3' % db
        self.structure=get_structure_db_sqlite3(file_db_objs,log,self.read_direct)
        self.structure_backup=get_structure_db_sqlite3(file_db_backup,log,self.read_backup)
        self.semaphore_idmax=Semaphore()

        
    def read_backup(self,cmd,params=[]):
        return self.connections.lecture_backup(cmd,params)

    def write_backup(self,cmd,params=[]):
        return self.connections.ecriture_backup(cmd,params)

    def read_direct(self,cmd,params=[]):
        return self.connections.lecture(cmd,params)

    def read(self,cmd,params=[]):
        rcmd=rq[cmd]
        return self.read_direct(rcmd,params)

    def read1(self,cmd,params=[]):
        res=self.read(cmd,params)
        if res:
            return res[0]
        else:
            return []
        
    def write(self,cmd,params=[]):
        rcmd=rq[cmd]
        #self.backup_action(cmd,rcmd % tuple(check_params_sql(params)))
        res=self.connections.ecriture(rcmd,params)
        return res

    def stop_database(self):
        self.connections.detruire_connections()

    def analyse_chaine_affectation(self,chaine):
        champs=[]
        valeurs=[]
        lastchamp=''
        lastvalue=''
        lastvaluenum=''
        flagvalue=False
        openvalue=False

        for c in chaine:
            if flagvalue:
                if c in '0123456789.':
                    lastvaluenum+=c
                    
                if not openvalue:
                    if c=='"' or c=="'":
                        openvalue=c
                        lastvalue+=c
                    if c==',':
                        v=lastvalue.strip()
                        if v=='':
                            valeurs.append(lastvaluenum)
                        else:
                            valeurs.append(v)
                        lastvalue=''
                        lastvaluenum=''
                        flagvalue=False
                else:
                    lastvalue+=c
                    if openvalue==c:
                        openvalue=False
            else:
                if c=='=':
                    champs.append(lastchamp.strip())
                    lastchamp=''
                    flagvalue=True
                else:
                    lastchamp+=c
        v=lastvalue.strip()
        if v=='':
            valeurs.append(lastvaluenum)
        else:
            valeurs.append(v)                                      

        """
        self.log.debug("DEBUG analyse-chaine-affect")
        self.log.debug(chaine)
        self.log.debug(champs)
        self.log.debug(valeurs)
        self.log.debug("DEBUG FIN analyse-chaine-affect")
        """

        val2=[]
        for v in valeurs:
            if type(v)==type(''):
                v=stou(v)
            val2.append(v)
        
        return (champs,val2)

    def analyse_chaine_valeurs(self,chaine):
        valeurs=[]
        lastvalue=''
        openvalue=False
        lastvaluenum=''
        for c in chaine:
            if c in '0123456789.':
                lastvaluenum+=c
                    
            if not openvalue:
                if c=='"' or c=="'":
                    openvalue=c
                    lastvalue+=c
                if c==',':
                    v=lastvalue.strip()
                    if v=='':
                        valeurs.append(lastvaluenum)
                    else:
                        valeurs.append(v)
                    lastvalue=''
                    lastvaluenum=''
            else:
                lastvalue+=c
                if openvalue==c:
                    openvalue=False

        v=lastvalue.strip()
        if v=='':
            valeurs.append(lastvaluenum)
        else:
            valeurs.append(v)

        """
        self.log.debug("DEBUG analyse-chaine-valeur")
        self.log.debug(chaine)
        self.log.debug(valeurs)
        self.log.debug("DEBUG FIN analyse-chaine-valeur")
        """
        
        val2=[]
        for v in valeurs:
            if type(v)==type(''):
                v=v.decode('utf-8')
            val2.append(v)
        
        return val2

    def backup_action(self,idsql,commande):
        id_backup=self.get_id_backup_sql()
        commande=commande.strip()
        (action,suite)=commande.split(' ',1)
        action=action.lower()
        if not action in ['insert','update','delete']:
            raise('action sql inconnue : %s' % action)

        #DECOUPE DE LA REQUETE
        nomtable=""
        champs=[]
        valeurs=[]
        conditions=";"

        if action=='insert':
            # format requete : insert into NOMTABLE (LISTECHAMPS) values (LISTVALEURS);
            suite=suite.split('into',1)[1]
            (nomtable,suite)=suite.split('(',1)
            nomtable=nomtable.strip()
            (champs_str,suite)=suite.split(')',1)
            champs=champs_str.split(',')
            champs=map(strip,champs)
            suite=suite.split('(',1)[1] 
            tabtmp=suite.split(')')
            chaine=')'.join(tabtmp[:-1])
            valeurs=self.analyse_chaine_valeurs(chaine)

        if action=='update':
            # format requete : update NOMTABLE set LISTESAFFECTATION where CONDITIONS
            (nomtable,suite)=suite.split(' set ',1)
            nomtable=nomtable.strip()
            tabtmp=suite.split(' where ',1)
            chaine=' where '.join(tabtmp[:-1])
            (champs,valeurs)=self.analyse_chaine_affectation(chaine)
            conditions=tabtmp[-1];

        if action=='delete':
            # format requete : delete from NOMTABLE where CONDITIONS
            suite=suite.split('from',1)[1]
            (nomtable,conditions)=suite.split(' where ',1)
            nomtable=nomtable.strip()
            conditions=conditions.strip()

        # CREATION TABLE BACKUP SI NECESSAIRE
        if not idsql in self.structure_backup.keys():
            structure_table=["id_backup integer",]
            dicostruc={}
            if action=="insert":
                for ch in champs:
                    typech=self.structure[nomtable][ch]
                    structure_table.append('%s %s ' % (ch,typech))
                    dicostruc[ch]=typech
            if action=="update":
                for ch in champs:
                    typech=self.structure[nomtable][ch]
                    structure_table.append('old_%s %s ' % (ch,typech))
                    structure_table.append('new_%s %s ' % (ch,typech))
                    dicostruc['old_%s' % ch]=typech
                    dicostruc['new_%s' % ch]=typech
                all=self.structure[nomtable].keys()
                for ch in all:
                    if not ch in champs:
                        typech=self.structure[nomtable][ch]
                        structure_table.append('fixe_%s %s ' % (ch,typech))
                        dicostruc['fixe_%s' % ch]=typech
            if action=="delete":
                champs=self.structure[nomtable].keys()
                for ch in champs:
                    typech=self.structure[nomtable][ch]
                    structure_table.append('%s %s ' % (ch,typech))
                    dicostruc[ch]=typech

            requete='create table %s (%s);' % (idsql , ','.join(structure_table))
            self.write_backup(requete)
            self.structure_backup[idsql]=dicostruc

        
        #ENREGISTREMENT BACKUP DATAS
        if action=='insert':
            champs.insert(0,'id_backup')
            valeurs.insert(0,str(id_backup))
            requete='insert into %s (%s) values (%s);' % (idsql , ' ,'.join(champs), ' ,'.join(valeurs))
            self.write_backup(requete)

        if action=='update':
            allchamps=self.structure[nomtable].keys()
            requete='select %s from %s where %s' % (' ,'.join(allchamps), nomtable, conditions) 
            r=self.read_direct(requete)
            for l in r:
                dicoold={}
                i=0
                for ch in allchamps :
                    if self.structure[nomtable][ch]==u'integer':
                        dicoold[ch]=str(l[i])
                    else:
                        dicoold[ch]="'"+l[i].replace("'","''")+"'"
                    if type(dicoold[ch])==type(''):
                        dicoold[ch]=dicoold[ch].decode('utf-8')
                    i+=1
                backchamps=['id_backup',]
                backvalues=[str(id_backup),]
                i=0
                for ch in champs:
                    if ch!="":
                        backchamps.append('old_%s' % ch)
                        backchamps.append('new_%s' % ch)
                        backvalues.append(dicoold[ch])
                        backvalues.append(unicode(valeurs[i]))
                        i+=1
                for ch in allchamps:
                    if not ch in champs:
                        if ch!='':
                            backchamps.append('fixe_%s' % ch)
                            backvalues.append(dicoold[ch])
                requete=u'insert into %s (%s) values (%s);' % (idsql,' ,'.join(backchamps),' ,'.join(backvalues))
                self.write_backup(requete)
                
        if action=='delete':
            champs=self.structure[nomtable].keys()
            requete='select %s from %s where %s' % (' ,'.join(champs), nomtable, conditions) 
            r=self.read_direct(requete)
            champs.insert(0,'id_backup')
            
            for l in r:
                valeurs=[]
                for i in l:
                    if type(i)==type(0):
                        valeurs.append(str(i))
                    elif type(i)==type(''):
                        valeurs.append("'"+i.replace("'","''")+"'")
                    elif type(i)==type(u''):
                        i=i.encode('utf-8')
                        valeurs.append("'"+i.replace("'","''")+"'")
                        
                requete='insert into %s (%s) values (%s ,%s);' % (idsql,' ,'.join(champs),id_backup,' ,'.join(valeurs)) 
                self.write_backup(requete)

        requete="insert into action_backup (id, action, type) values (%s , '%s' , '%s');" % (id_backup,idsql,action)
        self.write_backup(requete)
                
        # ajout de la reference dans req pour traitement global des actions!

    def get_id_backup_sql(self):
        id_backup=None
        self.semaphore_id_backup.acquire()
        try:
            r=self.read_backup("select * from id_backup_actu;")
            id_backup=r[0][0]+1
            self.write_backup("update id_backup_actu set id=%s;" % id_backup)
        except:
            id_backup=0
        self.semaphore_id_backup.release()
        return id_backup



