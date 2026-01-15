"""
Local Runner Module

Executes Codex CLI in background with streaming output and cancellation support.
"""

import subprocess
import threading
import queue
import time
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum


class RunnerState(Enum):
    """Runner execution states."""
    IDLE = "idle"
    RUNNING = "running"
    CANCELLING = "cancelling"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class RunnerEvent:
    """Event from runner execution."""
    type: str  # stdout, stderr, command, status, error
    data: str
    timestamp: float


class LocalRunner:
    """
    Executes Codex CLI with streaming output.
    
    Features:
    - Background execution
    - Real-time stdout/stderr streaming
    - Cancellation support
    - Event logging
    """
    
    def __init__(self, codex_path: str = "codex"):
        """
        Initialize runner.
        
        Args:
            codex_path: Path to codex CLI executable
        """
        self.codex_path = codex_path
        self.state = RunnerState.IDLE
        self.process: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.event_queue = queue.Queue()
        self.output_callback: Optional[Callable[[RunnerEvent], None]] = None
        self.events = []
    
    def execute(
        self,
        prompt: str,
        working_dir: str,
        callback: Optional[Callable[[RunnerEvent], None]] = None
    ):
        """
        Execute Codex CLI command.
        
        Args:
            prompt: The prompt to execute
            working_dir: Working directory for execution
            callback: Callback for streaming events
        """
        if self.state == RunnerState.RUNNING:
            raise RuntimeError("Runner is already executing")
        
        self.output_callback = callback
        self.state = RunnerState.RUNNING
        self.events = []
        
        # Start execution thread
        self.thread = threading.Thread(
            target=self._execute_thread,
            args=(prompt, working_dir),
            daemon=True
        )
        self.thread.start()
    
    def _execute_thread(self, prompt: str, working_dir: str):
        """Thread function for execution."""
        try:
            # Build command
            cmd = [
                self.codex_path,
                "exec",
                "--yolo",
                "--skip-git-repo-check",
                prompt
            ]
            
            # Log command
            self._emit_event(RunnerEvent(
                type="command",
                data=f"Executing: {' '.join(cmd)}",
                timestamp=time.time()
            ))
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            # Read output streams
            stdout_thread = threading.Thread(
                target=self._read_stream,
                args=(self.process.stdout, "stdout"),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self._read_stream,
                args=(self.process.stderr, "stderr"),
                daemon=True
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for completion
            exit_code = self.process.wait()
            
            # Wait for output threads
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            
            # Determine final state
            if self.state == RunnerState.CANCELLING:
                self.state = RunnerState.CANCELLED
                self._emit_event(RunnerEvent(
                    type="status",
                    data="Execution cancelled",
                    timestamp=time.time()
                ))
            elif exit_code == 0:
                self.state = RunnerState.COMPLETED
                self._emit_event(RunnerEvent(
                    type="status",
                    data=f"Completed successfully (exit code: {exit_code})",
                    timestamp=time.time()
                ))
            else:
                self.state = RunnerState.FAILED
                self._emit_event(RunnerEvent(
                    type="error",
                    data=f"Execution failed (exit code: {exit_code})",
                    timestamp=time.time()
                ))
                
        except Exception as e:
            self.state = RunnerState.FAILED
            self._emit_event(RunnerEvent(
                type="error",
                data=f"Error during execution: {str(e)}",
                timestamp=time.time()
            ))
        finally:
            self.process = None
    
    def _read_stream(self, stream, stream_name: str):
        """Read from output stream."""
        try:
            for line in iter(stream.readline, ''):
                if not line:
                    break
                
                # Emit event
                self._emit_event(RunnerEvent(
                    type=stream_name,
                    data=line.rstrip(),
                    timestamp=time.time()
                ))
                
                # Check if cancelled
                if self.state == RunnerState.CANCELLING:
                    break
        except Exception as e:
            self._emit_event(RunnerEvent(
                type="error",
                data=f"Error reading {stream_name}: {str(e)}",
                timestamp=time.time()
            ))
    
    def _emit_event(self, event: RunnerEvent):
        """Emit event to callback and store in history."""
        self.events.append(event)
        
        if self.output_callback:
            try:
                self.output_callback(event)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def cancel(self):
        """Cancel running execution."""
        if self.state != RunnerState.RUNNING:
            return
        
        self.state = RunnerState.CANCELLING
        
        if self.process:
            try:
                self.process.terminate()
                
                # Wait a bit for graceful shutdown
                time.sleep(0.5)
                
                # Force kill if still running
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                print(f"Error cancelling process: {e}")
    
    def is_running(self) -> bool:
        """Check if runner is currently executing."""
        return self.state == RunnerState.RUNNING
    
    def get_state(self) -> RunnerState:
        """Get current state."""
        return self.state
    
    def get_events(self) -> list:
        """Get all events from last execution."""
        return self.events.copy()
