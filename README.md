# 🤖 Eddie Chatbot: Google Agent Development Kit (ADK) Implementation

Welcome to the **Eddie Chatbot** project! This repository demonstrates a powerful, multi-tool AI agent built using the **Google Agent Development Kit (ADK)** and integrated with **Azure OpenAI** via LiteLLM.

## 🚀 Key Features

- **Multi-Tool Agent**: Eddie is a helpful chatbot capable of performing arithmetic operations using specialized tools (`add`, `subtract`, `multiply`, `divide`).
- **Azure OpenAI Integration**: Seamlessly switches from Gemini to Azure OpenAI (e.g., GPT-5.2) using the `LiteLlm` model class.
- **Detailed Execution Logging**: 
    - Full transparency into the "Thinking" process.
    - Captures **Microsecond Timestamps**, **Execution Durations**, **Invocation IDs**, and **Event IDs**.
- **Dual Interface**:
    - **Streamlit Web UI**: A premium, dark-themed dashboard with real-time status blocks and persistent message history.
    - **CLI Chatbot**: A lightweight command-line interface with formatted request/response blocks for developers.
- **Scalable Architecture**: Uses ADK's `Runner`, `App`, and `InMemorySessionService` for robust session management.

## 📂 Project Structure

- `eddie/`: Core agent logic and math tool definitions.
- `streamlit_app.py`: The premium Streamlit web application.
- `chatbot.py`: The command-line interactive interface.
- `requirements.txt`: Project dependencies.
- `.env`: (User-provided) Environment variables for Azure credentials.

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10+ (Recommended for ADK/MCP compatibility)
- Azure OpenAI Service credentials

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/sri1642917/google_agent_development_kit.git
cd google_agent_development_kit
python3 -m venv google_adk
source google_adk/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory with the following contents:
```env
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
OPENAI_API_VERSION=your_api_version
DEPLOYMENT_NAME=gpt-5.2-chat
```

## 🎮 How to Run

### Command Line Interface
```bash
python3 chatbot.py
```

### Streamlit Web UI
```bash
streamlit run streamlit_app.py
```

## 🔍 Detailed Logging in Action
When Eddie performs a calculation, the logs will show:
- `⚡ [REQUEST] at 23:14:00.830`: Tool invocation metadata.
- `✅ [RESPONSE] returned in 0.05s`: Execution performance metrics.
- `Invocation ID`: Unique trace for every conversation turn.

---
Built with ❤️ using [Google ADK](https://github.com/google/adk).
