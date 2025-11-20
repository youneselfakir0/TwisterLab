#!/usr/bin/env python3
"""Insert workflow method into orchestrator"""

# Read the orchestrator file
with open("/home/twister/TwisterLab/agents/orchestrator/autonomous_orchestrator.py", "r") as f:
    lines = f.readlines()

# Read the workflow method
with open("/home/twister/TwisterLab/workflow_method.py", "r") as f:
    workflow_lines = f.readlines()

# Find where to insert (before get_orchestrator function or at end of class)
insert_index = -1
for i, line in enumerate(lines):
    if "async def get_orchestrator" in line or "# Global orchestrator instance" in line:
        insert_index = i
        break

if insert_index == -1:
    # Insert before last few lines
    insert_index = len(lines) - 5

# Insert the workflow method
new_lines = lines[:insert_index] + ["\n"] + workflow_lines + ["\n"] + lines[insert_index:]

# Write back
with open("/home/twister/TwisterLab/agents/orchestrator/autonomous_orchestrator.py", "w") as f:
    f.writelines(new_lines)

print(f"Workflow method inserted at line {insert_index}")
print("Verification:")
print(f"Total lines before: {len(lines)}")
print(f"Total lines after: {len(new_lines)}")
print(f"Workflow method lines: {len(workflow_lines)}")
