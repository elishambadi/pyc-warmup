document.addEventListener('DOMContentLoaded', function() {
    const audioPlayer = document.getElementById('audio-player');
    const mp3Id = audioPlayer.dataset.mp3Id;

    // Load existing timestamps when page loads
    loadTimestamps(mp3Id);

    // Handle timestamp setting
    document.querySelectorAll('.sync-btn').forEach(button => {
        button.addEventListener('click', function() {
            const lyricLine = this.closest('.lyric-line');
            const lyricId = lyricLine.dataset.lyricId;
            const currentTime = audioPlayer.currentTime;

            saveTimestamp(lyricId, mp3Id, currentTime, lyricLine);
        });
    });

    // Handle timestamp deletion
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const lyricLine = this.closest('.lyric-line');
            const lyricId = lyricLine.dataset.lyricId;

            if (confirm('Delete this timestamp?')) {
                deleteTimestamp(lyricId, mp3Id, lyricLine);
            }
        });
    });
});

function saveTimestamp(lyricId, mp3Id, timestamp, lyricLine) {
    fetch('/save-timestamp/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            lyric_id: lyricId,
            mp3_id: mp3Id,
            timestamp: timestamp
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const timestampDisplay = lyricLine.querySelector('.timestamp-display');
            timestampDisplay.textContent = `[${timestamp.toFixed(2)}s]`;
            lyricLine.classList.add('synced');
        }
    })
    .catch(error => {
        console.error('Error saving timestamp:', error);
        alert('Failed to save timestamp');
    });
}

function deleteTimestamp(lyricId, mp3Id, lyricLine) {
    fetch('/delete-timestamp/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            lyric_id: lyricId,
            mp3_id: mp3Id
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const timestampDisplay = lyricLine.querySelector('.timestamp-display');
            timestampDisplay.textContent = '';
            lyricLine.classList.remove('synced');
        }
    })
    .catch(error => {
        console.error('Error deleting timestamp:', error);
        alert('Failed to delete timestamp');
    });
}

function loadTimestamps(mp3Id) {
    fetch(`/get-timestamps/${mp3Id}/`)
        .then(response => response.json())
        .then(data => {
            data.timestamps.forEach(ts => {
                const lyricLine = document.querySelector(`.lyric-line[data-lyric-id="${ts.lyric_id}"]`);
                if (lyricLine) {
                    const timestampDisplay = lyricLine.querySelector('.timestamp-display');
                    timestampDisplay.textContent = `[${ts.timestamp.toFixed(2)}s]`;
                    lyricLine.classList.add('synced');
                }
            });
        })
        .catch(error => {
            console.error('Error loading timestamps:', error);
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
