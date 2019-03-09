
//mouse_timer
var mouseStartTime = Date.now();

function mouseStartTimer() {
    mouseStartTime = Date.now();
    
}

function mouseStopTimer() {
    var elapsedTime = Date.now() - mouseStartTime;
    return elapsedTime;
}

//keyboard_timer
var startTime = Date.now();
var jumpStartTime = Date.now();
var index = 0;
var keyArray = [];
var mouseEvents = [];
function startTimer() {
    var jumpElapsedTime = Date.now() - jumpStartTime;
    jumpMillis = jumpElapsedTime;
    startTime = Date.now();
    return jumpMillis;
}

function stopTimer() {
    var elapsedTime = Date.now() - startTime;
    millis = elapsedTime;
    jumpStartTime = Date.now();
    return millis;
}

function checkFont(strFamily) {
    var objDiv = document.createElement('div');
    objDiv.setAttribute("style", "font-family: "+strFamily+";");
    objDiv.appendChild(document.createTextNode('FONT TEST'));
    
    if (window.getComputedStyle) {
        console.log(window.getComputedStyle(objDiv).getPropertyValue('font-family'));
        return window.getComputedStyle(objDiv, null).getPropertyValue('font-family') === strFamily;
    }
    return objDiv.currentStyle.fontFamily === strFamily;
}
var ele = document.getElementsByClassName('.signature');
// var ele = document.getElementById('test');
ele.addEventListener('keydown', function() {
    jumpTicks = startTimer();
    keyArray[index] = {};
    keyArray[index]["id"] = this.id;
    keyArray[index]["keyCode"] = event.keyCode;
    keyArray[index]["jumpTicks"] = jumpTicks;
    keyArray[index]["keyUpTicks"] = 0;
}, false);

var c=document.getElementById("myCanvas");
var ctx=c.getContext("2d");
ctx.shadowOffsetX = 0.2;
ctx.shadowOffsetY = 0.3;
ctx.shadowColor = 'black';
ctx.shadowBlur = 9.0;
ctx.beginPath();
ctx.moveTo(50,20);
ctx.bezierCurveTo(20, 30, 150, 80, 150, 100);
ctx.bezierCurveTo(150, 30, 150, 60, 50, 100);
ctx.stroke();


var gradient = ctx.createLinearGradient(10, 0, 500, 0);
gradient.addColorStop(0, 'red');
gradient.addColorStop(1 / 6, 'orange');
gradient.addColorStop(2 / 6, 'yellow');
gradient.addColorStop(3 / 6, 'green');
gradient.addColorStop(4 / 6, 'blue');
gradient.addColorStop(5 / 6, 'indigo');
gradient.addColorStop(1, 'violet');
ctx.font="20px Arial";
ctx.fillStyle = gradient;
ctx.fillText("Cwm fjordbank glyphs vext quiz, &#x2660;",10,50);
var canvas_signature = c.toDataURL();
ctx.clearRect(0, 0, c.width, c.height);

// alert(signature);
// console.log(signature);
// var shaObj = new jsSHA("SHA-256",signature,"HEX");

// alert(shaObj);

var navi_keys = {};
navi_keys["cookieEnabled"] = navigator.cookieEnabled;
navi_keys["appName"] = navigator.appName;
navi_keys["product"] = navigator.product;
navi_keys["appCodeName"] = navigator.appCodeName;
navi_keys["appVersion"] = navigator.appVersion;
navi_keys["userAgent"] = navigator.userAgent;
navi_keys["platform"] = navigator.platform;
navi_keys["onLine"] = navigator.onLine;
navi_keys["javaEnabled"] = navigator.javaEnabled();
navi_keys["height"] = window.screen.availHeight;
navi_keys["width"] = window.screen.availWidth;
navi_keys["localStorage"] = window.localStorage || 0;
navi_keys['colorDepth'] = window.screen.colorDepth;
navi_keys['doNotTrack'] = window.navigator.doNotTrack;
navi_keys['hardwareConcurrency'] = window.navigator.hardwareConcurrency;
var userLang = navigator.language || navigator.userLanguage;
navi_keys['language'] = userLang;
navi_keys["canvas"] = canvas_signature;
var d = new Date();
navi_keys["timezone"] = d.getTimezoneOffset();
navi_keys['']

