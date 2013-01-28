/* PARAM DE LA CARTE*/

var XMax = 1500 ;
var YMax = 850 ;

var XMin = 900 ;
var YMin = 510 ;

var PosX =1115;
var PosY =310;

var facteurloupe = 100;
var sizenum=20;
var nbnum=50;

var num_x=new Array()
var num_y=new Array()

num_x[1]=2145;
num_y[1]=940;
num_x[2]=2130;
num_y[2]=995;
num_x[3]=2255;
num_y[3]=935;
num_x[4]=2520;
num_y[4]=1130;
num_x[5]=2625;
num_y[5]=1150;
num_x[6]=2665;
num_y[6]=1245;
num_x[7]=2705;
num_y[7]=1185;
num_x[8]=2055;
num_y[8]=880;
num_x[9]=2085;
num_y[9]=825;
num_x[10]=2165;
num_y[10]=770;
num_x[11]=2060;
num_y[11]=695;
num_x[12]=2230;
num_y[12]=620;
num_x[13]=2370;
num_y[13]=555;
num_x[14]=2075;
num_y[14]=375;
num_x[15]=2475;
num_y[15]=605;
num_x[16]=2560;
num_y[16]=620;
num_x[17]=2645;
num_y[17]=520;
num_x[18]=2570;
num_y[18]=440;
num_x[19]=2780;
num_y[19]=480;
num_x[20]=2700;
num_y[20]=225;
num_x[21]=2790;
num_y[21]=150;
num_x[22]=2485;
num_y[22]=110;
num_x[23]=1850;
num_y[23]=730;
num_x[24]=1810;
num_y[24]=575;
num_x[25]=1805;
num_y[25]=505;
num_x[26]=1360;
num_y[26]=455;
num_x[27]=1245;
num_y[27]=190;
num_x[28]=1730;
num_y[28]=770;
num_x[29]=1700;
num_y[29]=810;
num_x[30]=1570;
num_y[30]=840;
num_x[31]=1390;
num_y[31]=800;
num_x[32]=1500;
num_y[32]=890;
num_x[33]=1400;
num_y[33]=930;
num_x[34]=1530;
num_y[34]=990;
num_x[35]=1595;
num_y[35]=1040;
num_x[36]=1260;
num_y[36]=985;
num_x[37]=1170;
num_y[37]=1035;
num_x[38]=1095;
num_y[38]=930;
num_x[39]=1070;
num_y[39]=1100;
num_x[40]=945;
num_y[40]=915;
num_x[41]=450;
num_y[41]=1000;
num_x[42]=435;
num_y[42]=860;
num_x[43]=200;
num_y[43]=1120;
num_x[44]=570;
num_y[44]=1295;
num_x[45]=1310;
num_y[45]=1105;
num_x[46]=1240;
num_y[46]=1200;
num_x[47]=1360;
num_y[47]=1240;
num_x[48]=1125;
num_y[48]=1365;
num_x[49]=1080;
num_y[49]=1420;
num_x[50]=880;
num_y[50]=1550;


/* Fin param carte*/


var Vitesse = 4;
var timeVitesse = 30;
var tab_objnum=new Array()
var tab_objinfo=new Array()
var binfo=0;
var objmap=0;
var objpointeur=0;
var pos_mouse_x=0;
var pos_mouse_y=0;
var XActu = XMax;
var YActu = YMax;
var tailleX =300;
var tailleY =380;
var CentreX =tailleX/2;
var CentreY =tailleY/2;
var InfoActive= 0;

function mouse_pos(e)
{
  pos_mouse_x = (navigator.appName.substring(0,3) == "Net") ? e.pageX : event.x+document.body.scrollLeft;
  pos_mouse_y = (navigator.appName.substring(0,3) == "Net") ? e.pageY : event.y+document.body.scrollTop;
}

if(navigator.appName.substring(0,3) == "Net") document.captureEvents(Event.MOUSEMOVE);
if(navigator.appName.substring(0,3) == "Net") document.captureEvents(Event.MOUSEUP);

