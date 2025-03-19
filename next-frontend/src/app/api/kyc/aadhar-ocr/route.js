import { NextResponse } from "next/server";

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions";

export async function POST(request) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");

    if (!file) {
      return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
    }

    // Convert file to base64
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const base64Image = buffer.toString("base64");

    // Construct Data URL (needed for Groq API)
    const mimeType = file.type || "image/jpeg";
    const base64Url = `data:${mimeType};base64,${base64Image}`;

    console.log("Calling Groq API for OCR processing...");

    // Make API request to Groq with a more detailed prompt
    const response = await fetch(GROQ_API_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.2-90b-vision-preview", // Using a vision-capable model
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: `This is an Indian Aadhaar card image. Extract the following information:
                1. The full name of the person (in English)
                2. The 12-digit Aadhaar number (often in format: #### #### ####)
                
                Return ONLY a valid JSON object with these two keys:
                {
                  "name": "The extracted name",
                  "aadharNumber": "The 12-digit number with no spaces"
                }`,
              },
              {
                type: "image_url",
                image_url: { url: base64Url },
              },
            ],
          },
        ],
        temperature: 0.1, // Lower temperature for more deterministic output
        max_tokens: 500,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Groq API error:", errorData);
      throw new Error(
        errorData.error?.message || "Failed to process image with Groq AI"
      );
    }

    const groqData = await response.json();
    console.log("Groq API response received");

    // Extract the JSON from the model response
    let extractedText = groqData.choices?.[0]?.message?.content || "";
    console.log("Raw extracted text:", extractedText);

    // Try to parse the JSON from the response
    let extractedInfo = { name: null, aadharNumber: null };

    try {
      // First, try to find JSON in the text if it's wrapped in markdown or other text
      const jsonMatch = extractedText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        extractedInfo = JSON.parse(jsonMatch[0]);
      } else {
        // If no JSON format is detected, try to extract the information using regex
        const nameMatch = extractedText.match(/name["\s:]+([^",\n]+)/i);
        const aadhaarMatch = extractedText.match(
          /aadhar(?:Number|card)?["\s:]+([0-9\s]+)/i
        );

        if (nameMatch) extractedInfo.name = nameMatch[1].trim();
        if (aadhaarMatch)
          extractedInfo.aadharNumber = aadhaarMatch[1].replace(/\s/g, "");
      }
    } catch (parseError) {
      console.error("Error parsing JSON from model response:", parseError);

      // Additional fallbacks for complex cases
      // Try to find lines that might contain the name or number
      const lines = extractedText.split("\n");

      for (const line of lines) {
        // Look for Aadhaar number pattern
        const numMatch = line.match(/\d{4}\s?\d{4}\s?\d{4}/);
        if (numMatch && !extractedInfo.aadharNumber) {
          extractedInfo.aadharNumber = numMatch[0].replace(/\s/g, "");
        }

        // Look for name (heuristic: words that aren't numbers, dates or common Aadhaar terms)
        if (
          !extractedInfo.name &&
          !line.match(
            /aadhaar|government|india|male|female|dob|year|birth|address/i
          ) &&
          line.match(/^[A-Za-z\s]{3,40}$/)
        ) {
          extractedInfo.name = line.trim();
        }
      }
    }

    // Clean up the data
    if (extractedInfo.aadharNumber) {
      // Ensure it's exactly 12 digits
      extractedInfo.aadharNumber = extractedInfo.aadharNumber
        .replace(/\D/g, "")
        .substring(0, 12);
      // Add stars if we need to mask some digits
      if (extractedInfo.aadharNumber.length < 12) {
        extractedInfo.aadharNumber = extractedInfo.aadharNumber.padStart(
          12,
          "*"
        );
      }
    }

    console.log("Extracted info:", extractedInfo);

    return NextResponse.json({
      success: true,
      data: {
        name: extractedInfo.name || null,
        aadharNumber: extractedInfo.aadharNumber || null,
      },
    });
  } catch (error) {
    console.error("Groq AI OCR Error:", error);
    return NextResponse.json(
      { error: "Failed to process Aadhaar image: " + error.message },
      { status: 500 }
    );
  }
}
