import streamlit as st
import base64
import os
import httpx
import asyncio
from uuid import uuid4

from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    Part,
    TextPart,
    FilePart,
    FileWithBytes,
    Task,
    TaskState,
    Message,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    MessageSendConfiguration,
    SendStreamingMessageRequest,
    MessageSendParams,
    GetTaskRequest,
    TaskQueryParams,
    JSONRPCErrorResponse,
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'client' not in st.session_state:
    st.session_state.client = None
if 'context_id' not in st.session_state:
    st.session_state.context_id = None
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'agent_url' not in st.session_state:
    st.session_state.agent_url = "http://localhost:10010"
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = []
if 'show_debug' not in st.session_state:
    st.session_state.show_debug = False

async def process_message(message_text, file_data=None):
    # Create containers for debug and response
    debug_container = st.empty()
    response_container = st.empty()
    
    async with httpx.AsyncClient(timeout=30) as httpx_client:
        card_resolver = A2ACardResolver(httpx_client, st.session_state.agent_url)
        card = await card_resolver.get_agent_card()
        client = A2AClient(httpx_client, agent_card=card)
        
        # Add initial debug info
        st.session_state.debug_info.append({
            "type": "Agent Card",
            "data": card.model_dump_json(exclude_none=True)
        })
        
        # Show initial debug info
        with debug_container.container():
            st.info("🔄 Processing Request...")
            with st.expander("Debug Information", expanded=True):
                st.write("**Agent Card:**")
                st.json(card.model_dump_json(exclude_none=True))
        
        message = Message(
            role='user',
            parts=[TextPart(text=message_text)],
            messageId=str(uuid4()),
            taskId=st.session_state.task_id,
            contextId=st.session_state.context_id,
        )

        if file_data:
            file_content = base64.b64encode(file_data).decode('utf-8')
            file_name = st.session_state.uploaded_file.name
            message.parts.append(
                Part(
                    root=FilePart(
                        file=FileWithBytes(
                            name=file_name, bytes=file_content
                        )
                    )
                )
            )

        payload = MessageSendParams(
            id=str(uuid4()),
            message=message,
            configuration=MessageSendConfiguration(
                acceptedOutputModes=['text'],
            ),
        )

        response_stream = client.send_message_streaming(
            SendStreamingMessageRequest(
                id=str(uuid4()),
                params=payload,
            )
        )

        response_text = ""
        task_result = None
        status_message = st.empty()  # Create a placeholder for status updates
        
        async for result in response_stream:
            if isinstance(result.root, JSONRPCErrorResponse):
                st.error(f"Error: {result.root.error}")
                return
            
            event = result.root.result
            
            # Add event to debug info
            st.session_state.debug_info.append({
                "type": "Stream Event",
                "data": event.model_dump_json(exclude_none=True)
            })
            
            # Update debug display
            with debug_container.container():
                st.info("🔄 Processing Request...")
                with st.expander("Debug Information", expanded=True):
                    for debug_item in st.session_state.debug_info:
                        st.write(f"**{debug_item['type']}:**")
                        st.json(debug_item['data'])
            
            st.session_state.context_id = event.contextId
            
            if isinstance(event, Task):
                st.session_state.task_id = event.id
                task_result = event
            elif isinstance(event, TaskStatusUpdateEvent):
                # Only show meaningful status updates
                if event.status.state == TaskState.working:
                    if hasattr(event.status, 'message') and event.status.message:
                        # Properly access the text from the part
                        for part in event.status.message.parts:
                            if isinstance(part.root, TextPart):
                                status_message.info(part.root.text)
            elif isinstance(event, TaskArtifactUpdateEvent):
                if event.artifact.name == "llama_summary":
                    # Display the summary in a nice format
                    for part in event.artifact.parts:
                        if isinstance(part.root, TextPart):
                            with response_container.container():
                                st.success("Document Summary:")
                                st.write(part.root.text)
            elif isinstance(event, Message):
                for part in event.parts:
                    if isinstance(part.root, TextPart):
                        response_text += part.root.text

        # If we have a task result, get the full task
        if task_result:
            task_response = await client.get_task(
                GetTaskRequest(
                    id=str(uuid4()),
                    params=TaskQueryParams(id=task_result.id),
                )
            )
            task_result = task_response.root.result
            # Add final task result to debug info
            st.session_state.debug_info.append({
                "type": "Final Task Result",
                "data": task_result.model_dump_json(exclude_none=True)
            })
            
            # Update final debug display
            with debug_container.container():
                st.success("✅ Processing Complete")
                with st.expander("Debug Information", expanded=True):
                    for debug_item in st.session_state.debug_info:
                        st.write(f"**{debug_item['type']}:**")
                        st.json(debug_item['data'])

        # Clear the status message when done
        status_message.empty()

        if response_text:
            with response_container.container():
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.write(response_text)

# Streamlit UI
st.title("File Chat Assistant")

# Agent URL input
agent_url = st.text_input("Agent URL", value=st.session_state.agent_url)
if agent_url != st.session_state.agent_url:
    st.session_state.agent_url = agent_url
    st.session_state.client = None  # Reset client when URL changes

# File upload
uploaded_file = st.file_uploader("Upload a file", type=['pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg'])
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    st.success(f"File uploaded: {uploaded_file.name}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about the document?"):
    if not st.session_state.uploaded_file:
        st.warning("Please upload a file first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            asyncio.run(process_message(prompt, st.session_state.uploaded_file.getvalue()))