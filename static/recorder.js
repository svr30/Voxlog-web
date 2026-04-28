console.log("Recorder JS Loaded");

document.addEventListener('DOMContentLoaded', () => {

    const recordBtn = document.getElementById('recordButton');
    const stopBtn = document.getElementById('stopButton');
    const audio = document.getElementById('audioPlayback');
    const status = document.getElementById('recordingStatus');
    const timer = document.getElementById('timer');
    const fileInput = document.getElementById('audio_file');
    const useBtn = document.getElementById('useRecordingButton');
    const container = document.getElementById('audioPlaybackContainer');

    if (!recordBtn) {
        console.error("Record button not found");
        return;
    }

    let recorder;
    let chunks = [];
    let blob;
    let interval;
    let seconds = 0;

    function updateTimer() {
        seconds++;
        timer.textContent = "00:" + String(seconds).padStart(2, '0');
    }

    recordBtn.onclick = async () => {
        console.log("Clicked Record");

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            recorder = new MediaRecorder(stream);
            chunks = [];

            recorder.ondataavailable = e => chunks.push(e.data);

            recorder.onstart = () => {
                status.textContent = "Recording...";
                recordBtn.disabled = true;
                stopBtn.disabled = false;

                seconds = 0;
                timer.textContent = "00:00";
                interval = setInterval(updateTimer, 1000);
            };

            recorder.onstop = () => {
                clearInterval(interval);

                blob = new Blob(chunks, { type: 'audio/webm' });
                audio.src = URL.createObjectURL(blob);

                container.style.display = 'block';

                recordBtn.disabled = false;
                stopBtn.disabled = true;
                status.textContent = "Recording done";
            };

            recorder.start();

        } catch (e) {
            alert("Allow microphone access!");
            console.error(e);
        }
    };

    stopBtn.onclick = () => {
        if (recorder && recorder.state === "recording") {
            recorder.stop();
        }
    };

    useBtn.onclick = () => {
        if (!blob) return;

        const file = new File([blob], "record.webm");
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;

        alert("Recording ready for upload!");
    };

});
