from mcp.server import FastMCP
from mcp.types import ToolAnnotations
import json
import asyncio

# This is our "database" (just a dictionary for this example)
notes = {
    "note1": "Buy milk and eggs",
    "note2": "Call mom on Sunday",
    "note3": "Finish project report"
}

# Create a FastMCP server instance with custom settings
app = FastMCP(
    name="NotesServer",
    host="0.0.0.0",  # Listen on all interfaces
    port=8080,
    # Set debug mode to get more information
    debug=True,
    # Set log level to DEBUG for more detailed logs
    log_level="DEBUG"
)

# Define resource handler
@app.resource(uri="resource://notes", name="Notes", mime_type="application/json")
async def notes_resource() -> str:
    """Get a list of all available notes."""
    return json.dumps({
        "note_ids": list(notes.keys())
    })

# Define tool handlers
@app.tool(
    name="ReadNote",
    description="Read a specific note by its ID.",
    annotations=ToolAnnotations(
        inputSchema={
            "type": "object",
            "properties": {
                "note_id": {"type": "string", "description": "The ID of the note to read"}
            },
            "required": ["note_id"]
        }
    )
)
async def read_note(note_id: str) -> str:
    """Read a specific note by its ID."""
    if note_id in notes:
        return notes[note_id]
    else:
        return "Note not found"

@app.tool(
    name="CreateNote",
    description="Create a new note with the given ID and content.",
    annotations=ToolAnnotations(
        inputSchema={
            "type": "object",
            "properties": {
                "note_id": {"type": "string", "description": "The ID for the new note"},
                "content": {"type": "string", "description": "The content of the new note"}
            },
            "required": ["note_id", "content"]
        }
    )
)
async def create_note(note_id: str, content: str) -> str:
    """Create a new note with the given ID and content."""
    if note_id in notes:
        return "Error: This note ID already exists"
    
    notes[note_id] = content
    return f"Note {note_id} created successfully"

# Add a simple root handler for debugging
@app.custom_route("/", methods=["GET"])
async def root(request):
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "ok",
        "message": "Notes MCP Server is running",
        "endpoints": {
            "sse": "/sse"
        }
    })

# Start the server
if __name__ == "__main__":
    print("Starting Notes MCP server on port 8080...")
    # Use SSE transport instead of streamable-http
    app.run(transport="sse")
