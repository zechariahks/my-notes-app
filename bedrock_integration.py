import boto3
import json
import asyncio
import uuid
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'  # Change to your region
)

async def message_handler(message):
    """Handle incoming messages from the server."""
    if isinstance(message, Exception):
        print(f"Error in message handler: {message}")
        return
    
    print(f"Received message from server: {message}")

async def get_notes_from_mcp():
    """Connect to MCP server and get notes."""
    async with sse_client("http://localhost:8080/sse") as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
            message_handler=message_handler,
            client_info=types.Implementation(name="BedrockClient", version="1.0.0")
        ) as session:
            await session.initialize()
            
            # Get notes
            notes_resource = await session.read_resource("resource://notes")
            notes_json = notes_resource.contents[0].text
            notes = json.loads(notes_json)
            
            # Read each note
            note_contents = {}
            for note_id in notes["note_ids"]:
                note_result = await session.call_tool("ReadNote", {"note_id": note_id})
                note_contents[note_id] = note_result.content[0].text
                
            return note_contents

def invoke_bedrock_model(prompt, notes):
    """Invoke Bedrock model with notes information."""
    # Format notes for the model
    notes_text = "\n".join([f"{note_id}: {content}" for note_id, content in notes.items()])
    
    # Create the full prompt with notes context
    full_prompt = f"""You are a helpful assistant with access to the following notes:

{notes_text}

Please answer the user's question based on these notes.

User question: {prompt}
"""
    
    # Call Bedrock with Claude model
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Use an appropriate model
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        })
    )
    
    # Parse and return the response
    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']

async def main():
    # Get user input
    user_question = input("Ask a question about your notes: ")
    
    # Get notes from MCP server
    print("Fetching notes from MCP server...")
    notes = await get_notes_from_mcp()
    print(f"Retrieved {len(notes)} notes")
    
    # Call Bedrock with the notes context
    print("Asking Bedrock...")
    answer = invoke_bedrock_model(user_question, notes)
    
    # Display the answer
    print("\nBedrock's answer:")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