function change_pos_un_num(idunnum){
		    if (idunnum<10) {
			strnum='0'+idunnum;
		    } else {
			strnum=''+idunnum;
		    }
		    posxnum=num_x[idunnum]/2;
		    posynum=num_y[idunnum]/2;
		    
		    objnum=tab_objnum[idunnum];
		    XPropnum=CentreX+(XActu*posxnum/XMax)-XProp-sizenum/2;
		    YPropnum=CentreY+(YActu*posynum/YMax)-YProp-sizenum/2;
		    
		    
		    objnum.style.left=XPropnum+'px';
		    objnum.style.top=YPropnum+'px';
}


function hide_num(){
    for (var idnum=1;idnum<=nbnum;idnum+=1) 
	{
	    if (idnum<10) {
		strnum='0'+idnum;
	    } else {
		strnum=''+idnum;
	    }
            objnum=tab_objnum[idnum];
	    objnum.style.display='none';

	    if (idnum==InfoActive)
		{
		    info=tab_objinfo[idnum]
		    info.style.display='none';
                }

	}
    binfo.style.display='none';
}

function show_num(){
    for (var idnum=1;idnum<=nbnum;idnum+=1) 
	{
	    if (idnum<10) {
		strnum='0'+idnum;
	    } else {
		strnum=''+idnum;
	    }

	    if (idnum==InfoActive)
		{
		    info=tab_objinfo[idnum]
		    info.style.display='block';
                } else {
  		    objnum=tab_objnum[idnum];
		    objnum.style.display='block';
	    }
	    
	}
    if (InfoActive!=0){
      binfo.style.display='block';
    }
}

function change_pos_num(){
    for (var idnum=1;idnum<=nbnum;idnum+=1) 
	{
	    if (idnum==InfoActive)
		{
		    overnum(idnum);
		} else {
		    if (idnum<10) {
			strnum='0'+idnum;
		    } else {
			strnum=''+idnum;
		    }
		    posxnum=num_x[idnum]/2;
		    posynum=num_y[idnum]/2;
		    

		    objnum=tab_objnum[idnum];
		    XPropnum=CentreX+(XActu*posxnum/XMax)-XProp-sizenum/2;
		    YPropnum=CentreY+(YActu*posynum/YMax)-YProp-sizenum/2;
		    
		    
		    objnum.style.left=XPropnum+'px';
		    objnum.style.top=YPropnum+'px';

		}
	}
}


function mapchange(){
  XProp=XActu*PosX/XMax;
  YProp=YActu*PosY/YMax;
  objmap.style.left=(CentreX-XProp)+'px';
  objmap.style.top=(CentreY-YProp)+'px';

  if (dragdroppointeur==0 && dragdropmap==0) change_pos_num();

}

function mapchange_haut(){
  DY=YMax*Vitesse/YActu;
  PosY=PosY+DY;
  mapchange();
}

function mapchange_gauche(){
  DX=XMax*Vitesse/XActu;
  PosX=PosX+DX;
  mapchange();
}

function mapchange_bas(){
  DY=YMax*Vitesse/YActu;
  PosY=PosY-DY;
  mapchange();
}

function mapchange_droite(){
  DX=XMax*Vitesse/XActu;
  PosX=PosX-DX;
  mapchange();
}


var flag_up=0;
var flag_down=0;
var flag_left=0;
var flag_right=0;
var flag_hg=0;
var flag_hd=0;
var flag_bg=0;
var flag_bd=0;



function do_hg(){
  if (flag_hg==1){
    mapchange_haut();
    mapchange_gauche();
    setTimeout("do_hg()",timeVitesse)
  }
}

function fl_over_hg(){
  if (flag_hg==0){
    fl1=document.getElementById('fl_hg1'); 
    fl1.style.opacity=.4;
    fl2=document.getElementById('fl_hg2'); 
    fl2.style.opacity=.4;
    flag_hg=1;
    do_hg();  
  }
}

function fl_out_hg(){
  flag_hg=0;
  fl1=document.getElementById('fl_hg1'); 
  fl1.style.opacity=.8;
  fl2=document.getElementById('fl_hg2'); 
  fl2.style.opacity=.8;
}

function do_hd(){
  if (flag_hd==1){
    mapchange_haut();
    mapchange_droite();
    setTimeout("do_hd()",timeVitesse)
  }
}

function fl_over_hd(){
  if (flag_hd==0){
    fl1=document.getElementById('fl_hd1'); 
    fl1.style.opacity=.4;
    fl2=document.getElementById('fl_hd2'); 
    fl2.style.opacity=.4;
    flag_hd=1;
    do_hd();  
  }
}

