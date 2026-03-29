import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional

from environment.env import DataCleaningEnv
from environment.models import Action
from environment.tasks import list_tasks

app = FastAPI(
    title="OpenEnv — Data Cleaning Environment",
    description="An OpenEnv-compliant data cleaning environment for AI agents.",
    version="1.0.0",
)

# One env instance per task, keyed by task_id
_envs: Dict[str, DataCleaningEnv] = {}


def _get_env(task_id: str) -> DataCleaningEnv:
    if task_id not in _envs:
        _envs[task_id] = DataCleaningEnv(task_id=task_id)
    return _envs[task_id]


# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "env": "data-cleaning", "tasks": list_tasks()}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return {"tasks": list_tasks()}


@app.post("/reset")
def reset(task_id: str = "task_easy"):
    if task_id not in list_tasks():
        raise HTTPException(status_code=400, detail=f"Unknown task_id: {task_id}")
    env = _get_env(task_id)
    obs = env.reset()
    return obs.model_dump()


@app.post("/step")
def step(action: Action, task_id: str = "task_easy"):
    if task_id not in list_tasks():
        raise HTTPException(status_code=400, detail=f"Unknown task_id: {task_id}")
    env = _get_env(task_id)
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state(task_id: str = "task_easy"):
    if task_id not in list_tasks():
        raise HTTPException(status_code=400, detail=f"Unknown task_id: {task_id}")
    env = _get_env(task_id)
    return env.state()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
