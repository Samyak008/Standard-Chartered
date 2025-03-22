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

  // Handle starting a call
  const handleCall = async () => {
    setCallStatus(CALL_STATUS.CONNECTING);

    const userName = session?.user?.name || "User";
    const userId = session?.user?.id || "";

    try {
      await vapi.start(
        process.env.NEXT_PUBLIC_VAPI_WORKFLOW_ID || financialAdvisor,
        {
          variableValues: {
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
          },
        }
      );
    } catch (error) {
      console.error("Error starting call:", error);
      setCallStatus(CALL_STATUS.INACTIVE);
    }
  };

  // Handle ending a call
  const handleDisconnect = () => {
    vapi.stop();
    setCallStatus(CALL_STATUS.FINISHED);
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
      </div>
    </DashboardLayout>
  );
}