function fl_out_hd(){
  flag_hd=0;
  fl1=document.getElementById('fl_hd1'); 
  fl1.style.opacity=.8;
  fl2=document.getElementById('fl_hd2'); 
  fl2.style.opacity=.8;
}




function do_bg(){
  if (flag_bg==1){
    mapchange_bas();
    mapchange_gauche();
    setTimeout("do_bg()",timeVitesse)
  }
}

function fl_over_bg(){
  if (flag_bg==0){
    fl1=document.getElementById('fl_bg1'); 
    fl1.style.opacity=.4;
    fl2=document.getElementById('fl_bg2'); 
    fl2.style.opacity=.4;
    flag_bg=1;
    do_bg();  
  }
}

function fl_out_bg(){
  flag_bg=0;
  fl1=document.getElementById('fl_bg1'); 
  fl1.style.opacity=.8;
  fl2=document.getElementById('fl_bg2'); 
  fl2.style.opacity=.8;
}

function do_bd(){
  if (flag_bd==1){
    mapchange_bas();
    mapchange_droite();
    setTimeout("do_bd()",timeVitesse)
  }
}

function fl_over_bd(){
  if (flag_bd==0){
    fl1=document.getElementById('fl_bd1'); 
    fl1.style.opacity=.4;
    fl2=document.getElementById('fl_bd2'); 
    fl2.style.opacity=.4;
    flag_bd=1;
    do_bd();  
  }
}

function fl_out_bd(){
  flag_bd=0;
  fl1=document.getElementById('fl_bd1'); 
  fl1.style.opacity=.8;
  fl2=document.getElementById('fl_bd2'); 
  fl2.style.opacity=.8;
}




function do_up(){
  if (flag_up==1){
    mapchange_haut();
    setTimeout("do_up()",timeVitesse)
  }
}

function fl_over_up(){
  if (flag_up==0){
    fl=document.getElementById('fl_haut'); 
    fl.style.opacity=.4;
    flag_up=1;
    do_up();  
  }
}

function fl_out_up(){
  flag_up=0;
  fl=document.getElementById('fl_haut'); 
  fl.style.opacity=.8;
}

function do_down(){
  if (flag_down==1){
    mapchange_bas();
    setTimeout("do_down()",timeVitesse)
  }
}

function fl_over_down(){
  if (flag_down==0){
    fl=document.getElementById('fl_bas'); 
    fl.style.opacity=.4;
    flag_down=1;
    do_down();  
  }
}

function fl_out_down(){
  flag_down=0;
  fl=document.getElementById('fl_bas'); 
  fl.style.opacity=.8;
}


function do_left(){
  if (flag_left==1){
    mapchange_gauche();
    setTimeout("do_left()",timeVitesse)
  }
}

function fl_over_left(){
  if (flag_left==0){
    fl=document.getElementById('fl_gauche'); 
    fl.style.opacity=.4;
    flag_left=1;
    do_left();  
  }
}

function fl_out_left(){
  flag_left=0;
  fl=document.getElementById('fl_gauche'); 
  fl.style.opacity=.8;
}


function do_right(){
  if (flag_right==1){
    mapchange_droite();
    setTimeout("do_right()",timeVitesse)
  }
}

function fl_over_right(){
  if (flag_right==0){
    fl=document.getElementById('fl_droite'); 
    fl.style.opacity=.4;
    flag_right=1;
    do_right();  
  }
}

function fl_out_right(){
  flag_right=0;
  fl=document.getElementById('fl_droite'); 
  fl.style.opacity=.8;
}




var dragdroppointeur=0;
var dragdropmap=0;
var pos_mouse_x_init=0;
var pos_mouse_y_init=0;
var pos_pointeur_x_init=0;
var pos_pointeur_y_init=0;
var pos_map_x_init=0;
var pos_map_y_init=0;

function pointeur_drag(){
  pos_mouse_x_init=pos_mouse_x;
  pos_pointeur_x_init=objpointeur.offsetLeft;
  dragdroppointeur=1;
  hide_num();
}

function map_drag(){
  pos_map_x_init=pos_mouse_x;
  pos_map_y_init=pos_mouse_y;
  dragdropmap=1;
  hide_num();
  InfoActive=0;
}


