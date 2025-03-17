import React, { useState } from 'react';
import axios from 'axios';

const OCRUpload = () => {
    const [file, setFile] = useState(null);
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            setError('Please upload a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post('/api/ocr/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResponse(res.data);
            setError(null);
        } catch (err) {
            setError('Error uploading file');
            setResponse(null);
        }
    };

    return (
        <div>
            <h2>Upload Document for OCR</h2>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} />
                <button type="submit">Upload</button>
            </form>
            {response && <div>OCR Result: {JSON.stringify(response)}</div>}
            {error && <div style={{ color: 'red' }}>{error}</div>}
        </div>
    );
};

export default OCRUpload;