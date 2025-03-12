"""
Tools integration for GoalSeek Agent.

This module provides functionality for integrating with OpenHands tools system.
"""

from typing import Dict, List, Any, Optional
import logging

from openhands.runtime.plugins import (
    AgentSkillsRequirement,
    JupyterRequirement,
    PluginRequirement,
)

logger = logging.getLogger(__name__)

def get_tools(enable_browsing: bool = True, 
             enable_jupyter: bool = True) -> List[PluginRequirement]:
    """
    Get the tools for the GoalSeek Agent.
    
    Args:
        enable_browsing: Whether to enable browsing
        enable_jupyter: Whether to enable Jupyter
        
    Returns:
        List of plugin requirements
    """
    tools = []
    
    # Add agent skills
    tools.append(AgentSkillsRequirement())
    
    # Add Jupyter if enabled
    if enable_jupyter:
        tools.append(JupyterRequirement())
    
    # Add browsing if enabled
    if enable_browsing:
        # Note: Browsing is typically handled through the agent configuration
        # rather than through plugins in OpenHands
        pass
    
    return tools
