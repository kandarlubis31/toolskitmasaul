"""Background task worker for non-blocking operations.
Uses Python threading.Thread instead of QThread to avoid C++ segfaults
when running as Administrator in PyInstaller builds."""
import threading
from PyQt6.QtCore import QObject, pyqtSignal


class TaskWorker(QObject):
    progress = pyqtSignal(str)
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, target, args=None, kwargs=None):
        super().__init__()
        self._target = target
        self._args = args or ()
        self._kwargs = kwargs or {}
        self._cancelled = False
        self._thread = None

    def start(self):
        def _run():
            if self._cancelled:
                return
            try:
                output = self._target(*self._args, **self._kwargs)
                if not self._cancelled:
                    self.result.emit(output)
            except Exception as e:
                if not self._cancelled:
                    self.error.emit(str(e))

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def cancel(self):
        self._cancelled = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)


class MultiStepWorker(QObject):
    """Worker for multi-step tasks with progress reporting."""

    progress = pyqtSignal(str)
    step_completed = pyqtSignal(int, str)
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, steps: list):
        super().__init__()
        self.steps = steps
        self._cancelled = False
        self._thread = None

    def start(self):
        def _run():
            results = []
            try:
                for i, (name, func) in enumerate(self.steps):
                    if self._cancelled:
                        return
                    self.progress.emit(f"Running: {name}...")
                    result = func()
                    results.append(result)
                    self.step_completed.emit(i + 1, name)
                if not self._cancelled:
                    self.result.emit(results)
            except Exception as e:
                if not self._cancelled:
                    self.error.emit(str(e))

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def cancel(self):
        self._cancelled = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
