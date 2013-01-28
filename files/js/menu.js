/* ***************************************************** */
/* Variables ajustables a sortir en parametre de scripts */
/* ***************************************************** */

var baseobj = document.getElementById('baseurl');
var urlbase = baseobj.href;
var taburl = urlbase.split("/");
if (taburl.length>2){
    urldomaine=taburl[0]+"//"+taburl[2];
} else {
    urldomaine='';
}
/* CORRESPONDANCES FONCTION MENU */

/* action in_box_nomal */
var a_n_n = new Array();
var a_n_u = new Array();

a_n_n.push("addpage");
a_n_u.push('/ajoute_page/form');

a_n_n.push("editpage");
a_n_u.push('/edit_page/form');

a_n_n.push("addimage");
a_n_u.push('/ajoute_image/form');

a_n_n.push("addgalerie");
a_n_u.push('/ajoute_galerie/form');

a_n_n.push("addelemgal");
a_n_u.push('/ajoute/form');

a_n_n.push("editgalinfo");
a_n_u.push('/edit/form');

a_n_n.push("addfile");
a_n_u.push('/ajoute_file/form');

a_n_n.push("movepage");
a_n_u.push('/move_page/form');

var action_box_normal = new Array(a_n_n,a_n_u);

/* action in_box_nomal_param */
var a_n_p_n = new Array();
var a_n_p_u = new Array();
var a_n_p_p = new Array();

a_n_p_n.push("skingencolors");
a_n_p_u.push('/gencolors');
a_n_p_p.push(urldomaine+'/skins/%s/gencolors');

a_n_p_n.push("skincolors");
a_n_p_u.push('/colors');
a_n_p_p.push(urldomaine+'/skins/%s/colors');

a_n_p_n.push("skinimages");
a_n_p_u.push('/images');
a_n_p_p.push(urldomaine+'/skins/%s/images');

a_n_p_n.push("skinstyles");
a_n_p_u.push('/styles');
a_n_p_p.push(urldomaine+'/skins/%s/styles');

a_n_p_n.push("skindisposition");
a_n_p_u.push('/disposition');
a_n_p_p.push(urldomaine+'/skins/%s/disposition');

var action_box_normal_param = new Array(a_n_p_n,a_n_p_u,a_n_p_p);

/* action in_box_nomal_racine */
var a_n_r_n = new Array();
var a_n_r_u = new Array();
var str_url_end="";

a_n_r_n.push("apropos");
a_n_r_u.push('/action/apropos');

a_n_r_n.push("editsite");
a_n_r_u.push('/edit_site/form');

a_n_r_n.push("editskins");
a_n_r_u.push('/skins');


var action_box_normal_racine = new Array(a_n_r_n,a_n_r_u);


/* action in_box_alerte */

var a_a_n = new Array();
var a_a_u = new Array();

a_a_n.push("delpage");
a_a_u.push('/delete_page/confirm');

var action_box_alert = new Array(a_a_n,a_a_u);

/* action redirect */

var a_r_n = new Array();
var a_r_u = new Array();

a_r_n.push("logout");
a_r_u.push('/user/logout');

a_r_n.push("editusers");
a_r_u.push('/admin/users');

var action_redirect = new Array(a_r_n,a_r_u);

/* action send info*/

var str_action_infos="";

var a_i_n = new Array();
var a_i_u = new Array();

a_i_n.push("fixepalette");
a_i_u.push('/palette/position');


var action_infos = new Array(a_i_n,a_i_u);


/* WIKI */
var max_elem_in_line=4;

/* ****** */
/*  CODE  */
/* ****** */

/* MENU */

var liste_div_restore_display_css = new Array();


function div_restore_display_css(){
    while (liste_div_restore_display_css.length!=0){
	var obj=liste_div_restore_display_css.pop();
	obj.style['display']='';
    }
}

function menu2_click(e,id){
    var obj=getObjetByEvent(e);
    obj.parentNode.style.display='none';
    liste_div_restore_display_css.push(obj.parentNode);
    setTimeout(div_restore_display_css,0.2);
    menu_click(id);
}

function pal_click(e,idpalclick){
    menu_click(idpalclick);
}

var param_menu_click='';

