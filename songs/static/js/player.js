const audioPlayer = document.getElementById("audio-player");
const playPauseBtn = document.getElementById("play-pause-btn");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const seekBar = document.getElementById("seek-bar");
const currentTimeDisplay = document.getElementById("current-time");
const totalTimeDisplay = document.getElementById("total-time");
const audioBar = document.getElementById("audio-player-bar");
const mp3List = document.querySelectorAll(".mp3-voice");

let playlist = [];
let currentTrackIndex = 0;

// Function to load and play track
function loadTrack(index) {
    if (index < 0 || index >= playlist.length) return;
    currentTrackIndex = index;
    audioPlayer.src = playlist[currentTrackIndex];
    audioPlayer.play();
    updatePlayPauseButton();
    audioBar.classList.remove("d-none"); // Show player when track starts
}

// Function to toggle play/pause
function togglePlayPause() {
    if (audioPlayer.paused) {
        audioPlayer.play();
    } else {
        audioPlayer.pause();
    }
    updatePlayPauseButton();
}

// Update play/pause button icon
function updatePlayPauseButton() {
    playPauseBtn.textContent = audioPlayer.paused ? "▶" : "⏸";
}

// Play next track
function playNextTrack() {
    if (currentTrackIndex < playlist.length - 1) {
        loadTrack(currentTrackIndex + 1);
    }
}

// Play previous track
function playPreviousTrack() {
    if (currentTrackIndex > 0) {
        loadTrack(currentTrackIndex - 1);
    }
}

// Update seek bar and time
function updateSeekBar() {
    seekBar.value = (audioPlayer.currentTime / audioPlayer.duration) * 100;
    currentTimeDisplay.textContent = formatTime(audioPlayer.currentTime);
}

// Seek to position
function seekAudio(event) {
    const percent = event.target.value;
    audioPlayer.currentTime = (percent / 100) * audioPlayer.duration;
}

// Format time helper function
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
}

// Event listener for clicking an MP3 file
mp3List.forEach((mp3Item, index) => {
    mp3Item.addEventListener("click", function () {
        const mp3Url = this.getAttribute("data-mp3-url");

        // If the song is already in the playlist, just play it
        if (playlist.includes(mp3Url)) {
            currentTrackIndex = playlist.indexOf(mp3Url);
        } else {
            playlist.push(mp3Url);
            currentTrackIndex = playlist.length - 1;
        }

        loadTrack(currentTrackIndex);
    });
});

// Event listeners for controls
playPauseBtn.addEventListener("click", togglePlayPause);
prevBtn.addEventListener("click", playPreviousTrack);
nextBtn.addEventListener("click", playNextTrack);
audioPlayer.addEventListener("timeupdate", updateSeekBar);
audioPlayer.addEventListener("loadedmetadata", () => {
    totalTimeDisplay.textContent = formatTime(audioPlayer.duration);
});
seekBar.addEventListener("input", seekAudio);
audioPlayer.addEventListener("ended", playNextTrack);