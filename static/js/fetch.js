function togglePlayPause() {
    fetch("/toggle_play_pause", {
        method: "POST",
    }).then(response => response.json())
      .then(data => {
          console.log(data);
      });
}

function nextChapter() {
    fetch("/next_chapter", {
        method: "POST",
    }).then(response => response.json())
      .then(data => {
          console.log(data);
      });
}

function previousChapter() {
    fetch("/previous_chapter", {
        method: "POST",
    }).then(response => response.json())
      .then(data => {
          console.log(data);
      });
}

document.querySelector("#play-pause-btn").addEventListener("click", togglePlayPause);
document.querySelector("#next-chapter-btn").addEventListener("click", nextChapter);
document.querySelector("#previous-chapter-btn").addEventListener("click", previousChapter);