function action_mouse_move(e){
  mouse_pos(e);
  if (dragdroppointeur==1){;
    newpos=pos_pointeur_x_init-pos_mouse_x_init+pos_mouse_x;
    if (newpos>133) newpos=133;
    if (newpos<5) newpos=5;
    facteurloupe=newpos-5;
    XActu=Math.floor(XMin+(facteurloupe/128)*(XMax-XMin));
    YActu=Math.floor(YMin+(facteurloupe/128)*(YMax-YMin));
    objmap.style.width=XActu+'px';
    objmap.style.height=YActu+'px';
    objpointeur.style.left=newpos+'px';
    mapchange();
  }
  if (dragdropmap==1){;

    npx=pos_mouse_x;
    npy=pos_mouse_y;

    nx=Math.floor((npx-pos_map_x_init)*XMax/XActu);
    ny=Math.floor((npy-pos_map_y_init)*YMax/YActu);

    pos_map_x_init=npx;
    pos_map_y_init=npy;

    PosX=PosX-nx;
    PosY=PosY-ny;
    mapchange();

  }

  return 0;
}

function action_mouse_drop(e){
  dragdroppointeur=0;
  dragdropmap=0;
  show_num();
  mapchange();
}

function hide_num_noinfo(){
    hide_num();
  InfoActive=0;
}


function gonum(a){
  PosX =num_x[a]/2;
  PosY =num_y[a]/2;
  /*facteurloupe=128;*/
  XActu=Math.floor(XMin+(facteurloupe/128)*(XMax-XMin));
  YActu=Math.floor(YMin+(facteurloupe/128)*(YMax-YMin));
  objmap.style.width=XActu+'px';
  objmap.style.height=YActu+'px';
  newpos=facteurloupe+5;
  objpointeur.style.left=newpos+'px';
  mapchange();
  overnum(a);
}




function overnum(idnum){

    change_pos_un_num(idnum);
    if (InfoActive>0){
      if (InfoActive!=idnum){

	outnum(InfoActive);
      }
    }

    if (idnum<10) {
	strnum='0'+idnum;
    } else {
	strnum=''+idnum;
    }

    info=tab_objinfo[idnum]
    
    posxnum=num_x[idnum]/2;
    posynum=num_y[idnum]/2;
    XPropnum=CentreX+(XActu*posxnum/XMax)-XProp;
    YPropnum=CentreY+(YActu*posynum/YMax)-YProp;

    XPropinfo=XPropnum-120;
    YPropinfo=-YPropnum+60;

    XPropbinfo=XPropnum-2;
    YPropbinfo=-YPropnum;


    info.style.left=XPropinfo+'px';
    info.style.bottom=YPropinfo+'px';
    info.style.display='block';


    binfo.style.left=XPropbinfo+'px';
    binfo.style.bottom=YPropbinfo+'px';
    binfo.style.display='block';
 
    objnum=tab_objnum[idnum];
    objnum.style.display='none';

    InfoActive=idnum;

}

function outnum(idonum){
    change_pos_un_num(idonum);
    InfoActive=0;

    if (idonum<10) {
	strnum='0'+idonum;
    } else {
	strnum=''+idonum;
    }
    info=tab_objinfo[idonum]
    info.style.display='none';
    binfo.style.display='none';
    objnum=tab_objnum[idonum];
    objnum.style.display='block';
}


function mapready(){
  for (var idnum=1;idnum<=nbnum;idnum+=1) {
    if (idnum<10) {
	strnum='0'+idnum;
    } else {
	strnum=''+idnum;
    }
    tab_objnum[idnum]=document.getElementById('num_'+strnum);
    tab_objinfo[idnum]=document.getElementById('num_info_'+strnum);
  }
  binfo=document.getElementById('bar_info');
  objmap=document.getElementById('imgmap');
  objpointeur=document.getElementById("pointeur");

  newpos=facteurloupe+5;
  objpointeur.style.left=newpos+'px';

  XActu=Math.floor(XMin+(facteurloupe/128)*(XMax-XMin));
  YActu=Math.floor(YMin+(facteurloupe/128)*(YMax-YMin));

  objmap.style.width=XActu+'px';
  objmap.style.height=YActu+'px';
  objload=document.getElementById('loading');

  mapchange();
  show_num();

  objmap.style.display='block';
  objload.style.display='none';
  document.onmousemove = action_mouse_move;
  document.onmouseup = action_mouse_drop;


}

