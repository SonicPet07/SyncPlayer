let socket = new WebSocket("ws://localhost:8000/ws");

socket.onopen = function(e) {
  console.log("[open] Connection established");
};

socket.onmessage = function(event) {
  console.log(`[message] Data received from server: ${event.data}`);
};

socket.onclose = function(event) {
  if (event.wasClean) {
    console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
  } else {
    console.log('[close] Connection died');
  }
};

socket.onerror = function(error) {
  console.log(`[error] ${error.message}`);
};

function sendPlayPause() {
    socket.send("toggle_play_pause");
}

function sendNextChapter() {
    socket.send("next_chapter");
}

function sendPreviousChapter() {
    socket.send("previous_chapter");
}

document.querySelector("#play-pause-btn").addEventListener("click", sendPlayPause);
document.querySelector("#next-chapter-btn").addEventListener("click", sendNextChapter);
document.querySelector("#previous-chapter-btn").addEventListener("click", sendPreviousChapter);
