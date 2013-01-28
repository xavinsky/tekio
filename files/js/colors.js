
/* FUNCTIONS COLORS */

function hsvToRgb(hue, saturation, value)
{
    var red;
    var green;
    var blue;
    if (value == 0.0)
    {
        red = 0;
        green = 0;
        blue = 0;
    }
    else
    {
        var i = Math.floor(hue * 6);
        var f = (hue * 6) - i;
        var p = value * (1 - saturation);
        var q = value * (1 - (saturation * f));
        var t = value * (1 - (saturation * (1 - f)));
        switch (i)
        {
            case 1: red = q; green = value; blue = p; break;
            case 2: red = p; green = value; blue = t; break;
            case 3: red = p; green = q; blue = value; break;
            case 4: red = t; green = p; blue = value; break;
            case 5: red = value; green = p; blue = q; break;
            case 6: // fall through
            case 0: red = value; green = t; blue = p; break;
        }
    }
    return {r: red, g: green, b: blue};
}

function rgbToHsv(red, green, blue)
{
    var max = Math.max(Math.max(red, green), blue);
    var min = Math.min(Math.min(red, green), blue);
    var hue;
    var saturation;
    var value = max;
    if (min == max)
    {
        hue = 0;
        saturation = 0;
    }
    else
    {
        var delta = (max - min);
        saturation = delta / max;
        if (red == max)
        {
            hue = (green - blue) / delta;
        }
        else if (green == max)
        {
            hue = 2 + ((blue - red) / delta);
        }
        else
        {
            hue = 4 + ((red - green) / delta);
        }
        hue /= 6;
        if (hue < 0)
        {
            hue += 1;
        }
        if (hue > 1)
        {
            hue -= 1;
        }
    }
    return {
        h: hue,
        s: saturation,
        v: value
    };
}

function hexToRgb(hex_string, default_)
{
    if (default_ == undefined)
    {
        default_ = null;
    }
    if (hex_string.substr(0, 1) == '#')
    {
        hex_string = hex_string.substr(1);
    }   
    var r;
    var g;
    var b;
    if (hex_string.length == 3)
    {
        r = hex_string.substr(0, 1);
        r += r;
        g = hex_string.substr(1, 1);
        g += g;
        b = hex_string.substr(2, 1);
        b += b;
    }
    else if (hex_string.length == 6)
    {
        r = hex_string.substr(0, 2);
        g = hex_string.substr(2, 2);
        b = hex_string.substr(4, 2);
    }
    else
    {
        return default_;
    }
    
    r = parseInt(r, 16);
    g = parseInt(g, 16);
    b = parseInt(b, 16);
    if (isNaN(r) || isNaN(g) || isNaN(b))
    {
        return default_;
    }
    else
    {
        return {r: r / 255, g: g / 255, b: b / 255};
    }
}

function rgbToHex(r, g, b, includeHash)
{
    r = Math.round(r * 255);
    g = Math.round(g * 255);
    b = Math.round(b * 255);
    if (includeHash == undefined)
    {
        includeHash = true;
    }
    
    r = r.toString(16);
    if (r.length == 1)
    {
        r = '0' + r;
    }
    g = g.toString(16);
    if (g.length == 1)
    {
        g = '0' + g;
    }
    b = b.toString(16);
    if (b.length == 1)
    {
        b = '0' + b;
    }
    return ((includeHash ? '#' : '') + r + g + b).toUpperCase();
}

