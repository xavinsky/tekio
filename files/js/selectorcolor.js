// A few configuration settings
var CROSSHAIRS_LOCATION = '/includes/images/interface/colorselector/crosshairs.png';
var HUE_SLIDER_LOCATION = '/includes/images/interface/colorselector/h.png';
var HUE_SLIDER_ARROWS_LOCATION = '/includes/images/interface/colorselector/position.png';
var SAT_VAL_SQUARE_LOCATION = '/includes/images/interface/colorselector/sv.png';
var PIXEL_LOCATION = '/includes/images/interface/util/pixel.gif';

function vers_un(x){
    return x+((1-x)*.5);
}
function makeColorSelector3(inputBox){
    var rgb, hsv

    function colorChanged()
    {
        var hex = rgbToHex(rgb.r, rgb.g, rgb.b);
        var hueRgb = hsvToRgb(hsv.h, 1, 1);
        var hueHex = rgbToHex(hueRgb.r, hueRgb.g, hueRgb.b);
        previewDiv.style.background = hex;
        inputBox.value = hex;
        satValDivIn.style.background = hueHex;
        crossHairs.style.left = ((hsv.v*99)-10).toString() + 'px';
        crossHairs.style.top = (((1-hsv.s)*99)-10).toString() + 'px';
        huePos.style.top = ((hsv.h*99)-2).toString() + 'px';

	hsvtmp=rgbToHsv(rgb.r, rgb.g, rgb.b);
	rgbsombre=hsvToRgb(hsvtmp.h,vers_un(hsvtmp.s),hsvtmp.v/2);
	var hexSombre = rgbToHex(rgbsombre.r, rgbsombre.g, rgbsombre.b);
	/*var hexSombre = rgbToHex(rgb.r*.6, rgb.g*.6, rgb.b*.6);*/
        previewLDiv.style.background = hexSombre;
	LinputBox.value= hexSombre;

	hsvtmp=rgbToHsv(rgb.r, rgb.g, rgb.b);
	rgbclair=hsvToRgb(hsvtmp.h,hsvtmp.s/2,vers_un(hsvtmp.v));
	var hexClair = rgbToHex(rgbclair.r, rgbclair.g, rgbclair.b);
        previewRDiv.style.background = hexClair;
	RinputBox.value= hexClair;


    }
    function rgbChanged()
    {
        hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);
        colorChanged();
    }
    function hsvChanged()
    {
        rgb = hsvToRgb(hsv.h, hsv.s, hsv.v);
        colorChanged();
    }
    function satValDragged(x, y)
    {
        hsv.s = 1-(y/99);
        hsv.v = (x/99);
        hsvChanged();
    }
    function hueDragged(x, y)
    {
        hsv.h = y/99;
        hsvChanged();
    }
    function inputBoxChanged()
    {
        rgb = hexToRgb(inputBox.value, {r: 0, g: 0, b: 0});
        rgbChanged();
    }


    var previewsDiv = document.createElement('div');
    if (inputBox.className=='color3_up'){
	previewsDiv.className = 'previews_up';
    } else {
	previewsDiv.className = 'previews_down';
    }


    var previewLDiv = document.createElement('div');
    previewLDiv.className = 'previewL';
    var pixelPreviewL = document.createElement('img');
    pixelPreviewL.className = 'pixel2Preview';
    pixelPreviewL.galleryImg = false;
    pixelPreviewL.src = PIXEL_LOCATION;
    previewLDiv.appendChild(pixelPreviewL);
    var previewRDiv = document.createElement('div');
    previewRDiv.className = 'previewR';
    var pixelPreviewR = document.createElement('img');
    pixelPreviewR.className = 'pixel2Preview';
    pixelPreviewR.galleryImg = false;
    pixelPreviewR.src = PIXEL_LOCATION;
    previewRDiv.appendChild(pixelPreviewR);

    var LinputBox = document.createElement('input');
    LinputBox.className = 'invisible';
    LinputBox.name=inputBox.name+'S';
    var RinputBox = document.createElement('input');
    RinputBox.className = 'invisible';
    RinputBox.name=inputBox.name+'C';
    inputBox.name=inputBox.name+'N';
    previewsDiv.appendChild(LinputBox);
    previewsDiv.appendChild(RinputBox);

    var previewDiv = document.createElement('div');
    previewDiv.className = 'preview';

    var pixelPreview = document.createElement('img');
    pixelPreview.className = 'pixelPreview';
    pixelPreview.galleryImg = false;
    pixelPreview.src = PIXEL_LOCATION;
    previewDiv.appendChild(pixelPreview);

    previewsDiv.appendChild(previewLDiv);
    previewsDiv.appendChild(previewDiv);
    previewsDiv.appendChild(previewRDiv);



    var satValDiv = document.createElement('div');
    satValDiv.className = 'change_gris';
    previewsDiv.appendChild(satValDiv);
    var satValDivIn = document.createElement('div');
    satValDivIn.className = 'change_gris_in';
    satValDiv.appendChild(satValDivIn);

    var satValImg = document.createElement('img');
    satValImg.className = 'change_gris_img';
    satValImg.galleryImg = false;
    satValImg.src = SAT_VAL_SQUARE_LOCATION;
    var newSatValImg = fixPNG(satValImg);
    satValDivIn.appendChild(newSatValImg);

    var crossHairs = document.createElement('img');
    crossHairs.className = 'change_gris_pointer';
    crossHairs.galleryImg = false;
    crossHairs.src = CROSSHAIRS_LOCATION;
    satValDivIn.appendChild(crossHairs);

    trackDrag(satValDivIn, satValDragged);


    var hueDiv = document.createElement('div');
    hueDiv.className = 'spectre_colors';
    previewsDiv.appendChild(hueDiv);

    var huePositionImg = document.createElement('img');
    huePositionImg.className = 'spectre_colors_pointer';
    huePositionImg.galleryImg = false;
    huePositionImg.src = HUE_SLIDER_ARROWS_LOCATION;
    var huePos = fixPNG(huePositionImg);
    hueDiv.appendChild(huePos);


    var hueSelectorImg = document.createElement('img');
    hueSelectorImg.className = 'spectre_colors_img';
    hueSelectorImg.galleryImg = false;
    hueSelectorImg.src = HUE_SLIDER_LOCATION;
    hueDiv.appendChild(hueSelectorImg);

    trackDrag(hueDiv, hueDragged);

    myAddEventListener(inputBox, 'change', inputBoxChanged);

    var displaydivs='none';

    function switchvue(){
	if (displaydivs=='none'){
	    displaydivs='block';
	} else {
	    displaydivs='none';
	}
	satValDiv.style.display=displaydivs;
	hueDiv.style.display=displaydivs;
    }
	
    myAddEventListener(pixelPreview, 'mouseup', switchvue);
    inputBoxChanged();

    return previewsDiv;

}

