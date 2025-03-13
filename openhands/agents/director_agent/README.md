# Director Agent Implementation

This project implements a Director Agent using the OpenAI Agents SDK. The Director Agent analyzes user requests, determines the appropriate workflow or API to call, executes the workflow, evaluates results, and provides a final response to the user.

## Overview

The Director Agent follows this workflow:

1. **Request Analysis**: The agent analyzes the user's request to understand their intent and needs.
2. **Workflow Selection**: The agent determines which workflow or API is most appropriate to fulfill the request, or if it can answer directly.
3. **Execution**: The agent calls the selected workflow or API with appropriate parameters.
4. **Evaluation**: The agent evaluates the results from the workflow or API to determine if they satisfy the user's request.
5. **Additional Processing**: The agent determines if additional workflows or processing is needed to fully address the request.
6. **Response Generation**: The agent creates a clear, concise, and helpful response for the user based on all gathered information.

## Components

### Director Agent

The main agent that orchestrates the entire workflow. It is implemented as an OpenAI Agent with:

- **System Instructions**: Define the agent's role as a workflow director
- **Tools**: Various workflow API tools that the agent can call
- **Handoffs**: Optional specialized agents for specific tasks
- **Guardrails**: Input/output validation to ensure proper functioning

### Workflow Tools

Each workflow is implemented as a function tool that the Director Agent can call. Example workflows include:

- **Workflow X**: For retrieving specific data based on a search query
- **Workflow Y**: For retrieving categorized information with a specified limit
- **Workflow Z**: For retrieving detailed information about a specific item by ID

### Evaluation Logic

The Director Agent includes logic to evaluate workflow results and determine if additional processing is needed to fully address the user's request.

## Usage

### Basic Usage

```python
from director_agent import create_director_agent
from workflow_tools import workflow_x_tool, workflow_y_tool

# Create the Director Agent
director_agent = create_director_agent(
    workflow_tools=[workflow_x_tool, workflow_y_tool],
)

# Process a user request
response = await director_agent.process_request(
    user_request="Find information about the latest smartphones",
)

print(response)
```

### Streaming Usage

```python
from director_agent import create_director_agent
from workflow_tools import workflow_x_tool, workflow_y_tool

# Create the Director Agent
director_agent = create_director_agent(
    workflow_tools=[workflow_x_tool, workflow_y_tool],
)

# Process a user request with streaming
result = await director_agent.run_streamed(
    user_request="Find information about the latest smartphones",
)

async for event in result.stream_events():
    # Handle streaming events
    pass
```

## Examples

See the `src/examples/director_example.py` file for complete examples of using the Director Agent.

## Flow Diagram

```
A[Start: User Request] --> B[LLM Analyzes Request]
B --> C{Determine API to Call}
C -->|Workflow X is Optimal| D[Call Workflow X API]
C -->|Workflow Y is Optimal| E[Call Workflow Y API]
C -->|Direct Answer Possible| F[LLM Creates Direct Answer]
D --> G[Get Workflow X Results]
E --> H[Get Workflow Y Results]
G --> I[LLM Re-evaluates Results]
H --> I
I --> J{Additional Processing Needed?}
J -->|YES| C
J -->|NO| K[LLM Creates Final Answer]
F --> K
K --> L[Return Result to User]
L --> M[End or Wait for Next Request]
```

## Implementation Details

### Workflow API Format

Workflows are defined as function tools with a specific format:

```python
@function_tool
def workflow_x_tool(query: str) -> Dict[str, Any]:
    """
    Execute Workflow X with the given query.
    
    This workflow is designed for retrieving specific data based on a search query.
    
    Args:
        query: The search query or parameters for the workflow
        
    Returns:
        A dictionary containing the workflow results
    """
    # Implementation
    return {
        "success": True,
        "data": {
            "items": [
                {"id": 1, "name": f"Result 1 for {query}", "score": 0.95},
                # More items...
            ],
            "total_count": 3,
            "query_time_ms": 120,
        },
        "message": "データを正常に取得しました",
    }
```

This translates to the following OpenAI Function format:

```json
{
  "name": "workflow_x_tool",
  "description": "Execute Workflow X with the given query. This workflow is designed for retrieving specific data based on a search query.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query or parameters for the workflow"
      }
    },
    "required": ["query"]
  }
}
```

### Workflow Response Format

Workflows return responses in a standardized format:

```json
{
  "success": true,
  "data": {
    "items": [
      {"id": 1, "name": "Result 1 for query", "score": 0.95},
      {"id": 2, "name": "Result 2 for query", "score": 0.87},
      {"id": 3, "name": "Result 3 for query", "score": 0.76}
    ],
    "total_count": 3,
    "query_time_ms": 120
  },
  "message": "データを正常に取得しました"
}
```

### Result Evaluation

The Director Agent evaluates workflow results using a template:

```markdown
# Workflow Result Evaluation

## Original User Request
{user_request}

## Workflow Used
{workflow_name}

## Workflow Results
{workflow_results}

## Evaluation Questions

1. Do these results fully address the user's request? If not, what's missing?
2. Is additional information or processing needed? If so, which workflow would be most appropriate next?
3. How should these results be presented to the user in a clear and helpful way?
4. Are there any inconsistencies, errors, or issues with the results that should be addressed?

Based on this evaluation, determine if:
A) The results are sufficient and a final response can be created
B) Additional workflows should be called to gather more information
C) The results indicate an error or issue that needs to be handled
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/director-agent-implementation.git
cd director-agent-implementation
```

2. Install the OpenAI Agents SDK:
```bash
pip install openai-agents
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

4. Run the example:
```bash
python -m src.examples.director_example
```

## Requirements

- Python 3.8+
- OpenAI Agents SDK
- OpenAI API key

## License

This project is licensed under the MIT License - see the LICENSE file for details.
