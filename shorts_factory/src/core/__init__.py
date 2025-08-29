"""
Core functionality for Shorts Factory
"""

from core.config import config
from core.approval_workflow import ApprovalWorkflowMonitor
from core.script_generator import ScriptGenerator
from core.audio_generator import AudioGenerator

__all__ = ['config', 'ApprovalWorkflowMonitor', 'ScriptGenerator', 'AudioGenerator']