function makeColorSelector(inputBox){
    var rgb, hsv
    function colorChanged()
    {
        var hex = rgbToHex(rgb.r, rgb.g, rgb.b);
        var hueRgb = hsvToRgb(hsv.h, 1, 1);
        var hueHex = rgbToHex(hueRgb.r, hueRgb.g, hueRgb.b);
        previewDiv.style.background = hex;
        inputBox.value = hex;
        satValDivIn.style.background = hueHex;
        crossHairs.style.left = ((hsv.v*99)-10).toString() + 'px';
        crossHairs.style.top = (((1-hsv.s)*99)-10).toString() + 'px';
        huePos.style.top = ((hsv.h*99)-2).toString() + 'px';



    }
    function rgbChanged()
    {
        hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);
        colorChanged();
    }
    function hsvChanged()
    {
        rgb = hsvToRgb(hsv.h, hsv.s, hsv.v);
        colorChanged();
    }
    function satValDragged(x, y)
    {
        hsv.s = 1-(y/99);
        hsv.v = (x/99);
        hsvChanged();
    }
    function hueDragged(x, y)
    {
        hsv.h = y/99;
        hsvChanged();
    }
    function inputBoxChanged()
    {
        rgb = hexToRgb(inputBox.value, {r: 0, g: 0, b: 0});
        rgbChanged();
    }


    var previewsDiv = document.createElement('div');
    if (inputBox.className=='color_up'){
	previewsDiv.className = 'previews_up';
    } else {
	previewsDiv.className = 'previews_down';
    }


    var previewDiv = document.createElement('div');
    previewDiv.className = 'preview';

    var pixelPreview = document.createElement('img');
    pixelPreview.className = 'pixelPreview';
    pixelPreview.galleryImg = false;
    pixelPreview.src = PIXEL_LOCATION;
    previewDiv.appendChild(pixelPreview);

    previewsDiv.appendChild(previewDiv);



    var satValDiv = document.createElement('div');
    satValDiv.className = 'change_gris';
    previewsDiv.appendChild(satValDiv);
    var satValDivIn = document.createElement('div');
    satValDivIn.className = 'change_gris_in';
    satValDiv.appendChild(satValDivIn);

    var satValImg = document.createElement('img');
    satValImg.className = 'change_gris_img';
    satValImg.galleryImg = false;
    satValImg.src = SAT_VAL_SQUARE_LOCATION;
    var newSatValImg = fixPNG(satValImg);
    satValDivIn.appendChild(newSatValImg);

    var crossHairs = document.createElement('img');
    crossHairs.className = 'change_gris_pointer';
    crossHairs.galleryImg = false;
    crossHairs.src = CROSSHAIRS_LOCATION;
    satValDivIn.appendChild(crossHairs);

    trackDrag(satValDivIn, satValDragged);


    var hueDiv = document.createElement('div');
    hueDiv.className = 'spectre_colors';
    previewsDiv.appendChild(hueDiv);

    var huePositionImg = document.createElement('img');
    huePositionImg.className = 'spectre_colors_pointer';
    huePositionImg.galleryImg = false;
    huePositionImg.src = HUE_SLIDER_ARROWS_LOCATION;
    var huePos = fixPNG(huePositionImg);
    hueDiv.appendChild(huePos);


    var hueSelectorImg = document.createElement('img');
    hueSelectorImg.className = 'spectre_colors_img';
    hueSelectorImg.galleryImg = false;
    hueSelectorImg.src = HUE_SLIDER_LOCATION;
    hueDiv.appendChild(hueSelectorImg);

    trackDrag(hueDiv, hueDragged);

    myAddEventListener(inputBox, 'change', inputBoxChanged);

    var displaydivs='none';

    function switchvue(){
	if (displaydivs=='none'){
	    displaydivs='block';
	} else {
	    displaydivs='none';
	}
	satValDiv.style.display=displaydivs;
	hueDiv.style.display=displaydivs;
    }
	
    myAddEventListener(pixelPreview, 'mouseup', switchvue);
    inputBoxChanged();

    return previewsDiv;

}

