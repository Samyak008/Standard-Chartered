"use client";

export default function DocumentVerification({
  onNextStep,
  onPrevStep,
  updateFormData,
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    updateFormData({ documentsVerified: true });
    onNextStep();
  };

  return (
    <div className="space-y-6">
      <p className="text-gray-300">
        In this step, we would normally verify the documents you have uploaded.
        For this demo, we will simulate document verification.
      </p>

      <div className="p-4 bg-gray-800/70 rounded-lg border border-gray-700 mb-6">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-blue-600/20 flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 text-blue-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <span className="text-gray-200 font-medium">
            Document Verification
          </span>
        </div>
        <p className="text-gray-400 text-sm pl-11">
          We are checking the authenticity of your documents. This usually takes
          a few minutes.
        </p>
      </div>

      <div className="flex justify-between">
        <button
          onClick={onPrevStep}
          className="px-6 py-2.5 border border-gray-600 text-gray-300 font-medium rounded-lg hover:bg-gray-800 transition-all duration-300 flex items-center"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 mr-2"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
          <span>Previous</span>
        </button>

        <button
          onClick={handleSubmit}
          className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium rounded-lg transition-all duration-300 shadow-md shadow-blue-900/20 flex items-center"
        >
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
        </button>
      </div>
    </div>
  );
}
