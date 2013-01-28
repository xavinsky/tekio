# -*- coding: utf-8 -*-

####### ATTENTION POUR QUE LE SYSTEM DE BACKUP FONCTIONNE,
####### les mots cles sql (from, into, where...) doivent etre en minuscule.
######## update et delete doivent contenir where

rq = {
  'get_max'          : "select max(obj)          from types;",
  'get_classe'       : "select class             from types                where obj=%s;",
  'get_proprietes'   : "select name,value        from proprietes_texte     where obj=%s;",
  'get_proprietes_i' : "select name,value        from proprietes_entier    where obj=%s;",
  'get_fils'         : "select lie               from liaisons             where obj=%s and type=1;",
  'get_responsables' : "select obj,lie           from liaisons             where type=2;",
  'get_membres'      : "select obj,lie           from liaisons             where type=3;",
  'get_alls'         : "select obj,class         from types;",

  'add_type'         : "insert into types              (obj, class)       values ( %s, %s);",
  'add_propriete'    : "insert into proprietes_texte   (obj, name, value) values ( %s, '%s', '%s');",
  'add_propriete_i'  : "insert into proprietes_entier  (obj, name, value) values ( %s, '%s', %s  );",
  'add_liaison'      : "insert into liaisons           (obj, lie,  type)  values ( %s, '%s', %s  );",

  'set_propriete'    : "update proprietes_texte   set value='%s'   where obj=%s and name='%s';",
  'set_propriete_i'  : "update proprietes_entier  set value=%s     where obj=%s and name='%s';",

  'del_classe'       : "delete from types              where obj=%s;",
  'del_propriete'    : "delete from proprietes_texte   where obj=%s and name='%s';",
  'del_propriete_i'  : "delete from proprietes_entier  where obj=%s and name='%s';",
  'del_proprietes'   : "delete from proprietes_texte   where obj=%s;",
  'del_proprietes_i' : "delete from proprietes_entier  where obj=%s;",
  'del_liaison'      : "delete from liaisons           where obj=%s and lie=%s;",
  'del_liaisons'     : "delete from liaisons           where obj=%s or lie=%s;",
  'del_my_groupes'   : "delete from liaisons           where lie=%s and type=3;",
}

old_SKIN = {
  'add_obj'          : "insert into contenus (pere, name, fils, langue) values (%s,'%s',%s,'%s');",
  'get_fils_by_type' : """select contenus.fils, contenus.name ,contenus.langue
                            from types, contenus 
                           where contenus.pere=%s 
                             and contenus.fils=types.obj 
                             and types.class=%s """,
  'get_name'         : "select name,langue from contenus where pere=%s and fils=%s;",
  'get_names'        : "select name from contenus where fils=%s;",
  'get_fils'         : "select fils from contenus where pere=%s;",
  'get_fil'          : "select fils from contenus where pere=%s and name='%s';",
  'get_rendus'       : "select template,disposition,presentation,pos from rendus where obj=%s;",
  'get_dispo_normal' : "select normal,file from dispositions where disposition=%s and type_spe=0;",
  'add_rendus_complet' : """insert into rendus (obj, template, disposition, presentation, pos)
                                         values ( %s,       %s,          %s,           %s,  %s);""",
  'set_dispos'       : "update dispositions set normal='%s',parent='%s' where disposition=%s;",

}
