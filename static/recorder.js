// core/static/app/js/recorder.js
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

    let mediaRecorder;
    let audioChunks = [];
    let recordedBlob = null;
    let timerInterval;
    let seconds = 0;

    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
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

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        recordButton.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstart = () => {
                    recordButton.disabled = true;
                    stopButton.disabled = false;
                    recordButton.classList.add('recording');
                    stopButton.classList.add('recording');
                    recordingStatus.textContent = "Recording...";
                    audioPlaybackContainer.style.display = 'none';
                    audioChunks = []; // Reset chunks for new recording
                    recordedBlob = null;
                    audioFileInput.value = ''; // Clear file input if user records
                    startTimer();
                };

                mediaRecorder.onstop = () => {
                    recordButton.disabled = false;
                    stopButton.disabled = true;
                    recordButton.classList.remove('recording');
                    stopButton.classList.remove('recording');
                    recordingStatus.textContent = "Recording finished. Preview below.";
                    stopTimer();

                    recordedBlob = new Blob(audioChunks, { type: 'audio/wav' }); // You can change type, e.g., 'audio/webm' or 'audio/ogg'
                    const audioUrl = URL.createObjectURL(recordedBlob);
                    audioPlayback.src = audioUrl;
                    audioPlaybackContainer.style.display = 'block';
                };
                
                mediaRecorder.start();

            } catch (err) {
                console.error("Error accessing microphone:", err);
                recordingStatus.textContent = "Error: Could not access microphone. " + err.message;
                alert("Could not access microphone. Please ensure permission is granted and try again.");
            }
        });

        stopButton.addEventListener('click', () => {
            if (mediaRecorder && mediaRecorder.state === "recording") {
                mediaRecorder.stop();
            }
        });

        useRecordingButton.addEventListener('click', () => {
            if (recordedBlob) {
                const audioFile = new File([recordedBlob], `recording_${Date.now()}.wav`, { type: 'audio/wav' });
                
                // Create a DataTransfer object to simulate a file selection
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(audioFile);
                audioFileInput.files = dataTransfer.files;

                recordingStatus.textContent = "Recording selected for upload.";
                
                alert("Recording selected! It will be uploaded when you submit the post.");
            } else {
                recordingStatus.textContent = "No recording available to use.";
            }
        });

        // If user selects a file, clear any recording status
        audioFileInput.addEventListener('change', () => {
            if (audioFileInput.files.length > 0) {
                recordingStatus.textContent = "File selected for upload. Any recording will be ignored.";
                audioPlaybackContainer.style.display = 'none';
                recordedBlob = null; // Clear recorded blob if a file is chosen
                 if (mediaRecorder && mediaRecorder.state === "recording") {
                    mediaRecorder.stop(); // Stop recording if active
                }
                stopTimer();
                timerDisplay.textContent = "00:00";
            }
        });

    } else {
        recordingStatus.textContent = "Audio recording is not supported by your browser.";
        recordButton.disabled = true;
        stopButton.disabled = true;
    }
});
