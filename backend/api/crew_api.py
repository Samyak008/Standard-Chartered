import os
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from langchain_groq import ChatGroq
from crewai_tools import SerperDevTool, WebsiteSearchTool
from dotenv import load_dotenv
import json
# Load environment variables
load_dotenv()
os.environ["SERPER_API_KEY"] = "e92edcc2cd3ee13129db6fe3aec941cf46f696aa" # serper.dev API key
os.environ["OPENAI_API_KEY"] = "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" # OpenAI API key
# Initialize CrewAI tools
search_tool = SerperDevTool()
web_search_tool = WebsiteSearchTool()

# Configure the model
# model_agent = ChatGroq(
#     groq_api_key=os.getenv("GROQ_API_KEY"),
#     model="llama3-8b-8192"
# )
model_agent = LLM(
    model="openai/gpt-4o-mini"
)

async def process_loan_application(user_inputs: dict):
    # Initialize agents and tools
    loan_expert_backstory = """
        You are a loan specialist with extensive knowledge of various loan products, interest rates, and lending criteria. 
        You can access and analyze data from multiple lenders to identify the most suitable loan options for borrowers based on their financial situation, creditworthiness, and loan requirements.
        """

    loan_analyst_backstory = """
        You are a financial analyst specializing in risk assessment and loan analysis. 
        You can evaluate borrower information, assess their creditworthiness, and analyze the potential risks associated with different loan options.
        """

    report_generator_backstory = """
        You are a skilled report writer with expertise in presenting complex financial information in a clear, concise, and easy-to-understand format. 
        You can tailor your reports to specific audiences, highlighting key insights and recommendations.
        """

    loan_recommender = Agent(
        role="Loan Recommendation Expert",
        goal="Analyze borrower information and recommend suitable loan options",
        backstory=loan_expert_backstory,
        verbose=True,
        allow_delegation=False,
        tools=[search_tool, web_search_tool],
        llm=model_agent
    )

    loan_analyst = Agent(
    role="Loan Risk Analyst",
    goal="Assess borrower creditworthiness and analyze potential loan risks",
    backstory=loan_analyst_backstory,
    verbose=True,
    allow_delegation=False,
    tools=[search_tool, web_search_tool],
    llm=model_agent
    )

    report_generator = Agent(
        role="Financial Report Writer",
        goal="Generate clear and concise reports on loan options and recommendations",
        backstory=report_generator_backstory,
        verbose=True,
        allow_delegation=False,
        tools=[search_tool, web_search_tool],
        llm=model_agent
    )
    # ... (rest of your agent initialization code)

    # Create tasks
    task1 = Task(
        description=f"""
        Analyze the loan request based on the following user information: {user_inputs}. 
        Research and identify potential loan options from various lenders.
        """,
        expected_output="List of potential loan options with key details (lender, interest rate, term, etc.)",
        agent=loan_recommender,
        async_execution=True
    )

    task2 = Task(
        description="""
        Evaluate the borrower's creditworthiness and assess the potential risks associated with each loan option identified in the previous task.
        Consider factors such as credit score, debt-to-income ratio, employment history, and collateral. 
        """,
        expected_output="Analysis of borrower's creditworthiness and risk assessment for each loan option available in only India ",
        agent=loan_analyst,
        async_execution=True
    )

    task3 = Task(
        description="""
        Based on the loan options and risk assessments, generate a comprehensive report for the user. 
        Clearly present the most suitable loan options, highlighting their terms, interest rates, potential risks, and benefits.
        Explain the rationale behind the recommendations and provide additional insights to guide the user's decision-making process.
        """,
        expected_output="Comprehensive report with clear highlighted loan recommendations and explanations and give the numerical data of loan options with Lender,Interest Rate, Loan Type, Loan Term, Monthly Payments in a different Tables so,the user can compare & choose the right one easily",
        agent=report_generator,
        context=[task1,task2]
    )
    # Create and run crew
    crew = Crew(
        agents=[loan_recommender, loan_analyst, report_generator],
        tasks=[task1, task2, task3],
        verbose=True,  # Increased verbosity for better debugging
        planning=True  # Enable planning feature
    )

    result = crew.kickoff()
    
    # Format the response to match expected structure
    return {
        "loan_options": {
            "raw_text": result.tasks_output[0].raw,
            "recommendations": [],
            "products": [],
            "terms": []
        },
        "risk_analysis": {
            "raw_text": result.tasks_output[1].raw,
            "summary": "",
            "risk_score": 0,
            "risk_level": "Medium",
            "recommendations": []
        }
    }