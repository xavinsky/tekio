/* TODO si possible : 
Remetre la selection comme originale apres action !


*/


var tek_et_ids_zones_edit = new Array();
var tek_et_ids_zones_edit_visible = new Array();

var tek_et_repere_init='%%%%%%INIT%%%%%%'; 
var tek_et_repere_fin='%%%%%%END%%%%%%';

var tek_et_styles_by_type= new Array();
var tek_et_styles= new Array();
var tek_et_flag_source=false;
var tek_et_nb_visible=0;

function pos_in_array(elem,list){
    for (var i=0;i<list.length;i++){
	if (elem==list[i]){
	    return i;
	}
    }
    return -1;
}

function is_in_array(elem,list){
    for (var i=0;i<list.length;i++){
	if (elem==list[i]){
	    return true;
	}
    }
    return false;
}

function get_balise_style(s){
    if (s=='none'){
	return '';
    }
    if (s.substr(1,3)==' c '){
	return 'span class="'+s.substr(4,s.length-4)+'"';
    }
    if (s.substr(1,3)==' d '){
	return 'div class="'+s.substr(4,s.length-4)+'"';
    }
    return s.substr(2,s.length-2);
}

function get_type_style(s){
    if (s=='none'){
	return -1;
    }
    return parseInt(s.substr(0,1));
}

function get_no_compatible(idtype,balise){
    if (idtype==-1){
	return tek_et_styles;
    } 
    if (idtype==0){
	var tmp = new Array();
	tmp.push(balise);
	return tmp;
    } 
    return tek_et_styles_by_type[idtype];
}


function StartEditeurText(){
  var kids = document.getElementsByTagName('DIV');
  for (var i=0; i < kids.length; i++) {
    if (kids[i].className == "imagebutton") {
      kids[i].onmousedown = tbmousedown;
      kids[i].onmouseup = tbmouseup;
      kids[i].onclick = tbclick;
    }
  }

  var fils = document.getElementById('selectstyle').childNodes;
  for (var i=0;i<fils.length;i++){
      var f=fils[i];
      if (f.nodeName=='OPTION'){
	  var s=fils[i].value;
	  if ((s!='none') && (s!='')){
	      var idtype=get_type_style(s);
	      while (tek_et_styles_by_type.length<=idtype){
		  var tmp = new Array();
		  tek_et_styles_by_type.push(tmp);
              }
	      var name=get_balise_style(s);
	      tek_et_styles_by_type[idtype].push(name);
	      tek_et_styles.push(name);
	  }
      }
  }
  var tmp = new Array();
  tek_et_styles_by_type.push(tmp);
  tek_et_styles_by_type[2].push('sub');
  tek_et_styles_by_type[2].push('sup');
}

function StartEditeurText_l(id_zone_edit) {
    var inittext = document.getElementById('ftext_'+id_zone_edit).innerHTML;
    var doc=document.getElementById('ftext_'+id_zone_edit).contentWindow.document;
    doc.designMode = "on";
    doc.execCommand( 'enableObjectResizing', false ,null ) ;
    doc.execCommand( 'enableInlineTableEditing', false ,null ) ;

    // Disable the standard table editing features of Firefox.

    var v=document.getElementById(id_zone_edit).value;
    doc.body.innerHTML = v;

}

var nbframeload=0;
function frameload(moi){
    elemiframes=document.getElementsByTagName('IFRAME')
    nbframeload+=1;
    avider=tek_et_ids_zones_edit_visible.length;
    for (var i=0;i<avider;i++){
	tek_et_ids_zones_edit_visible.pop();
    }
    avider=tek_et_ids_zones_edit.length;
    for (var i=0;i<avider;i++){
	tek_et_ids_zones_edit.pop();
    }
    tek_et_nb_visible=0;
    if (nbframeload==elemiframes.length){
	for (var i=0;i<elemiframes.length;i++){
	    nameframe=elemiframes[i].id;
	    verif=nameframe.substr(0,6);
	    idzone=nameframe.substr(6,nameframe.length-6);
	    if (verif=="ftext_"){
		if (elemiframes[i].className=='novisu'){
		    tek_et_ids_zones_edit_visible.push(false);
		} else {
		    tek_et_ids_zones_edit_visible.push(true);
		    tek_et_nb_visible+=1;
                }

		tek_et_ids_zones_edit.push(idzone);
		StartEditeurText_l(idzone);
	    }
	}
	nbframeload=0;
    }
}

