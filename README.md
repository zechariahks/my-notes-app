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
   pip install mcp httpx httpx-sse
   ```

## Running the Server

You can run the MCP server using different transport protocols:

### HTTP with Server-Sent Events (SSE)

```
python new_notes_server.py
```

The server will start on http://localhost:8080 with the SSE endpoint at /sse.

### Standard Input/Output (stdio)

```
python stdio_server.py
```

This runs the server using standard input/output streams, which is useful for direct integration with other processes.

## Testing the Clients

Several client implementations are provided to demonstrate different ways to interact with the MCP server:

### SSE Client (Recommended)

```
python sse_client.py
```

This client connects to the server using the SSE transport protocol. Make sure the server is running with `python new_notes_server.py` before starting this client.

### stdio Client

```
python stdio_client.py
```

This client automatically starts the stdio server and communicates with it directly through standard input/output streams.

### Custom HTTP Client

```
python test_client.py
```

This is a custom implementation that uses direct HTTP requests to communicate with the server.

All clients will:
1. Connect to the MCP server
2. List available tools
3. Get the list of notes
4. Read a specific note
5. Create a new note
6. Verify the new note was created

## MCP Server Implementation

The server is implemented using the FastMCP class from the MCP package. It provides:

- A resource endpoint at `resource://notes` that returns a list of all note IDs
- A `ReadNote` tool that reads a specific note by ID
- A `CreateNote` tool that creates a new note with a given ID and content

## Transport Protocols

The MCP protocol supports multiple transport mechanisms:

1. **SSE (Server-Sent Events)**: A web standard for server-to-client push notifications over HTTP. Used in `new_notes_server.py` and `sse_client.py`.

2. **stdio**: Uses standard input/output streams for communication. Useful for direct integration with other processes. Used in `stdio_server.py` and `stdio_client.py`.

3. **streamable-http**: An HTTP-based protocol that allows for bidirectional communication. This was our initial approach but we encountered compatibility issues.

## Using with AI Assistants

This MCP server can be used with AI assistants that support the Model Context Protocol. The assistant can:

1. Get the list of available notes
2. Read specific notes
3. Create new notes

## File Structure

- `new_notes_server.py`: The MCP server implementation using SSE transport
- `stdio_server.py`: The MCP server implementation using stdio transport
- `sse_client.py`: Client that connects to the server using SSE transport
- `stdio_client.py`: Client that connects to the server using stdio transport
- `test_client.py`: Custom HTTP client implementation (may not work with all server configurations)
- `mcp_client.py`: Alternative client using MCP client library
- `simple_test_client.py`: Simplified client for testing
- `README.md`: This file

## Troubleshooting

If you encounter issues:

1. **406 Not Acceptable Error**: This occurs when the client doesn't accept the correct content type. Make sure your client accepts `text/event-stream` for SSE transport.

2. **Connection Issues**: If you have trouble connecting to the server, try using the stdio transport which bypasses network connectivity issues.

3. **Response Parsing Errors**: The MCP protocol returns structured objects. Make sure your client correctly handles the response structure:
   - `session.list_tools()` returns a `ListToolsResult` object with a `tools` attribute
   - `session.read_resource()` returns a `ReadResourceResult` object with a `contents` attribute
   - `session.call_tool()` returns a `CallToolResult` object with a `content` attribute

4. **Server Not Found**: When using the stdio client, make sure the server script is in the current directory or provide the full path.

5. **Debug Mode**: Enable debug mode and set the log level to DEBUG in the server for more detailed logs:
   ```python
   app = FastMCP(
       name="NotesServer",
       debug=True,
       log_level="DEBUG"
   )
   ```


(venv) ➜  my-notes-mcp python bedrock_tool_calling.py
Ask a question about your notes: get the note with eggs
Asking Bedrock...
Model wants to call tool: ReadNote with args: {'note_id': 'eggs'}

Bedrock's answer:
Looks like the note with ID 'eggs' contains a reminder to buy eggs. What would you like me to do with this note? I can update or delete it, or we can create a new note.

(venv) ➜  my-notes-mcp python bedrock_tool_calling.py
Ask a question about your notes: create a new note with content "Go out for a walk"
Asking Bedrock...
Model wants to call tool: CreateNote with args: {'note_id': 'note1', 'content': 'Go out for a walk'}
Model wants to call tool: CreateNote with args: {'note_id': 'newNote', 'content': 'Go out for a walk'}
Model wants to call tool: ReadNote with args: {'note_id': 'newNote'}

Bedrock's answer:
Let me know if you need to create any other notes, read existing ones, or if you have any other requests for managing your notes!

