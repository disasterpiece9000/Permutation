
var asyncRequest;
var refreshRequest;
var playlistRequest;
var playlistSelectRequest;
var recommendedRequest;
var numSelected = 0;

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

function getSelectedPlaylist(playlist)
{
    playlist = playlist.target;
    playlist = playlist.id;
    if(playlist.substring(0,3)=="img" || playlist.substring(0,3)=="txt")
    {
        playlist = playlist.substring(3);
    }
    try
    {
        playlistSelectRequest = new XMLHttpRequest();
        playlistSelectRequest.addEventListener(
            "readystatechange", setSelectedPlaylist, false);
        playlistSelectRequest.open('POST', 'http://127.0.0.1:5000/confirm', true);
        playlistSelectRequest.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
        playlistSelectRequest.send("playlist="+playlist);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}

function setSelectedPlaylist()
{
    console.log("loading page");
    if (playlistSelectRequest.readyState == 4 && playlistSelectRequest.status == 200)
    {
        window.location.href = "confirm.html";
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
        recommendedRequest.open('GET','http://127.0.0.1:5000/recommended',true);
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
        for(var i=0;i<recommendedJson['tracks'].length;i++)
        {
            var row = table.insertRow(i);
            var cell0 = row.insertCell(0);
            var cell1 = row.insertCell(1);
            cell1.setAttribute("style","user-select: none;");
            cell0.setAttribute("align","center");
            cell0.setAttribute("valign","bottom");
            var img = document.createElement('img');
            var altImg = document.createElement('img');
            altImg.src = "alt.png";
            img.src=recommendedJson['tracks'][i]['album']['images'][2]['url'];
            img.setAttribute("onerror","this.src='alt.png';");
            img.setAttribute('id',recommendedJson['tracks'][i]['name']+i);
            cell0.appendChild(img);
            cell1.innerHTML=recommendedJson['tracks'][i]['name']+" - "+
                recommendedJson['tracks'][i]['album']['artists'][0]['name'];
            var audio = document.createElement('audio');
            audio.id = recommendedJson['tracks'][i]['name']+i+'audio';
            audio.src=recommendedJson['tracks'][i]['preview_url'];
            audio.setAttribute('type','audio/mpeg');
            audio.setAttribute('isplaying','false');
            //audio.controls = 'controls';
            cell0.appendChild(audio);
            cell0.addEventListener('click',function(){playPreview(event)},false);

        }
    }
    

}



function playPreview(e)
{
    target = e.target;
    name = target.id+'audio';
    console.log('element id:'+name);
    var audio = document.getElementById(name);
    var isPlaying = audio.getAttribute('isplaying');
    if(isPlaying=='true')
    {
        audio.pause();
        audio.setAttribute('isplaying','false');
    }
    else
    {
        audio.play();
        audio.setAttribute('isplaying','true');
    }
    
}



function setPlaylists(response)
{
    var playlists = response.split(";");
    var table = document.getElementById("playlistTable");
    
    while(table.hasChildNodes())
    {
        table.removeChild(table.firstChild);
    }
    var count = 0;
    for(var i=0;i<playlists.length;i++)
    {
        var row= table.insertRow(count);
        row.setAttribute("class", "tr");
        for(var j=0;j<4;j++)
        {
            var cell0 = row.insertCell(j);
            cell0.setAttribute("class", "td");
            var kv = playlists[i].split("|");
            var playlist = kv[0];
            var image = kv[1];
            var div = createBox(image,playlist);
            cell0.appendChild(div);
            console.log(cell0.childNodes[0].id);
            i++;
        }
        count++;
    }
    document.documentElement.setAttribute('style','height: 100%;');
}

function createBox(src, title)
{
    var div = document.createElement("div");
    div.id = title;
    div.setAttribute('class','box');
    div.setAttribute("isSelected", "false");
    div.style.borderRadius = "55px";
    div.style.width = "175px";
    div.style.height = "185px";
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
    
    div.appendChild(img);
    var text = document.createElement("h4");
    text.style.marginTop = "5%";
    text.innerHTML = title;
    text.setAttribute("id","txt"+title);
    text.style.userSelect = "none";
    div.appendChild(text);
    div.addEventListener("mouseenter", function () {bigBox(event)}, false);
    div.addEventListener("mouseleave",function() {littleBox(event)},false);
    div.addEventListener("click" , function() {getSelectedPlaylist(event)}, false);
    //div.addEventListener("mousedown", function() {littleBox(event)}, false);
    //div.addEventListener("mouseup", function () {selectBox(event)}, false);
    div.style.userSelect = "none";
    return div;
}

function bigBox(e)
{
    target = e.target;
    if(target.id.substring(0,3) == "img" || target.id.substring(0,3) == "txt")
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
    if(numSelected>=1)
    {
        return;
    }
    if(target.id.substring(0,3) == "img" || target.id.substring(0,3) == "txt")
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
    if(target.id.substring(0,3) == "img" || target.id.substring(0,3) == "txt")
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
    var table = document.getElementById("playlistTable");
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

function displayDesription(e)
            {
                target = e.target;
                var text = target.innerHTML;
                if(text[0]=="*")
                {
                    text=text.substring(1,text.length-2);
                }
                else
                {
                    text = "* "+text+" *";
                }
                
                target.innerHTML=text;
            }