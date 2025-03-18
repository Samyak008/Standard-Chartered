"use client";

import { useState, useEffect, useRef } from "react";

const TesseractPromise = import("tesseract.js");

export default function ImageUploader() {
  const [Tesseract, setTesseract] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [extractedText, setExtractedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Dynamically import Tesseract.js to prevent SSR issues
    TesseractPromise.then((mod) => setTesseract(mod.default));
  }, []);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageURL = URL.createObjectURL(file);
      setSelectedImage(imageURL);
      setExtractedText("");
      extractTextFromImage(file);
    }
  };

  const extractTextFromImage = async (file) => {
    if (!Tesseract) return;

    setLoading(true);
    setProgress(0);

    try {
      const {
        data: { text },
      } = await Tesseract.recognize(file, "eng", {
        logger: (m) => {
          if (m.status === "recognizing text") {
            setProgress(parseInt(m.progress * 100));
          }
        },
      });
      setExtractedText(text);
    } catch (error) {
      console.error("Error extracting text:", error);
    }
    setLoading(false);
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">
        Document Text Extraction
      </h2>

      {/* Upload Section */}
      <div className="mb-8">
        <div
          onClick={triggerFileInput}
          className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center cursor-pointer hover:bg-blue-50 transition-colors duration-200"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-12 w-12 mx-auto text-blue-500 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="text-blue-600 font-medium mb-1">
            Click to upload an image
          </p>
          <p className="text-sm text-gray-500">PNG, JPG up to 10MB</p>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            className="hidden"
          />
        </div>
      </div>

      {/* Preview Section */}
      {selectedImage && (
        <div className="mb-8">
          <h3 className="text-lg font-medium mb-3 text-gray-700">
            Document Preview
          </h3>
          <div className="border rounded-lg overflow-hidden bg-gray-50">
            <img
              src={selectedImage}
              alt="Document preview"
              className="w-full object-contain max-h-[300px]"
            />
          </div>
        </div>
      )}

      {/* Loading Section */}
      {loading && (
        <div className="mb-8">
          <h3 className="text-lg font-medium mb-2 text-gray-700">Processing</h3>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 text-center">
            {progress}% complete
          </p>
        </div>
      )}

      {/* Results Section */}
      {extractedText && !loading && (
        <div>
          <h3 className="text-lg font-medium mb-3 text-gray-700">
            Extracted Text
          </h3>
          <div className="bg-gray-50 border rounded-lg p-4">
            <div className="flex justify-end mb-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(extractedText);
                }}
                className="text-xs bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-gray-600 flex items-center"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-3.5 w-3.5 mr-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                Copy
              </button>
            </div>
            <div className="max-h-[300px] overflow-y-auto">
              <p className="text-gray-700 whitespace-pre-wrap font-mono text-sm p-2">
                {extractedText}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
