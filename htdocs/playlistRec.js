
var asyncRequest;
var refreshRequest;
var playlistRequest;
var recommendedRequest;
var numSelected = 0;
var oneIsPlaying = '';

function start(){
    var baseURL=window.location.href;
    var splitURL = baseURL.split('=',2);
    var code = splitURL[1];
    var myurl = "http://localhost:8080/main.html";
    var mysecret = "decd57a138e64e5c9ff46d742a4428aa";
    var myid = "56a50cf4ff574e438f3e1858604a780a";
    var Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/++[++^A-Za-z0-9+/=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/\r\n/g,"n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}
    
    var encodedScret = Base64.encode(mysecret);
    var encodedId = Base64.encode(myid);
    console.log("Code is: "+code);
    var url = "https://accounts.spotify.com/api/token";
    var data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": myurl,
    };

    try
    {
        asyncRequest = new XMLHttpRequest();
        asyncRequest.addEventListener(
            "readystatechange", processResponse, false); 
        asyncRequest.open('POST','http://127.0.0.1:5000/start',true);
        asyncRequest.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
        asyncRequest.send("code="+code);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}

function getRefresh()
{
    try
    {
        refreshRequest = new XMLHttpRequest();
        refreshRequest.addEventListener(
            "readystatechange", setRefresh, false); 
        refreshRequest.open('POST','http://127.0.0.1:5000/refresh',true);
        refreshRequest.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
        refreshRequest.send(null);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}

function setRefresh()
{
    if ( refreshRequest.readyState == 4 && refreshRequest.status == 200)
    {
        //document.getElementById("text").innerHTML="Refresh Token: "+this.responseText;
    }
}

function processResponse()
{
    console.log("ready state: "+asyncRequest.readyState+ " status: "+asyncRequest.status);
    if ( asyncRequest.readyState == 4 && asyncRequest.status == 200)
    {
        var data = JSON.parse(asyncRequest.responseText);
        var username = data['username'];
        var playlists = data['playlists'];
        document.getElementById("h1").innerHTML=username+"'s Playlists";
        setPlaylists(playlists);
    }
    return null;
}

function getRecommended()
{
    try
    {
        recommendedRequest = new XMLHttpRequest();
        recommendedRequest.addEventListener(
            "readystatechange", setRecommended, false); 
        recommendedRequest.open('GET','http://127.0.0.1:5000/playRec',true);
        recommendedRequest.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
        recommendedRequest.send(null);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}
function setRecommended(e)
{
    if(recommendedRequest.readyState == 4 && recommendedRequest.status == 200)
    {
        document.getElementById('but').style.visibility = 'visible';
        target = e.target;
        response = target.responseText;
        //console.log(response);
        var recommendedJson = JSON.parse(response);
        var table = document.getElementById("recommendedTable");
        table.setAttribute("style","visibility: visible;");

        while(table.hasChildNodes())
        {
            table.removeChild(table.firstChild);
        }
        var count = 0;
        for(var i=0;i<recommendedJson['tracks'].length;i++)
        {
            var row= table.insertRow(count);
            row.setAttribute("class","tr");
            for(var j=0;j<4;j++)
            {
                var cell0 = row.insertCell(j);
                cell0.setAttribute("class","td");
                var name = recommendedJson['tracks'][i]['name']+" - "+
                    recommendedJson['tracks'][i]['album']['artists'][0]['name'];
                var src = recommendedJson['tracks'][i]['album']['images'][2]['url'];
                var audioId = recommendedJson['tracks'][i]['name']+i+'audio';
                var audioSrc = recommendedJson['tracks'][i]['preview_url'];
                var imgId = recommendedJson['tracks'][i]['name']+i;
                var div = createBox(src,name, audioSrc, audioId, imgId);
                cell0.appendChild(div);
                console.log(cell0.childNodes[0].id);
                i++;
            }
            count++;
        }
    document.documentElement.setAttribute('style','height: 100%;');
       
    }
    

}



function playPreview(e)
{
    target = e.target;
    var audio = target.childNodes[0];
    if(audio.getAttribute("src") == 'null')
    {
        console.log("No Src");
        return;
    }
    if(oneIsPlaying != '' && oneIsPlaying !=audio.getAttribute('id'))
    {
        console.log("one Already Playing");
        return;
    }
    var isPlaying = audio.getAttribute('isplaying');
    if(isPlaying=='true')
    {
        audio.pause();
        audio.setAttribute('isplaying','false');
        oneIsPlaying = '';
    }
    else
    {
        audio.play();
        audio.setAttribute('isplaying','true');
        oneIsPlaying = audio.getAttribute('id');
    }
    
}




function createBox(src, title, audioSrc, audioId, imgId)
{
    var div = document.createElement("div");
    div.id = title;
    div.setAttribute("isSelected", "false");
    div.style.borderRadius = "55px";
    div.style.width = "200px";
    div.style.height = "240px";
    div.style.padding = "20px";
    div.style.paddingTop = "30px";
    div.style.textAlign = "center";
    div.style.marginLeft = "auto";
    div.style.marginRight = "auto";
    div.style.marginTop = "auto";
    div.style.marginBottom = "auto";
    div.style.display = "block";

    var img = document.createElement("img");
    img.src = src;
    img.style.width = "70%";
    img.style.height = "70%";
    img.style.marginLeft = "auto";
    img.style.marginRight = "auto";
    img.style.display = "block";
    img.setAttribute("id","img"+title);
    img.setAttribute("onerror","this.src=\"alt.png\"");
    img.style.userSelect = "none";

    var audio = document.createElement('audio');
    audio.id = audioId;
    audio.src = audioSrc;
    audio.setAttribute('type','audio/mpeg');
    audio.setAttribute('isplaying','false');
    img.appendChild(audio);
    img.addEventListener('click',function(){playPreview(event)},false);

    div.appendChild(img);
    var text = document.createElement("h4");
    text.style.marginTop = "5%";
    text.innerHTML = title;
    text.setAttribute("id","txt"+title);
    text.style.userSelect = "none";
    div.appendChild(text);
    div.addEventListener("mouseenter", function () {bigBox(event)}, false);
    div.addEventListener("mouseleave",function() {littleBox(event)},false);
    div.addEventListener("mousedown", function() {littleBox(event)}, false);
    div.addEventListener("mouseup", function () {selectBox(event)}, false);
    div.style.userSelect = "none";

    
    return div;
}

function bigBox(e)
{
    target = e.target;
    if(target.id.substring(0,3) == "img")
    {
        return;
    }
    if(target.id.substring(0,3) == "txt")
    {
        target = document.getElementById(target.id.substring(3));
    }
    var selected = target.getAttribute("isSelected");
    if(selected == "false")
    {
        target.style.backgroundColor = "rgb(56, 56, 56)";
    }
   // target.style.width="185px";
    //target.style.height="195px";
}

function selectBox(e)
{
    target = e.target;
    if(target.id.substring(0,3) == "img")
    {
        return;
    }
    if(target.id.substring(0,3) == "txt")
    {
        target = document.getElementById(target.id.substring(3));
    }
    var selected = target.getAttribute("isSelected");
    console.log(selected);
    if(selected == "true")
    {
        console.log("deselect");
        target.style.backgroundColor = "black";
        //target.removeAttribute("isSelected");
        target.setAttribute("isSelected","false");
        numSelected--;
    }
    else
    {
        console.log("select");
        target.style.backgroundColor = "rgb(56, 56, 56)";
        //target.removeAttribute("isSelected");
        target.setAttribute("isSelected", "true");
        numSelected++;
    }
    if(numSelected>0)
    {
        document.getElementById("submitButton").style.visibility = "visible";
    }
    if(numSelected<=0)
    {
        document.getElementById("submitButton").style.visibility = "hidden";
    }
}


function littleBox(e)
{
    target = e.target;
    if(target.id.substring(0,3) == "img")
    {
        return;
    }
    if(target.id.substring(0,3) == "txt")
    {
        target = document.getElementById(target.id.substring(3));
    }
    
    var selected = target.getAttribute("isSelected");
    if(selected == "false")
    {
        target.style.backgroundColor = "black";
    }
    //target.style.width="175px";
    //target.style.height="185px";
}



function test()
{
    console.log("clearing table");
    var table = document.getElementById("recommendedTable");
    var selectedPlaylists = new Array();
    var count = 0;
    for(var i=0;i<table.rows.length;i++)
    {
        var row= table.rows[i];
        for(var j=0;j<row.cells.length;j++)
        {
            var cell = table.rows[i].cells[j];
            var div = cell.childNodes[0];
            if(div.getAttribute("isSelected") == "true")
            {
                div.style.backgroundColor = "black";
                selectedPlaylists.push(cell.childNodes[0].id);
                div.setAttribute("isSelected", "false");
                console.log("adding "+cell.childNodes[0].id);
            }
            
           
        }
    }
    

}

