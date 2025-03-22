Sure, here's the contents for the file: /face-kyc/src/static/js/face-verify.js

// This file contains JavaScript functions related to face verification, including handling file uploads and making API calls to the backend for verification.

document.addEventListener('DOMContentLoaded', function() {
    const referenceInput = document.getElementById('referenceInput');
    const verifyInput = document.getElementById('verifyInput');
    const verifyBtn = document.getElementById('verifyBtn');
    const successResult = document.getElementById('successResult');
    const failureResult = document.getElementById('failureResult');
    const loader = document.getElementById('loader');

    referenceInput.addEventListener('change', handleReferenceUpload);
    verifyInput.addEventListener('change', handleVerifyUpload);
    verifyBtn.addEventListener('click', performVerification);

    function handleReferenceUpload() {
        const file = referenceInput.files[0];
        if (file && file.type.match('image.*')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Display the uploaded reference image
                const referencePreview = document.getElementById('referencePreview');
                referencePreview.src = e.target.result;
                referencePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }

    function handleVerifyUpload() {
        const file = verifyInput.files[0];
        if (file && file.type.match('image.*')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Display the uploaded verification image
                const verifyPreview = document.getElementById('verifyPreview');
                verifyPreview.src = e.target.result;
                verifyPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }

    function performVerification() {
        // Hide previous results
        successResult.style.display = 'none';
        failureResult.style.display = 'none';
        loader.style.display = 'block';
        verifyBtn.disabled = true;

        const referenceImageData = referenceInput.files[0];
        const verifyImageData = verifyInput.files[0];

        const formData = new FormData();
        formData.append('reference', referenceImageData);
        formData.append('verify', verifyImageData);

        fetch('/api/verify-face', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loader.style.display = 'none';
            verifyBtn.disabled = false;

            if (data.success) {
                if (data.is_match) {
                    successResult.style.display = 'flex';
                } else {
                    failureResult.style.display = 'flex';
                }
            } else {
                console.error(data.error);
                failureResult.style.display = 'flex';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loader.style.display = 'none';
            verifyBtn.disabled = false;
            failureResult.style.display = 'flex';
        });
    }
});