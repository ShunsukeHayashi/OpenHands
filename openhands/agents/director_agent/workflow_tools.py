"""
Workflow tools for the Director Agent.

This module implements various workflow tools that the Director Agent
can use to fulfill user requests.
"""

from typing import Dict, List, Optional, Any
import asyncio
import json
import random

from agents import function_tool


@function_tool
async def workflow_x_tool(query: str) -> Dict[str, Any]:
    """
    Execute Workflow X with the given query.
    
    This workflow is designed for retrieving specific data based on a search query.
    
    Args:
        query: The search query or parameters for the workflow
        
    Returns:
        A dictionary containing the workflow results
    """
    # Simulate API call with a delay
    await asyncio.sleep(1)
    
    # Simulate workflow execution
    # In a real implementation, this would call an actual API or service
    return {
        "success": True,
        "data": {
            "items": [
                {"id": 1, "name": f"Result 1 for {query}", "score": 0.95},
                {"id": 2, "name": f"Result 2 for {query}", "score": 0.87},
                {"id": 3, "name": f"Result 3 for {query}", "score": 0.76},
            ],
            "total_count": 3,
            "query_time_ms": 120,
        },
        "message": "データを正常に取得しました",
    }


@function_tool
async def workflow_y_tool(category: str, limit: int) -> Dict[str, Any]:
    """
    Execute Workflow Y with the given category and limit.
    
    This workflow is designed for retrieving categorized information with a specified limit.
    
    Args:
        category: The category to retrieve information for
        limit: Maximum number of items to return
        
    Returns:
        A dictionary containing the workflow results
    """
    # Simulate API call with a delay
    await asyncio.sleep(1.5)
    
    # Simulate workflow execution
    # In a real implementation, this would call an actual API or service
    items = []
    for i in range(min(limit, 10)):
        items.append({
            "id": i + 1,
            "title": f"{category} Item {i + 1}",
            "description": f"Description for {category} item {i + 1}",
            "rating": round(random.uniform(3.0, 5.0), 1),
        })
    
    return {
        "success": True,
        "data": {
            "category": category,
            "items": items,
            "total_available": min(limit, 10),
            "query_time_ms": 180,
        },
        "message": f"{category}のデータを{len(items)}件取得しました",
    }


@function_tool
async def workflow_z_tool(id: int, include_details: bool) -> Dict[str, Any]:
    """
    Execute Workflow Z to retrieve detailed information about a specific item.
    
    This workflow is designed for retrieving detailed information about a specific item by ID.
    
    Args:
        id: The ID of the item to retrieve
        include_details: Whether to include additional details
        
    Returns:
        A dictionary containing the workflow results
    """
    # Simulate API call with a delay
    await asyncio.sleep(0.8)
    
    # Simulate workflow execution
    # In a real implementation, this would call an actual API or service
    
    # Basic item data
    item_data = {
        "id": id,
        "name": f"Item {id}",
        "created_at": "2023-01-15T12:30:45Z",
        "updated_at": "2023-03-22T09:15:30Z",
        "status": "active",
    }
    
    # Add details if requested
    if include_details:
        item_data["details"] = {
            "description": f"Detailed description for Item {id}",
            "attributes": {
                "color": random.choice(["red", "blue", "green", "yellow"]),
                "size": random.choice(["small", "medium", "large"]),
                "weight": round(random.uniform(0.5, 10.0), 2),
            },
            "tags": [f"tag{random.randint(1, 10)}" for _ in range(3)],
        }
    
    return {
        "success": True,
        "data": item_data,
        "message": f"ID {id}のアイテム情報を取得しました",
    }


@function_tool
async def error_simulation_tool(error_type: str) -> Dict[str, Any]:
    """
    Simulate an error response for testing error handling.
    
    Args:
        error_type: The type of error to simulate
        
    Returns:
        A dictionary containing an error response
    """
    # Simulate API call with a delay
    await asyncio.sleep(0.5)
    
    # Simulate different error types
    if error_type == "not_found":
        return {
            "success": False,
            "data": None,
            "message": None,
            "error": "Requested resource not found",
        }
    elif error_type == "permission_denied":
        return {
            "success": False,
            "data": None,
            "message": None,
            "error": "Permission denied to access this resource",
        }
    elif error_type == "rate_limit":
        return {
            "success": False,
            "data": None,
            "message": None,
            "error": "Rate limit exceeded. Please try again later.",
        }
    else:
        return {
            "success": False,
            "data": None,
            "message": None,
            "error": f"Unknown error: {error_type}",
        }
