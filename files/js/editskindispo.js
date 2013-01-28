function calcnav(){
  d=document.getElementById('marge_elements');
  var marge_elements=parseInt(d.value);
  d=document.getElementById('marge_editor');
  var marge_editor=parseInt(d.value);
  d=document.getElementById('nb_cols');
  var nb_cols=parseInt(d.value);
  d=document.getElementById('width_site');
  var w_site=parseInt(d.value);
  d=document.getElementById('width_editor');
  var w_editor=parseInt(d.value);

  w_nav=w_site-2*marge_editor-w_editor;
  d=document.getElementById('width_nav');
  d.innerHTML='<option value="'+w_nav+'">'+w_nav+'</option>';

  cols="";
  for (var i=1;i<nb_cols+1;i++){
    cols+=i+" col(s) : " + parseInt(w_editor/i) + " = ";
    cols+= parseInt(w_editor/i) -2 * marge_elements + ' + 2*' + marge_elements;     
    cols+= '<br />';
  }
  d=document.getElementById('cols');
  d.innerHTML=cols;

}

function calculpossibilite(){

  var d=document.getElementById('pos_menu');
  var active_menu=true;
  if (d.value=='top'){
      active_menu=false;
  };

  d=document.getElementById('marge_editor');
  var marge_editor=parseInt(d.value);

  d=document.getElementById('nb_cols');
  var nb_cols=parseInt(d.value);
  var divisor=1;  
  if (nb_cols==1){
    divisor=6; /* 1 est possible ici */
  }
  if (nb_cols==2){
    divisor=6; /* 2 est possible ici */
  }
  if (nb_cols==3){
    divisor=6; 
  }
  if (nb_cols==4){
    divisor=12; 
  }
  if (nb_cols==5){
    divisor=60; 
  }


  d=document.getElementById('width_site');
  var w_site=parseInt(d.value);

  base=w_site-2*marge_editor;

  if (active_menu==true){
    mini=Math.floor(base*0.66/divisor)*divisor; 
    maxi=Math.floor(base*0.75/divisor)*divisor;
    var w_options = "";
    for (var i =mini;i<=maxi ; i+=divisor){
      w_options+='<option value="'+i+'">'+i+'</option>';
    } 
    d=document.getElementById('width_editor');
    d.innerHTML=w_options;

  } else {
    newbase= Math.floor(base/divisor)*divisor;
    d=document.getElementById('width_site');
    d.value=newbase+2*marge_editor;
    d=document.getElementById('width_editor');
    w_options='<option value="'+newbase+'">'+newbase+'</option>';
    d.innerHTML=w_options;
  }
  d=document.getElementById('width_nav');
  d.innerHTML='';
  d=document.getElementById('cols');
  d.innerHTML='';
  calcnav();
}
