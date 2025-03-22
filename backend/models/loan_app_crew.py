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
os.environ["OPENAI_API_KEY"] = "your-openai-api-key" # OpenAI API key
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

# Title and Introduction
st.title("Personalized Loan Recommendation Agent")
st.write("Discover the best Loans tailored to your needs!")

# Streamlit User Inputs
st.sidebar.header("Tell us about yourself:")

age = st.sidebar.number_input("Age", min_value=18, max_value=100, value=30)

loan_purpose = st.sidebar.selectbox(
    "Loan Purpose", 
    options=["Home Purchase", "Auto Loan", "Personal Loan", "Business loan", "Educational loan", "Debt Consolidation", "Other"]
)

loan_amount = st.sidebar.number_input("Loan Amount", min_value=1000)

loan_term = st.sidebar.selectbox(
    "Desired Loan Term",
    options=["Short-term (< 5 years)", "Medium-term (5-10 years)", "Long-term (> 10 years)"]
)

credit_score = st.sidebar.number_input("Credit Score", min_value=300, max_value=850)

income = st.sidebar.number_input("Annual Income", value=50000)

employment_length = st.sidebar.selectbox(
    "Employment Length",
    options=["< 1 year", "1-3 years", "3-5 years", "5+ years"]
)

debt_to_income_ratio = st.sidebar.number_input("Debt-to-Income Ratio (DTI)", min_value=0.0, format="%.2f")

has_coi = st.sidebar.checkbox("Do you have a co-signer?")

has_collateral = st.sidebar.checkbox("Do you have collateral?")

has_employment_guarantee = st.sidebar.checkbox("Do you have an employment guarantee?")

# Create User Input Dictionary
user_inputs = {
    "loan_purpose":loan_purpose,
    "loan_amount": loan_amount,
    "loan_term": loan_term,
    "credit_score": credit_score,
    "income": income,
    "employment_length": employment_length,
    "debt_to_income_ratio": debt_to_income_ratio,
    "has_coi": has_coi,
    "has_collateral": has_collateral,
    "has_employment_guarantee": has_employment_guarantee
}

# Agent Backstory and Role

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

# Implementation of Agents with multiple tools

loan_recommender = Agent(
    role="Loan Recommendation Expert",
    goal="Analyze borrower information and recommend suitable loan options in India",
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

# Tasks
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

# Create Crew with planning enabled
crew = Crew(
    agents=[loan_recommender, loan_analyst, report_generator],
    tasks=[task1, task2, task3],
    verbose=True,  # Increased verbosity for better debugging
    planning=True  # Enable planning feature
)

# Recommendation Button with improved error handling
if st.sidebar.button("Get Recommendations"):
    st.header("Recommended Products for You:")
    
    # try:
    #     with st.spinner("Analyzing your request and generating recommendations...\nPlease wait patiently (2-3 minutes)"):
    #         crew_output = crew.kickoff()
    #         print(f"Raw Output: {crew_output.raw}")
    #         if crew_output.json_dict:
    #             print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
    #         if crew_output.pydantic:
    #             print(f"Pydantic Output: {crew_output.pydantic}")
    #         print(f"Tasks Output: {crew_output.tasks_output}")
    #         print(f"Token Usage: {crew_output.token_usage}")
    #         # Display results in a structured format
    #         st.subheader("Loan Recommendations Report")
    #         # st.markdown(task3.output.raw_output)
    try:
        with st.spinner("Analyzing your request and generating recommendations...\nPlease wait patiently (2-3 minutes)"):
            crew_output = crew.kickoff()
            
            # Extract loan options and analysis from task outputs
            loan_options = crew_output.tasks_output[0].raw
            risk_analysis = crew_output.tasks_output[1].raw
            
            # Display the results in formatted sections
            st.subheader("📊 Loan Recommendations Report")
            
            # Display Loan Options
            st.markdown("### 🏦 Available Loan Options")
            st.markdown(loan_options)
            
            # Display Risk Analysis
            st.markdown("### ⚖️ Risk Assessment")
            st.markdown(risk_analysis)
            
            # Display Statistics
            st.sidebar.markdown("### 📈 Analysis Statistics")
            st.sidebar.markdown(f"""
            * Total Tokens Used: {crew_output.token_usage.total_tokens:,}
            * Completion Tokens: {crew_output.token_usage.completion_tokens:,}
            * Successful Requests: {crew_output.token_usage.successful_requests}
            """)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")

async def process_loan_application(user_inputs: dict):
    # Initialize agents and tools
    loan_recommender = Agent(
        role="Loan Recommendation Expert",
        goal="Analyze borrower information and recommend suitable loan options",
        backstory=loan_expert_backstory,
        verbose=True,
        allow_delegation=False,
        tools=[search_tool, web_search_tool],
        llm=model_agent
    )
    
    # ... (rest of your agent initialization code)

    # Create tasks
    tasks = [
        Task(
            description=f"Analyze the loan request based on: {user_inputs}",
            agent=loan_recommender
        ),
        # ... (other tasks)
    ]

    # Create and run crew
    crew = Crew(
        agents=[loan_recommender, loan_analyst, report_generator],
        tasks=tasks,
        verbose=True
    )

    result = await crew.kickoff()
    
    return {
        "loan_options": result.tasks_output[0].raw,
        "risk_analysis": result.tasks_output[1].raw
    }
