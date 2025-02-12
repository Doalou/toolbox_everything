from typing import Dict, Callable
import threading
import queue
import uuid
import time

class Task:
    def __init__(self, task_id: str, total_steps: int = 100):
        self.id = task_id
        self.progress = 0
        self.total_steps = total_steps
        self.status = "pending"
        self.result = None
        self.error = None
        self.cancel_requested = False
        self._callbacks: Dict[str, Callable] = {}

    def update_progress(self, current: int, message: str = ""):
        self.progress = min(100, int((current / self.total_steps) * 100))
        self._notify_progress(message)

    def _notify_progress(self, message: str):
        if "progress" in self._callbacks:
            self._callbacks["progress"](self.progress, message)

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def create_task(self, func: Callable, *args, **kwargs) -> str:
        task_id = str(uuid.uuid4())
        task = Task(task_id)
        self.tasks[task_id] = task
        
        # Wrapper pour capturer la progression
        def wrapped_func():
            try:
                task.status = "running"
                task.result = func(task, *args, **kwargs)
                task.status = "completed"
            except Exception as e:
                task.error = str(e)
                task.status = "failed"

        self.queue.put((task_id, wrapped_func))
        return task_id

    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].cancel_requested = True

    def _worker(self):
        while True:
            try:
                task_id, func = self.queue.get()
                if task_id in self.tasks:
                    func()
            except Exception as e:
                print(f"Worker error: {e}")
            finally:
                self.queue.task_done()

# Instance globale du gestionnaire de tâches
task_manager = TaskManager()
