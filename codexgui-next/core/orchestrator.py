"""
Orchestrator Module

Manages application state and coordinates between components.
"""

from enum import Enum
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import json

from core.openai_client import OpenAIClient
from core.runner import LocalRunner, RunnerEvent, RunnerState
from core.storage import get_storage


class OrchestratorState(Enum):
    """Application states."""
    IDLE = "idle"
    PLANNING = "planning"          # Generating plan with OpenAI
    CLARIFYING = "clarifying"      # Waiting for user clarification
    REVIEWING = "reviewing"        # User reviewing plan
    RUNNING = "running"            # Executing with Runner
    SUMMARIZING = "summarizing"    # Summarizing results
    APPLYING = "applying"          # Applying changes (M3)
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Task:
    """Current task information."""
    task_id: str
    task_title: str
    user_request: str
    folder_path: str
    selected_files: list
    plan: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class Orchestrator:
    """
    Orchestrates the workflow between OpenAI API and Codex CLI.
    
    State machine:
    IDLE → PLANNING → [CLARIFYING] → REVIEWING → RUNNING → SUMMARIZING → COMPLETED
                                                         ↓
                                                       ERROR
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.state = OrchestratorState.IDLE
        self.storage = get_storage()
        self.openai_client: Optional[OpenAIClient] = None
        self.runner = LocalRunner()
        self.current_task: Optional[Task] = None
        
        # Callbacks
        self.on_state_changed: Optional[Callable[[OrchestratorState], None]] = None
        self.on_message: Optional[Callable[[str, str], None]] = None  # (message, sender)
        self.on_plan_ready: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_runner_event: Optional[Callable[[RunnerEvent], None]] = None
    
    def initialize(self):
        """Initialize OpenAI client with API key."""
        api_key = self.storage.get_api_key()
        
        if not api_key:
            return False
        
        try:
            self.openai_client = OpenAIClient(api_key)
            return True
        except Exception as e:
            self._emit_message(f"OpenAI API の初期化に失敗: {e}", "system")
            return False
    
    def start_task(
        self,
        task_id: str,
        task_title: str,
        user_request: str,
        folder_path: str,
        selected_files: list
    ):
        """
        Start a new task.
        
        Args:
            task_id: Task template ID
            task_title: Task title
            user_request: User's request text
            folder_path: Target folder path
            selected_files: Selected file paths
        """
        # Check if OpenAI is initialized
        if not self.openai_client:
            if not self.initialize():
                self._emit_message(
                    "OpenAI API キーが設定されていません。設定画面で API キーを入力してください。",
                    "system"
                )
                return
        
        # Create task
        self.current_task = Task(
            task_id=task_id,
            task_title=task_title,
            user_request=user_request,
            folder_path=folder_path,
            selected_files=selected_files
        )
        
        # Start planning
        self._transition_to(OrchestratorState.PLANNING)
        self._generate_plan()
    
    def _generate_plan(self):
        """Generate execution plan using OpenAI."""
        if not self.current_task or not self.openai_client:
            return
        
        self._emit_message("実行計画を生成しています...", "system")
        
        try:
            # Prepare context
            task_context = {
                "id": self.current_task.task_id,
                "title": self.current_task.task_title
            }
            
            folder_info = {
                "path": self.current_task.folder_path,
                "selected_files": self.current_task.selected_files,
                "file_count": len(self.current_task.selected_files) if self.current_task.selected_files else 0
            }
            
            # Generate plan
            plan = self.openai_client.generate_plan(
                self.current_task.user_request,
                task_context,
                folder_info
            )
            
            self.current_task.plan = plan
            
            # Check plan type
            if plan.get('type') == 'clarify':
                # Need clarification
                self._transition_to(OrchestratorState.CLARIFYING)
                question = plan.get('question', '追加情報が必要です')
                self._emit_message(question, "assistant")
                
            elif plan.get('type') == 'plan':
                # Plan ready
                self._transition_to(OrchestratorState.REVIEWING)
                self._emit_plan_ready(plan)
                
        except Exception as e:
            self._transition_to(OrchestratorState.ERROR)
            self._emit_message(f"計画生成エラー: {e}", "system")
    
    def provide_clarification(self, answer: str):
        """
        Provide answer to clarification question.
        
        Args:
            answer: User's answer
        """
        if self.state != OrchestratorState.CLARIFYING:
            return
        
        # Add to request and regenerate plan
        if self.current_task:
            self.current_task.user_request += f"\n\n補足: {answer}"
            self._transition_to(OrchestratorState.PLANNING)
            self._generate_plan()
    
    def execute_plan(self):
        """Execute the current plan with Runner."""
        if self.state != OrchestratorState.REVIEWING or not self.current_task:
            return
        
        plan = self.current_task.plan
        if not plan:
            return
        
        self._transition_to(OrchestratorState.RUNNING)
        self._emit_message("実行を開始します...", "system")
        
        # Build prompt from plan
        prompt = self._build_prompt_from_plan(plan)
        
        # Execute with Runner
        self.runner.execute(
            prompt=prompt,
            working_dir=self.current_task.folder_path,
            callback=self._on_runner_event_received
        )
    
    def _build_prompt_from_plan(self, plan: Dict[str, Any]) -> str:
        """Build Codex CLI prompt from plan."""
        steps = plan.get('steps', [])
        
        if not steps:
            return self.current_task.user_request
        
        # Simple prompt building for M2
        # TODO: M3 will have more sophisticated prompt generation
        prompt_parts = []
        
        for step in steps:
            description = step.get('description', '')
            if description:
                prompt_parts.append(description)
        
        return '\n'.join(prompt_parts) if prompt_parts else self.current_task.user_request
    
    def _on_runner_event_received(self, event: RunnerEvent):
        """Handle Runner event."""
        # Emit to UI
        if self.on_runner_event:
            self.on_runner_event(event)
        
        # Check if execution finished
        if event.type in ['status', 'error']:
            state = self.runner.get_state()
            
            if state in [RunnerState.COMPLETED, RunnerState.FAILED, RunnerState.CANCELLED]:
                self._on_execution_finished(state)
    
    def _on_execution_finished(self, runner_state: RunnerState):
        """Handle execution completion."""
        if not self.current_task:
            return
        
        # Store result
        events = self.runner.get_events()
        self.current_task.execution_result = {
            'state': runner_state.value,
            'exit_code': 0 if runner_state == RunnerState.COMPLETED else -1,
            'stdout': '\n'.join([e.data for e in events if e.type == 'stdout']),
            'stderr': '\n'.join([e.data for e in events if e.type == 'stderr']),
            'events': [{'type': e.type, 'data': e.data} for e in events]
        }
        
        # Summarize result
        if runner_state == RunnerState.COMPLETED:
            self._transition_to(OrchestratorState.SUMMARIZING)
            self._summarize_result()
        else:
            self._transition_to(OrchestratorState.ERROR)
            self._emit_message("実行に失敗しました", "system")
    
    def _summarize_result(self):
        """Summarize execution result using OpenAI."""
        if not self.current_task or not self.openai_client:
            return
        
        try:
            summary = self.openai_client.summarize_result(
                self.current_task.plan,
                self.current_task.execution_result
            )
            
            self.current_task.summary = summary
            
            self._transition_to(OrchestratorState.COMPLETED)
            self._emit_message(summary, "assistant")
            
            # Save to history
            self._save_to_history()
            
        except Exception as e:
            self._transition_to(OrchestratorState.ERROR)
            self._emit_message(f"要約エラー: {e}", "system")
    
    def cancel(self):
        """Cancel current operation."""
        if self.state == OrchestratorState.RUNNING:
            self.runner.cancel()
        
        self._transition_to(OrchestratorState.IDLE)
        self._emit_message("操作をキャンセルしました", "system")
    
    def _save_to_history(self):
        """Save current task to history."""
        if not self.current_task:
            return
        
        entry = {
            'task_id': self.current_task.task_id,
            'task_title': self.current_task.task_title,
            'user_request': self.current_task.user_request,
            'folder_path': self.current_task.folder_path,
            'success': self.current_task.execution_result.get('exit_code', -1) == 0,
            'summary': self.current_task.summary
        }
        
        self.storage.add_history_entry(entry)
    
    def _transition_to(self, new_state: OrchestratorState):
        """Transition to new state."""
        self.state = new_state
        
        if self.on_state_changed:
            self.on_state_changed(new_state)
    
    def _emit_message(self, message: str, sender: str):
        """Emit message to UI."""
        if self.on_message:
            self.on_message(message, sender)
    
    def _emit_plan_ready(self, plan: Dict[str, Any]):
        """Emit plan ready event."""
        if self.on_plan_ready:
            self.on_plan_ready(plan)
    
    def get_state(self) -> OrchestratorState:
        """Get current state."""
        return self.state
    
    def is_busy(self) -> bool:
        """Check if orchestrator is busy."""
        return self.state not in [
            OrchestratorState.IDLE,
            OrchestratorState.COMPLETED,
            OrchestratorState.ERROR
        ]
