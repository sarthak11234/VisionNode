"""
LangGraph Agent State.

This defines the TypedDict representing the core state passed between 
nodes in our LangGraph execution sequence.
"""

from typing import TypedDict, Optional, Any

class AgentState(TypedDict):
    """
    State object passed across LangGraph nodes.
    
    Attributes:
        rule_id: The ID of the matching AgentRule.
        row_id: The ID of the Row that triggered the rule.
        row_data: The JSON data payload of the Row.
        action_type: What to do (e.g. 'email', 'whatsapp').
        trigger_column: The column that triggered this action.
        trigger_value: The value that caused the trigger.
        action_result: Detailed outcome dict (e.g., Message SID).
        status: The final status ('success', 'failed', 'skipped').
        error_message: If failed, what went wrong.
    """
    rule_id: str
    row_id: str
    row_data: dict[str, Any]
    action_type: str
    trigger_column: str
    trigger_value: str
    
    # Written by execution nodes
    action_result: Optional[dict[str, Any]]
    status: Optional[str]
    error_message: Optional[str]
