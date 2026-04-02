import streamlit as st
import sys
import os
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Suppress liteLLM warnings and logging to maintain a clean console output
os.environ["LITELLM_LOG"] = "ERROR"
os.environ["ADK_SUPPRESS_GEMINI_LITELLM_WARNINGS"] = "true"

import litellm
# Disable verbose logging and debug information for litellm
litellm.set_verbose = False
litellm.suppress_debug_info = True

from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from eddie.agent import root_agent

# Ensure the package can be found by appending the current working directory to the system path
sys.path.append(os.getcwd())

def main():
    """
    Task: Runs the Eddie Chatbot Streamlit web interface with detailed tool logging.
    
    input_params:
        None
    
    output_params:
        None
    
    returns:
        None
    
    raises:
        None (catches internal exceptions and displays them via st.error)
    """
    # Configure the basic settings of the Streamlit page
    st.set_page_config(
        page_title="Eddie Chatbot",
        page_icon="🤖",
        layout="centered"
    )

    # Inject premium styling using custom CSS for a modern Look and Feel
    st.markdown("""
    <style>
        /* Main application background styling */
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e9e9e9;
        }
        /* Custom styling for chat message bubbles */
        .stChatMessage {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            margin-bottom: 10px !important;
        }
        /* Chat input field customization */
        .stChatInput {
            border-radius: 25px !important;
            border: 1px solid #4ecca3 !important;
        }
        /* Header title gradient and styling */
        h1 {
            background: linear-gradient(to right, #4ecca3, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            text-align: center;
            margin-bottom: 30px;
        }
        /* Tool invocation logging style */
        .tool-log {
            font-size: 0.85rem;
            color: #4ecca3;
            font-family: monospace;
        }
        /* Metadata text styling for smaller details */
        .tool-meta {
            color: #888;
            font-size: 0.75rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Display the main header title
    st.title("🤖 Eddie Chatbot")

    # Initialize the Agent Development Kit (ADK) components in the session state
    # This ensures that these instances persist across Streamlit app reruns
    if "adk_initialized" not in st.session_state:
        # Create the ADK App with the root agent
        app = App(name="EddieStreamlit", root_agent=root_agent)
        
        # Instantiate a session service using an in-memory store
        session_service = InMemorySessionService()
        
        # Define a static user ID and a unique session ID based on the current time
        user_id = "streamlit_user"
        session_id = str(int(time.time())) # Unique session per refresh
        
        # Attempt to create the session asynchronously (required by the Runner)
        try:
            asyncio.run(session_service.create_session(
                app_name=app.name, 
                user_id=user_id, 
                session_id=session_id
            ))
        except Exception:
            # Silently pass if the session might already exist
            pass
        
        # Store essential ADK state objects in Streamlit's session_state
        st.session_state.runner = Runner(app=app, session_service=session_service)
        st.session_state.user_id = user_id
        st.session_state.session_id = session_id
        st.session_state.messages = []  # List to track conversation history
        st.session_state.adk_initialized = True

    # Display all existing chat messages stored in session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Provide a chat input block for user interaction
    if prompt := st.chat_input("Ask me a math problem!"):
        # Append the new user message to the historical conversation
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Render the just-sent user message on the interface immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Container for the assistant's response handling
        with st.chat_message("assistant"):
            # Empty placeholder intended for streaming or appending final response text
            response_placeholder = st.empty()
            full_response = ""
            
            # Local state dictionary for tracking the start times of individual tool executions
            tool_start_times = {} # Maps tool_call_id -> start_time
            
            # Package the user's prompt into a Google GenAI content type format
            new_message = types.Content(role="user", parts=[types.Part(text=prompt)])
            
            try:
                # Use a collapsible status block that visibly indicates active processing steps to the user
                with st.status("Eddie is processing...", expanded=True) as status:
                    # Retrieve the underlying stream of events using ADK's runner interface
                    for event in st.session_state.runner.run(
                        user_id=st.session_state.user_id,
                        session_id=st.session_state.session_id,
                        new_message=new_message
                    ):
                        # Extract and format the event timestamp nicely for UI context
                        timestamp_str = datetime.fromtimestamp(event.timestamp).strftime('%H:%M:%S.%f')[:-3]
                        
                        # Process and log any external tool invocations requested by the agent
                        for func_call in event.get_function_calls():
                            # Generate a simple unique ID for tracking specific function invocations
                            call_id = getattr(func_call, 'id', func_call.name)
                            tool_start_times[call_id] = time.time()
                            
                            # Render UI representations of the system calling external capabilities
                            st.markdown(f"---")
                            st.markdown(f"🚀 **[REQUEST]** at `{timestamp_str}`")
                            st.markdown(f"<div class='tool-meta'>Invocation ID: {event.invocation_id}<br>Event ID: {event.id}</div>", unsafe_allow_html=True)
                            st.markdown(f"📥 **Invoking:** `{func_call.name}`")
                            st.code(func_call.args, language="json")
                            # Inform the user visually of the current tool being executed
                            status.update(label=f"Calculating with {func_call.name}...", state="running")
                        
                        # Process and log any external tool responses that completed fetching data
                        for func_resp in event.get_function_responses():
                            # Attempt to correlate the received function response with its invocation timestamp
                            call_id = getattr(func_resp, 'id', func_resp.name)
                            duration = ""
                            if call_id in tool_start_times:
                                # Provide metric measurements reflecting operational duration of each requested sequence call
                                duration = f" (in {(time.time() - tool_start_times[call_id]):.2f}s)"
                            
                            # Log tool finishing metadata along with its resolved payloads to UI
                            st.markdown(f"📥 **[RESPONSE]** at `{timestamp_str}`{duration}")
                            st.markdown(f"📤 **Tool `{func_resp.name}` Output:**")
                            st.json(func_resp.response)
                            # Update visual context conveying parsing task status progress
                            status.update(label="Gathering final answer...", state="running")

                        # Validate and render the generated stream tokens directly from the Model's logic payload response
                        if event.author == "Eddie" and event.content:
                            # Safely extract incoming parts handling possible multi-modal logic layouts recursively 
                            for part in event.content.parts:
                                if part.text:
                                    # Incrementally build out the final dialogue chunk response appending streams mapping block states.
                                    full_response += part.text
                                    # Visually signify streaming behaviour via terminal-like cursor "▌" at sequence end points
                                    response_placeholder.markdown(full_response + "▌")
                    
                    # Conclude the event handler pipeline setting the UI scope visual flags to "completed" state respectively
                    status.update(label="Eddie has finished processing!", state="complete", expanded=False)

                # Final render output eliminating partial text states cursor elements safely replacing DOM block node statically
                response_placeholder.markdown(full_response)
                
                # Register valid responses in central session cache ensuring persistence capabilities on next page lifecycle resets
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                # Catch all execution faults surfacing trace notifications via framework built blocks avoiding silent component crashes effectively!
                st.error(f"Error: {e}")

if __name__ == "__main__":
    # Point of execution entry routine invocation
    main()