var canvas = document.createElement('canvas');
// We get a WebGL drawing context to get access to the functions of the API
var ctx = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
webGLVendor = "";
webGLRenderer = "";
// If the debug extension is present , we collect the information
// If not , we say it is not supported
if(ctx.getSupportedExtensions().indexOf("WEBGL_debug_renderer_info") >= 0) {
    var debugExt = ctx.getExtension('WEBGL_debug_renderer_info') ;
    webGLVendor = ctx.getParameter(debugExt.UNMASKED_VENDOR_WEBGL);
    webGLRenderer = ctx.getParameter(debugExt.UNMASKED_RENDERER_WEBGL);
} else {
    webGLVendor = " Not supported ";
    webGLRenderer = "Not supported ";
}
navi_keys["productSub"] = navigator.productSub;
navi_keys["maxTouchPoints"] = navigator.maxTouchPoints;
navi_keys["connection_downlink"] = "";
navi_keys["connection_effectiveType"] = "";
navi_keys["connection_rtt"] = "";
if (navigator.connection != undefined) {
    navi_keys["connection_downlink"] = navigator.connection['downlink'];
    navi_keys["connection_effectiveType"] = navigator.connection['effectiveType'];
    navi_keys["connection_rtt"] = navigator.connection['rtt'];
}
navi_keys["webGLVendor"] = webGLVendor;
navi_keys["webGLRenderer"] = webGLRenderer;
// navi_keys["plugins"] = navigator.plugins;
var plugins = [];
for (var i in navigator.plugins) {
    plugins.push(navigator.plugins[i].name);
}
navi_keys["plugins"] = plugins;
var mimeTypes = [];
for (var i in navigator.mimeTypes) {
    mimeTypes.push(navigator.mimeTypes[i].type);
}
navi_keys["mimetypes"] = mimeTypes;
navi_keys["vendor"] = navigator.vendor;
var fonts = [];
for (var font in ["Agency FB","Arial Black","Arial","Bauhaus 93","Bell MT","Bodoni MT","Bookman Old Style","Broadway","Calibri Light","Calibri","Californian FB","Cambria Math","Cambria","Candara","Castellar","Centaur","Century Gothic","Colonna MT","Comic Sans MS","Consolas","Constantia","Copperplate Gothic Light","Corbel","Courier New","Ebrima","Engravers MT","Forte","Franklin Gothic Heavy","Franklin Gothic Medium","French Script MT","Gabriola","Georgia","Gigi","Goudy Old Style","Haettenschweiler","Harrington","Impact","Informal Roman","Lucida Bright","Lucida Console","Lucida Fax","Lucida Sans Unicode","MS Gothic","MS PGothic","MS Reference Sans Serif","MS UI Gothic","MV Boli","Magneto","Malgun Gothic","Marlett","Matura MT Script Capitals","Microsoft Himalaya","Microsoft JhengHei","Microsoft New Tai Lue","Microsoft PhagsPa","Microsoft Sans Serif","Microsoft Tai Le","Microsoft YaHei","Microsoft Yi Baiti","MingLiU-ExtB","MingLiU_HKSCS-ExtB","Mongolian Baiti","NSimSun","Niagara Solid","PMingLiU-ExtB","Palace Script MT","Palatino Linotype","Papyrus","Perpetua","Playbill","Rockwell","Segoe Print","Segoe Script","Segoe UI Light","Segoe UI Semibold","Segoe UI Symbol","Segoe UI","Showcard Gothic","SimSun","SimSun-ExtB","Snap ITC","Sylfaen","Symbol","Tahoma","Times New Roman","Trebuchet MS","Verdana","Vladimir Script","Webdings","Wide Latin","Wingdings"]) {
    if (checkFont(font)) {
        fonts.push(font);
    }
}
navi_keys['fonts'] = fonts;
var emp_form = document.getElementById('emp_form');
emp_form.innerHTML += "<input type='hidden' name='navigator' id='navigator' value='" + JSON.stringify(navi_keys) + "'/>";
// $("#emp_form").append();

var ele = document.getElementsByClassName('.signature');
// var ele = document.getElementById('test');
ele.addEventListener('keydown', function() {
        ticks = stopTimer();
    if (keyArray[index] == null) {
        jumpTicks = startTimer();
        keyArray[index] = {};
        keyArray[index]["id"] = this.id;
        keyArray[index]["keyCode"] = event.keyCode;
        keyArray[index]["keyUpTicks"] = ticks;
        keyArray[index]["jumpTicks"] = jumpTicks;
    } else {
        keyArray[index]["keyUpTicks"] = ticks;
    }
    var mouseEventsHandler = document.getElementById('mouseEvents');
    if (mouseEventsHandler.value == undefined){
        var emp_form = document.getElementById('emp_form');
        emp_form.innerHTML += "<input type='hidden' name='mouseEvents' id='mouseEvents' value='" + JSON.stringify(mouseEvents) + "'/>";
    } else {
        mouseEventsHandler.value = JSON.stringify(mouseEvents);
    }
    index += 1;
}, false);


// $(".signature").keyup(function(event) {

//     if ($("#mouseEvents").val() == undefined) {
//         $("#emp_form").append();
//     } else {
//         $("#mouseEvents").val(JSON.stringify(mouseEvents));
//     }
//     index += 1;
    // console.log(String.fromCharCode(event.keyCode));
    // console.log(keyArray);
    // console.log(navigator.userAgent);
    // console.log(navigator.plugins);
    // console.log(navigator);
    // console.log('ticks '+ticks);
// });
var mouse_sig = document.getElementsByClassName('mouse_signature');
mouse_sig.onmousemove = function(event) {
    mouseEvents.push({'x':event.clientX,'y':event.clientY,'timestamp':Date.now()});
    var keyArrayField = document.getElementById('keyArrayField');
    if (keyArrayField.value == undefined) {
        var emp_form = document.getElementById('emp_form');
        emp_form.innerHTML += "<input type='hidden' name='keyArray' id='keyArrayField' value='" + JSON.stringify(keyArray) + "'/>";
    } else {
        keyArrayField.value = JSON.stringify(keyArray);
    }
}
// $(".mouse_signature").mousemove(function(event) {
    
//     if ($("#keyArrayField").val() == undefined) {
//         $("#emp_form").append();
//     } else {
//         $("#keyArrayField").val();
//     }
// });