function tbmousedown(e)
{
  var evt = e ? e : window.event; 
  this.className = "imagebuttonclick";
  if (evt.returnValue) {
    evt.returnValue = false;
  } else if (evt.preventDefault) {
    evt.preventDefault();
  } else {
    return false;
  }
  return false;
}

function tbmouseup()
{
  this.className = "imagebutton";
  return false;

}

function tbclick()
{
  if (this.id == "source") {
    viewsource();
    return false
  } 

  if (tek_et_flag_source){
      alert('deselectionner le mode SOURCE');
      return false;
  }

  if (this.id == "createlink") {
    var szURL = prompt("Enter a URL:", "http://");
    if ((szURL != null) && (szURL != "")) {
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  create_link(szURL,tek_et_ids_zones_edit[i]);
	}
    }
  } else if (this.id == "bold"){
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  applique_style('0 b',tek_et_ids_zones_edit[i]);
      }
  } else if (this.id == "italic"){
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  applique_style('0 i',tek_et_ids_zones_edit[i]);
      }
  } else if (this.id == "underline"){
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  applique_style('0 c underline',tek_et_ids_zones_edit[i]);
      }
  } else if (this.id == "textbarre"){
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  applique_style('0 c textbarre',tek_et_ids_zones_edit[i]);
      }
  } else if (this.id == "sup"){
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  applique_style('2 sup',tek_et_ids_zones_edit[i]);
      }
  } else if (this.id == "sub"){
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  applique_style('2 sub',tek_et_ids_zones_edit[i]);
      }
  } else {
      for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	  document.getElementById('ftext_'+tek_et_ids_zones_edit[i]).contentWindow.document.execCommand(this.id, false, null);
      }
  }
  return false;

}

function viewsource(){
    var ds=document.getElementById('source');
    if (tek_et_flag_source){
	tek_et_flag_source=false;
	ds.innerHTML="HTML";
    } else {
	tek_et_flag_source=true;
	ds.innerHTML="VUE";
    }
    for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	viewsource_l(tek_et_flag_source,tek_et_ids_zones_edit[i]);
    }
  return false;

}

function viewsource_l(source,id_zone_edit)
{
  var html;
  if (source) {
    html = document.createTextNode(document.getElementById('ftext_'+id_zone_edit).contentWindow.document.body.innerHTML);
    document.getElementById('ftext_'+id_zone_edit).contentWindow.document.body.innerHTML = "";
    html = document.getElementById('ftext_'+id_zone_edit).contentWindow.document.importNode(html,false);
    document.getElementById('ftext_'+id_zone_edit).contentWindow.document.body.appendChild(html);
  } else {
    html = document.getElementById('ftext_'+id_zone_edit).contentWindow.document.body.ownerDocument.createRange();
    html.selectNodeContents(document.getElementById('ftext_'+id_zone_edit).contentWindow.document.body);
    document.getElementById('ftext_'+id_zone_edit).contentWindow.document.body.innerHTML = html.toString();
  }
  return false;

}

function create_link(valuelink,id_zone_edit)
{
    document.getElementById('ftext_'+id_zone_edit).contentWindow.document.execCommand("CreateLink",false,valuelink);
}

function SelectStyle(selectname)
{
    if (tek_et_flag_source){
	alert('deselectionner le mode SOURCE!');
	return false;
    }
    var cursel = document.getElementById(selectname).selectedIndex;
    if (cursel != 0) {
	var selected = document.getElementById(selectname).options[cursel].value;
	if (selected != ''){
	    for (var i=0;i<tek_et_ids_zones_edit.length;i++){
		applique_style(selected,tek_et_ids_zones_edit[i]);
	    }
	}
	document.getElementById(selectname).selectedIndex = 0;
    }
    return false;
}


function is_child_rec(nodePere,nodeFils){
    if (nodePere.hasChildNodes()){
	var fils=nodePere.childNodes;
	for(var i=0;i<fils.length;i++){
	    var f=fils[i];
	    if (f==nodeFils) {
		return 1;
	    }
	    var res=is_child_rec(f,nodeFils);
	    if (res!=0){
		return res;
            }
	}
    }
    return 0;
}


function cherchefirstchildnode(node,initNode,endNode){
    if (node.hasChildNodes()){
	var fils=node.childNodes;
	for(var i=0;i<fils.length;i++){
	    var f=fils[i];
	    if (f==initNode) {
		return 1;
	    }
	    if (f==endNode) {
		return 2;
	    }
	    var res=cherchefirstchildnode(f,initNode,endNode);
	    if (res!=0){
		return res;
            }
	}
    }
    return 0;
}


