/* technique classique */
ul.nav_conteneur_normales_1 li{
  position: relative;
  cursor: pointer;
  color: /*+COL:4N+*/;
}
ul.nav_conteneur_normales_1 ul{
  position: relative;
}

li.nav_element_normales_2 div.nav_popup_normales_2 {
  display: none;
}
li.nav_element_normales_2:hover div.nav_popup_normales_2 {
  display: block;
}
div.nav_popup_normales_2 {
  position: absolute;
  z-index: 200;
}

/* dimention */

div.nav_popup_normales_2 {
  width: /*+DISPO:WNAV+*/px;
  left: /*+DISPO:WNAV+*/px;
  top: -1px; /* border-top patch */
}

ul.nav_conteneur_normales_1 li {
line-height: 21px;
}

li.nav_element_normales_2 {
padding-left: 21px;
}

div.nav_popup_normales_2 li.nav_element_normales_3 {
padding-left: 3px;
}

li.nav_element_normales_3 {
padding-left: 3px;
}


/* background et bordure + texte ?*/

ul.nav_conteneur_normales_1 {
border-bottom: 1px solid /*+COL:1S+*/;
}

li.nav_element_normales_2 {
background-image: url(/*+IMG:flecha1.png+*/);
background-position: left center;
background-repeat: no-repeat;
background-color: /*+COL:1C+*/;
border-top: 1px solid /*+COL:1S+*/;
}

li.nav_element_normales_2:hover {
background-color: /*+COL:1N+*/;
}

li.nav_element_normales_2.actif {
background-color: /*+COL:1N+*/;
background-image: url(/*+IMG:flecha2.png+*/);
background-position: left center;
background-repeat: no-repeat;
}

li.nav_element_normales_3 {
background-color: /*+COL:2C+*/;
border-top: 1px solid /*+COL:2N+*/;
}

li.nav_element_normales_3.actif {
background-color: /*+COL:2N+*/;
}

li.nav_element_normales_3:hover {
background-color: /*+COL:2N+*/;
}

div.nav_popup_normales_2 {
border-left: 1px solid /*+COL:2N+*/;
border-right: 1px solid /*+COL:2N+*/;
border-bottom: 1px solid /*+COL:2N+*/;
}
div.nav_popup_normales_2 li.nav_element_normales_3 {
background-color: /*+COL:2C+*/;
border-top: 1px solid /*+COL:2N+*/;
}
div.nav_popup_normales_2 li.nav_element_normales_3:hover {
background-color: /*+COL:2N+*/;
}
