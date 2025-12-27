from typing import TypedDict

class DevOpsState(TypedDict):
    """
    Working Memory for the DevOps Agent
    """
    mission: str            # The user request
    rag_context: str        # Retrieved docs/files
    terraform_plan: str     # The generated HCL code
    deployment_log: str     # Simulation output
    human_approval: str     # Coworking Gate
    iteration: int