function next_balise(txtetude){
    var start_bal=txtetude.indexOf('<', 0);
    var stop_bal=-1;
    if (start_bal!=-1){
	stop_bal=txtetude.indexOf('>', start_bal);
    }
    if (stop_bal==-1){
	var tmp=new Array();
	tmp.push(txtetude);
	tmp.push('');
	tmp.push('');
	tmp.push(false);
	tmp.push(false);
	tmp.push(false);
	tmp.push('');
	tmp.push('');
	return tmp;
    }
    var pretxt=txtetude.substr(0,start_bal);
    var balisetxt=txtetude.substr(start_bal,stop_bal-start_bal+1);
    var newtxtetude=txtetude.substr(stop_bal+1,txtetude.length-stop_bal-1);
    var autofermante;
    var ouverture;
    var balisename;
    var baliseentry;

    var lbt=balisetxt.length;
    if ('/'==balisetxt.substr(lbt-2,1) || balisetxt=="<br>" || balisetxt=="<BR>"){
	autofermante=true;
	ouverture=false;
	balisename='';
	baliseentry='';
    } else {
	autofermante=false;
	if ('/'==balisetxt.substr(1,1)){
	    ouverture=false;
	    baliseentry=balisetxt.substr(2,lbt-3);
	} else {
	    ouverture=true;
	    baliseentry=balisetxt.substr(1,lbt-2);
	}

	var indexspace1=baliseentry.indexOf(' ',0);
	if (indexspace1==-1){
	    balisename=baliseentry;
	} else {
	    var lbe=baliseentry.length
	    if (lbe>10){
		var indexspace2=baliseentry.indexOf(' ',indexspace1);
		if (indexspace2!=-1){
		    if (baliseentry.substr(0,12)=='span class="'){
			indexspace1=1+baliseentry.indexOf('"',13);
		    }
		    if (baliseentry.substr(0,12)=="span class='"){
			indexspace1=1+baliseentry.indexOf("'",13);
		    }
		    if (baliseentry.substr(0,12)=='span style="'){
			indexspace1=1+baliseentry.indexOf('"',13);
		    }
		    if (baliseentry.substr(0,12)=="span style='"){
			indexspace1=1+baliseentry.indexOf("'",13);
		    }
		}
	    }
	    balisename=baliseentry.substr(0,indexspace1+1);
	}
    }

    var tmp=new Array();
    tmp.push(pretxt);
    tmp.push(balisetxt);
    tmp.push(newtxtetude);
    tmp.push(true);
    tmp.push(autofermante);
    tmp.push(ouverture);
    tmp.push(balisename);
    tmp.push(baliseentry);
    return tmp;

}

function get_bstart(balise_entry){
    if(balise_entry==''){
	return '';
    }
    return '<'+balise_entry+'>';
    

}

function get_bfin(balise_name){
    var bi=balise_name.indexOf(' ',0);
    var bfin;
    if (bi==-1){
	bfin='</'+balise_name+'>';
    } else {
	bfin='</'+balise_name.substr(0,bi)+'>';
    }
    return bfin;
}

