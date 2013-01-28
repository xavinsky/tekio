var jsbox_name = new Array();
var jsbox_px = new Array();
var jsbox_py = new Array();
var jsbox_dx = new Array();
var jsbox_dy = new Array();
var jsbox_move = new Array();
var jsbox_check_move = new Array();
var jsbox_sx = new Array();
var jsbox_rx = new Array();
var mouse_x=0;
var mouse_y=0;

var zindexmax=20;

if (document.getElementById){
  if(navigator.appName.substring(0,3) == "Net")
    document.captureEvents(Event.MOUSEMOVE);
  document.onmousemove = Pos_Souris;
}

function jsbox_init_box(name,px,py,lx,sx,color){
  jsbox_name.push(name);
  jsbox_px.push(px);
  jsbox_py.push(py);
  jsbox_dx.push(0);
  jsbox_dy.push(0);
  jsbox_move.push(0);
  jsbox_check_move.push(0);
  jsbox_sx.push(sx);
  jsbox_rx.push(0);
  var div_base=document.getElementById(name);
  div_base.style.left=px+'px';
  div_base.style.top=py+'px';
  div_base.style.width=lx+'px';
  div_base.style.height=sx+'px';
  div_base.style.position="absolute";

  var html_base=div_base.innerHTML;
  var html_header='<div class="ombre_pal_haut_droite">';
  html_header+='<div id="barre_'+name+'" class="barrebox" onmousedown="start_box(this);" onmouseup="stop_box(this);" onmouseout="check_stop_box(this,1);" onmouseover="check_stop_box(this,0);">';
  html_header+='<div id="reduce_'+name+'" class="reducebox" onclick="reduce_box(this);">'
  html_header+='<img class="img_div_base" src="/includes/images/interface/reduire.png" />';
  html_header+='<img class="img_div_hover" src="/includes/images/interface/reduire_r.png" />';
  html_header+='</div>';

  html_header+='<div id="fixepal_'+name+'" class="fixepalette" onclick="fixe_palette(this);">'
  html_header+='<img class="img_div_base" src="/includes/images/interface/reduire.png" />';
  html_header+='</div>';

  html_header+='</div></div><div class="ombre_pal_droite">';
  html_header+='<div class="decal_haut_moin_barre"></div>';
  html_header+='<div id="contenu_'+name+'" class="contenu_'+name+'">';
  var html_footer="</div>";
  html_footer+='</div>';
  html_footer+='<div class="ombre_pal_bas_gauche">';
  html_footer+='</div>';
  html_footer+='<div class="ombre_pal_bas">';
  html_footer+='</div>';
  html_footer+='<div class="ombre_pal_bas_droite">';
  html_footer+='</div>';

  var html_total=html_header+html_base+html_footer;
  div_base.innerHTML=html_total;

  var div_contenu=document.getElementById("contenu_"+name);
  div_contenu.style.backgroundColor=color;
  div_contenu.style.zindex=2;
}

function find_indice_box(tab,value){
    var nbe=tab.length;
    for (var i=0;i<nbe;i++){
	if ("barre_"+tab[i]==value) return i;
    }
    return -1;
}

function find_in_indice(tab,value){
    var nbe=tab.length;
    for (var i=0;i<nbe;i++){
	if ("reduce_"+tab[i]==value) return i;
    }
    return -1;
}
function find_fix_indice(tab,value){
    var nbe=tab.length;
    for (var i=0;i<nbe;i++){
	if ("fixepal_"+tab[i]==value) return i;
    }
    return -1;
}

function Pos_Souris(e){
    mouse_x = (navigator.appName.substring(0,3) == "Net") ? e.pageX : event.x+document.body.scrollLeft;
    mouse_y = (navigator.appName.substring(0,3) == "Net") ? e.pageY : event.y+document.body.scrollTop;
    var len=jsbox_name.length;
    for (var id=0;id<len;id++){
	if (jsbox_move[id]==1){
	    var name=jsbox_name[id];
	    jsbox_px[id]=mouse_x+jsbox_dx[id];
	    jsbox_py[id]=mouse_y+jsbox_dy[id];
	    document.getElementById(name).style.left=jsbox_px[id]+'px';
	    document.getElementById(name).style.top=jsbox_py[id]+'px';
	    if (jsbox_check_move[id]==1){
		jsbox_move[id]==0;
	    }
	}
    }
}

function noselect(ev){
    return false;
}

function start_box(a){
    var id=find_indice_box(jsbox_name,a.id);
    var name=jsbox_name[id];
    jsbox_dx[id]=jsbox_px[id]-mouse_x;
    jsbox_dy[id]=jsbox_py[id]-mouse_y;
    jsbox_move[id]=1;
    document.getElementById(name).style.zIndex=zindexmax;
    window.onselect = noselect;
}

function stop_box(a){
    var id=find_indice_box(jsbox_name,a.id);
    if (jsbox_move[id]==1){
	jsbox_move[id]=0; 
	window.onselect = false;
    }
}

function check_stop_box(a,out){
    var id=find_indice_box(jsbox_name,a.id);
    jsbox_check_move[id]=out; 
}

function reduce_box(a){
    var id=find_in_indice(jsbox_name,a.id);
    var name=jsbox_name[id];
    if (jsbox_rx[id]==0){
	jsbox_rx[id]=1;
	document.getElementById(name).style.height="20px";
	document.getElementById("contenu_"+name).style.display="none";
    } else {
	jsbox_rx[id]=0;
	document.getElementById(name).style.height=jsbox_sx[id];
	document.getElementById("contenu_"+name).style.display="block";
    }
}

function fixe_palette(a){
    var id=find_fix_indice(jsbox_name,a.id);
    str_action_infos = "/"+jsbox_px[id]+"/"+jsbox_py[id];
    pal_click(false,'fixepalette');
}

function load_palette()
{
    var value=recup_http_url_datas();
    if (value!=0){
	var divcontenupalette = document.getElementById('contenu_palette');
	divcontenupalette.innerHTML = value;
    }
}

