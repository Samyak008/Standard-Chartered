"use client";

import { useState } from 'react';
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import DashboardLayout from "@/components/dashboard/DashboardLayout";

export default function LoanEligibilityPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleAnalyze = async () => {
    setIsLoading(true);
    
    const loanData = {
      loan_purpose: "personal",
      loan_amount: 100000,
      loan_term: "24 months",
      credit_score: 750,
      income: 60000,
      employment_length: "2 years",
      debt_to_income_ratio: 0.3,
      has_coi: true,
      has_collateral: false,
      has_employment_guarantee: true
    };

    try {
      const response = await fetch('http://127.0.0.1:5000/process-loan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loanData)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to process loan analysis');
      }

      // Log the response data for debugging
      console.log('API Response:', data);

      setResults(data);
      
    } catch (error) {
      console.error('Error:', error);
      // Add error display in UI
      setResults({
        error: error.message
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Redirect if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/login");
    }
  }, [status, router]);

  // Show loading state while checking authentication
  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-purple-950 to-slate-900">
        <div className="backdrop-blur-lg bg-white/5 p-8 rounded-2xl border border-gray-700/30 shadow-lg flex items-center space-x-4">
          <div className="w-8 h-8 border-4 border-t-blue-500 border-r-transparent border-b-purple-500 border-l-transparent rounded-full animate-spin"></div>
          <p className="text-white font-medium">Loading loan eligibility...</p>
        </div>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-8">
          <div className="bg-purple-600/20 p-3 rounded-lg mr-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-purple-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white">Loan Analysis</h1>
            <p className="text-gray-300">Get instant loan recommendations</p>
          </div>
        </div>

        {/* Analysis Button */}
        <div className="backdrop-blur-md bg-gray-800/50 p-6 rounded-xl border border-gray-700/50 mb-8">
          <button
            onClick={handleAnalyze}
            disabled={isLoading}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-t-transparent border-white rounded-full animate-spin mr-2"></div>
                Analyzing...
              </div>
            ) : (
              'Generate Loan Analysis'
            )}
          </button>
        </div>

        {/* Results */}
        {results && (
          <div className="space-y-6">
            {results.error ? (
              <div className="backdrop-blur-md bg-red-900/50 p-6 rounded-xl border border-red-500/20">
                <h3 className="text-2xl font-semibold text-white mb-4">Error</h3>
                <div className="text-red-200">{results.error}</div>
              </div>
            ) : (
              <>
                {/* Loan Options */}
                <div className="backdrop-blur-md bg-gray-800/50 p-6 rounded-xl border border-purple-500/20">
                  <h3 className="text-2xl font-semibold text-white mb-4 flex items-center">
                    <span className="bg-purple-600/20 p-2 rounded-lg mr-3">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </span>
                    Loan Options
                  </h3>
                  <div className="prose prose-invert max-w-none">
                    <h4 className="text-lg font-medium text-purple-300">Analysis</h4>
                    <div dangerouslySetInnerHTML={{ __html: marked(results.loan_options.raw_text) }} />
                    
                    {results.loan_options.recommendations.length > 0 && (
                        <>
                            <h4 className="text-lg font-medium text-purple-300 mt-4">Key Recommendations</h4>
                            <ul>
                                {results.loan_options.recommendations.map((rec, index) => (
                                    <li key={index}>{rec}</li>
                                ))}
                            </ul>
                        </>
                    )}
                  </div>
                </div>

                {/* Risk Analysis */}
                <div className="backdrop-blur-md bg-gray-800/50 p-6 rounded-xl border border-purple-500/20">
                  <h3 className="text-2xl font-semibold text-white mb-4 flex items-center">
                    <span className="bg-purple-600/20 p-2 rounded-lg mr-3">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                      </svg>
                    </span>
                    Risk Analysis
                  </h3>
                  <div className="prose prose-invert max-w-none">
                    <h4 className="text-lg font-medium text-purple-300">Risk Assessment</h4>
                    <div dangerouslySetInnerHTML={{ __html: marked(results.risk_analysis.raw_text) }} />
                    
                    <div className="mt-4">
                        <p className="text-sm text-purple-300">Risk Level: 
                            <span className={`ml-2 ${getRiskLevelColor(results.risk_analysis.risk_level)}`}>
                                {results.risk_analysis.risk_level}
                            </span>
                        </p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
