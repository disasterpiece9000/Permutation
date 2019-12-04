var playlistSelectRequest;
var playlistSubmitRequest;
var playlistId;
var username;
function start()
{
    try
    {
        playlistSelectRequest = new XMLHttpRequest();
        playlistSelectRequest.addEventListener(
            "readystatechange", setSelectedPlaylist, false); 
        playlistSelectRequest.open('GET','http://127.0.0.1:5000/confirm',true);
        playlistSelectRequest.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
        playlistSelectRequest.send(null);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}

function setAsMain()
{
    try
    {
        playlistSubmitRequest = new XMLHttpRequest();
        playlistSubmitRequest.addEventListener(
            "readystatechange", done, false); 
        playlistSubmitRequest.open('POST','http://127.0.0.1:5000/submit',true);
        playlistSubmitRequest.setRequestHeader('content-type', 'application/json');
        data = JSON.stringify({"type": "main", "username": username, "playlistId": playlistId})
        playlistSubmitRequest.send(data);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}

function setAsBackup()
{
    try
    {
        playlistSubmitRequest = new XMLHttpRequest();
        playlistSubmitRequest.addEventListener(
            "readystatechange", done, false); 
        playlistSubmitRequest.open('POST','http://127.0.0.1:5000/submit',true);
        playlistSubmitRequest.setRequestHeader('content-type', 'application/json');
        data = JSON.stringify({"type": "backup", "username": username, "playlistId": playlistId})
        playlistSubmitRequest.send(data);
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}

function done()
{
    if (playlistSubmitRequest.readyState == 4 && playlistSubmitRequest.status == 200)
    {
        window.location.href = "main.html";
    }
}

function setSelectedPlaylist()
{
    if (playlistSelectRequest.readyState == 4 && playlistSelectRequest.status == 200)
    {
        var playlistData = JSON.parse(playlistSelectRequest.responseText);
        playlistId = playlistData['playlist']['id'];
        username = playlistData['playlist']['owner']['id'];
        var head = document.getElementById("head");
        head.innerHTML = playlistData['playlist']['name'];
        var table = document.getElementById("songs")
        while(table.hasChildNodes())
        {
            table.removeChild(table.firstChild);
        }
        var playlist = playlistData['tracks']['items'];
        for(var i=0;i<playlist.length;i++)
        {
            var track = playlistData['tracks']['items'][i]['track'];
            console.log(track['name']);
            var row = table.insertRow(i);
            row.setAttribute("class",'confrimTr');
            var cell0 = row.insertCell(0);
            var cell1 = row.insertCell(1);
            cell0.setAttribute('class', 'confirmTd');
            cell1.setAttribute('class', 'confirmTd');
            cell1.setAttribute("style","user-select: none;");
            cell0.setAttribute("align","center");
            cell0.setAttribute("valign","bottom");
            var img = document.createElement('img');
            var altImg = document.createElement('img');
            altImg.src = "alt.png";
            img.src=track['album']['images'][2]['url'];
            img.setAttribute("onerror","this.src='alt.png';");
            img.setAttribute('id',track['name']+i);
            cell0.appendChild(img);
            cell1.innerHTML=track['name']+" - "+
                track['album']['artists'][0]['name'];
            

        }
    }
}