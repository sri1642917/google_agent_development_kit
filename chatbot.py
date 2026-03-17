import sys
import os
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Suppress liteLLM warnings and logging
os.environ["LITELLM_LOG"] = "ERROR"
os.environ["ADK_SUPPRESS_GEMINI_LITELLM_WARNINGS"] = "true"
import litellm
litellm.set_verbose = False
litellm.suppress_debug_info = True

# Ensure the package can be found
sys.path.append(os.getcwd())

from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from eddie.agent import root_agent

async def run_chatbot():
    """
    Task: Runs the Eddie Chatbot CLI with detailed tool logging.
    
    input_params:
        None
    
    output_params:
        None
    
    returns:
        None
    
    raises:
        None
    """
    app = App(name="EddieChat", root_agent=root_agent)
    session_service = InMemorySessionService()
    runner = Runner(app=app, session_service=session_service)
    
    user_id = "cli_user"
    session_id = "cli_session"
    
    # Create the session (required by Runner)
    await session_service.create_session(app_name=app.name, user_id=user_id, session_id=session_id)
    
    print("\n--- 🧙‍♂️ Eddie Math Wizard ---")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Eddie: Goodbye! 🪄")
                break
            
            if not user_input.strip():
                continue

            # Prepare the user message content
            new_message = types.Content(role="user", parts=[types.Part(text=user_input)])
            
            # Local state for tracking tool execution time
            tool_start_times = {} 
            first_text = True
            
            # Run the agent using the runner
            for event in runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                timestamp_str = datetime.fromtimestamp(event.timestamp).strftime('%H:%M:%S.%f')[:-3]
                
                # Check for tool calls and responses
                for func_call in event.get_function_calls():
                    call_id = getattr(func_call, 'id', func_call.name)
                    tool_start_times[call_id] = time.time()
                    print(f"\n[{timestamp_str}] 🚀 [REQUEST] Invoking {func_call.name}")
                    print(f"    Args: {func_call.args}")
                    print(f"    Invocation ID: {event.invocation_id}")
                
                for func_resp in event.get_function_responses():
                    call_id = getattr(func_resp, 'id', func_resp.name)
                    duration = (time.time() - tool_start_times.get(call_id, time.time()))
                    print(f"[{timestamp_str}] ✅ [RESPONSE] {func_resp.name} returned in {duration:.2f}s")
                    print(f"    Output: {func_resp.response}\n")

                # We look for model responses
                if event.author == "Eddie" and event.content:
                    for part in event.content.parts:
                        if part.text:
                            if first_text:
                                print(f"[{timestamp_str}] Eddie: ", end="", flush=True)
                                first_text = False
                            print(part.text, end="", flush=True)
            print() # Newline after response

        except KeyboardInterrupt:
            print("\nEddie: Goodbye! 🪄")
            break
        except Exception as e:
            print(f"\nEddie: Oops! A miscast spell occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_chatbot())
