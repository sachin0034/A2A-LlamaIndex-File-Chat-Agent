# 🤖 LlamaIndex File Chat Agent

> A powerful conversational agent that can understand and chat about your documents using LlamaIndex and A2A Protocol

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![A2A Protocol](https://img.shields.io/badge/A2A-Protocol-orange.svg)](https://google.github.io/A2A/)

## 📚 Overview

This project demonstrates a state-of-the-art conversational agent built with [LlamaIndex Workflows](https://docs.llamaindex.ai/en/stable/understanding/workflows/) and exposed through the A2A (Agent-to-Agent) protocol. It enables natural conversations about your documents with features like file parsing, multi-turn dialogue, and real-time streaming responses.

---

### Architecture

```mermaid
sequenceDiagram
    participant Client as A2A Client
    participant Server as A2A Server
    participant Workflow as ParseAndChat Workflow
    participant Services as External APIs

    Client->>Server: Send message (with or without attachment)
    Server->>Workflow: Forward as InputEvent

    alt Has Attachment
        Workflow-->>Server: Stream LogEvent "Parsing document..."
        Server-->>Client: Stream status update
        Workflow->>Services: Parse document
        Workflow-->>Server: Stream LogEvent "Document parsed successfully"
        Server-->>Client: Stream status update
    end

    Workflow-->>Server: Stream LogEvent about chat processing
    Server-->>Client: Stream status update

    Workflow->>Services: LLM Chat (with document context if available)
    Services->>Workflow: Structured LLM Response
    Workflow-->>Server: Stream LogEvent about response processing
    Server-->>Client: Stream status update

    Workflow->>Server: Return final ChatResponseEvent
    Server->>Client: Return response with citations (if available)
```

---

## 🏗️ Project Structure

```
.
├── README.md                 # This file
├── agents/                   # Agent implementations
│   └── llama_index_file_chat/  # LlamaIndex file chat agent
├── hosts/                    # Host implementations
│   ├── cli/                 # Command-line interface host
│   ├── multiagent/          # Multi-agent host implementation
│   └── agent.py             # Base agent implementation
├── common/                   # Shared utilities and components
├── .env                     # Environment variables (create this)
├── pyproject.toml           # Project dependencies and metadata
├── uv.lock                  # UV package manager lock file
└── .python-version          # Python version specification
```

---

## 🔑 What is A2A?

A2A (Agent-to-Agent) is a standardized protocol for agent communication that enables:

- **Standardized Communication**: Common interface for agent interactions
- **Real-time Updates**: Streaming responses and status updates
- **Multi-modal Support**: Handle text, files, and other data types
- **Session Management**: Maintain conversation context
- **Push Notifications**: Webhook-based updates
- **Security**: JWK authentication for secure communications

---

## ✨ Key Features

- 📄 **Smart File Processing**

  - Upload and parse various document formats
  - Intelligent content extraction
  - Context-aware responses

- 💬 **Advanced Chat Capabilities**

  - Multi-turn conversations
  - Context retention
  - In-line citations with source references

- 🔄 **Real-time Experience**

  - Live status updates
  - Streaming responses
  - Progress indicators

- 🔒 **Enterprise Ready**
  - Session management
  - Secure communications
  - Scalable architecture

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- Google Gemini API key ([Get it here](https://aistudio.google.com/))
- LlamaParse API key ([Get it here](https://cloud.llamaindex.ai/project/073112ec-6bcb-464a-bbbe-0915fe1fff6b))

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Set up your environment:

   ```bash
   # Create .env file with your API keys
   echo "GOOGLE_API_KEY=your_api_key_here" >> .env
   echo "LLAMA_CLOUD_API_KEY=your_api_key_here" >> .env
   ```

3. Run the agent in your first terminal:

   ```bash
   # Navigate to the agent directory
   cd agents/llama_index_file_chat

   # Run with default port (10010)
   uv run .
   ```

4. Open a new terminal window and start the A2A client:

   ```bash
   # Navigate to the CLI host directory
   cd hosts/cli

   # Start the A2A client
   uv run . --agent http://localhost:10010
   ```

> 💡 **Note**: Make sure to keep both terminals open - one running the agent server and another running the A2A client.

## 💡 Example Usage

1. Start a conversation:
   ```bash
   What do you want to send to the agent? (:q or quit to exit): What does this file talk about?
   Select a file path to attach? (press enter to skip): ./Reference MSA Document.pdf
   ```

---

## 🛠️ Technical Details

### Implementation Highlights

- **LlamaIndex Workflows**: Custom workflow for document parsing and chat
- **Streaming Support**: Real-time updates during processing
- **Context Management**: Session-based memory with persistence options
- **A2A Protocol**: Full compliance with agent communication standards

## ⚠️ Limitations

- Text-only output (multimodal support coming soon)
- LlamaParse free tier: 10K credits (~3333 pages)
- In-memory session storage (not persistent)
- Large document handling requires vector DB integration

## 📚 Learn More

- [A2A Protocol Documentation](https://google.github.io/A2A/#/documentation)
- [LlamaIndex Workflows](https://docs.llamaindex.ai/en/stable/understanding/workflows/)
- [LlamaParse Documentation](https://github.com/run-llama/llama_cloud_services/blob/main/parse.md)
- [Google Gemini API](https://ai.google.dev/gemini-api)
