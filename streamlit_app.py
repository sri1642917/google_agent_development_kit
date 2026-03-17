import streamlit as st
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

from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from eddie.agent import root_agent

# Ensure the package can be found
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
    # Page configuration
    st.set_page_config(
        page_title="Eddie Math Wizard",
        page_icon="🧙‍♂️",
        layout="centered"
    )

    # Premium Styling
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e9e9e9;
        }
        .stChatMessage {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            margin-bottom: 10px !important;
        }
        .stChatInput {
            border-radius: 25px !important;
            border: 1px solid #4ecca3 !important;
        }
        h1 {
            background: linear-gradient(to right, #4ecca3, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            text-align: center;
            margin-bottom: 30px;
        }
        .tool-log {
            font-size: 0.85rem;
            color: #4ecca3;
            font-family: monospace;
        }
        .tool-meta {
            color: #888;
            font-size: 0.75rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🧙‍♂️ Eddie Math Wizard")

    # Initialize ADK components in session state
    if "adk_initialized" not in st.session_state:
        app = App(name="EddieStreamlit", root_agent=root_agent)
        session_service = InMemorySessionService()
        
        user_id = "streamlit_user"
        session_id = str(int(time.time())) # Unique session per refresh
        
        # Create the session (required by Runner)
        try:
            asyncio.run(session_service.create_session(
                app_name=app.name, 
                user_id=user_id, 
                session_id=session_id
            ))
        except Exception:
            pass # Session might already exist
        
        st.session_state.runner = Runner(app=app, session_service=session_service)
        st.session_state.user_id = user_id
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.session_state.adk_initialized = True

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me a math problem!"):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # Local state for tracking tool execution time
            tool_start_times = {} # tool_call_id -> start_time
            
            # Prepare the user message content
            new_message = types.Content(role="user", parts=[types.Part(text=prompt)])
            
            try:
                # Use a status block that stays at the top of the message
                with st.status("Eddie is processing...", expanded=True) as status:
                    # Run the agent using the runner
                    for event in st.session_state.runner.run(
                        user_id=st.session_state.user_id,
                        session_id=st.session_state.session_id,
                        new_message=new_message
                    ):
                        # Metadata common to the event
                        timestamp_str = datetime.fromtimestamp(event.timestamp).strftime('%H:%M:%S.%f')[:-3]
                        
                        # Logs tool calls
                        for func_call in event.get_function_calls():
                            # Generate a simple unique ID for tracking if not present
                            call_id = getattr(func_call, 'id', func_call.name)
                            tool_start_times[call_id] = time.time()
                            
                            st.markdown(f"---")
                            st.markdown(f"🚀 **[REQUEST]** at `{timestamp_str}`")
                            st.markdown(f"<div class='tool-meta'>Invocation ID: {event.invocation_id}<br>Event ID: {event.id}</div>", unsafe_allow_html=True)
                            st.markdown(f"📥 **Invoking:** `{func_call.name}`")
                            st.code(func_call.args, language="json")
                            status.update(label=f"Calculating with {func_call.name}...", state="running")
                        
                        # Logs tool responses
                        for func_resp in event.get_function_responses():
                            # Match with start time
                            call_id = getattr(func_resp, 'id', func_resp.name)
                            duration = ""
                            if call_id in tool_start_times:
                                duration = f" (in {(time.time() - tool_start_times[call_id]):.2f}s)"
                            
                            st.markdown(f"📥 **[RESPONSE]** at `{timestamp_str}`{duration}")
                            st.markdown(f"📤 **Tool `{func_resp.name}` Output:**")
                            st.json(func_resp.response)
                            status.update(label="Gathering final answer...", state="running")

                        # We look for model responses
                        if event.author == "Eddie" and event.content:
                            for part in event.content.parts:
                                if part.text:
                                    full_response += part.text
                                    response_placeholder.markdown(full_response + "▌")
                    
                    status.update(label="Math wizardry complete!", state="complete", expanded=False)

                # Final render without the cursor
                response_placeholder.markdown(full_response)
                
                # Add assistant message to history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
