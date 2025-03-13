# Director Agent Documentation

This document provides detailed information about the Director Agent implementation using the OpenAI Agents SDK.

## Introduction

The Director Agent is designed to orchestrate workflows based on user requests. It analyzes user requests, determines the appropriate workflow or API to call, executes the workflow, evaluates results, and provides a final response to the user.

The agent follows the "Working Backwards" methodology, starting with the user's request and working backwards to determine the most appropriate workflow to fulfill that request.

## Architecture

The Director Agent architecture consists of the following components:

1. **Director Agent**: The main agent that orchestrates the entire workflow
2. **Workflow Tools**: Function tools that represent different API workflows the agent can call
3. **Evaluation Logic**: Logic to evaluate API responses and determine next steps
4. **Specialized Agents**: Optional agents for specific tasks that the Director Agent can hand off to

### Flow Diagram

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

### Director Agent

The Director Agent is implemented as a class that wraps an OpenAI Agent:

```python
class DirectorAgent:
    def __init__(
        self,
        name: str = "DirectorAgent",
        description: str = "A director agent that orchestrates workflows",
        workflow_tools: Optional[List[Any]] = None,
        specialized_agents: Optional[List[Agent]] = None,
    ):
        self.name = name
        self.description = description
        self.workflow_tools = workflow_tools or []
        self.specialized_agents = specialized_agents or []
        
        # Create the OpenAI Agent
        self.agent = Agent(
            name=name,
            instructions=DIRECTOR_AGENT_INSTRUCTIONS,
            tools=self.workflow_tools,
            handoffs=self.specialized_agents,
        )
```

The `process_request` method handles the entire workflow:

```python
async def process_request(
    self,
    user_request: str,
    trace_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    context = context or {}
    
    # Create a trace for the entire process
    with trace("Director Agent Workflow", trace_id=trace_id):
        with custom_span("Request Analysis"):
            # Step B: LLM analyzes and classifies the request
            result = await Runner.run(
                self.agent,
                input=user_request,
            )
            
        with custom_span("Result Evaluation"):
            # Steps I-J: LLM re-evaluates results and determines if additional processing is needed
            if self._needs_additional_processing(result, user_request):
                # Call another workflow or process further
                additional_input = self._create_additional_input(result, user_request)
                result = await Runner.run(
                    self.agent,
                    input=additional_input,
                )
        
        # Steps K-L: LLM creates final answer and returns to user
        return str(result.final_output)
```

### Workflow Tools

Workflow tools are implemented as function tools using the `@function_tool` decorator:

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

### Prompt Templates

The Director Agent uses several prompt templates to guide its behavior:

1. **System Instructions**: Define the agent's role and responsibilities
2. **Result Evaluation Template**: Guide the evaluation of workflow results
3. **Final Response Template**: Guide the creation of the final response
4. **Error Handling Template**: Guide the handling of errors
5. **Workflow Selection Template**: Guide the selection of workflows

Example of the Result Evaluation Template:

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

## Usage Examples

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
    if isinstance(event, RawResponsesStreamEvent):
        data = event.data
        if isinstance(data, ResponseTextDeltaEvent):
            print(data.delta, end="", flush=True)
```

### Creating Custom Workflows

You can create custom workflows by defining function tools:

```python
@function_tool
def custom_workflow_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Execute a custom workflow with the given parameters.
    
    Args:
        param1: The first parameter
        param2: The second parameter (default: 10)
        
    Returns:
        A dictionary containing the workflow results
    """
    # Implementation
    return {
        "success": True,
        "data": {
            # Custom data
        },
        "message": "Custom workflow executed successfully",
    }
```

### Creating Specialized Agents

You can create specialized agents for specific tasks:

```python
specialized_agent = Agent(
    name="SpecializedAgent",
    instructions="You are a specialized agent for handling specific tasks.",
    tools=[specialized_tool_1, specialized_tool_2],
)

# Add the specialized agent to the Director Agent
director_agent = create_director_agent(
    workflow_tools=[workflow_x_tool, workflow_y_tool],
    specialized_agents=[specialized_agent],
)
```

## Advanced Features

### Tracing

The Director Agent uses tracing to track the execution of workflows:

```python
with trace("Director Agent Workflow", trace_id=trace_id):
    with custom_span("Request Analysis"):
        # Request analysis code
    
    with custom_span("Result Evaluation"):
        # Result evaluation code
```

You can view traces in the OpenAI Platform:

```
https://platform.openai.com/traces/{trace_id}
```

### Error Handling

The Director Agent includes error handling for workflow errors:

```python
if not result.success:
    error_input = ERROR_HANDLING_TEMPLATE.format(
        user_request=user_request,
        error_details=result.error,
    )
    error_result = await Runner.run(
        self.agent,
        input=error_input,
    )
    return str(error_result.final_output)
```

## Best Practices

1. **Clear Workflow Descriptions**: Provide clear descriptions for each workflow tool to help the agent select the most appropriate one.
2. **Comprehensive System Instructions**: Define the agent's role and responsibilities clearly in the system instructions.
3. **Proper Error Handling**: Implement proper error handling for workflow errors.
4. **Evaluation Logic**: Implement thorough evaluation logic to determine if additional processing is needed.
5. **Tracing**: Use tracing to track the execution of workflows and debug issues.

## Conclusion

The Director Agent provides a powerful way to orchestrate workflows based on user requests. By following the "Working Backwards" methodology, it can determine the most appropriate workflow to fulfill a request and provide a clear, concise response to the user.
