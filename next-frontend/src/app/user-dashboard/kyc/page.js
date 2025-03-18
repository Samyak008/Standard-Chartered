"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import PersonalDetailsForm from "@/components/kyc/PersonalDetailsForm";
import DocumentVerification from "@/components/kyc/DocumentVerification";
import FaceVerification from "@/components/kyc/FaceVerification";
import VerificationComplete from "@/components/kyc/VerificationComplete";

export default function KycVerificationPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    personal: {},
    documents: {},
    faceVerification: false,
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/login");
    }
  }, [status, router]);

  const handleNextStep = () => {
    setCurrentStep((prev) => prev + 1);
  };

  const handlePrevStep = () => {
    setCurrentStep((prev) => Math.max(1, prev - 1));
  };

  const updateFormData = (step, data) => {
    setFormData((prev) => {
      if (step === 1) return { ...prev, personal: data };
      if (step === 2) return { ...prev, documents: data };
      if (step === 3) return { ...prev, faceVerification: data };
      return prev;
    });
  };

  // Show loading state while checking authentication
  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-950 to-slate-900">
        <div className="backdrop-blur-lg bg-white/5 p-8 rounded-2xl border border-gray-700/30 shadow-lg flex items-center space-x-4">
          <div className="w-8 h-8 border-4 border-t-blue-500 border-r-transparent border-b-purple-500 border-l-transparent rounded-full animate-spin"></div>
          <p className="text-white font-medium">Loading KYC verification...</p>
        </div>
      </div>
    );
  }

  // Render step progress indicator
  const renderStepIndicator = () => {
    return (
      <div className="flex items-center justify-center mb-8">
        {[1, 2, 3, 4].map((step) => (
          <div key={step} className="flex items-center">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center ${
                currentStep === step
                  ? "bg-blue-600 text-white"
                  : currentStep > step
                  ? "bg-green-600 text-white"
                  : "bg-gray-700 text-gray-400"
              }`}
            >
              {currentStep > step ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                step
              )}
            </div>
            {step < 4 && (
              <div
                className={`w-12 h-1 ${
                  currentStep > step ? "bg-green-600" : "bg-gray-700"
                }`}
              ></div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-8">
          <div className="bg-blue-600/20 p-3 rounded-lg mr-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">KYC Verification</h1>
            <p className="text-gray-300">
              Complete your identity verification process
            </p>
          </div>
        </div>

        {/* KYC Status Card */}
        <div className="backdrop-blur-md bg-gray-800/50 p-6 rounded-xl border border-gray-700/50 mb-8">
          <div className="flex items-center">
            <div className="h-16 w-16 rounded-full bg-yellow-600/20 flex items-center justify-center text-yellow-500 mr-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">
                {currentStep < 4
                  ? "Verification In Progress"
                  : "Verification Complete"}
              </h3>
              <p className="text-gray-300 mt-1">
                {currentStep < 4
                  ? "Please complete all steps of the verification process."
                  : "Your identity has been verified successfully!"}
              </p>
            </div>
          </div>
        </div>

        {/* Step indicator */}
        {renderStepIndicator()}

        {/* Multi-step form content */}
        <div className="backdrop-blur-md bg-gray-800/50 p-6 rounded-xl border border-gray-700/50">
          {currentStep === 1 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-6">
                Personal Information
              </h3>
              <PersonalDetailsForm
                onNextStep={handleNextStep}
                updateFormData={(data) => updateFormData(1, data)}
              />
            </div>
          )}

          {currentStep === 2 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-6">
                Document Verification
              </h3>
              <DocumentVerification
                onNextStep={handleNextStep}
                onPrevStep={handlePrevStep}
                updateFormData={(data) => updateFormData(2, data)}
              />
            </div>
          )}

          {currentStep === 3 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-6">
                Face Verification
              </h3>
              <FaceVerification
                onNextStep={handleNextStep}
                onPrevStep={handlePrevStep}
                updateFormData={(data) => updateFormData(3, data)}
              />
            </div>
          )}

          {currentStep === 4 && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-6">
                Verification Complete
              </h3>
              <VerificationComplete formData={formData} />
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
