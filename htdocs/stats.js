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
        playlistSelectRequest.open('POST','http://127.0.0.1:5000/stats',true);
        playlistSelectRequest.setRequestHeader('content-type', 'application/json');
        playlistSelectRequest.send(JSON.stringify({"username": username}));
    }
    catch(e)
    {
        console.log("Exception: "+e.stack);
    }
}


function setSelectedPlaylist()
{
    if (playlistSelectRequest.readyState == 4 && playlistSelectRequest.status == 200)
    {
        var playlistData = JSON.parse(playlistSelectRequest.responseText);
        console.log('bitch')
        var table = document.getElementById('songs');
        while(table.hasChildNodes())
        {
            table.removeChild(table.firstChild);
        }
        for(var i=0;i<playlistData['tracks'].length;i++)
        {
            var title = playlistData['tracks'][i]["title"];
            var artist = playlistData['tracks'][i]["artist"];
            var album = playlistData['tracks'][i]["album"];
            var date_added = playlistData['tracks'][i]["date added"];
            var listen_count = playlistData['tracks'][i]["listen count"];
           
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
            img.src=img_url;
            img.setAttribute("onerror","this.src='alt.png';");
            cell0.appendChild(img);
            cell1.innerHTML=title+" - "+
                artist;
            

        }
    }
}