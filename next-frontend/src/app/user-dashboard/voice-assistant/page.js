"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import Image from "next/image";
import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { vapi } from "@/lib/vapi.sdk";
import { financialAdvisor } from "@/constants";

// Helper function to combine classNames conditionally
const cn = (...classes) => {
  return classes.filter(Boolean).join(" ");
};

// Define call status enum
const CALL_STATUS = {
  INACTIVE: "INACTIVE",
  CONNECTING: "CONNECTING",
  ACTIVE: "ACTIVE",
  FINISHED: "FINISHED",
};

export default function VoiceAssistant() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [callStatus, setCallStatus] = useState(CALL_STATUS.INACTIVE);
  const [messages, setMessages] = useState([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [lastMessage, setLastMessage] = useState("");
  const [userProfile, setUserProfile] = useState(null);
  const [debugInfo, setDebugInfo] = useState({
    callStarted: false,
    variables: null,
    callEnded: false,
    apiCalled: false,
    apiResponse: null,
  });
  const [manualUserData, setManualUserData] = useState({});
  const [apiResults, setApiResults] = useState(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/login");
    }
  }, [status, router]);

  // Set up VAPI event listeners
  useEffect(() => {
    const onCallStart = () => {
      setCallStatus(CALL_STATUS.ACTIVE);
    };

    const onCallEnd = () => {
      setCallStatus(CALL_STATUS.FINISHED);
    };

    const onMessage = (message) => {
      if (message.type === "transcript" && message.transcriptType === "final") {
        const newMessage = { role: message.role, content: message.transcript };
        setMessages((prev) => [...prev, newMessage]);
      }
    };

    const onSpeechStart = () => {
      console.log("speech start");
      setIsSpeaking(true);
    };

    const onSpeechEnd = () => {
      console.log("speech end");
      setIsSpeaking(false);
    };

    const onError = (error) => {
      console.log("Error:", error);
    };

    // Add event listeners
    vapi.on("call-start", onCallStart);
    vapi.on("call-end", onCallEnd);
    vapi.on("message", onMessage);
    vapi.on("speech-start", onSpeechStart);
    vapi.on("speech-end", onSpeechEnd);
    vapi.on("error", onError);

    // Clean up event listeners
    return () => {
      vapi.off("call-start", onCallStart);
      vapi.off("call-end", onCallEnd);
      vapi.off("message", onMessage);
      vapi.off("speech-start", onSpeechStart);
      vapi.off("speech-end", onSpeechEnd);
      vapi.off("error", onError);
    };
  }, []);

  // Fetch user profile when session is available
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (status !== "authenticated") return;

      try {
        const response = await fetch("/api/user/profile");
        if (!response.ok) {
          throw new Error("Failed to fetch user profile");
        }
        const data = await response.json();
        setUserProfile(data.user);
      } catch (error) {
        console.error("Error fetching user profile:", error);
      }
    };

    fetchUserProfile();
  }, [status]);

  // Update last message when messages change
  useEffect(() => {
    if (messages.length > 0) {
      setLastMessage(messages[messages.length - 1].content);
    }
  }, [messages]);

  // IMPORTANT: Move this useEffect to the top level with other hooks
  // This useEffect tracks and saves conversations when finished
  useEffect(() => {
    const saveConversationToMongo = async () => {
      if (callStatus === CALL_STATUS.FINISHED && messages.length > 0) {
        try {
          setDebugInfo((prev) => ({ ...prev, apiCalled: true }));

          // Extract user data from messages
          const userData = extractUserDataFromConversation(messages);

          // Get MongoDB ObjectId from session
          const userId =
            session?.user?.id ||
            session?.user?._id ||
            "67dd8a40c5a37685131d95c6";

          // Map missing values to valid enum values that match your MongoDB schema
          const genderMapping = {
            "Not specified": "Other", // Use "Other" instead of "Not specified"
            Male: "Male",
            Female: "Female",
          };

          const maritalStatusMapping = {
            "Not specified": "Single", // Default to Single if not specified
            Single: "Single",
            Married: "Married",
            Divorced: "Divorced",
            Widowed: "Widowed",
          };

          // Ensure we have valid enum values
          const gender = genderMapping[userData.gender || "Not specified"];
          const maritalStatus =
            maritalStatusMapping[userData.maritalStatus || "Not specified"];

          console.log("Using MongoDB ObjectId:", userId);
          console.log("Mapped gender:", gender);
          console.log("Mapped marital status:", maritalStatus);

          const response = await fetch("/api/vapi/generate", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              age: userData.age || 21,
              gender: gender, // Use mapped value
              maritalStatus: maritalStatus, // Use mapped value
              educationLevel: userData.educationLevel || "Bachelor's",
              employmentStatus: userData.employmentStatus || "Student",
              incomeType: userData.incomeType || "Fixed",
              additionalIncome: userData.additionalIncome || false,
              existingLoan: userData.existingLoan || false,
              monthlyIncome: userData.monthlyIncome || 0,
              userid: userId,
            }),
          });

          const data = await response.json();
          setDebugInfo((prev) => ({ ...prev, apiResponse: data }));

          console.log("API Response:", data);

          if (data.success) {
            // Show success notification and set results to display
            setApiResults(data.data);
            alert(
              "Your conversation with the financial assistant has been analyzed successfully!"
            );
          } else {
            throw new Error(data.error || "Unknown error");
          }
        } catch (error) {
          console.error("Error saving conversation to MongoDB:", error);
          setDebugInfo((prev) => ({ ...prev, apiError: error.message }));
        }
      }
    };

    saveConversationToMongo();
  }, [callStatus, messages, session?.user?.id]);

  // Add this useEffect at the top level to debug session data issues
  useEffect(() => {
    if (session) {
      console.log("Session Object:", session);
      console.log("User ID:", session.user?.id);
      console.log("User ID type:", typeof session.user?.id);
    }
  }, [session]);

  // Function to extract user data from conversation
  const extractUserDataFromConversation = (messages) => {
    // Initialize with default values
    const userData = {
      age: null,
      gender: null,
      maritalStatus: null,
      educationLevel: null,
      employmentStatus: null,
      incomeType: "Fixed", // Default
      additionalIncome: false,
      existingLoan: false,
      monthlyIncome: null,
    };

    // Search through user messages for relevant information
    for (const msg of messages) {
      const content = msg.content.toLowerCase();

      // Extract age
      const ageMatch = content.match(
        /(\b[1-9][0-9]\b|\b[1-9]\b) years old|age is (\b[1-9][0-9]\b|\b[1-9]\b)/i
      );
      if (ageMatch) {
        userData.age = parseInt(ageMatch[1] || ageMatch[2]);
      }

      // Extract gender
      if (content.includes("male") && !content.includes("female")) {
        userData.gender = "Male";
      } else if (content.includes("female")) {
        userData.gender = "Female";
      }

      // Extract marital status
      if (content.includes("single")) {
        userData.maritalStatus = "Single";
      } else if (content.includes("married")) {
        userData.maritalStatus = "Married";
      } else if (content.includes("divorced")) {
        userData.maritalStatus = "Divorced";
      } else if (content.includes("widow")) {
        userData.maritalStatus = "Widowed";
      }

      // Extract education
      if (content.includes("bachelor") || content.includes("undergraduate")) {
        userData.educationLevel = "Bachelor's";
      } else if (content.includes("master") || content.includes("mba")) {
        userData.educationLevel = "Master's";
      } else if (content.includes("phd") || content.includes("doctorate")) {
        userData.educationLevel = "Doctorate";
      } else if (
        content.includes("high school") ||
        content.includes("secondary")
      ) {
        userData.educationLevel = "Secondary";
      }

      // Extract employment
      if (content.includes("employed")) {
        userData.employmentStatus = "Employed";
      } else if (
        content.includes("self-employed") ||
        content.includes("freelance")
      ) {
        userData.employmentStatus = "Self-employed";
      } else if (content.includes("business owner")) {
        userData.employmentStatus = "Business Owner";
      } else if (content.includes("student")) {
        userData.employmentStatus = "Student";
      } else if (content.includes("retired")) {
        userData.employmentStatus = "Retired";
      } else if (content.includes("unemployed")) {
        userData.employmentStatus = "Unemployed";
      }

      // Extract income type
      if (
        content.includes("variable income") ||
        content.includes("commission")
      ) {
        userData.incomeType = "Variable";
      } else if (
        content.includes("fixed income") ||
        content.includes("salary")
      ) {
        userData.incomeType = "Fixed";
      } else if (content.includes("mixed income")) {
        userData.incomeType = "Mixed";
      }

      // Extract additional income
      if (
        content.includes("additional income") ||
        content.includes("side income") ||
        content.includes("extra income")
      ) {
        userData.additionalIncome = true;
      }

      // Extract existing loan
      if (
        content.includes("existing loan") ||
        content.includes("current loan") ||
        content.includes("already have a loan")
      ) {
        userData.existingLoan = true;
      }

      // Extract monthly income
      const incomeMatch = content.match(
        /(\d+)[k\s]*(?:per month|monthly|a month|income is|earn)/i
      );
      if (incomeMatch) {
        let income = parseInt(incomeMatch[1]);
        if (content.includes("k") || content.includes("thousand")) {
          income *= 1000;
        }
        userData.monthlyIncome = income;
      }
    }

    // Fill in missing data from user profile if available
    if (userProfile) {
      if (!userData.age && userProfile.age) userData.age = userProfile.age;
      if (!userData.gender && userProfile.gender)
        userData.gender = userProfile.gender;
      if (!userData.maritalStatus && userProfile.marital_status)
        userData.maritalStatus = userProfile.marital_status;
      if (!userData.educationLevel && userProfile.education_level)
        userData.educationLevel = userProfile.education_level;
      if (!userData.employmentStatus && userProfile.employment_status)
        userData.employmentStatus = userProfile.employment_status;
      if (!userData.monthlyIncome && userProfile.income)
        userData.monthlyIncome = userProfile.income;
    }

    return userData;
  };

  // Handle starting a call
  const handleCall = async () => {
    setCallStatus(CALL_STATUS.CONNECTING);
    setDebugInfo((prev) => ({ ...prev, callStarted: true }));

    const userName = session?.user?.name || "User";
    const userId = session?.user?.id || "";

    // Create variable values to send to VAPI
    const variableValues = {
      username: userName,
      userid: userId,
      // Add user profile data if available
      ...(userProfile && {
        kycStatus: userProfile.kycStatus || "Not Started",
        age: userProfile.age || "",
        gender: userProfile.gender || "",
        maritalStatus: userProfile.marital_status || "",
        educationLevel: userProfile.education_level || "",
        employmentStatus: userProfile.employment_status || "",
        monthlyIncome: userProfile.income || 0,
      }),
      // Tell assistant to collect specific data
      endingScript:
        "Thank you for using our financial assistant. I'll analyze your information to provide personalized loan recommendations. Could you please confirm your age, employment status, monthly income, and whether you have any existing loans before we end this call?",
    };

    // Log what we're sending to VAPI
    setDebugInfo((prev) => ({ ...prev, variables: variableValues }));
    console.log("Starting call with variables:", variableValues);

    try {
      await vapi.start(
        process.env.NEXT_PUBLIC_VAPI_WORKFLOW_ID || financialAdvisor,
        { variableValues }
      );
    } catch (error) {
      console.error("Error starting call:", error);
      setCallStatus(CALL_STATUS.INACTIVE);
      setDebugInfo((prev) => ({ ...prev, callError: error.message }));
    }
  };

  // Handle ending a call
  const handleDisconnect = () => {
    vapi.stop();
    setCallStatus(CALL_STATUS.FINISHED);
  };

  // Add this function to handle manual submissions
  const handleManualSubmit = async () => {
    try {
      // Combine extracted and manually entered data
      const userData = {
        ...extractUserDataFromConversation(messages),
        ...manualUserData,
      };

      // Ensure required fields have values
      const requiredFields = [
        "age",
        "gender",
        "maritalStatus",
        "educationLevel",
        "employmentStatus",
        "incomeType",
        "monthlyIncome",
      ];

      const missingFields = requiredFields.filter((field) => !userData[field]);

      if (missingFields.length > 0) {
        alert(
          `Please fill in these required fields: ${missingFields.join(", ")}`
        );
        return;
      }

      // Get the user ID directly from session
      const userId = session?.user?.id || "65a87b2e1f85a1234567890a";
      console.log("Submitting with user ID:", userId);

      console.log("Submitting data to API:", userData);

      const response = await fetch("/api/vapi/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          age: parseInt(userData.age),
          gender: userData.gender,
          maritalStatus: userData.maritalStatus,
          educationLevel: userData.educationLevel,
          employmentStatus: userData.employmentStatus,
          incomeType: userData.incomeType,
          additionalIncome: userData.additionalIncome || false,
          existingLoan: userData.existingLoan || false,
          monthlyIncome: parseInt(userData.monthlyIncome),
          userid: userId || "65a87b2e1f85a1234567890a", // Use actual string ID
        }),
      });

      const data = await response.json();

      if (data.success) {
        // Show recommendations
        setApiResults(data.data);
        alert("Analysis complete! Your loan recommendations are ready.");
      } else {
        throw new Error(data.error || "Unknown error");
      }
    } catch (error) {
      console.error("Error submitting data manually:", error);
      alert("An error occurred. Please try again: " + error.message);
    }
  };

  // Show loading state while checking authentication
  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-950 to-slate-900">
        <div className="backdrop-blur-lg bg-white/5 p-8 rounded-2xl border border-gray-700/30 shadow-lg flex items-center space-x-4">
          <div className="w-8 h-8 border-4 border-t-blue-500 border-r-transparent border-b-purple-500 border-l-transparent rounded-full animate-spin"></div>
          <p className="text-white font-medium">Loading your assistant...</p>
        </div>
      </div>
    );
  }

  // Check for session before rendering content
  if (!session) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col items-center space-y-8 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-white">
          Financial Voice Assistant
        </h2>

        <div className="w-full flex flex-col items-center space-y-8 px-4">
          {/* Assistant and User Cards */}
          <div className="w-full flex flex-col md:flex-row justify-between items-center space-y-6 md:space-y-0 md:space-x-6">
            {/* AI Assistant Card */}
            <div className="w-full md:w-1/2 bg-blue-600/10 backdrop-blur-md p-6 rounded-xl border border-blue-500/30 flex items-center space-x-4">
              <div className="relative">
                <Image
                  src="/ai-avatar.png" // Replace with your actual avatar
                  alt="AI Assistant"
                  width={65}
                  height={65}
                  className="rounded-full"
                />
                {isSpeaking && (
                  <span className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 rounded-full animate-pulse"></span>
                )}
              </div>
              <div>
                <h3 className="text-lg font-medium text-white">
                  Financial Assistant
                </h3>
                <p className="text-sm text-blue-300">
                  {callStatus === CALL_STATUS.ACTIVE
                    ? "Speaking..."
                    : "Ready to assist you"}
                </p>
              </div>
            </div>

            {/* User Card */}
            <div className="w-full md:w-1/2 bg-purple-600/10 backdrop-blur-md p-6 rounded-xl border border-purple-500/30 flex items-center space-x-4">
              <Image
                src="/user-avatar.png" // Replace with actual user avatar
                alt="User"
                width={65}
                height={65}
                className="rounded-full"
              />
              <div>
                <h3 className="text-lg font-medium text-white">
                  {session.user?.name || "User"}
                </h3>
                <p className="text-sm text-purple-300">
                  {callStatus === CALL_STATUS.ACTIVE
                    ? "In conversation"
                    : "Ready to talk"}
                </p>
              </div>
            </div>
          </div>

          {/* Conversation Display */}
          {messages.length > 0 && (
            <div className="w-full bg-gray-800/50 backdrop-blur-md border border-gray-700/50 rounded-xl p-6 max-h-64 overflow-y-auto">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`mb-4 ${
                    msg.role === "user" ? "text-right" : "text-left"
                  }`}
                >
                  <span className="inline-block text-xs text-gray-400 mb-1">
                    {msg.role === "user" ? "You" : "Assistant"}
                  </span>
                  <p
                    className={cn(
                      "inline-block p-3 rounded-lg max-w-[80%] animate-fadeIn",
                      msg.role === "user"
                        ? "bg-purple-600/20 text-purple-100"
                        : "bg-blue-600/20 text-blue-100"
                    )}
                  >
                    {msg.content}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Call Controls */}
          <div className="w-full flex justify-center pt-4">
            {callStatus !== CALL_STATUS.ACTIVE ? (
              <button
                className={cn(
                  "relative px-8 py-3 rounded-full font-medium transition-all duration-300",
                  callStatus === CALL_STATUS.CONNECTING
                    ? "bg-yellow-600 text-white cursor-wait"
                    : "bg-green-600 hover:bg-green-700 text-white"
                )}
                onClick={handleCall}
                disabled={callStatus === CALL_STATUS.CONNECTING}
              >
                <span
                  className={cn(
                    "absolute w-full h-full rounded-full bg-green-500/50 animate-ping opacity-75",
                    callStatus !== CALL_STATUS.CONNECTING && "hidden"
                  )}
                ></span>
                <span className="relative flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 8V5z"
                    />
                  </svg>
                  {callStatus === CALL_STATUS.CONNECTING
                    ? "Connecting..."
                    : "Start Voice Assistant"}
                </span>
              </button>
            ) : (
              <button
                className="px-8 py-3 rounded-full bg-red-600 hover:bg-red-700 text-white font-medium transition-colors duration-300 flex items-center"
                onClick={handleDisconnect}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
                End Call
              </button>
            )}
          </div>
        </div>

        {/* Display API Results if available */}
        {apiResults && (
          <div className="w-full bg-gradient-to-br from-green-900/30 to-blue-900/30 backdrop-blur-md border border-green-500/20 rounded-xl p-6 mt-8">
            <h3 className="text-2xl font-bold text-white mb-4">
              Your Loan Recommendations
            </h3>

            <div className="flex items-center mb-6">
              <div className="w-1/2 flex items-center">
                <div
                  className={`w-3 h-3 rounded-full mr-2 ${
                    apiResults.riskAssessment === "Low"
                      ? "bg-green-500"
                      : apiResults.riskAssessment === "Medium"
                      ? "bg-yellow-500"
                      : "bg-red-500"
                  }`}
                ></div>
                <span className="text-gray-300 mr-2">Risk Assessment:</span>
                <span className="font-semibold text-white">
                  {apiResults.riskAssessment}
                </span>
              </div>

              <div className="w-1/2">
                <span className="text-gray-300 mr-2">Affordability Score:</span>
                <span className="font-semibold text-white">
                  {apiResults.affordabilityScore}/100
                </span>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="text-lg font-medium text-white mb-3">
                Suggested Loans
              </h4>
              <div className="flex flex-wrap gap-2">
                {apiResults.suggestedLoans.map((loan, index) => (
                  <div
                    key={index}
                    className="bg-blue-600/20 border border-blue-500/30 text-white px-4 py-2 rounded-md"
                  >
                    {loan}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-lg font-medium text-white mb-3">Analysis</h4>
              <p className="text-gray-300 leading-relaxed">
                {apiResults.reasoningExplanation}
              </p>
            </div>

            <button
              className="mt-6 bg-green-600 hover:bg-green-700 text-white font-medium px-5 py-2 rounded-md transition-colors flex items-center"
              onClick={() => router.push("/user-dashboard/loan-applications")}
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Apply for a Loan
            </button>
          </div>
        )}

        {/* Manual entry form for when voice data is incomplete */}
        {callStatus === CALL_STATUS.FINISHED &&
          messages.length > 0 &&
          !apiResults && (
            <div className="w-full bg-blue-900/30 backdrop-blur-sm border border-blue-700/30 rounded-xl p-6 mt-8">
              <h3 className="text-lg font-semibold text-white mb-3">
                Confirm Your Information
              </h3>
              <p className="text-gray-300 mb-4">
                Please verify or update your details before analysis:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-blue-300 mb-1">
                    Age
                  </label>
                  <input
                    type="number"
                    className="w-full bg-blue-950/60 border border-blue-800 rounded-md p-2 text-white"
                    value={manualUserData.age || ""}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        age: e.target.value,
                      })
                    }
                  />
                </div>

                <div>
                  <label className="block text-sm text-blue-300 mb-1">
                    Gender
                  </label>
                  <select
                    className="w-full bg-blue-950/60 border border-blue-800 rounded-md p-2 text-white"
                    value={manualUserData.gender || ""}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        gender: e.target.value,
                      })
                    }
                  >
                    <option value="">Select...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-blue-300 mb-1">
                    Marital Status
                  </label>
                  <select
                    className="w-full bg-blue-950/60 border border-blue-800 rounded-md p-2 text-white"
                    value={manualUserData.maritalStatus || ""}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        maritalStatus: e.target.value,
                      })
                    }
                  >
                    <option value="">Select...</option>
                    <option value="Single">Single</option>
                    <option value="Married">Married</option>
                    <option value="Divorced">Divorced</option>
                    <option value="Widowed">Widowed</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-blue-300 mb-1">
                    Education Level
                  </label>
                  <select
                    className="w-full bg-blue-950/60 border border-blue-800 rounded-md p-2 text-white"
                    value={manualUserData.educationLevel || ""}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        educationLevel: e.target.value,
                      })
                    }
                  >
                    <option value="">Select...</option>
                    <option value="Secondary">Secondary</option>
                    <option value="Bachelor's">Bachelor's</option>
                    <option value="Master's">Master's</option>
                    <option value="Doctorate">Doctorate</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-blue-300 mb-1">
                    Employment Status
                  </label>
                  <select
                    className="w-full bg-blue-950/60 border border-blue-800 rounded-md p-2 text-white"
                    value={manualUserData.employmentStatus || ""}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        employmentStatus: e.target.value,
                      })
                    }
                  >
                    <option value="">Select...</option>
                    <option value="Employed">Employed</option>
                    <option value="Self-employed">Self-employed</option>
                    <option value="Business Owner">Business Owner</option>
                    <option value="Student">Student</option>
                    <option value="Retired">Retired</option>
                    <option value="Unemployed">Unemployed</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-blue-300 mb-1">
                    Monthly Income
                  </label>
                  <input
                    type="number"
                    className="w-full bg-blue-950/60 border border-blue-800 rounded-md p-2 text-white"
                    value={manualUserData.monthlyIncome || ""}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        monthlyIncome: e.target.value,
                      })
                    }
                  />
                </div>

                <div>
                  <label className="block text-sm text-blue-300 mb-1">
                    Income Type
                  </label>
                  <select
                    className="w-full bg-blue-950/60 border border-blue-800 rounded-md p-2 text-white"
                    value={manualUserData.incomeType || "Fixed"}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        incomeType: e.target.value,
                      })
                    }
                  >
                    <option value="Fixed">Fixed</option>
                    <option value="Variable">Variable</option>
                    <option value="Mixed">Mixed</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="additionalIncome"
                    className="mr-2"
                    checked={manualUserData.additionalIncome || false}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        additionalIncome: e.target.checked,
                      })
                    }
                  />
                  <label
                    htmlFor="additionalIncome"
                    className="text-sm text-blue-300"
                  >
                    I have additional income sources
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="existingLoan"
                    className="mr-2"
                    checked={manualUserData.existingLoan || false}
                    onChange={(e) =>
                      setManualUserData({
                        ...manualUserData,
                        existingLoan: e.target.checked,
                      })
                    }
                  />
                  <label
                    htmlFor="existingLoan"
                    className="text-sm text-blue-300"
                  >
                    I have existing loans
                  </label>
                </div>

                <button
                  className="md:col-span-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-md transition-colors"
                  onClick={handleManualSubmit}
                >
                  Analyze My Financial Profile
                </button>
              </div>
            </div>
          )}

        {/* Instructions Panel */}
        <div className="w-full bg-gray-900/30 backdrop-blur-sm border border-gray-700/30 rounded-xl p-6 mt-8">
          <h3 className="text-lg font-semibold text-white mb-3">
            How to use the Voice Assistant
          </h3>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-start">
              <span className="text-green-400 mr-2">1.</span>
              Click the Start Voice Assistant button to begin a conversation.
            </li>
            <li className="flex items-start">
              <span className="text-green-400 mr-2">2.</span>
              Ask about loan options, eligibility requirements, or financial
              advice.
            </li>
            <li className="flex items-start">
              <span className="text-green-400 mr-2">3.</span>
              The assistant can help check your loan eligibility based on your
              profile.
            </li>
            <li className="flex items-start">
              <span className="text-green-400 mr-2">4.</span>
              End the call by clicking the End Call button when you are
              finished.
            </li>
          </ul>
          <div className="mt-4 pt-4 border-t border-gray-700/50">
            <h4 className="font-medium text-white mb-2">Example questions:</h4>
            <p className="text-blue-300 mb-1">
              • What loan options are available for me?
            </p>
            <p className="text-blue-300 mb-1">
              • How can I improve my eligibility for a home loan?
            </p>
            <p className="text-blue-300">
              • What documents do I need for a car loan application?
            </p>
          </div>
        </div>

        {/* Debug Panel - only show in development */}
        {process.env.NODE_ENV === "development" && (
          <div className="w-full mt-8 bg-black/60 backdrop-blur-sm border border-yellow-500/30 rounded-xl p-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-yellow-400 font-mono">Debug Info</h3>
              <button
                onClick={() => console.log({ session, debugInfo, messages })}
                className="text-xs bg-yellow-500/20 text-yellow-300 px-2 py-1 rounded"
              >
                Log to Console
              </button>
            </div>
            <div className="font-mono text-xs text-yellow-200/70 overflow-auto max-h-40">
              <div>User ID: {session?.user?.id || "Not available"}</div>
              <div>Call Status: {callStatus}</div>
              <div>Messages: {messages.length}</div>
              <div>API Called: {debugInfo.apiCalled ? "Yes" : "No"}</div>
              <div>
                API Response:{" "}
                {debugInfo.apiResponse
                  ? JSON.stringify(debugInfo.apiResponse).substring(0, 50) +
                    "..."
                  : "None"}
              </div>
              {debugInfo.apiError && (
                <div className="text-red-400">Error: {debugInfo.apiError}</div>
              )}
              {lastMessage && (
                <div>Last Message: {lastMessage.substring(0, 50)}...</div>
              )}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
