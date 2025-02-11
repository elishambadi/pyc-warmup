document.addEventListener('DOMContentLoaded', function() {
    const audioPlayer = document.getElementById('audio-player');
    const lyricLines = document.querySelectorAll('.lyric-line');
    let timestamps = {};
    let currentLine = null;

    // Process timestamps for current MP3
    function processTimestamps(mp3Id) {
        timestamps = {};
        lyricLines.forEach(line => {
            const lineId = line.dataset.lineId;
            const lineTimestamps = JSON.parse(line.dataset.timestamps);
            if (lineTimestamps[mp3Id]) {
                timestamps[lineTimestamps[mp3Id]] = lineId;
            }
        });
    }

    // Update lyrics display based on current time
    function updateLyrics(currentTime) {
        const times = Object.keys(timestamps).map(Number);
        const currentTimestamp = times.reduce((prev, curr) => {
            return (Math.abs(curr - currentTime) < Math.abs(prev - currentTime) ? curr : prev);
        });

        if (timestamps[currentTimestamp] && 
            (!currentLine || currentLine.dataset.lineId !== timestamps[currentTimestamp])) {
            // Remove active class from previous line
            if (currentLine) {
                currentLine.classList.remove('active');
                currentLine.classList.add('played');
            }

            // Add active class to current line
            currentLine = document.querySelector(`.lyric-line[data-line-id="${timestamps[currentTimestamp]}"]`);
            if (currentLine) {
                currentLine.classList.add('active');
                currentLine.classList.remove('played');
                
                // Scroll line into view
                currentLine.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        }
    }

    // Handle MP3 selection change
    mp3List.forEach(mp3Item => {
        mp3Item.addEventListener('click', function() {
            const mp3Id = this.dataset.mp3Id;
            processTimestamps(mp3Id);
            
            // Reset lyric display
            lyricLines.forEach(line => {
                line.classList.remove('active', 'played');
            });
            currentLine = null;
        });
    });

    // Update lyrics on timeupdate
    audioPlayer.addEventListener('timeupdate', () => {
        updateLyrics(audioPlayer.currentTime);
    });

    // Reset lyrics when audio ends
    audioPlayer.addEventListener('ended', () => {
        if (currentLine) {
            currentLine.classList.remove('active');
        }
        lyricLines.forEach(line => line.classList.remove('played'));
        currentLine = null;
    });
});