var inputNodesOk=new Array();

function makeColorSelectors(ev)
{
    var inputNodes = document.getElementsByTagName('input');
    var i;
    for (i = 0; i < inputNodes.length; i++)
    {
        var node = inputNodes[i];
	
        if ((node.className == 'color_up') || (node.className == 'color_down'))
        {
	    newnode=true;
	    for (j = 0; j < inputNodesOk.length; j++){
		if (node==inputNodesOk[j]){
		    newnode=false;
		}
	    }
	    if (newnode==true){
		var parent = node.parentNode;
		var prevNode = node.previousSibling;
		var selector = makeColorSelector(node);
		parent.insertBefore(selector, (prevNode ? prevNode.nextSibling : null));
		inputNodesOk.push(node)
            }
        } else if ((node.className == 'color3_up') || (node.className == 'color3_down'))
	{
	    newnode=true;
	    for (j = 0; j < inputNodesOk.length; j++){
		if (node==inputNodesOk[j]){
		    newnode=false;
		}
	    }
	    if (newnode==true){
		var parent = node.parentNode;
		var prevNode = node.previousSibling;
		var selector = makeColorSelector3(node);
		parent.insertBefore(selector, (prevNode ? prevNode.nextSibling : null));
		inputNodesOk.push(node)
            }
	}
    }
}

myAddEventListener(window, 'load', makeColorSelectors);
