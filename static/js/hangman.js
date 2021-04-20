var alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
        'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
        't', 'u', 'v', 'w', 'x', 'y', 'z'];
  
var getHint ;           // Word getHint
var word = "Default";   // Selected word
var guess ;             // guess
var guesses = [ ];      // Stored guesses
var lives ;             // Lives
var counter ;           // Count correct guesses
var space;              // Number of spaces in word '-'

var me = true;
var myName = "bukvalno az";
var gameActive = false;
var gameState = "";
const lobby_id = parseInt(location.href.split("/")[location.href.split("/").length-1])
const lobby_type = location.href.split("/")[location.href.split("/").length-2]

var socket = io('localhost:5000');
socket.on('connect', function() {
    socket.emit('join', {'room': 10 * lobby_id + 2, 'lobby type': lobby_type});
});
var clue = "No hint provided."; 
var hint = document.getElementById("hint");
// Get elements
var showLives = document.getElementById("mylives");
var getHint = document.getElementById("hint");
var showClue = document.getElementById("clue");


// create alphabet ul
var buttons = function () {
    myButtons = document.getElementById('buttons');
    letters = document.createElement('ul');

    for (var i = 0; i < alphabet.length; i++) {
        letters.id = 'alphabet';
        list = document.createElement('li');
        list.id = 'letter';
        list.innerHTML = alphabet[i];
        check();
        myButtons.appendChild(letters);
        letters.appendChild(list);
    }
}


  
// Show lives
comments = function () {
    showLives.innerHTML = "You have " + lives + " lives";
    if (lives < 1) {
        showLives.innerHTML = "Game Over";
    }
	if (counter + space === guesses.length) {
	    gameActive = false;
	    showLives.innerHTML = myName + " Win!";
	    if(me){
			socket.emit("win",{"lobby type" : lobby_type, "player" : myName})
	    }
	    return;
	}
}

// Animate man
var animate = function () {
    var drawMe = lives ;
    drawArray[drawMe]();
}

  
// Hangman
canvas =  function(){

    myStickman = document.getElementById("stickman");
    context = myStickman.getContext('2d');
    context.beginPath();
    context.strokeStyle = "#000";
    context.lineWidth = 2;
};
  
head = function(){
    myStickman = document.getElementById("stickman");
    context = myStickman.getContext('2d');
    context.beginPath();
    context.arc(60, 25, 10, 0, Math.PI*2, true);
    context.stroke();
}
    
draw = function($pathFromx, $pathFromy, $pathTox, $pathToy) {
    
    context.moveTo($pathFromx, $pathFromy);
    context.lineTo($pathTox, $pathToy);
    context.stroke(); 
}

frame1 = function() {
    draw (0, 150, 150, 150);
};
   
frame2 = function() {
    draw (10, 0, 10, 600);
};
  
frame3 = function() {
    draw (0, 5, 70, 5);
};
  
frame4 = function() {
    draw (60, 5, 60, 15);
};
  
torso = function() {
    draw (60, 36, 60, 70);
};
  
rightArm = function() {
    draw (60, 46, 100, 50);
};
  
leftArm = function() {
    draw (60, 46, 20, 50);
};
  
rightLeg = function() {
    draw (60, 70, 100, 100);
};
  
leftLeg = function() {
    draw (60, 70, 20, 100);
};
  
drawArray = [rightLeg, leftLeg, rightArm, leftArm,  torso,  head, frame4, frame3, frame2, frame1]; 


// OnClick Function
check = function () {
    list.onclick = function () {
        if(!gameActive || !me){
            return;
        }
        var guess = (this.innerHTML);
        this.setAttribute("class", "active");
        this.onclick = null;
        gameState += ";" + guess;
        socket.emit("move", {'lobby type': lobby_type, 'room': 10 * lobby_id + 2, 'gameState':gameState, "me":me, "player" : myName});
    }
}


init = function () {
    document.getElementById("popupForm").style.display = "block";
    if(!word.localeCompare("Default")){
        console.log(!word.localeCompare("Default"))
        while(!word.localeCompare("Default")){
            if(document.getElementById("popupForm").style.display.localeCompare("none")){
                word = document.getElementById("word").value.toLowerCase();
                console.log(document.getElementById("hintt").value.length);
                if(document.getElementById("hintt").value.length !== 0){
                    hint = document.getElementById("hintt").value;
                }
                break;
            }
        }
    }    
}
  
hint.onclick = function() {
    if(!gameActive || !me){
        return;
    }
    showClue.innerHTML = "Clue: - " +  clue;
};
   
// Reset
document.getElementById('reset').onclick = function() {
    socket.emit("reset", {'room': 10*lobby_id + 2});
}


//socket 
socket.on("start", function(data){
    
    if(me){
        document.getElementById("popupForm").remove();
        console.log("ok");
        guesses = [ ];
        lives = 10;
        counter = 0;
        space = 0;
        buttons();
        comments();
        canvas();
    }
    document.getElementsByClassName("flashes")[0].remove();
    document.querySelectorAll('.players')[0].innerHTML = data["user1"] + " vs " + data["user2"];
    gameActive = me;
    myName = data["user2"];
    console.log("kekw");
    gameState = word + ";" + hint;
    console.log(gameState);
    if(!me){
        socket.emit("move", {'lobby type': lobby_type, 'room': 10 * lobby_id + 2, 'gameState':gameState, 'player' : myName});
    }
})

socket.on("move", function(data){
    console.log(word)
    console.log(data['gameState'].split(";").length)
    if(data['gameState'].split(";").length === 2 && me){
        word = data['gameState'].split(";")[0];
        hint = data['gameState'].split(";")[1];
        wordHolder = document.getElementById('hold');
        correct = document.createElement('ul');
        for (var i = 0; i < word.length; i++) {
            correct.setAttribute('id', 'my-word');
            guess = document.createElement('li');
            guess.setAttribute('class', 'guess');
            if (word[i] === " ") {
                guess.innerHTML = " ";
                space = 1;
            } else {
                guess.innerHTML = "_";
            }

            guesses.push(guess);
            wordHolder.appendChild(correct);
            correct.appendChild(guess);
        }
        console.log(word);
    }
    if(data['gameState'].split(";")[data['gameState'].split(";").length - 1].length === 1){
        var guess = data['gameState'].split(";")[data['gameState'].split(";").length - 1].charAt(0);
        for (var i = 0; i < word.length; i++) {
            if (word[i] === guess) {
                guesses[i].innerHTML = guess;
                counter += 1;
                
            }
        }
        var j = (word.indexOf(guess));
        if (j === -1) {
            lives -= 1;
            comments();
            animate();
        } else {
            comments();
        }
    }
    for(let i = 0; i < data['gameState'].length; i++){
        gameState[i] = data['gameState'].charAt(i);
    }
})

socket.on("you first", function(data){
    me = false;
    document.getElementsByClassName("flashes")[0].style.display = "none";
    console.log("ok");
    guesses = [ ];
    lives = 10;
    counter = 0;
    space = 0;
    buttons();
    comments();
    canvas();
    init();
    console.log("perhaps");
})

socket.on("leaving", function(data){
    if(gameActive){
        gameActive = false;
        statusDisplay.innerHTML = "Opponent left.";
    }
})

//prototip, oshte ne bachka
/*socket.on("reset", function(data){
    me = !me;
    correct.parentNode.removeChild(correct);
    letters.parentNode.removeChild(letters);
    showClue.innerHTML = "";
    context.clearRect(0, 0, 400, 400);
    play();
})*/

window.addEventListener('beforeunload', function(event) {
    socket.emit("leaving", {'room': 10 * lobby_id + 2})
});
  
