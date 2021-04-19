
const statusDisplay = document.querySelector('.game--status');

let gameActive = false;
let gametype = "tictactoe"
let me = 'O';
let gameState = [" ", " ", " ", " ", " ", " ", " ", " ", " "];
let myTurn = false;
let currentPlayerName = "";
let cells = document.querySelectorAll(".cell");
let otherPlayer = ""
const winningMessage = () => `Player ${otherPlayer} has won!`;
const drawMessage = () => `Game ended in a draw!`;
const currentPlayerTurn = () => `It's ${currentPlayerName}'s turn`;
const lobby_id = parseInt(location.href.split("/")[location.href.split("/").length-1])
const lobby_type = location.href.split("/")[location.href.split("/").length-2]

var socket = io('localhost:5000');
socket.on('connect', function() {
    socket.emit('join', {'room': 10*lobby_id + 1, 'lobby type': lobby_type});
});

const winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
];

function handlePlayerChange() {
    myTurn = !myTurn;
    statusDisplay.innerHTML = currentPlayerTurn();
}

function handleResultValidation() {
    let roundWon = false;
    for (let i = 0; i <= 7; i++) {
        const winCondition = winningConditions[i];
        let a = gameState[winCondition[0]];
        let b = gameState[winCondition[1]];
        let c = gameState[winCondition[2]];
        if (a === ' ' || b === ' ' || c === ' ') {
            continue;
        }
        if (a === b && b === c) {
            roundWon = true;
            break
        }
    }

    if (roundWon) {
        statusDisplay.innerHTML = winningMessage();
        gameActive = false;
        console.log(myTurn);
        if(myTurn){
		socket.emit("win", {"lobby type" : lobby_type, "player" : otherPlayer});
	}
        //window.location.href = window.location.href.split('/')[0];
        return;
    }

    let roundDraw = !gameState.includes(" ");
    if (roundDraw) {
        statusDisplay.innerHTML = drawMessage();
        gameActive = false;
        //window.location.href = window.location.href.split('/')[0];
        return;
    }

    handlePlayerChange();
}

function handleGameState(gameState){
    cells.forEach(function(cell){
        cell.innerHTML = gameState[parseInt(cell.getAttribute('data-cell-index'))];
    });
}



function handleCellClick(clickedCellEvent) {
    const clickedCell = clickedCellEvent.target;
    const clickedCellIndex = parseInt(clickedCell.getAttribute('data-cell-index'));
    if (gameState[clickedCellIndex] !== " " || !gameActive || !myTurn) {
        console.log(players[1]);
        return;
    }
    gameState[clickedCellIndex] = me;
    socket.emit("move", {'lobby type': gametype, 'room': 10 * lobby_id + 1, 'gameState':gameState, "me":me, "player":currentPlayerName});
    //handleCellPlayed(clickedCell, clickedCellIndex);
    //handleGameState(data[gameState].split());
    //gameState = data[gameState].split()
    //handleResultValidation();
    
}

socket.on("start", function(data){
    document.querySelectorAll('.players')[0].innerHTML = data["user1"] + " vs " + data["user2"];
    currentPlayerName = data["user1"];
    otherPlayer = data["user2"];
    statusDisplay.innerHTML = currentPlayerTurn();
    gameActive = true;
    console.log("kek");
    
})

socket.on("move", function(data){
    for(let i = 0; i < 9; i++){
        gameState[i] = data['gameState'].charAt(i);
    }
    otherPlayer = currentPlayerName;
    currentPlayerName = data["player"];
    handleGameState(gameState);
    handleResultValidation();
})

socket.on("you first", function(data){
    myTurn = true;
    me = "X";
    console.log("perhaps");
})

socket.on("leaving", function(data){
    if(gameActive){
        gameActive = false;
        statusDisplay.innerHTML = "Opponent left.";
    }
})

window.addEventListener('beforeunload', function(event) {
    socket.emit("leaving", {'room': 10 * lobby_id + 1})
});

cells.forEach(cell => cell.addEventListener('click', handleCellClick));
