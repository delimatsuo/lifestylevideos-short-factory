"""
Core functionality for Shorts Factory
"""

from core.config import config
from core.approval_workflow import ApprovalWorkflowMonitor
from core.script_generator import ScriptGenerator
from core.audio_generator import AudioGenerator
from core.video_sourcing import VideoSourcingManager
from core.video_assembly import VideoAssemblyManager
from core.caption_manager import CaptionManager

__all__ = ['config', 'ApprovalWorkflowMonitor', 'ScriptGenerator', 'AudioGenerator', 'VideoSourcingManager', 'VideoAssemblyManager', 'CaptionManager']