function applique_style(lestyle,id_zone_edit){

    var select_balise=get_balise_style(lestyle);
    var select_idtype=get_type_style(lestyle);
    var non_compatible=get_no_compatible(select_idtype,select_balise);

    var select_bstart=get_bstart(select_balise);
    var select_bfin=get_bfin(select_balise);

    var win = document.getElementById('ftext_'+id_zone_edit).contentWindow;
    var selection = win.getSelection();
    if (selection==null){
	return;
    }
    var initNode=selection.anchorNode;
    var endNode=selection.focusNode;
    var initOffset=selection.anchorOffset;
    var endOffset=selection.focusOffset;

    var NodeBody=win.document.body;
    var ordre;

    /*
    if (is_child_rec(NodeBody,initNode)==0){
	alert('initnode out');
	alert(initNode);
	alert(initOffset);
    }
    if (is_child_rec(NodeBody,endNode)==0){
	alert('endnode out');
	alert(endNode);
	alert(endOffset);
    }
    */
    if (initNode==NodeBody && endNode==NodeBody){
	return;
    }

    if (initNode==NodeBody && initOffset==1){
	initNode=NodeBody.firstChild;
	initOffset=0;
	/*
	  initNode=NodeBody.lastChild;
	  initOffset=initNode.textContent.length;
	*/
    }
    if (endNode==NodeBody && initOffset==1){
	endNode=NodeBody.firstChild;
	endOffset=0;
	/*
	  endNode=NodeBody.lastChild;
	  endOffset=endNode.textContent.length;
	*/
    }

    if (initNode!=endNode){
	ordre=cherchefirstchildnode(NodeBody,initNode,endNode);
    } else {
	if (initOffset<endOffset){
	    ordre=1;
	} else {
	    ordre=2;
	}
	if (initOffset==endOffset){
	    return;
	}
    }

    if (ordre==2){
	var tmpNode=initNode;
	var tmpOffset=initOffset;
	initOffset=endOffset;
	initNode=endNode;
	endOffset=tmpOffset;
	endNode=tmpNode;
    }

    var txtbefore;
    var txtbody=NodeBody.innerHTML;

    if (initNode==endNode){
	var txtnode=initNode.textContent;
	var ta=txtnode.substr(0,initOffset);
	var tb=txtnode.substr(initOffset,endOffset-initOffset);
	var tc=txtnode.substr(endOffset,txtnode.length-endOffset);
	initNode.textContent=ta+tek_et_repere_init+tb+tek_et_repere_fin+tc;
	txtbefore=NodeBody.innerHTML;
    }  else {
	var txtnodeinit=initNode.textContent;
	var txtnodeinitav=initNode.textContent.substr(0,initOffset);
	var txtnodeinitap=initNode.textContent.substr(initOffset,txtnodeinit.length-initOffset);
	var newtxtnodeinit=txtnodeinitav+tek_et_repere_init+txtnodeinitap; 
	var txtnodeend=endNode.textContent;
	var txtnodeendav=endNode.textContent.substr(0,endOffset);
	var txtnodeendap=endNode.textContent.substr(endOffset,txtnodeend.length-endOffset);
	var newtxtnodeend=txtnodeendav+tek_et_repere_fin+txtnodeendap;	
	initNode.textContent=newtxtnodeinit;
	endNode.textContent=newtxtnodeend;
	txtbefore=NodeBody.innerHTML;
    }
    NodeBody.innerHTML=txtbody;

    if (txtbefore.indexOf(tek_et_repere_init,0)==-1){
	txtbefore=tek_et_repere_init+txtbefore;
    }
    if (txtbefore.indexOf(tek_et_repere_fin,0)==-1){
	txtbefore=txtbefore+tek_et_repere_fin;
    }

    /*
    alert(txtbefore);
    */

    var tek_et_pos_repere_init=txtbefore.indexOf(tek_et_repere_init, 0);
    var tek_et_pos_repere_fin=txtbefore.indexOf(tek_et_repere_fin, 0);
    var txtav=txtbefore.substr(0,tek_et_pos_repere_init);
    var txtin=txtbefore.substr(tek_et_pos_repere_init+tek_et_repere_init.length,tek_et_pos_repere_fin-tek_et_pos_repere_init-tek_et_repere_init.length);
    var txtap=txtbefore.substr(tek_et_pos_repere_fin+tek_et_repere_fin.length,txtbefore.length-tek_et_pos_repere_fin-tek_et_repere_fin.length);

    var frontiereinitpre='';
    var frontiereinitpost='';

    var newtxtin='';
    var frontierefinpre='';
    var frontierefinpost='';

    var balise_name_ouverte=new Array();
    var balise_entry_ouverte=new Array();
    var balise_name_reouverte=new Array();
    var balise_entry_reouverte=new Array();

    var flag_txtin_change=false;
    var flag_actived_same=false;
    var indice_flag=0;

    /* analyse chaine txtav */
    
    var txtetude=txtav;
    var continueetude=true;
    while (continueetude){
	var ret=next_balise(txtetude);
	var pretxt=ret[0];
	var balisetxt=ret[1];
	txtetude=ret[2];
	continueetude=ret[3];
	var autofermante=ret[4];
	var ouverture=ret[5];
	var balisename=ret[6];
	var baliseentry=ret[7];

	if (continueetude){
	    if (!(autofermante)){
		if (ouverture){
		    if ( !(flag_actived_same) && select_bstart==balisetxt){
			flag_actived_same=true;
			indice_flag=0;
		    }
		    balise_name_ouverte.push(balisename);
		    balise_entry_ouverte.push(baliseentry);
		    if (flag_actived_same) {
			indice_flag+=1;
		    }
		} else {
		    balise_name_ouverte.pop();
		    balise_entry_ouverte.pop();
		    if (flag_actived_same) {
			indice_flag-=1;
			if (indice_flag==0){
			    flag_actived_same=false;
			}
		    }
		}
	    }
	}
    }

    /* traitement frontiere init */


    var premier_non_compatible=-1;
    for (var i=0;i<balise_name_ouverte.length;i++){
	if (premier_non_compatible==-1){
	    if (is_in_array(balise_name_ouverte[i],non_compatible)){
		premier_non_compatible=i;
	    }
	}
    }

    if (premier_non_compatible!=-1){
	var nbtransfert=balise_name_ouverte.length-premier_non_compatible;
	for (i=0;i<nbtransfert;i++){
	    var balise_name=balise_name_ouverte.pop();
	    var balise_entry=balise_entry_ouverte.pop();
	    var bstart=get_bstart(balise_entry);
	    var bfin=get_bfin(balise_name);
	    frontiereinitpre=frontiereinitpre+bfin;
	    if (!(is_in_array(balise_name,non_compatible))){
		frontiereinitpost=bstart+frontiereinitpost;
	    }
	    balise_name_reouverte.unshift(balise_name);
	    balise_entry_reouverte.unshift(balise_entry);
	}
    } 

    /* analyse chaine txtin */
    txtetude=txtin;
    continueetude=true;


    while (continueetude){
	var ret=next_balise(txtetude);
	var pretxt=ret[0];
	var balisetxt=ret[1];
	txtetude=ret[2];
	continueetude=ret[3];
	var autofermante=ret[4];
	var ouverture=ret[5];
	var balisename=ret[6];
	var baliseentry=ret[7];
	
	newtxtin+=pretxt;
	if (!(flag_actived_same) && pretxt!=''){
	    flag_txtin_change=true;
	}

	if (continueetude){
	    if ((autofermante)){
		newtxtin+=balisetxt;
	    }else{
		if (ouverture){
		    if ( !(flag_actived_same) && select_bstart==balisetxt){
			flag_actived_same=true;
			indice_flag=0;
		    }
		    if (!(is_in_array(balisename,non_compatible))){
			newtxtin+=balisetxt;
		    }
		    balise_name_reouverte.push(balisename);
		    balise_entry_reouverte.push(baliseentry);
		    if (flag_actived_same) {
			indice_flag+=1;
		    }
		} else {
		    if (balise_name_reouverte.length>0){
			var balisename=balise_name_reouverte.pop();
			balise_entry_reouverte.pop();
			if (!(is_in_array(balisename,non_compatible))){
			    newtxtin+=balisetxt;
			}
		    } else {
			newtxtin+=balisetxt;
			balise_name_ouverte.pop();
			var baliseentry=balise_entry_ouverte.pop();
			var bstart=get_bstart(baliseentry);
			frontiereinitpre=frontiereinitpre+balisetxt;
			frontiereinitpost=bstart+frontiereinitpost;
		    }
		    if (flag_actived_same) {
			indice_flag-=1;
			if (indice_flag==0){
			    flag_actived_same=false;
			}
		    }

		}
	    }
	} 
    }


    /* traitement frontiere fin */

    while(balise_name_reouverte.length>0){
	var balise_name=balise_name_reouverte.pop();
	var balise_entry=balise_entry_reouverte.pop();
	var bstart=get_bstart(balise_entry);
	var bfin=get_bfin(balise_name);
	if (!(is_in_array(balise_name,non_compatible))){
	    frontierefinpre=frontierefinpre+bfin;
	} 
	frontierefinpost=bstart+frontierefinpost;
    }

    /* concatenation */
    if (!(flag_txtin_change)){
	select_bstart='';
	select_bfin='';
    }

    var concatenation;
    concatenation=txtav+frontiereinitpre;
    concatenation+=select_bstart;
    concatenation+=frontiereinitpost+newtxtin+frontierefinpre;
    concatenation+=select_bfin;
    concatenation+=frontierefinpost+txtap;



    /* netoyage 'dd<x></x>ee ' => ddee */
    var txtavantclean=concatenation;
    var passageutile=true;
    var txtapresclean="";

    while(passageutile){

	txtetude=txtavantclean;
	txtapresclean="";
	passageutile=false;
	continueetude=true;
	var lastbaliseopen='';

	while (continueetude){
	    var ret=next_balise(txtetude);
	    var pretxt=ret[0];
	    var balisetxt=ret[1];
	    txtetude=ret[2];
	    continueetude=ret[3];
	    var autofermante=ret[4];
	    var ouverture=ret[5];
	    var balisename=ret[6];
	    var baliseentry=ret[7];
	    

	    if (continueetude){
		if ((autofermante)){
		    txtapresclean+=lastbaliseopen;
		    txtapresclean+=pretxt;
		    txtapresclean+=balisetxt;
		    lastbaliseopen='';
		} else {
		    if (ouverture){
			txtapresclean+=lastbaliseopen;
			txtapresclean+=pretxt;
			lastbaliseopen=balisetxt;
		    } else {
			if (lastbaliseopen=='' || pretxt!=''){
			    txtapresclean+=lastbaliseopen;
			    txtapresclean+=pretxt;
			    txtapresclean+=balisetxt;
			    lastbaliseopen='';
			} else {
			    lastbaliseopen='';
			    passageutile=true;
			}
		    }
		}
	    } else {
		txtapresclean+=lastbaliseopen;
		txtapresclean+=pretxt;
		txtavantclean=txtapresclean;
	    }
	}
    }

    /* TODO autre netoyage : <x d>rr<b>r</b>r</x><x d>ee<i>e</i>e</x> */
    /*                      => <x d>rr<b>r</b>ree<i>e</i>e</x> */

    var txtavantclean=concatenation;
    var passageutile=true;
    var txtapresclean="";

    while(passageutile){

	txtetude=txtavantclean;
	txtapresclean="";
	passageutile=false;
	continueetude=true;
	var balises_open=new Array();
	var oldbaliseclose='';
	var lastentryclosed='';

	while (continueetude){
	    var ret=next_balise(txtetude);
	    var pretxt=ret[0];
	    var balisetxt=ret[1];
	    txtetude=ret[2];
	    continueetude=ret[3];
	    var autofermante=ret[4];
	    var ouverture=ret[5];
	    var balisename=ret[6];
	    var baliseentry=ret[7];

	    if (continueetude){
		if ((autofermante)){
		    lastentryclosed='';
		    txtapresclean+=oldbaliseclose;
		    oldbaliseclose='';
		    txtapresclean+=pretxt;
		    txtapresclean+=balisetxt;
		} else {
		    if (ouverture){
			if (lastentryclosed==balisetxt && lastentryclosed!='' && pretxt==''){
			    lastentryclosed='';
			    oldbaliseclose='';
			    passageutile=true;
                        } else {
			    lastentryclosed='';
			    txtapresclean+=oldbaliseclose;
			    oldbaliseclose='';
			    txtapresclean+=pretxt;
			    txtapresclean+=balisetxt;
			}
			balises_open.push(balisetxt);

		    } else {
			lastentryclosed=balises_open.pop();
			txtapresclean+=oldbaliseclose;
			txtapresclean+=pretxt;
			oldbaliseclose=balisetxt;
		    }
		}
	    } else {
		txtapresclean+=oldbaliseclose;
		oldbaliseclose='';
		txtapresclean+=pretxt;
		txtavantclean=txtapresclean;
		txtavantclean=txtapresclean;
	    }
	}
    }

    var txtfinal=txtapresclean;
    NodeBody.innerHTML=txtfinal;

}

function swap_zones_edit(id_zone_edit){
    var pl=pos_in_array(id_zone_edit,tek_et_ids_zones_edit);
    if (tek_et_ids_zones_edit_visible[pl]){
	tek_et_ids_zones_edit_visible[pl]=false;
	tek_et_nb_visible-=1;
    } else {
	tek_et_ids_zones_edit_visible[pl]=true;
	tek_et_nb_visible+=1;
    } 

    for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	var de = document.getElementById('ftext_'+tek_et_ids_zones_edit[i]);

	if (tek_et_ids_zones_edit_visible[i]==true){
	    de.className='visu'+tek_et_nb_visible+'_3'
	} else {
	    de.className='novisu';
	}
    }

}

function prepare_value_editeurtext(){
    if (tek_et_flag_source){
	viewsource();
    } 
    for (var i=0;i<tek_et_ids_zones_edit.length;i++){
	id_zone_edit=tek_et_ids_zones_edit[i];
	html = document.getElementById('ftext_'+id_zone_edit).contentWindow.document.body.innerHTML;
	document.getElementById(id_zone_edit).value=html;
	document.getElementById(id_zone_edit).innerHTML=html;
    }
    return false;
}
