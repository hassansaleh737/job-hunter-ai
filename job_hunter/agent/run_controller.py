"""Session-local background run controller; one running job per user session.

Streamlit session state is never touched from worker threads. A shared registry
blocks starting a replacement run until the prior network worker has finished,
even after the UI clears its pointer to a cancelled run.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import threading, uuid
from job_hunter.agent.orchestrator import run_pipeline


class RunBusyError(RuntimeError):
    """The previous worker for this user session has not exited yet."""


_registry_lock = threading.Lock()
_session_futures: dict[str, Future] = {}


def is_running(session_key: str) -> bool:
    with _registry_lock:
        current = _session_futures.get(session_key)
        return current is not None and not current.done()


class RunController:
    def __init__(self, profile, pref, mode, version, pipeline=run_pipeline, session_key=None):
        self.run_id = uuid.uuid4().hex
        self.session_key = session_key or uuid.uuid4().hex
        self.version = version
        self.mode = mode
        self.queue = Queue()
        self.cancel_flag = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.stages = {s: "Pending" for s in [
            "Preparing search based on your profile", "Searching Remotive",
            "Searching Greenhouse", "Verifying job details and restrictions",
            "Evaluating skills match and eligibility", "Preparing results",
        ]}
        self.messages = []
        self.checked = 0
        self.total = 0
        self.state = "Running"
        self.result = []
        self.outcomes = {}
        self.collected = ""
        with _registry_lock:
            previous = _session_futures.get(self.session_key)
            if previous is not None and not previous.done():
                self.executor.shutdown(wait=False)
                raise RunBusyError("A previous search is still finishing. Retry after it exits.")
            self.future = self.executor.submit(
                self._worker, pipeline, profile.model_copy(deep=True), pref.model_copy(deep=True)
            )
            _session_futures[self.session_key] = self.future

        def release(future):
            with _registry_lock:
                if _session_futures.get(self.session_key) is future:
                    _session_futures.pop(self.session_key, None)
        self.future.add_done_callback(release)

    def _worker(self, pipeline, profile, pref):
        try:
            result, outcomes, collected = pipeline(
                profile, pref, self.mode,
                lambda kind, payload: self.queue.put((kind, payload)),
                self.cancel_flag.is_set,
            )
            self.queue.put(("done", {"result": result, "outcomes": outcomes, "collected": collected}))
        except InterruptedError:
            self.queue.put(("cancelled", {}))
        except Exception as exc:
            # Never expose raw provider exception messages (may contain CV text).
            self.queue.put(("failed", {
                "error": "Search failed. Please retry or use the dated snapshot option.",
                "type": type(exc).__name__,
            }))
        finally:
            self.executor.shutdown(wait=False, cancel_futures=True)

    def cancel(self):
        self.cancel_flag.set()
        self.state = "Cancelled"

    def poll(self):
        while True:
            try:
                kind, payload = self.queue.get_nowait()
            except Empty:
                break
            if self.cancel_flag.is_set():
                continue
            if kind == "stage":
                self.stages[payload["name"]] = payload["status"]
            elif kind == "info":
                self.messages.append(payload["message"])
            elif kind == "count":
                self.checked, self.total = payload["checked"], payload["total"]
            elif kind == "done":
                self.result = payload["result"]
                self.outcomes = payload["outcomes"]
                self.collected = payload["collected"]
                self.state = "Completed"
            elif kind == "failed":
                self.state = "Failed"
                self.messages.append(payload["error"])
            elif kind == "cancelled":
                self.state = "Cancelled"
