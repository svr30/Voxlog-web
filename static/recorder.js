console.log("Recorder JS Loaded");

document.addEventListener('DOMContentLoaded', () => {

    const recordButton = document.getElementById('recordButton');
    const stopButton = document.getElementById('stopButton');
    const audioPlayback = document.getElementById('audioPlayback');
    const audioFileInput = document.getElementById('audio_file');
    const recordingStatus = document.getElementById('recordingStatus');
    const audioPlaybackContainer = document.getElementById('audioPlaybackContainer');
    const useRecordingButton = document.getElementById('useRecordingButton');
    const timerDisplay = document.getElementById('timer');

    // ✅ Safety check (VERY IMPORTANT)
    if (!recordButton || !stopButton) {
        console.error("Buttons not found in DOM");
        return;
    }

    let mediaRecorder;
    let audioChunks = [];
    let recordedBlob = null;
    let timerInterval;
    let seconds = 0;

    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const secs = totalSeconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    function startTimer() {
        seconds = 0;
        timerDisplay.textContent = formatTime(seconds);
        timerInterval = setInterval(() => {
            seconds++;
            timerDisplay.textContent = formatTime(seconds);
        }, 1000);
    }

    function stopTimer() {
        clearInterval(timerInterval);
    }

    // ✅ Check browser support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        recordingStatus.textContent = "Audio recording not supported in this browser.";
        recordButton.disabled = true;
        stopButton.disabled = true;
        return;
    }

    // 🎤 RECORD BUTTON
    recordButton.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            mediaRecorder = new MediaRecorder(stream);

            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstart = () => {
                recordButton.disabled = true;
                stopButton.disabled = false;
                recordingStatus.textContent = "Recording...";
                audioPlaybackContainer.style.display = 'none';
                audioFileInput.value = '';
                startTimer();
            };

            mediaRecorder.onstop = () => {
                recordButton.disabled = false;
                stopButton.disabled = true;
                recordingStatus.textContent = "Recording finished.";
                stopTimer();

                // ✅ Use better format (webm works better than wav in browsers)
                recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });

                const audioUrl = URL.createObjectURL(recordedBlob);
                audioPlayback.src = audioUrl;

                audioPlaybackContainer.style.display = 'block';
            };

            mediaRecorder.start();

        } catch (err) {
            console.error("Mic error:", err);
            recordingStatus.textContent = "Microphone access denied.";
            alert("Please allow microphone access.");
        }
    });

    // 🛑 STOP BUTTON
    stopButton.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
    });

    // ✅ USE RECORDING
    if (useRecordingButton) {
        useRecordingButton.addEventListener('click', () => {
            if (recordedBlob) {
                const file = new File([recordedBlob], `recording_${Date.now()}.webm`, {
                    type: 'audio/webm'
                });

                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                audioFileInput.files = dataTransfer.files;

                recordingStatus.textContent = "Recording ready for upload!";
                alert("Recording added successfully!");
            } else {
                recordingStatus.textContent = "No recording available.";
            }
        });
    }

    // 📁 FILE SELECT
    audioFileInput.addEventListener('change', () => {
        if (audioFileInput.files.length > 0) {
            recordingStatus.textContent = "File selected.";
            audioPlaybackContainer.style.display = 'none';
            recordedBlob = null;

            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
            }

            stopTimer();
            timerDisplay.textContent = "00:00";
        }
    });

});