function menu_click(idmenuclick){
    var url;
    var tabidmenu=idmenuclick.split("_",2);
    if (tabidmenu.length>1){
	idmenuclick=tabidmenu[0];
	param_menu_click=tabidmenu[1];
    }

    for (var i=0;i<action_box_normal[0].length;i++){
	if (idmenuclick==action_box_normal[0][i]){
	    url=base_url+action_box_normal[1][i];
	    http_url_datas_to_fct(url,recup_simple);
	    return;
        }
    }

    for (var i=0;i<action_box_normal_param[0].length;i++){
	if (idmenuclick==action_box_normal_param[0][i]){
	    if (param_menu_click==''){
		url=base_url+action_box_normal_param[1][i];
	    } else {
		pre_url=action_box_normal_param[2][i];
		var dec_url= pre_url.split("%s",2);
		url=dec_url[0]+param_menu_click+dec_url[1];	
                param_menu_click="";
	    }
	    http_url_datas_to_fct(url,recup_simple);
	    return;
        }
    }

    for (var i=0;i<action_box_normal_racine[0].length;i++){
	if (idmenuclick==action_box_normal_racine[0][i]){
	    url=action_box_normal_racine[1][i]+str_url_end;
	    str_url_end="";
	    http_url_datas_to_fct(url,recup_simple);
	    return;
        }
    }

    for (var i=0;i<action_box_alert[0].length;i++){
	if (idmenuclick==action_box_alert[0][i]){
	    url=base_url+action_box_alert[1][i];
	    http_url_datas_to_fct(url,recup_alerte);
	    return;
        }
    }

    for (var i=0;i<action_redirect[0].length;i++){
	if (idmenuclick==action_redirect[0][i]){
	    document.location.href=action_redirect[1][i];
	    return;
        }
    }

    for (var i=0;i<action_infos[0].length;i++){
	if (idmenuclick==action_infos[0][i]){
	    url=base_url+action_infos[1][i];
	    http_url_datas_to_fct(url+str_action_infos,recup_infos);
	    str_action_infos="";
	    return;
        }
    }

    if (idmenuclick=="addtext"){
	url=base_url+'/ajoute_text/form';
        http_url_datas_to_fct(url,recup_simple_editeur_text);
	return;
    }

    if (idmenuclick=="wikion"){
	active_wiki();
	return;
    }

    alert('Pas encore implemente : '+ idmenuclick);

}

function recup_simple_editeur_text(){
    var value=recup_http_url_datas();
    if (value!=0){
	var divalerte = document.getElementById('div_panneau_alerte');
	divalerte.style.display='none';
	var divbase = document.getElementById('div_panneau_base');
	var divcontenu = document.getElementById('div_panneau_base_contenu');
	divcontenu.innerHTML=value;
	var divvalidinit = document.getElementById('div_valid');
	var divvalid = document.getElementById('div_panneau_valid');
	if (divvalidinit){
	    divvalid.innerHTML=divvalidinit.innerHTML;
	}
	divbase.style.display='block';
	StartEditeurText();
    }
}

function recup_simple(){
    var value=recup_http_url_datas();
    if (value!=0){
	var divalerte = document.getElementById('div_panneau_alerte');
	divalerte.style.display='none';
	var divbase = document.getElementById('div_panneau_base');
	var divcontenu = document.getElementById('div_panneau_base_contenu');
	divcontenu.innerHTML=value;
	var divvalidinit = document.getElementById('div_valid');
	var divvalid = document.getElementById('div_panneau_valid');
	if (divvalidinit){
	    divvalid.innerHTML=divvalidinit.innerHTML;
	}
	divbase.style.display='block';
	/* patch activation editeur text */
	if (value.search('twbaraction')!=-1){
            StartEditeurText();    
	}
	if (value.search('class="color')!=-1){
            makeColorSelectors(false);
	}

    }
}

function recup_alerte(){
    var value=recup_http_url_datas();
    if (value!=0){
	var divbase = document.getElementById('div_panneau_base');
	divbase.style.display='none';
	var divalerte = document.getElementById('div_panneau_alerte');
	var divcontenu = document.getElementById('div_panneau_alerte_contenu');
	divcontenu.innerHTML=value;
	var divvalidinitalerte = document.getElementById('div_valid');
	var divvalidalerte = document.getElementById('div_panneau_valid_alerte');
	if (divvalidinitalerte){
	    divvalidalerte.innerHTML=divvalidinitalerte.innerHTML;
	}
	divalerte.style.display='block';
    }
}

function recup_infos(){
    var value=recup_http_url_datas();

    if (value!=0){
	if (value.search('alert:')!=-1){
	    alert(value.substring(6));
	}
    }
}

/* DEPLACEMENT PAGE */
var posactu=-10;

function arbo_desactive_subs(pere){
    var enfants=pere.childNodes;
    for (var enfant=0; enfant<enfants.length; enfant+=1){
	if (enfants[enfant].childNodes[0].className=='arbo_move_over'){
	    var nivclos=enfants[enfant].childNodes[1].childNodes[0].childNodes[1];
	    nivclos.style.display='none';    
	    enfants[enfant].className="arbo_move_elem inactif";
	}
    }
}

