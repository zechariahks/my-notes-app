# Amazon Bedrock Integration with MCP

This directory contains examples of integrating the Model Context Protocol (MCP) with Amazon Bedrock.

## Prerequisites

1. AWS account with access to Amazon Bedrock
2. Appropriate IAM permissions to invoke Bedrock models
3. AWS CLI configured with your credentials
4. Python 3.10+ with boto3 installed

## Setup

1. Install the required packages:

   ```
   pip install boto3 mcp httpx httpx-sse
   ```

2. Make sure your AWS credentials are configured:
   ```
   aws configure
   ```

3. Start the MCP server:
   ```
   python notes_server.py
   ```

## Example Files

### Basic Integration (bedrock_integration.py)

This example demonstrates how to:
1. Connect to an MCP server
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

## How It Works

### Basic Integration

1. The client connects to the MCP server
2. It retrieves all notes and their contents
3. The notes are formatted and included in the prompt to Bedrock
4. Bedrock generates a response based on the notes content

### Tool Calling Integration

1. The client defines MCP tools in a format Bedrock understands
2. The user query is sent to Bedrock along with tool definitions
3. If Bedrock decides to use a tool, the client:
   - Extracts the tool name and arguments
   - Calls the corresponding MCP tool
   - Returns the result to Bedrock
4. Bedrock uses the tool results to generate a final response

## Customization

To adapt these examples for your own use:

1. Change the region and model ID to match your Bedrock setup
2. Modify the tool definitions to match your MCP server's tools
3. Adjust the prompt formatting to fit your use case
4. Add error handling and retries as needed for production use

## Troubleshooting

If you encounter issues:

1. Check that your AWS credentials are correctly configured
2. Verify that you have access to the specified Bedrock model
3. Make sure the MCP server is running and accessible
4. Check for any errors in the MCP server logs
5. Try using the stdio transport for simpler debugging
