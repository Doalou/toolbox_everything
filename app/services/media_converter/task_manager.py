import queue
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict


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
    def __init__(self, max_workers=4):
        self.tasks: Dict[str, Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.queue = queue.Queue()

    async def create_task(self, func: Callable, *args, **kwargs) -> str:
        task_id = str(uuid.uuid4())
        task = Task(task_id)
        self.tasks[task_id] = task

        future = self.executor.submit(func, task, *args, **kwargs)
        future.add_done_callback(lambda f: self._task_complete(task_id, f))

        return task_id

    def _task_complete(self, task_id: str, future):
        try:
            self.tasks[task_id].result = future.result()
            self.tasks[task_id].status = "completed"
        except Exception as e:
            self.tasks[task_id].error = str(e)
            self.tasks[task_id].status = "failed"
        finally:
            if task_id in self.tasks:
                # Nettoyer la tâche après un délai
                threading.Timer(3600, lambda: self.tasks.pop(task_id, None)).start()

    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].cancel_requested = True


# Instance globale du gestionnaire de tâches
task_manager = TaskManager()