function arbo_move_page(e,pos){
    var obj=getObjetByEvent(e);
    if (obj.className=='arbo_move_elem_titre') {obj=obj.parentNode;}
    if (obj.className=='arbo_move_over') {
        /* deplace elem_actu */
	var nodeactu = document.getElementById('arbo_move_elem_actu');
	nodeactu.parentNode.removeChild(nodeactu);
	var pere=obj.parentNode.parentNode;
	if (pos==posactu){
	    pos+=1;
	}
        var clicnode=pere.childNodes[pos];
	if (clicnode){
  	    pere.insertBefore(nodeactu,clicnode);
	} else {
  	    pere.appendChild(nodeactu);
	}
	posactu=pos;

        /* desactive sous-menu non utiliser */
	arbo_desactive_subs(pere);
    }
}

function arbo_ouvre_page(e){
    var obj=getObjetByEvent(e);
   
    if (obj.className=='arbo_indic_over'){

	arbo_desactive_subs(obj.parentNode.parentNode.parentNode.parentNode);

	/* ouvre page */
	var pere=obj.parentNode.childNodes[1];
	pere.style.display='block';    
	
	/* deplace actu */
	
	var nodeactu = document.getElementById('arbo_move_elem_actu');
	nodeactu.parentNode.removeChild(nodeactu);
	    
	var clicnode=pere.childNodes[0];
	if (clicnode){
	    pere.insertBefore(nodeactu,clicnode);
	} else {
	    pere.appendChild(nodeactu);
	}
	posactu=0;

        /* change color css...*/
	var grandpere=obj.parentNode.parentNode.parentNode;
        grandpere.className="arbo_move_elem actif";

    }
}


function go_move_page(e){
    var obj=getObjetByEvent(e);
    if (obj.className=="arbo_move_elem_titre"){
	obj=obj.parentNode;
    }
    if (obj.className=="arbo_move_elem actu"){
	var idpere=obj.parentNode.id;
        var url=urlbase+"/move_page?pere="+idpere+'&pos='+posactu;
        document.location.href=url;
    }
}


/* WIKI */

/* WIKI INIT */

var list_elems=[];
var list_cols=[];

var html_icon_actions_col='<div style="position: relative;"><div class="icon_actions_col">';
html_icon_actions_col+='<div class="icon_actions" onclick="action_col_move(event);"><img src="/includes/images/interface/deplacer_element.png" /></div>';
html_icon_actions_col+='</div></div>';
var html_icon_actions_elem='<div class="icon_actions_elem">';
html_icon_actions_elem+='<div class="icon_actions" onclick="action_elem_edit(event);"><img src="/includes/images/interface/editer_texte.png" /></div>';
/*html_icon_actions_elem+='[<div class="icon_actions" onclick="action_elem_move(event);">M</div>]';*/
html_icon_actions_elem+='<div class="icon_actions" onclick="action_elem_delete(event);"><img src="/includes/images/interface/detruire_element.png" /></div>';
html_icon_actions_elem+='</div>';

function ajouter_top_bottom(divcentre){
    var lines=divcentre.childNodes;
    var nblines=lines.length;
    
    var newnodetop = document.createElement("div"); 
    newnodetop.innerHTML = '<div class="col1" style="padding-bottom: 10px; padding-top: 10px;" ><div id="elemid_0" class="elem"><center><img src="/includes/images/interface/top_wiki.png"></center></div></div>';
    newnodetop.className='line';
    newnodetop.style.display='none';

    var newnodebottom = document.createElement("div"); 
    newnodebottom.innerHTML = '<div class="col1" style="padding-bottom: 10px; padding-top: 10px;"><div id="elemid_-1" class="elem"><center><img src="/includes/images/interface/bottom_wiki.png"></center></div></div>';
    newnodebottom.className='line';
    newnodebottom.style.display='none';

    divcentre.appendChild(newnodebottom);
    var lineref=lines[0];
    divcentre.insertBefore(newnodetop,lineref);
}



