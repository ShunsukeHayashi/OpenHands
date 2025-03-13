"""
Example usage of the Director Agent.

This script demonstrates how to use the Director Agent to process
various types of user requests.
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional

from agents import Agent, Runner, trace, gen_trace_id
from agents.tracing import Span

from ..agents.director_agent import DirectorAgent, create_director_agent
from ..tools.workflow_tools import (
    workflow_x_tool,
    workflow_y_tool,
    workflow_z_tool,
    error_simulation_tool,
)


async def run_example(user_request: str, trace_id: Optional[str] = None) -> None:
    """
    Run an example with the Director Agent.
    
    Args:
        user_request: The user's request
        trace_id: Optional trace ID for tracking
    """
    # Create workflow tools
    workflow_tools = [
        workflow_x_tool,
        workflow_y_tool,
        workflow_z_tool,
        error_simulation_tool,
    ]
    
    # Create specialized agents (optional)
    specialized_agents = []
    
    # Create the Director Agent
    director_agent = create_director_agent(
        workflow_tools=workflow_tools,
        specialized_agents=specialized_agents,
        name="ExampleDirectorAgent",
        description="An example Director Agent for demonstration",
    )
    
    # Generate a trace ID if not provided
    if trace_id is None:
        trace_id = gen_trace_id()
    
    print(f"Trace ID: {trace_id}")
    print(f"View trace: https://platform.openai.com/traces/{trace_id}")
    print("\n" + "="*50 + "\n")
    
    print(f"User request: {user_request}")
    print("\n" + "-"*50 + "\n")
    
    # Process the request
    response = await director_agent.process_request(
        user_request=user_request,
        trace_id=trace_id,
    )
    
    print("Director Agent response:")
    print("\n" + "-"*50 + "\n")
    print(response)
    print("\n" + "="*50 + "\n")


async def run_streaming_example(user_request: str, trace_id: Optional[str] = None) -> None:
    """
    Run a streaming example with the Director Agent.
    
    Args:
        user_request: The user's request
        trace_id: Optional trace ID for tracking
    """
    from openai.types.responses import ResponseTextDeltaEvent
    from agents import RawResponsesStreamEvent
    
    # Create workflow tools
    workflow_tools = [
        workflow_x_tool,
        workflow_y_tool,
        workflow_z_tool,
        error_simulation_tool,
    ]
    
    # Create specialized agents (optional)
    specialized_agents = []
    
    # Create the Director Agent
    director_agent = create_director_agent(
        workflow_tools=workflow_tools,
        specialized_agents=specialized_agents,
        name="ExampleDirectorAgent",
        description="An example Director Agent for demonstration",
    )
    
    # Generate a trace ID if not provided
    if trace_id is None:
        trace_id = gen_trace_id()
    
    print(f"Trace ID: {trace_id}")
    print(f"View trace: https://platform.openai.com/traces/{trace_id}")
    print("\n" + "="*50 + "\n")
    
    print(f"User request: {user_request}")
    print("\n" + "-"*50 + "\n")
    
    print("Director Agent response (streaming):")
    print("\n" + "-"*50 + "\n")
    
    # Process the request with streaming
    result = await director_agent.run_streamed(
        user_request=user_request,
        trace_id=trace_id,
    )
    
    async for event in result.stream_events():
        if isinstance(event, RawResponsesStreamEvent):
            data = event.data
            if isinstance(data, ResponseTextDeltaEvent):
                print(data.delta, end="", flush=True)
    
    print("\n" + "="*50 + "\n")


async def main() -> None:
    """Run the Director Agent examples."""
    # Example requests
    example_requests = [
        "東京の天気を教えてください",
        "Find information about the latest smartphones",
        "カテゴリ「スポーツ」の最新情報を3件取得してください",
        "Get detailed information about item with ID 42",
        "Simulate a 'not_found' error for testing",
    ]
    
    # Run examples
    for i, request in enumerate(example_requests):
        print(f"\nExample {i+1}:")
        await run_example(request)
    
    # Run a streaming example
    print("\nStreaming Example:")
    await run_streaming_example("Tell me about the weather in New York")


if __name__ == "__main__":
    asyncio.run(main())
