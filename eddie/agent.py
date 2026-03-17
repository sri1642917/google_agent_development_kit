import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os

load_dotenv()

# Map Azure environment variables for LiteLLM
if os.getenv("AZURE_OPENAI_API_KEY"):
    os.environ["AZURE_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
if os.getenv("AZURE_OPENAI_ENDPOINT"):
    os.environ["AZURE_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
if os.getenv("OPENAI_API_VERSION"):
    os.environ["AZURE_API_VERSION"] = os.getenv("OPENAI_API_VERSION")

def add(a: float, b: float) -> dict:
    """
    Task: Calculates the sum of two numbers.
    
    input_params:
        a (float): The first number.
        b (float): The second number.
    
    returns:
        dict: A dictionary containing 'status' ('success') and the 'result'.
    """
    return {"status": "success", "result": a + b}

def subtract(a: float, b: float) -> dict:
    """
    Task: Calculates the difference between two numbers (a - b).
    
    input_params:
        a (float): The number to subtract from.
        b (float): The number to be subtracted.
    
    returns:
        dict: A dictionary containing 'status' ('success') and the 'result'.
    """
    return {"status": "success", "result": a - b}

def multiply(a: float, b: float) -> dict:
    """
    Task: Calculates the product of two numbers.
    
    input_params:
        a (float): The first factor.
        b (float): The second factor.
    
    returns:
        dict: A dictionary containing 'status' ('success') and the 'result'.
    """
    return {"status": "success", "result": a * b}

def divide(a: float, b: float) -> dict:
    """
    Task: Calculates the quotient of two numbers (a / b).
    
    input_params:
        a (float): The dividend.
        b (float): The divisor.
    
    returns:
        dict: A dictionary containing 'status' ('success' or 'error') and the 'result' or 'error_message'.
    """
    if b == 0:
        return {"status": "error", "error_message": "Division by zero is not allowed."}
    return {"status": "success", "result": a / b}

root_agent = Agent(
    name="Eddie",
    model=LiteLlm(model=f"azure/{os.getenv('DEPLOYMENT_NAME', 'gpt-5.2-chat')}"),
    description=(
        "A brilliant and friendly assistant named Eddie Chatbot who can perform calculations like addition, subtraction, multiplication, and division."
    ),
    instruction=(
        "You are Eddie Chatbot, a helpful and friendly assistant. When a user asks for a calculation, use your tools to provide accurate results. "
        "Always explain your work in a friendly and conversational way. If a user asks a general question, answer it politely, but prioritize "
        "using your math tools for any numerical queries."
    ),
    tools=[add, subtract, multiply, divide],
)