function init_wiki_js(){
    var divcentre = document.getElementById('centre');
    var divscentre = divcentre.childNodes;
    ajouter_top_bottom(divcentre);
    var maxl=divscentre.length;
    var lactu=0;
    for (iddivline in divscentre){
	var divline=divscentre[iddivline];
        if (divline.className=='line'){
	    var divscols=divline.childNodes;
	    for (iddivcol in divscols){
		var divcol=divscols[iddivcol];
		if (divcol.className && divcol.className.substring(0,3)=='col'){
		    if ((lactu>0) &&(lactu+1<maxl)){
			divcol.innerHTML=html_icon_actions_col+divcol.innerHTML;
			var divselems=divcol.childNodes;
			for (iddivelem in divselems){
			    var divelem=divselems[iddivelem];
			    if (divelem.className && divelem.className.substring(0,4)=='elem'){
				divelem.innerHTML=html_icon_actions_elem+divelem.innerHTML;
				list_elems.push(divelem);
			    }
			}
		    }
		    list_cols.push(divcol);
		}
	    }
        }
	lactu+=1;
    }
}

function active_wiki(){
    var divcentre = document.getElementById('centre');
    var lines = divcentre.childNodes;
    var nblines=lines.length;

    lines[0].style.display='block';
    lines[nblines-1].style.display='block';

    for (ide in list_cols){
	var col=list_cols[ide];
        col.className='actived '+col.className;
    }
    for (ide in list_elems){
	var elem=list_elems[ide];
        elem.className='elem actived'+elem.className.substring(4);
    }
}

/* WIKI LIB */

function get_elemid_from_event(e){
    var obj=getObjetByEvent(e);
    var idobj=obj.parentNode.parentNode.parentNode.id;
    if (idobj.substring(0,7)=='elemid_'){
	return idobj.substring(7);
    } else { 
	return 0;
    }
}

/* WIKI DELETE */

function action_elem_delete(e){
    if (elemid_tomove==0){
	var location = window.location.href+'#top';
	var elemid=get_elemid_from_event(e);
	if (elemid!=0){
	    var url=base_url+'/element_delete_confirm/'+elemid;
	    http_url_datas_to_fct(url,recup_alerte);
	}
    }
}

/* WIKI EDIT */

function action_elem_edit(e){
    if (elemid_tomove==0){
	var location = window.location.href+'#top';
	var elemid=get_elemid_from_event(e);
	if (elemid>0){
	    var url=base_url+'/element_edit_form/'+elemid;
	    http_url_datas_to_fct(url,recup_simple);
	}
    }
}


/* WIKI MOVE */

var elemid_tomove=0;
var tomove_line=0;
var tomove_col=0;
var tomove_col_pos=0;
var parentlines=0;
var moved=0;
var lastover=0;


function get_elemid_from_event_move(e){
    var obj=getObjetByEvent(e);

    if (obj.className.substring(0,11)!="actived col"){
	obj=obj.parentNode;
    }
    if (obj.className.substring(0,11)!="actived col"){
	obj=obj.parentNode;
    }
    if (obj.className.substring(0,11)!="actived col"){
	obj=obj.parentNode;
    }
    if (obj.className.substring(0,11)!="actived col"){
	obj=obj.parentNode;
    }
    if (obj.childNodes.length>1){
	obj=obj.childNodes[1];
    } else {
	obj=obj.childNodes[0];
    }
    var idobj=obj.id;
    if (idobj.substring(0,7)=='elemid_'){
	return idobj.substring(7);
    } else { 
	return -2;
    }
}

function get_elemid_from_col_event(e){
    var obj=getObjetByEvent(e);

    var idobj=obj.parentNode.parentNode.parentNode.parentNode.childNodes[1].id;
    if (idobj.substring(0,7)=='elemid_'){
	return idobj.substring(7);
    } else { 
	return 0;
    }
}

function elemobj(elemid){
    return document.getElementById('elemid_'+elemid);
}


function position_objet(obj){
    var parent=obj.parentNode;
    var fils=parent.childNodes;
    for (idfils in fils){
	var filstmp=fils[idfils];
	if (filstmp==obj){
	    return idfils;
	}
    }
    return -1;
}

function move_is_col1(){
    if (tomove_line.childNodes.length==1){
	return 1;
    }
    return 0;
}


function action_col_move(e){
    /* en attendant */
    var elemid=get_elemid_from_col_event(e);
    if (elemid>0){
	elemid_tomove=elemid;
        var elem=elemobj(elemid);
        elem.className='elem moving'+elem.className.substring(12);
        tomove_col=elem.parentNode;
        tomove_line=tomove_col.parentNode;
        parentlines=tomove_line.parentNode;
	tomove_col_pos=position_objet(tomove_col);
	for (ide in list_cols){
	    var col=list_cols[ide];
	    col.onmouseover=move_over;
	}
	tomove_col.onmouseover=move_over_base;
	tomove_col.onclick=redirect_move_ok;
    
	lastover=tomove_col_pos;

	for (ide in list_cols){
	    var col=list_cols[ide];
	    var f=col.childNodes[0].childNodes[0];
	    if (f.className=='icon_actions_col'){
		f.className='nodisplay';
	    }
	}
	for (ide in list_elems){
	    var elem=list_elems[ide];
	    var f=elem.childNodes[0];
	    if (f.className=='icon_actions_elem'){
		f.className='nodisplay';
	    }
	}
    }
    return
}

