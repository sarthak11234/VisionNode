import traceback
import sys

try:
    from app.agents.workflow import agent_app
    print("Agent app imported successfully!")
except Exception as e:
    with open("import_error.txt", "w") as f:
        f.write(traceback.format_exc())
    print("Wrote error to import_error.txt")
