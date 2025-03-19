"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import Webcam from "react-webcam";
import { useSession } from "next-auth/react";

export default function FaceVerification({
  onNextStep,
  onPrevStep,
  updateFormData,
}) {
  const webcamRef = useRef(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [faceCaptured, setFaceCaptured] = useState(false);
  const [aadhaarMode, setAadhaarMode] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [ocrError, setOcrError] = useState(null);
  const [statusMessage, setStatusMessage] = useState({ type: "", message: "" });
  const [extractedData, setExtractedData] = useState({
    name: "",
    aadhaarNumber: "",
  });
  const [processingTime, setProcessingTime] = useState(null);
  const { data: session } = useSession();
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  // Start webcam for either face or aadhaar capture
  const startCamera = (forAadhaar = false) => {
    setCapturedImage(null);
    setOcrResult(null);
    setOcrError(null);
    setStatusMessage({ type: "", message: "" });
    setAadhaarMode(forAadhaar);
    setIsCameraActive(true);
    setFaceCaptured(false);
  };

  // Capture image from webcam
  const captureImage = useCallback(() => {
    if (!webcamRef.current) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
      setIsCameraActive(false);

      // If in Aadhaar mode, process the captured image with OCR
      if (aadhaarMode) {
        processAadhaarImage(imageSrc);
      } else {
        // For face verification, just mark as captured
        setFaceCaptured(true);
        setStatusMessage({
          type: "success",
          message: "Face captured successfully!",
        });
      }
    }
  }, [webcamRef, aadhaarMode]);

  // Process Aadhaar image with OCR
  const processAadhaarImage = async (imageSrc) => {
    try {
      setIsProcessing(true);
      setOcrResult(null);
      setOcrError(null);

      // Start performance timing
      const startTime = performance.now();

      // Convert base64 image to file
      const base64Data = imageSrc.split(",")[1];
      const blob = await fetch(`data:image/jpeg;base64,${base64Data}`).then(
        (res) => res.blob()
      );
      const file = new File([blob], "webcam-capture.jpg", {
        type: "image/jpeg",
      });

      const formData = new FormData();
      formData.append("file", file);

      console.log("Sending captured Aadhaar image for OCR processing...");

      const response = await fetch("/api/kyc/aadhar-ocr", {
        method: "POST",
        body: formData,
      });

      // End performance timing
      const endTime = performance.now();
      setProcessingTime(endTime - startTime);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("OCR API error response:", errorText);
        throw new Error(`Failed to process image: ${errorText}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || "Failed to extract information");
      }

      setOcrResult(result.data);
      setExtractedData({
        name: result.data.name || "",
        aadhaarNumber: result.data.aadharNumber || "",
      });

      setStatusMessage({
        type: "success",
        message: "Successfully extracted details from Aadhaar card!",
      });
    } catch (error) {
      console.error("Error processing Aadhaar image:", error);
      setOcrError(error.message);
      setStatusMessage({
        type: "error",
        message: "Failed to extract details. Please try again.",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
    setIsCameraActive(true);
    setFaceCaptured(false);
    setOcrResult(null);
    setOcrError(null);
  };

  const updateKycStatus = async () => {
    if (!session) return;

    try {
      setIsUpdatingStatus(true);

      console.log("Updating KYC status...");
      const response = await fetch("/api/kyc/update-status", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          faceVerified: true,
          kycStatus: "Verified", // Set to Verified if face verification is the final step
        }),
      });

      // Handle non-OK responses
      if (!response.ok) {
        const errorText = await response.text();
        console.error("KYC status update failed:", response.status, errorText);

        // Try to parse JSON if possible
        try {
          const errorJson = JSON.parse(errorText);
          throw new Error(
            errorJson.message || `Failed with status ${response.status}`
          );
        } catch (parseError) {
          throw new Error(
            `API error (${response.status}): Please check the server logs`
          );
        }
      }

      const result = await response.json();
      console.log("KYC status updated successfully:", result);

      setStatusMessage({
        type: "success",
        message: "Verification complete!",
      });
    } catch (error) {
      console.error("Error updating KYC status:", error);
      setStatusMessage({
        type: "error",
        message: `Verification saved but status update failed: ${error.message}`,
      });

      // Even if status update fails, we can still proceed to next step
      // since the basic face verification was successful
      setTimeout(() => {
        setStatusMessage({ type: "", message: "" });
      }, 3000);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // At least require face capture for proceeding
    if (!faceCaptured) {
      setStatusMessage({
        type: "error",
        message: "Please complete face verification first",
      });
      return;
    }

    // If we have OCR results, include them in the updated data
    if (typeof updateFormData === "function") {
      updateFormData({
        faceVerified: true,
        // Include OCR data if available
        ...(ocrResult && {
          name: extractedData.name || ocrResult.name,
          aadhaarNumber: extractedData.aadhaarNumber || ocrResult.aadharNumber,
        }),
      });
    }

    // Update KYC status in the database
    await updateKycStatus();

    onNextStep();
  };

  // For webcam video constraints
  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user", // Use front-facing camera if available
  };

  return (
    <div className="space-y-6">
      {/* Status message */}
      {statusMessage.message && (
        <div
          className={`p-4 mb-6 rounded-lg ${
            statusMessage.type === "success"
              ? "bg-green-900/30 border border-green-700/50 text-green-400"
              : "bg-red-900/30 border border-red-700/50 text-red-400"
          }`}
        >
          {statusMessage.message}
        </div>
      )}

      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-white">Verification Steps</h3>
      </div>

      {!isCameraActive && !capturedImage ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Face Verification */}
          <div className="flex flex-col items-center justify-center p-8 bg-gray-800/70 border border-gray-700 rounded-lg">
            <div className="w-20 h-20 mb-5 rounded-full bg-gray-700 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-10 w-10 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
            <h4 className="text-lg font-medium text-white mb-2">
              Face Verification
            </h4>
            <p className="text-gray-400 text-sm mb-4 text-center">
              Capture your face to verify your identity
            </p>
            <button
              onClick={() => startCamera(false)}
              className={`px-6 py-3 w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-blue-900/20 flex items-center justify-center ${
                faceCaptured ? "bg-green-600 hover:bg-green-700" : ""
              }`}
              disabled={isProcessing}
            >
              {faceCaptured ? (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 mr-2"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Verified
                </>
              ) : (
                <>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 mr-2"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Capture Face
                </>
              )}
            </button>
          </div>

          {/* Aadhaar OCR */}
          <div className="flex flex-col items-center justify-center p-8 bg-gray-800/70 border border-gray-700 rounded-lg">
            <div className="w-20 h-20 mb-5 rounded-full bg-gray-700 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-10 w-10 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
            </div>
            <h4 className="text-lg font-medium text-white mb-2">Aadhaar OCR</h4>
            <p className="text-gray-400 text-sm mb-4 text-center">
              Scan your Aadhaar card to extract details
            </p>
            <button
              onClick={() => startCamera(true)}
              className="px-6 py-3 w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-purple-900/20 flex items-center justify-center"
              disabled={isProcessing}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-2"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                  clipRule="evenodd"
                />
              </svg>
              Scan Aadhaar Card
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-gray-800/70 border border-gray-700 rounded-lg p-6">
          {isCameraActive ? (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-white mb-2">
                {aadhaarMode ? "Scan Aadhaar Card" : "Capture Face"}
              </h4>
              <p className="text-gray-400 text-sm mb-4">
                {aadhaarMode
                  ? "Position your Aadhaar card clearly in frame"
                  : "Make sure your face is clearly visible and well-lit"}
              </p>

              <div className="relative w-full max-w-lg mx-auto">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  videoConstraints={videoConstraints}
                  className="w-full rounded-lg"
                  style={{
                    aspectRatio: "1.33",
                    backgroundColor: "#111827", // Match dark theme
                  }}
                />

                {aadhaarMode && (
                  <div className="absolute inset-0 border-2 border-dashed border-blue-500 rounded-lg pointer-events-none flex items-center justify-center">
                    <div className="text-blue-500 text-xs bg-black/70 rounded-full px-2 py-1">
                      Position card here
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-center mt-4 space-x-3">
                <button
                  onClick={captureImage}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-all duration-300"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 mr-2 inline"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Capture
                </button>

                <button
                  onClick={() => setIsCameraActive(false)}
                  className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-all duration-300"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            capturedImage && (
              <div className="space-y-4">
                <h4 className="text-lg font-medium text-white mb-2">
                  {aadhaarMode ? "Aadhaar Card Captured" : "Face Captured"}
                </h4>

                <div className="relative w-full max-w-lg mx-auto">
                  <img
                    src={capturedImage}
                    alt={aadhaarMode ? "Captured Aadhaar" : "Captured face"}
                    className="w-full rounded-lg border border-gray-700"
                    style={{
                      aspectRatio: "1.33",
                      backgroundColor: "#111827", // Match dark theme
                    }}
                  />
                </div>

                {/* OCR Results */}
                {isProcessing && (
                  <div className="flex justify-center items-center py-4 space-x-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
                    <p className="text-blue-400">
                      Analyzing document with AI...
                    </p>
                  </div>
                )}

                {ocrError && !isProcessing && (
                  <div className="p-3 bg-red-900/20 border border-red-700/40 rounded-lg text-red-400 text-sm">
                    <p className="font-medium">Error analyzing document:</p>
                    <p>{ocrError}</p>
                  </div>
                )}

                {ocrResult && !isProcessing && aadhaarMode && (
                  <div className="p-4 bg-blue-900/20 border border-blue-800/40 rounded-lg mt-4">
                    <div className="flex justify-between items-start">
                      <h5 className="text-blue-400 font-medium mb-3">
                        Extracted Information
                      </h5>

                      {processingTime && (
                        <div className="text-xs text-gray-400">
                          Processed in {processingTime.toFixed(0)}ms
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span className="block text-gray-400 text-sm mb-1">
                          Name
                        </span>
                        <div className="p-2 bg-blue-900/30 rounded border border-blue-800/30 text-white">
                          {ocrResult.name || "Not detected"}
                        </div>
                      </div>
                      <div>
                        <span className="block text-gray-400 text-sm mb-1">
                          Aadhaar Number
                        </span>
                        <div className="p-2 bg-blue-900/30 rounded border border-blue-800/30 text-white font-mono">
                          {ocrResult.aadharNumber
                            ? ocrResult.aadharNumber.replace(
                                /(\d{4})(\d{4})(\d{4})/,
                                "$1 $2 $3"
                              )
                            : "Not detected"}
                        </div>
                      </div>
                    </div>

                    {/* Manual override section */}
                    <div className="mt-4 pt-4 border-t border-gray-700">
                      <p className="text-sm text-gray-400 mb-3">
                        If the extracted information is incorrect, please enter
                        the correct details below:
                      </p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-gray-300 text-sm font-medium mb-1">
                            Correct Name
                          </label>
                          <input
                            type="text"
                            value={extractedData.name}
                            onChange={(e) =>
                              setExtractedData((prev) => ({
                                ...prev,
                                name: e.target.value,
                              }))
                            }
                            className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="Enter the correct name"
                          />
                        </div>
                        <div>
                          <label className="block text-gray-300 text-sm font-medium mb-1">
                            Correct Aadhaar Number
                          </label>
                          <input
                            type="text"
                            value={extractedData.aadhaarNumber}
                            onChange={(e) =>
                              setExtractedData((prev) => ({
                                ...prev,
                                aadhaarNumber: e.target.value.replace(
                                  /\D/g,
                                  ""
                                ),
                              }))
                            }
                            className="w-full bg-gray-800/80 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="Enter the correct Aadhaar number"
                            maxLength={12}
                            pattern="\d{12}"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex justify-center mt-4 space-x-3">
                  <button
                    onClick={handleRetake}
                    className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-all duration-300"
                  >
                    Retake {aadhaarMode ? "Card" : "Photo"}
                  </button>

                  <button
                    onClick={() => {
                      setCapturedImage(null);
                      if (!aadhaarMode) {
                        setFaceCaptured(true);
                      }
                    }}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-all duration-300"
                  >
                    Confirm
                  </button>
                </div>
              </div>
            )
          )}
        </div>
      )}

      {/* Guidelines */}
      <div className="p-4 bg-gray-800/30 border border-gray-700/50 rounded-lg">
        <h5 className="text-white font-medium mb-3">Verification Guidelines</h5>
        <ul className="list-disc ml-5 text-gray-400 text-sm space-y-1">
          <li>
            Position your face or document clearly in the center of the frame
          </li>
          <li>Ensure good lighting for accurate verification</li>
          <li>Remove any obstacles (glasses, masks) for face verification</li>
          <li>Hold your Aadhaar card steady and avoid reflections</li>
          <li>Make sure all text in the Aadhaar card is clearly visible</li>
        </ul>
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between mt-8">
        <button
          onClick={onPrevStep}
          disabled={isUpdatingStatus}
          className="px-6 py-2.5 border border-gray-600 text-gray-300 font-medium rounded-lg hover:bg-gray-800 transition-all duration-300"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 mr-2 inline"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
          Previous
        </button>

        <button
          onClick={handleSubmit}
          disabled={
            isProcessing || isCameraActive || !faceCaptured || isUpdatingStatus
          }
          className={`px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-blue-900/20 flex items-center ${
            isProcessing || isCameraActive || !faceCaptured || isUpdatingStatus
              ? "opacity-50 cursor-not-allowed"
              : ""
          }`}
        >
          {isUpdatingStatus ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Updating...</span>
            </>
          ) : (
            <>
              <span>Complete Verification</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 ml-2"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
