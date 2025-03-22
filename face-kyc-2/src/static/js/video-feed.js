const video = document.getElementById('videoFeed');
const canvas = document.createElement('canvas');
const context = canvas.getContext('2d');
const captureBtn = document.getElementById('captureBtn');
const verifyBtn = document.getElementById('verifyBtn');
const loader = document.getElementById('loader');
const successResult = document.getElementById('successResult');
const failureResult = document.getElementById('failureResult');

// Start video stream
async function startVideoStream() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: {
                width: 640,
                height: 480,
                facingMode: 'user'
            } 
        });
        video.srcObject = stream;
        await video.play();
        captureBtn.disabled = false;
    } catch (error) {
        console.error("Error accessing webcam: ", error);
        alert("Could not access webcam. Please check permissions.");
    }
}

// Capture frame from video
function captureFrame() {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg');
    }
    return null;
}

// Verify captured frame against reference image
async function verifyVideoFrame() {
    const frameData = captureFrame();
    if (!frameData) {
        alert("Please wait for video to initialize");
        return;
    }

    const referenceInput = document.getElementById('referenceInput');
    if (!referenceInput.files[0]) {
        alert("Please upload a reference image first");
        return;
    }

    const formData = new FormData();
    formData.append('reference', referenceInput.files[0]);
    
    // Convert data URL to Blob
    const blob = await fetch(frameData).then(r => r.blob());
    formData.append('verify', blob, 'capture.jpg');

    try {
        const response = await fetch('/api/verify-face', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.success) {
            successResult.style.display = result.is_match ? 'flex' : 'none';
            failureResult.style.display = result.is_match ? 'none' : 'flex';
            failureResult.querySelector('.result-text').textContent = 
                result.is_match ? '' : `Verification failed (${result.confidence.toFixed(1)}% match)`;
        } else {
            failureResult.style.display = 'flex';
            failureResult.querySelector('.result-text').textContent = result.error;
        }
    } catch (error) {
        console.error("Verification failed:", error);
        failureResult.style.display = 'flex';
        failureResult.querySelector('.result-text').textContent = error.message;
    } finally {
        loader.style.display = 'none';
    }
}

// Convert Data URI to Blob
function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mimeString });
}

// Event listeners
captureBtn.addEventListener('click', () => {
    verifyVideoFrame();
});

// Start video stream when page loads
window.addEventListener('load', startVideoStream);