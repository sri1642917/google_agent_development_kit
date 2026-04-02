import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os
import math

load_dotenv()

# Map Azure environment variables for LiteLLM
if os.getenv("AZURE_OPENAI_API_KEY"):
    os.environ["AZURE_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
if os.getenv("AZURE_OPENAI_ENDPOINT"):
    os.environ["AZURE_API_BASE"] = os.getenv("AZURE_OPENAI_ENDPOINT")
if os.getenv("OPENAI_API_VERSION"):
    os.environ["AZURE_API_VERSION"] = os.getenv("OPENAI_API_VERSION")

def add(args: list[float]) -> dict:
    """
    Task: Calculates the sum of multiple numbers dynamically.
    
    input_params:
        args (float): The numerical values to add together.
    
    returns:
        dict: A dictionary containing 'status' ('success') and the 'result'.
    """
    return {"status": "success", "result": sum(args)}

def subtract(args: list[float]) -> dict:
    """
    Task: Calculates the difference between multiple numbers sequentially (dynamically).
    
    input_params:
        args (float): The numerical values to subtract from the first value.
    
    returns:
        dict: A dictionary containing 'status' ('success' or 'error') and the 'result'.
    """
    if not args:
        return {"status": "error", "error_message": "No numbers provided."}
    result = args[0]
    for n in args[1:]:
        result -= n
    return {"status": "success", "result": result}

def multiply(args: list[float]) -> dict:
    """
    Task: Calculates the product of multiple numbers dynamically.
    
    input_params:
        args (float): The numerical values to multiply together.
    
    returns:
        dict: A dictionary containing 'status' ('success') and the 'result'.
    """
    return {"status": "success", "result": math.prod(args) if args else 0}

def divide(args: list[float]) -> dict:
    """
    Task: Calculates the quotient of multiple numbers sequentially (dynamically).
    
    input_params:
        args (float): The numerical values. The first is divided by subsequent values.
    
    returns:
        dict: A dictionary containing 'status' ('success' or 'error') and the 'result' or 'error_message'.
    """
    if not args:
        return {"status": "error", "error_message": "No numbers provided."}
    result = args[0]
    for n in args[1:]:
        if n == 0:
            return {"status": "error", "error_message": "Division by zero is not allowed."}
        result /= n
    return {"status": "success", "result": result}

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
