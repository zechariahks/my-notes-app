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

async def call_mcp_tool(tool_name, arguments):
    """Call a specific MCP tool."""
    async with sse_client("http://localhost:8080/sse") as (read_stream, write_stream):
        async with ClientSession(
            read_stream,
            write_stream,
            message_handler=message_handler,
            client_info=types.Implementation(name="BedrockClient", version="1.0.0")
        ) as session:
            await session.initialize()
            
            # Call the tool
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

def invoke_bedrock_with_tools(prompt):
    """Invoke Bedrock model with tool definitions."""
    # Define the tools that match our MCP server
    tools = [
        {
            "toolSpec": {
                "name": "ReadNote",
                "description": "Read a specific note by its ID.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "note_id": {
                                "type": "string",
                                "description": "The ID of the note to read"
                            }
                        },
                        "required": ["note_id"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "CreateNote",
                "description": "Create a new note with the given ID and content.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "note_id": {
                                "type": "string",
                                "description": "The ID for the new note"
                            },
                            "content": {
                                "type": "string",
                                "description": "The content of the new note"
                            }
                        },
                        "required": ["note_id", "content"]
                    }
                }
            }
        }
    ]
    
    # Call Bedrock with Claude model and tools
    response = bedrock_runtime.converse(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Use an appropriate model
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        toolConfig={
            "tools": tools
        }
    )
    
    return response

async def handle_tool_calls(response):
    """Handle any tool calls from the model response."""
    # Check if the response contains tool use
    output = response.get('output', {})
    message = output.get('message', {})
    content = message.get('content', [])
    
    # Look for tool use in the content
    tool_uses = [item for item in content if 'toolUse' in item]
    
    if tool_uses:
        # Define the tools again for the follow-up call
        tools = [
            {
                "toolSpec": {
                    "name": "ReadNote",
                    "description": "Read a specific note by its ID.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "note_id": {
                                    "type": "string",
                                    "description": "The ID of the note to read"
                                }
                            },
                            "required": ["note_id"]
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "CreateNote",
                    "description": "Create a new note with the given ID and content.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "note_id": {
                                    "type": "string",
                                    "description": "The ID for the new note"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content of the new note"
                                }
                            },
                            "required": ["note_id", "content"]
                        }
                    }
                }
            }
        ]
        
        for tool_use_item in tool_uses:
            tool_use = tool_use_item['toolUse']
            tool_name = tool_use['name']
            tool_args = tool_use['input']
            tool_use_id = tool_use['toolUseId']
            
            print(f"Model wants to call tool: {tool_name} with args: {tool_args}")
            
            # Call the MCP tool
            result = await call_mcp_tool(tool_name, tool_args)
            
            # Prepare messages for follow-up call
            messages = [
                {
                    "role": "user",
                    "content": [{"text": "Please help me with my notes."}]
                },
                {
                    "role": "assistant",
                    "content": content
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"text": result}]
                            }
                        }
                    ]
                }
            ]
            
            # Send the tool result back to the model
            follow_up_response = bedrock_runtime.converse(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                messages=messages,
                toolConfig={
                    "tools": tools
                }
            )
            
            # Check if there are more tool calls
            follow_up_output = follow_up_response.get('output', {})
            follow_up_message = follow_up_output.get('message', {})
            follow_up_content = follow_up_message.get('content', [])
            follow_up_tool_uses = [item for item in follow_up_content if 'toolUse' in item]
            
            if follow_up_tool_uses:
                return await handle_tool_calls(follow_up_response)
            else:
                return follow_up_response
    
    return response

async def main():
    # Get user input
    user_question = input("Ask a question about your notes: ")
    
    # Call Bedrock with tools
    print("Asking Bedrock...")
    initial_response = invoke_bedrock_with_tools(user_question)
    
    # Handle any tool calls
    final_response = await handle_tool_calls(initial_response)
    
    # Display the answer
    print("\nBedrock's answer:")
    output = final_response.get('output', {})
    message = output.get('message', {})
    content = message.get('content', [])
    
    # Extract text content from the response
    for item in content:
        if 'text' in item:
            print(item['text'])
        elif 'toolUse' in item:
            print(f"Tool call: {item['toolUse']['name']}")
        elif 'toolResult' in item:
            print(f"Tool result: {item['toolResult']}")

if __name__ == "__main__":
    asyncio.run(main())
