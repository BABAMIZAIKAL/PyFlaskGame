var myhand = [];
var carddeck = ["pesho", "asdf", "bashtami", "lelkekw", "OwO"];
for(let i = 0; i < 100; i++){
    carddeck.push("a");
}
var blackcards = ["maikati", "bashtati", "pesho", "kelesho", "nasisveeeeeej", "tiktok", "kude sme", "tuka sme"];
var mycard = 'penisa na bashtati'
var owner = false;
var czar = false;
var want10white = true;
var wantwhite = true;
var last = 0;
var playedalready = true;
var czarpicking = false
var roundwhites = [];
var myid = 0;
var startable = false
users = [];
for(let i = 1; i <= 5; i++){
    users.push(document.getElementById('user' + i.toString()));
    console.log(users);
}
const blackcard = document.getElementById('1')
const playingfield = document.getElementById("playing field")
//const mycard = document.getElementById()
const lobby_id = parseInt(location.href.split("/")[location.href.split("/").length-1]);
const lobby_type = location.href.split("/")[location.href.split("/").length-2];
const room_id = 10 * lobby_id + 3

function shuffle(array) {
  var currentIndex = array.length,  randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    // And swap it with the current element.
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex], array[currentIndex]];
  }

  return array;
}


var socket = io();
socket.on('connect', function() {
    socket.emit('cahjoin', {'room': room_id, 'lobby type': lobby_type});
    socket.emit('want10white', {'room': room_id})
});

socket.on('czar', function(data){
console.log(myid)
console.log(data['czar'])
    if(myid != data['czar'] + 1){
        return
    }
    console.log(1)
    czar = true;
    myid = data['czar'] + 1
    let button = document.createElement('button');
    button.id = "izbor";
    button.style.position = 'fixed';
    button.style.bottom = "30";
    button.style.left = "30";
    button.style.width = "5%";
    button.style.height = "5%";
    button.innerHTML = "Izbiram";
    button.onclick = function(event){
        socket.emit('dai da izbiram', {'room': room_id});
        document.getElementById("izbor").remove();

    }
    document.body.appendChild(button);
})

socket.on('you first', function(data){
    if(owner) return;
    owner = true;
    czar = true;
    console.log(owner);
    let button = document.createElement('button');
    button.id = "start";
    button.style.position = 'fixed';
    button.style.bottom = "30";
    button.style.right = "30";
    button.style.width = "5%";
    button.style.height = "5%";
    button.innerHTML = "START";
    button.onclick = function(event){
        if(!startable) return;
        socket.emit('cahstart', {'room': room_id});
        let newbutton = document.createElement('button');
        console.log(newbutton)
        newbutton.id = "izbor";
        newbutton.style.position = 'fixed';
        newbutton.style.bottom = "30";
        newbutton.style.left = "30";
        newbutton.style.width = "5%";
        newbutton.style.height = "5%";
        newbutton.innerHTML = "Izbiram";
        newbutton.onclick = function(event){
            socket.emit('dai da izbiram', {'room': room_id});
            document.getElementById("izbor").remove();
        }
        document.body.appendChild(newbutton);
        console.log('ok wrat')
        document.getElementById("start").remove();

    }
    document.body.appendChild(button);
    console.log(button);
    carddeck = shuffle(carddeck)
    blackcards = shuffle(blackcards)
})

socket.on('update users', function(data){
        console.log('here1')

        document.getElementById('user1').innerHTML = data['user1'];
        if(data['user1'].localeCompare('Waiting for other players...') != 0){
            last = 1;
        }

        document.getElementById('user2').innerHTML = data['user2'];
        if(data['user2'].localeCompare('Waiting for other players...') != 0){
            last = 2;
            startable = true;
        }

        document.getElementById('user3').innerHTML = data['user3'];
        if(data['user3'].localeCompare('Waiting for other players...') != 0){
            last = 3;
        }

        document.getElementById('user4').innerHTML = data['user4'];
        if(data['user4'].localeCompare('Waiting for other players...') != 0){
            last = 4;
        }

        document.getElementById('user5').innerHTML = data['user5'];
        if(data['user5'].localeCompare('Waiting for other players...') != 0){
            last = 5;
        }
        if(myid == 0){
            if(data['user2'].localeCompare('Waiting for other players...') == 0){
                myid = 1
            }
            else if(data['user3'].localeCompare('Waiting for other players...') == 0){
                myid = 2;
            }
            else if(data['user4'].localeCompare('Waiting for other players...') == 0){
                myid = 3
            }
            else if(data['user5'].localeCompare('Waiting for other players...') == 0){
                myid = 4
            }
            else{
                myid = 5
            }
        }

})

