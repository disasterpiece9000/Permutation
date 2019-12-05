var playlistSelectRequest;
var playlistSubmitRequest;
var recommendRequest;
var playlistId;
var username;
var oneIsPlaying = '';
var top5 = [];

function getRecommended()
{
    window.location.href = "playlistRec.html";
}
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
        var table = document.getElementById('songs');
        while(table.hasChildNodes())
        {
            table.removeChild(table.firstChild);
        }
        var row = table.insertRow(0);
        row.setAttribute("class",'confrimTr');
        var cell0 = row.insertCell(0);
        var cell1 = row.insertCell(1);
        var cell2 = row.insertCell(2);
        var cell3 = row.insertCell(3);
        cell0.setAttribute('class', 'confirmTd');
        cell1.setAttribute('class', 'confirmTd');
        cell2.setAttribute('class', 'confirmTd');
        cell3.setAttribute('class', 'confirmTd');
        cell1.setAttribute('style', 'text-align: center;');
        cell2.setAttribute('style', 'text-align: center;');
        cell1.innerHTML = "Song - Album";
        cell2.innerHTML = "Date Added";
        cell3.innerHTML = "Listen Count";
        var img = document.createElement('img');
        img.src = "alt.png";
        img.style.width = "64px";
        img.style.height = "64px";
        cell0.appendChild(img);
        for(var i=0;i<playlistData['tracks'].length;i++)
        {
            if(i<5)
            {
                top5.push(playlistData['tracks'][i]['id'])
            }
            var title = playlistData['tracks'][i]["title"];
            var artist = playlistData['tracks'][i]["artist"];
            var album = playlistData['tracks'][i]["album"];
            var date_added = playlistData['tracks'][i]["date added"];
            var listen_count = playlistData['tracks'][i]["listen count"];
            var img_src = playlistData['tracks'][i]['src'];
            var audioSrc = playlistData['tracks'][i]['audioSrc'];
            var audioId = title+i;
            var row = table.insertRow(i+1);
            row.setAttribute("class",'confrimTr');
            var cell0 = row.insertCell(0);
            var cell1 = row.insertCell(1);
            var cell2 = row.insertCell(2);
            var cell3 = row.insertCell(3);
            var date = new Date(date_added*1000);
            cell2.innerHTML = date.getMonth()+"/"+date.getDay()+"/"+date.getFullYear();
            cell3.innerHTML = listen_count;
            cell0.setAttribute('class', 'confirmTd');
            cell1.setAttribute('class', 'confirmTd');
            cell2.setAttribute('class', 'confirmTd');
            cell3.setAttribute('class', 'confirmTd');
            cell1.setAttribute("style","user-select: none;");
            cell0.setAttribute("align","center");
            cell0.setAttribute("valign","bottom");
            var img = document.createElement('img');
            var altImg = document.createElement('img');
            altImg.src = "alt.png";
            img.src=img_src;
            img.setAttribute("onerror","this.src='alt.png';");
            var audio = document.createElement('audio');
            audio.id = audioId;
            audio.src = audioSrc;
            audio.setAttribute('type','audio/mpeg');
            audio.setAttribute('isplaying','false');
            img.appendChild(audio);
            img.addEventListener('click',function(){playPreview(event)},false);
            cell0.appendChild(img);
            cell1.innerHTML=title+" - "+
                artist;
            

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
}