"""
LangGraph Workflow Definition for Agent Rules.

State Machine Flow:
1. `check_condition`: Verifies the row matches the trigger criteria
2. `execute_action`: Calls the specific communication tool (Email, WhatsApp, etc)
3. `log_result`: Writes the final outcome to the database (handled by caller task)
"""

from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.tools import send_email_tool, send_whatsapp_tool, create_whatsapp_group_tool
from app.core.constants import ACTION_TYPE_WHATSAPP, ACTION_TYPE_GROUP, ACTION_TYPE_EMAIL

async def check_condition(state: AgentState) -> dict:
    """Validate that the trigger condition is met by the row data."""
    val = state["row_data"].get(state["trigger_column"])
    
    if str(val) == str(state["trigger_value"]):
        return {"status": "triggered"}
    else:
        return {
            "status": "skipped",
            "error_message": f"Condition not met: {val} != {state['trigger_value']}"
        }

async def execute_action(state: AgentState) -> dict:
    """Call the external communication provider."""
    # Skip if condition failed (should be caught by routing, but safe check)
    if state.get("status") == "skipped":
        return {}
        
    try:
        action = state["action_type"].lower()
        if action == "email":
            res = await send_email_tool(state)
            return {"action_result": res, "status": "success"}
        elif action in [ACTION_TYPE_WHATSAPP, "whatsapp"]:
            res = await send_whatsapp_tool(state)
            return {"action_result": res, "status": "success"}
        elif action in [ACTION_TYPE_GROUP, "create_whatsapp_group"]:
            res = await create_whatsapp_group_tool(state)
            return {"action_result": res, "status": "success"}
        else:
            return {"status": "failed", "error_message": f"Unknown action: {action}"}
    except Exception as e:
        return {"status": "failed", "error_message": str(e)}

# --- Routing ---

def should_execute(state: AgentState) -> str:
    """Route based on condition check."""
    if state.get("status") == "skipped":
        return END
    return "execute_action"

# --- Graph Assembly ---

workflow = StateGraph(AgentState)

workflow.add_node("check_condition", check_condition)
workflow.add_node("execute_action", execute_action)

workflow.add_edge(START, "check_condition")
workflow.add_conditional_edges("check_condition", should_execute)
workflow.add_edge("execute_action", END)

# Compile into a runnable app
agent_app = workflow.compile()