socket.on('start', function(data){
    let mycards = document.getElementById('mycards');
    for(const card of myhand){
        let li = document.createElement('li');
        let divkarta = document.createElement('div');
        divkarta.classList.add("kartawhite");
        let divinside = document.createElement('div');
        divinside.classList.add("inside");
        divinside.innerHTML = card;
        divkarta.appendChild(divinside);
        li.appendChild(divkarta);
        li.cursor = "crosshair";
        li.onclick = function(event){
            if(playedalready || czar) return;
            wantwhite = true;
            socket.emit('played white', {'room': room_id, 'white': divinside.innerHTML});
            playedalready = true;
            li.remove();
            mycard = divinside.innerHTML;

        };
        mycards.appendChild(li);
    }

})

socket.on('new round', function(data){
    playedalready = false;
    document.getElementById("1").innerHTML = data["black"];
})

socket.on('white', function(data){
    let li = document.createElement('li');
    let divkarta = document.createElement('div');
    divkarta.classList.add("kartawhite");
    let divinside = document.createElement('div');
    divinside.classList.add("inside");
    divkarta.appendChild(divinside);
    li.appendChild(divkarta);
    document.getElementById("playing field").appendChild(li)
    roundwhites.push(data['white'])

})

socket.on('black', function(data){
    playedalready = false;
    document.getElementById("1").innerHTML = data["black"];
})

socket.on('drawblack', function(data){
    console.log("herer");
    if(!owner){return;}
    socket.emit('black', {'room': room_id, 'black': blackcards.pop()});
})

socket.on('drawwhite', function(data){
    if(owner){
        socket.emit('drawnwhite', {'room': room_id, 'white': carddeck.pop()})
    }

})

socket.on('draw10white', function(data){
    if(owner){
        cards = []
        for(var i = 0; i < 10; i++){
            cards.push(carddeck.pop())
        }
        socket.emit('10white', {'room': room_id, 'white': cards})
    }

})

socket.on('10white', function(data){
    if(want10white){
        want10white = false;
        myhand = data['white'];
    }
})

socket.on('receivewhite', function(data){
    if(wantwhite){
        wantwhite = false;
        myhand.push(data['white'])
        let li = document.createElement('li');
        let divkarta = document.createElement('div');
        divkarta.classList.add("kartawhite");
        let divinside = document.createElement('div');
        divinside.classList.add("inside");
        divinside.innerHTML = myhand[myhand.length - 1]
        divkarta.appendChild(divinside);
        li.appendChild(divkarta);
        document.getElementById("mycards").appendChild(li)
    }
})

socket.on('flip playing field', function(){
    var counter = 0;
    var kek;
    while(roundwhites.length > 0){
        counter++;
        console.log(playingfield.children)
        kek = playingfield.children[counter].firstChild.firstChild
        kek.innerHTML = roundwhites.pop()
        kek.onclick = function(event){
            if(czar){
                console.log(myid)
                console.log(last)
                socket.emit('czarchoice', {'room': room_id, 'white': kek.innerHTML, 'new czar': (myid) % last});
                czar = false
            }
        };
    }
})

socket.on('czarchoice', function(data){
    while(playingfield.children.length > 1){
        playingfield.lastChild.remove()
    }
    if(mycard == data['white']){
        emit('cahme')
    }
    playedalready = false;


})
window.onbeforeunload = function(event){
    window.location.replace("http://" + location.href.split("/")[2]);
}
