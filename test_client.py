import asyncio
import json
import traceback
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types

async def message_handler(message):
    """Handle incoming messages from the server."""
    if isinstance(message, Exception):
        print(f"Error in message handler: {message}")
        traceback.print_exc()
        return
    
    print(f"Received message from server: {message}")

async def main():
    print("Connecting to Notes MCP server...")
    try:
        # Connect to the MCP server using the sse_client
        print("Establishing SSE connection...")
        async with sse_client("http://localhost:8080/sse") as (read_stream, write_stream):
            print("SSE connection established")
            
            # Create a client session
            print("Creating client session...")
            async with ClientSession(
                read_stream,
                write_stream,
                message_handler=message_handler,
                client_info=types.Implementation(name="TestClient", version="1.0.0")
            ) as session:
                # Initialize the session
                print("Initializing session...")
                await session.initialize()
                print("Session initialized")
                
                # List tools
                print("Listing tools...")
                try:
                    tools = await session.list_tools()
                    print(f"Tools response type: {type(tools)}")
                    print(f"Tools content: {tools}")
                    
                    # Handle different possible return types
                    if hasattr(tools, 'tools'):
                        # If tools is an object with a 'tools' attribute
                        tool_list = tools.tools
                        if isinstance(tool_list, list):
                            tool_names = [getattr(tool, 'name', str(tool)) for tool in tool_list]
                            print(f"Available tools: {tool_names}")
                        else:
                            print(f"Tools is not a list: {tool_list}")
                    elif isinstance(tools, list):
                        # If tools is directly a list
                        tool_names = [getattr(tool, 'name', str(tool)) for tool in tools]
                        print(f"Available tools: {tool_names}")
                    elif isinstance(tools, tuple):
                        # If tools is a tuple
                        print(f"Tools is a tuple: {tools}")
                        if len(tools) > 0 and hasattr(tools[0], 'name'):
                            tool_names = [tool.name for tool in tools]
                            print(f"Available tools: {tool_names}")
                        else:
                            print(f"Tools tuple elements don't have 'name' attribute")
                    else:
                        print(f"Unexpected tools type: {type(tools)}")
                        
                except Exception as e:
                    print(f"Error listing tools: {e}")
                    traceback.print_exc()
                    return
                
                # Read the notes resource
                print("Getting notes...")
                try:
                    notes_resource = await session.read_resource("resource://notes")
                    print(f"Notes resource type: {type(notes_resource)}")
                    print(f"Notes resource content: {notes_resource}")
                    
                    if hasattr(notes_resource, 'contents') and len(notes_resource.contents) > 0:
                        notes_json = notes_resource.contents[0].text
                        notes = json.loads(notes_json)
                        print(f"Available notes: {notes['note_ids']}")
                    else:
                        print("Could not extract notes content")
                        
                except Exception as e:
                    print(f"Error getting notes: {e}")
                    traceback.print_exc()
                    return
                
                # Read a note
                print("Reading note1...")
                try:
                    note1_result = await session.call_tool("ReadNote", {"note_id": "note1"})
                    print(f"Note1 result type: {type(note1_result)}")
                    print(f"Note1 result content: {note1_result}")
                    
                    if hasattr(note1_result, 'content') and len(note1_result.content) > 0:
                        note1_content = note1_result.content[0].text
                        print(f"Note 1 says: {note1_content}")
                    else:
                        print("Could not extract note content")
                        
                except Exception as e:
                    print(f"Error reading note: {e}")
                    traceback.print_exc()
                
                # Create a new note
                print("Creating a new note...")
                try:
                    create_result = await session.call_tool("CreateNote", {
                        "note_id": "note4", 
                        "content": "Learn more about MCP"
                    })
                    
                    if hasattr(create_result, 'content') and len(create_result.content) > 0:
                        create_message = create_result.content[0].text
                        print(f"Create note result: {create_message}")
                    else:
                        print("Could not extract create result")
                        
                except Exception as e:
                    print(f"Error creating note: {e}")
                    traceback.print_exc()
                
                # Check that our new note exists
                print("Getting updated notes...")
                try:
                    updated_notes_resource = await session.read_resource("resource://notes")
                    
                    if hasattr(updated_notes_resource, 'contents') and len(updated_notes_resource.contents) > 0:
                        updated_notes_json = updated_notes_resource.contents[0].text
                        updated_notes = json.loads(updated_notes_json)
                        print(f"Updated notes: {updated_notes['note_ids']}")
                    else:
                        print("Could not extract updated notes content")
                        
                except Exception as e:
                    print(f"Error getting updated notes: {e}")
                    traceback.print_exc()
                
                # Read our newly created note
                print("Reading new note...")
                try:
                    new_note_result = await session.call_tool("ReadNote", {"note_id": "note4"})
                    
                    if hasattr(new_note_result, 'content') and len(new_note_result.content) > 0:
                        new_note_content = new_note_result.content[0].text
                        print(f"New note says: {new_note_content}")
                    else:
                        print("Could not extract new note content")
                        
                except Exception as e:
                    print(f"Error reading new note: {e}")
                    traceback.print_exc()
                
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        traceback.print_exc()
        print("Make sure the server is running with: python new_notes_server.py")

if __name__ == "__main__":
    asyncio.run(main())
