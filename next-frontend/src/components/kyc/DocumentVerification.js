"use client";

import { useState, useRef } from "react";
import { useSession } from "next-auth/react";
import Image from "next/image";

export default function DocumentVerificationForm({
  onNextStep,
  updateFormData,
}) {
  const { data: session } = useSession();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState({ type: "", message: "" });

  // Document state
  const [documents, setDocuments] = useState({
    aadhaar: null,
    aadhaarPreview: null,
    pan: null,
    panPreview: null,
  });

  // OCR Processing state
  const [isProcessingAadhaar, setIsProcessingAadhaar] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [ocrError, setOcrError] = useState(null);
  const [ocrPerformance, setOcrPerformance] = useState(null);

  // Form data for extracted information
  const [extractedData, setExtractedData] = useState({
    name: "",
    aadhaarNumber: "",
  });

  // Handle file selection for all document types
  const handleFileChange = async (e, docType) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const previewUrl = URL.createObjectURL(file);

    setDocuments((prev) => ({
      ...prev,
      [docType]: file,
      [`${docType}Preview`]: previewUrl,
    }));

    // If this is an Aadhaar document, process it with OCR
    if (docType === "aadhaar") {
      await processAadhaarImage(file);
    }

    // Clear any previous status messages
    setStatusMessage({ type: "", message: "" });
  };

  // Process Aadhaar image with OCR using Groq AI
  const processAadhaarImage = async (file) => {
    if (!file) return;

    setIsProcessingAadhaar(true);
    setOcrResult(null);
    setOcrError(null);

    try {
      // Start performance timing
      const startTime = performance.now();

      const formData = new FormData();
      formData.append("file", file);

      console.log("Aadhaar image OCR processing...");

      const response = await fetch("/api/kyc/aadhar-ocr", {
        method: "POST",
        body: formData,
      });

      // End performance timing
      const endTime = performance.now();
      const processingTime = endTime - startTime;
      setOcrPerformance({
        time: processingTime,
        timestamp: new Date().toISOString(),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("OCR API error response:", errorText);
        throw new Error(
          `Server responded with ${response.status}: ${errorText}`
        );
      }

      const result = await response.json();
      console.log("OCR result:", result);

      if (!result.success) {
        throw new Error(result.error || "Failed to extract information");
      }

      setOcrResult(result.data);

      // Update extracted data state
      setExtractedData({
        name: result.data.name || "",
        aadhaarNumber: result.data.aadharNumber || "",
      });

      // Show success message
      setStatusMessage({
        type: "success",
        message: "Successfully extracted details from Aadhaar card!",
      });

      // Clear the message after 3 seconds
      setTimeout(() => {
        setStatusMessage({ type: "", message: "" });
      }, 3000);
    } catch (error) {
      console.error("Error processing Aadhaar image:", error);
      setOcrError(error.message);
      setStatusMessage({
        type: "error",
        message: error.message || "Failed to process Aadhaar image",
      });
    } finally {
      setIsProcessingAadhaar(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setStatusMessage({ type: "", message: "" });

    try {
      if (!session) {
        throw new Error("You must be signed in to complete KYC");
      }

      if (!documents.aadhaar || !documents.pan) {
        throw new Error("Please upload both Aadhaar and PAN card documents");
      }

      // Save the documents to storage (optional - implement if needed)
      const documentUrls = {
        aadhaar: null,
        pan: null,
      };

      // Store document files
      if (typeof updateFormData === "function") {
        updateFormData({
          aadhaarNumber: extractedData.aadhaarNumber || "",
          name: extractedData.name || "",
          documentsUploaded: true,
          documentUrls: documentUrls,
        });
      }

      setStatusMessage({
        type: "success",
        message: "Documents verified successfully!",
      });

      // Move to next step after a short delay
      setTimeout(() => {
        onNextStep();
      }, 1500);
    } catch (error) {
      console.error("Error in document verification:", error);
      setStatusMessage({
        type: "error",
        message: error.message || "Failed to complete document verification",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
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

      <div>
        <h3 className="text-xl font-semibold text-white mb-6">
          Document Verification
        </h3>
        <p className="text-gray-400 mb-4">
          Please upload clear images of your identification documents. Our AI
          system will automatically extract information from your Aadhaar card.
        </p>
      </div>

      {/* Aadhaar Card Upload with OCR */}
      <div className="space-y-4">
        <h4 className="text-lg font-medium text-white">
          Aadhaar Card <span className="text-red-400">*</span>
        </h4>
        <div className="border border-gray-700 rounded-lg p-4 bg-gray-800/30">
          <div className="space-y-4">
            <div className="flex flex-col items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-800/40 hover:bg-gray-800/60">
                {documents.aadhaarPreview ? (
                  <div className="relative w-full h-full">
                    <Image
                      src={documents.aadhaarPreview}
                      alt="Aadhaar Card Preview"
                      fill
                      className="rounded-lg object-contain p-2"
                    />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <svg
                      className="w-10 h-10 mb-3 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      ></path>
                    </svg>
                    <p className="mb-2 text-sm text-gray-400">
                      {isProcessingAadhaar
                        ? "Processing with AI..."
                        : "Click to upload or drag and drop"}
                    </p>
                    <p className="text-xs text-gray-400">
                      PNG, JPG or PDF (Max 5MB)
                    </p>
                  </div>
                )}
                <input
                  type="file"
                  name="aadhaar"
                  className="hidden"
                  accept=".png,.jpg,.jpeg"
                  onChange={(e) => handleFileChange(e, "aadhaar")}
                  disabled={isProcessingAadhaar}
                />
              </label>
            </div>

            {/* OCR Results */}
            {isProcessingAadhaar && (
              <div className="flex justify-center items-center py-4 space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
                <p className="text-blue-400">Analyzing document</p>
              </div>
            )}

            {ocrError && (
              <div className="p-3 bg-red-900/20 border border-red-700/40 rounded-lg text-red-400 text-sm">
                <p className="font-medium">Error analyzing document:</p>
                <p>{ocrError}</p>
              </div>
            )}

            {ocrResult && !isProcessingAadhaar && (
              <div className="p-4 bg-blue-900/20 border border-blue-800/40 rounded-lg mt-4">
                <div className="flex justify-between items-start">
                  <h5 className="text-blue-400 font-medium mb-3">
                    Extracted Information
                  </h5>

                  {ocrPerformance && (
                    <div className="text-xs text-gray-400">
                      Processed in {ocrPerformance.time.toFixed(0)}ms
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
                    If the extracted information is incorrect, please enter the
                    correct details below:
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
                            aadhaarNumber: e.target.value.replace(/\D/g, ""),
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
          </div>
        </div>
      </div>

      {/* PAN Card Upload */}
      <div className="space-y-4">
        <h4 className="text-lg font-medium text-white">
          PAN Card <span className="text-red-400">*</span>
        </h4>
        <div className="border border-gray-700 rounded-lg p-4 bg-gray-800/30">
          <div className="flex flex-col items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-800/40 hover:bg-gray-800/60">
              {documents.panPreview ? (
                <div className="relative w-full h-full">
                  <Image
                    src={documents.panPreview}
                    alt="PAN Card Preview"
                    fill
                    className="rounded-lg object-contain p-2"
                  />
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <svg
                    className="w-10 h-10 mb-3 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    ></path>
                  </svg>
                  <p className="mb-2 text-sm text-gray-400">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-400">
                    PNG, JPG or PDF (Max 5MB)
                  </p>
                </div>
              )}
              <input
                type="file"
                name="pan"
                className="hidden"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={(e) => handleFileChange(e, "pan")}
              />
            </label>
          </div>
        </div>
      </div>

      {/* Document Guidelines */}
      <div className="p-4 bg-gray-800/30 border border-gray-700/50 rounded-lg">
        <h5 className="text-white font-medium mb-3">Document Guidelines</h5>
        <ul className="list-disc ml-5 text-gray-400 text-sm space-y-1">
          <li>Upload clear, high-resolution images of your documents</li>
          <li>Ensure all text in the document is clearly visible</li>
          <li>Avoid glare or shadows on the document</li>
          <li>The entire document should be visible in the frame</li>
          <li>For best recognition results, use well-lit photographs</li>
        </ul>
      </div>

      {/* Tech info */}

      <div className="flex justify-end mt-8">
        <button
          type="submit"
          disabled={
            isSubmitting ||
            isProcessingAadhaar ||
            !documents.aadhaar ||
            !documents.pan
          }
          className={`px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-blue-900/20 flex items-center ${
            isSubmitting ||
            isProcessingAadhaar ||
            !documents.aadhaar ||
            !documents.pan
              ? "opacity-70 cursor-not-allowed"
              : ""
          }`}
        >
          {isSubmitting ? (
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
              <span>Processing...</span>
            </>
          ) : (
            <>
              <span>Next Step</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 ml-2"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
