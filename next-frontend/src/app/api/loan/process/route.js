import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "../../auth/[...nextauth]/route";

export async function POST(request) {
  try {
    // Check authentication
    const session = await getServerSession(authOptions);
    if (!session) {
      return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
    }

    const data = await request.json();
    
    // Call Python backend
    const response = await fetch('http://localhost:5000/process-loan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    
    return NextResponse.json(result);

  } catch (error) {
    console.error("Loan processing error:", error);
    return NextResponse.json(
      { error: "Failed to process loan application" },
      { status: 500 }
    );
  }
}