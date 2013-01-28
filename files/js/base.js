function show(id){
  var d = document.getElementById(id);
  d.style.display='block';
}

function hide(id){
  var d = document.getElementById(id);
  d.style.display='none';
}

function vide(id){
  var d = document.getElementById(id);
  d.innerHTML='';
}

function swapvisu(id){
  var d = document.getElementById(id);
  if (d){
    if (d.style.display=='block'){
        d.style.display='none';
    } else if (d.style.display=='none'){
        d.style.display='block';
    } else if (d.className.search('invisible')!=-1){
        d.style.display='block';
    } else {
        d.style.display='none';
    }
  }
}

function getObjetByEvent(e){
      var targ;
      if (!e)
	  {
	      e=window.event;
	  }
      if (e.target)
	  {
	      targ=e.target;
	  }
      else if (e.srcElement)
	  {
	      targ=e.srcElement;
	  }
      if (targ.nodeType==3)
	  {
	      targ = targ.parentNode;
	  }
      return targ;
}


function changecolor(e,color) {
  if (color==1){ color='#99CC99';}
  if (color==2){ color='#CCFFCC';}
  if (color==0){ color='#FFFFFF';}
  obj=getObjetByEvent(e);
  if (obj.tagName=='DT') obj.style.backgroundColor=color;
  if (obj.tagName=='LI') obj.style.backgroundColor=color;
  if (obj.tagName=='A'){
    obj.parentNode.style.backgroundColor=color;
  } 
}

function resizecentre(){
    var ce = document.getElementById("centre");
    l=ce.offsetHeight+'px';
    ce.style.height=l;
    ce.style.minHeight=l;
    ce.style.height="3000px";
    ce.style.minHeight="3000px";

}

var xmlhttp;

function http_url_datas_to_fct(url,fct)
{
    xmlhttp=null;
    if (window.XMLHttpRequest)
	{
	    xmlhttp=new XMLHttpRequest();
	}
    else if (window.ActiveXObject)
	{
	    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	}
    if (xmlhttp!=null)
	{
	    xmlhttp.onreadystatechange=fct;
	    xmlhttp.open("GET",url,true);
	    xmlhttp.send(null);
	}
    else
	{
	    alert(TextTrad[0]);
	}
}

var base_url=document.getElementById('baseurl').href;

if (base_url.substring(base_url.length-1,base_url.length-0)=='/'){
    base_url=base_url.substring(0,base_url.length-1)
}

function recup_http_url_datas()
{
    if (xmlhttp.readyState==4)
	{
	    if (xmlhttp.status==200)
		{
		    return xmlhttp.responseText;
		}
	    else
		{
		    alert(TextTrad[1] + xmlhttp.statusText);
                    return 0;
		}
	}
    else {
        return 0;
    }
}


function initialisation(){
    for (j in initialisation_js){
	initialisation_js[j]();
    }
}

var initialisation_js=Array();
window.onload=initialisation;