function enleve_col(){
    tomove_line.removeChild(tomove_col);
    var cols=tomove_line.childNodes;
    var nbcol=cols.length;
    if (nbcol==0){
	tomove_line.parentNode.removeChild(tomove_line);
    } else {
	for (var idcol=0; idcol<cols.length; idcol+=1){
	    var col=cols[idcol];
	    /* attention bug si depasse les 10 colonnes*/
	    col.className='actived col'+nbcol+col.className.substring(12);
	}
    }
}

function ajouter_ligne(pos){
    var lines=parentlines.childNodes;
    var nblines=lines.length;
    
    var newnode = document.createElement("div"); 
    newnode.innerHTML = '';
    newnode.className='line';

    if (pos>nblines){
	parentlines.appendChild(newnode);
    } else {
	lineref=lines[pos];
	parentlines.insertBefore(newnode,lineref);
    }
}

function inserer_dans_ligne(posline,poselem){
    var lines=parentlines.childNodes;
    var line=lines[posline];
    var cols=line.childNodes;
    var nbcols=cols.length;

    if (1*tomove_col_pos+1.0==1*poselem){
	poselem+=1;
    }

    if (poselem>nbcols){
	line.appendChild(tomove_col);
    } else {
	colref=cols[poselem];
	line.insertBefore(tomove_col,colref);
    }

    cols=line.childNodes;
    nbcols=cols.length;

    for (var idcol=0; idcol<cols.length; idcol+=1){
	var col=cols[idcol];
	/* attention bug si depasse les 10 colonnes*/
	col.className='actived col'+nbcols+col.className.substring(12);
    }

    tomove_line=line;
    tomove_col_pos=position_objet(tomove_col);

}

function move_over(e){
    var elemid=get_elemid_from_event_move(e);
    if (elemid==-2){
	return;
    }
    if (elemid==lastover){
	return;
    }
    lastover=elemid;
    
    var elem=elemobj(elemid);

    var col=elem.parentNode; 
    var line=col.parentNode; 
    var posline=position_objet(line);
    var poselem=position_objet(col);

    if (elemid==0){
	if (move_is_col1()!=1){
	    enleve_col();
	    posline=position_objet(line)+1;
	    ajouter_ligne(posline);
	    tomove_col_pos=-1;
	    inserer_dans_ligne(posline,0);
	    moved=1;
	}
	return;
    }
    if (elemid==-1){
	if (move_is_col1()!=1){
	    enleve_col();
	    posline=position_objet(line);
	    ajouter_ligne(posline);
	    tomove_col_pos=-1;
	    inserer_dans_ligne(posline,0);
	    moved=1;
	}
	return;
    }

    if (line==tomove_line){
	inserer_dans_ligne(posline,poselem);
	moved=1;

    } else {
	if (move_is_col1()==1 && line.childNodes.length<max_elem_in_line){
	    enleve_col();
	    tomove_col_pos=-1;
	    posline=position_objet(line);
	    inserer_dans_ligne(posline,poselem);
	    moved=1;
	} else {
	    if ( posline>position_objet(tomove_line) ){
		enleve_col();
		posline=position_objet(line);
		ajouter_ligne(posline);
		tomove_col_pos=-1;
		inserer_dans_ligne(posline,0);
		moved=1;

	    } else {
		enleve_col();
		posline=position_objet(line);
		ajouter_ligne(1*posline+1);
		tomove_col_pos=-1;
		inserer_dans_ligne(1*posline+1,0);
		moved=1;
	    
	    }
	}

    }

}

function move_over_base(e){
    var elemid=get_elemid_from_event_move(e);
    if (elemid==lastover){
	return;
    }
    lastover=elemid;
}

function redirect_move_ok(){
    if (moved!=0){
	var posline=position_objet(tomove_line);
	var poscol=position_objet(tomove_col);
	var solo;
	if (move_is_col1()==1){
	    solo='y';
	} else {
	    solo='n';
        }
	newurl=urlbase+"/element_move?id="+elemid_tomove+"&line="+posline+'&col='+poscol+'&solo='+solo;
	document.location = newurl;

    }
}



function remplit_initialiseur(){
  if (typeof (initialisation_js) == "undefined") {
      setTimeout('remplit_initialiseur();',200);
  } else {
      initialisation_js.push(init_wiki_js);
  }
}
remplit_initialiseur();

