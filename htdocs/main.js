var mainRequest;
var settingsRequest;
var username;
function start()
{
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
        mainRequest = new XMLHttpRequest();
        mainRequest.addEventListener(
            "readystatechange", load, false); 
        mainRequest.open('POST','http://127.0.0.1:5000/main',true);
        mainRequest.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
        mainRequest.send("code="+code);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}

function load()
{
    if (mainRequest.readyState == 4 && mainRequest.status == 200)
    {
        var playlistData = JSON.parse(mainRequest.responseText);
        username = playlistData['username'];
        if(playlistData == null)
        {
            document.getElementById('noPlaylist').style.visibility = 'visible';
        }
        else
        {
            document.getElementById('noPlaylist').style.display = 'none';
        }
        document.getElementById('managedPlaylist').style.visibility = 'visible';
        console.log(playlistData['backupPlaylist']);
        if(playlistData['backupPlaylist']!='none')
        {
            document.getElementById('backupPlaylist').style.visibility = 'visible';
        }
        var managedPlaylistCell = document.getElementById('managedPlaylist');
        var managedPlaylistName = playlistData['mainPlaylist']['name'];
        var managedPlaylistImageSrc = playlistData['mainPlaylist']["images"][0]['url'];
        var managedPlaylistBox = createBox('Managed Playlist',managedPlaylistImageSrc, managedPlaylistName);
        managedPlaylistCell.appendChild(managedPlaylistBox);

        var backupPlaylistCell = document.getElementById('backupPlaylist');
        var backupPlaylistName = playlistData['backupPlaylist']['name'];
        var backupPlaylistImageSrc = playlistData['backupPlaylist']["images"][0]['url'];
        var backupPlaylistBox = createBox('Backup Playlist',backupPlaylistImageSrc, backupPlaylistName);
        backupPlaylistCell.appendChild(backupPlaylistBox);

        document.getElementById('cap').value = playlistData['songCap'];
        document.getElementById('grace').value = playlistData['gracePeriod'];
        
    }
}

function submitSettings()
{
    try
    {
        var cap = document.getElementById('cap').value;
        var grace = document.getElementById('grace').value;
        data = JSON.stringify({"user": username, "song cap": cap, "grace period": grace})
        settingsRequest = new XMLHttpRequest();
        settingsRequest.open('POST','http://127.0.0.1:5000/settings',true);
        settingsRequest.setRequestHeader('content-type', 'application/json');
        settingsRequest.send(data);
    }
    catch(e)
    {
        console.log("Expeption: "+e.stack);
    }
}


function createBox(top,src, title)
{
    var div = document.createElement("div");
    div.id = title;
    div.setAttribute('class','playlistBox');
    div.setAttribute("isSelected", "false");
    div.style.borderRadius = "55px";
    div.style.padding = "20px";
    div.style.paddingTop = "20px";
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
    img.setAttribute("onclick","location.href='stats.html'");
    img.style.userSelect = "none";
    var topTitle = document.createElement('h3');
    topTitle.innerHTML = top;
    div.appendChild(topTitle);
    div.appendChild(img);
    var text = document.createElement("h4");
    text.style.marginTop = "5%";
    text.innerHTML = title;
    text.setAttribute("id","txt"+title);
    text.style.userSelect = "none";
    div.appendChild(text);
    div.style.userSelect = "none";
    return div;
}