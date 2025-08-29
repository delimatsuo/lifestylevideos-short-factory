"""
Core functionality for Shorts Factory
"""

from core.config import config
from core.approval_workflow import ApprovalWorkflowMonitor
from core.script_generator import ScriptGenerator

__all__ = ['config', 'ApprovalWorkflowMonitor', 'ScriptGenerator']
