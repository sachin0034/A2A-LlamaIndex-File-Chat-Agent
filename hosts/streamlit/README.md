# A2A Streamlit Client

A Streamlit-based web interface for interacting with A2A agents. This client provides a user-friendly way to upload files and chat with the agent about their contents.

## Features

- File upload interface supporting multiple formats (PDF, DOC, DOCX, TXT, PNG, JPG, JPEG)
- Real-time chat interface
- Streaming responses
- Session state management
- Progress indicators

## Usage

1. Make sure the A2A agent server is running:

```bash
cd agents/llama_index_file_chat
uv run .
```

2. Run the Streamlit app:

```bash
cd hosts/streamlit
uv run streamlit run app.py -- --agent http://localhost:10010
```

3. Open your browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

4. Upload a file and start chatting!
