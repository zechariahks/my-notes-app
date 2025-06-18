# Notes MCP Server

This is a simple MCP (Model Context Protocol) server that provides a notes API. It demonstrates how to create an MCP server with resources and tools that can be used by AI assistants and other MCP clients.

## Features

- List all available notes
- Read a specific note by ID
- Create new notes

## Setup

1. Make sure you have Python 3.10+ installed
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```
4. Install the required packages:
   ```
   pip install mcp httpx httpx-sse boto3
   ```

## Running the Server

You can run the MCP server using the HTTP with Server-Sent Events (SSE) transport protocol:

```
python notes_server.py
```

The server will start on http://localhost:8080 with the SSE endpoint at /sse.

## Testing the Client

A test client implementation is provided to demonstrate how to interact with the MCP server:

```
python test_client.py
```

This client will:
1. Connect to the MCP server
2. List available tools
3. Get the list of notes
4. Read a specific note
5. Create a new note
6. Verify the new note was created

## Amazon Bedrock Integration

This project includes examples of integrating the MCP server with Amazon Bedrock:

### Basic Integration (bedrock_integration.py)

This example demonstrates how to:
1. Connect to the MCP server
2. Retrieve all notes
3. Pass the notes as context to a Bedrock model
4. Get a response from the model

To run:
```
python bedrock_integration.py
```

### Tool Calling Integration (bedrock_tool_calling.py)

This more advanced example demonstrates how to:
1. Define MCP tools as Bedrock tools
2. Let the model decide when to call tools
3. Execute MCP tool calls based on the model's decisions
4. Return tool results to the model
5. Get the final response

To run:
```
python bedrock_tool_calling.py
```

## MCP Server Implementation

The server is implemented using the FastMCP class from the MCP package. It provides:

- A resource endpoint at `resource://notes` that returns a list of all note IDs
- A `ReadNote` tool that reads a specific note by ID
- A `CreateNote` tool that creates a new note with a given ID and content

## Bedrock Integration Details

For more information about the Bedrock integration, see the [bedrock_readme.md](bedrock_readme.md) file.

## Troubleshooting

If you encounter issues:

1. **406 Not Acceptable Error**: This occurs when the client doesn't accept the correct content type. Make sure your client accepts `text/event-stream` for SSE transport.

2. **Connection Issues**: Check that the server is running on the expected port and address.

3. **Response Parsing Errors**: The MCP protocol returns structured objects. Make sure your client correctly handles the response structure:
   - `session.list_tools()` returns a `ListToolsResult` object with a `tools` attribute
   - `session.read_resource()` returns a `ReadResourceResult` object with a `contents` attribute
   - `session.call_tool()` returns a `CallToolResult` object with a `content` attribute

4. **AWS Credentials**: For Bedrock integration, ensure your AWS credentials are correctly configured and you have access to the specified Bedrock model.

5. **Debug Mode**: Enable debug mode and set the log level to DEBUG in the server for more detailed logs:
   ```python
   app = FastMCP(
       name="NotesServer",
       debug=True,
       log_level="DEBUG"
   )
   ```

## File Structure

- `notes_server.py`: The MCP server implementation using SSE transport
- `test_client.py`: Client that connects to the server using SSE transport
- `bedrock_integration.py`: Example of integrating MCP with Amazon Bedrock
- `bedrock_tool_calling.py`: Example of using Bedrock's tool calling with MCP
- `bedrock_readme.md`: Additional documentation for Bedrock integration
- `README.md`: This file
