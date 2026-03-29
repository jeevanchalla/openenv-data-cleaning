from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class Observation(BaseModel):
    task_id: str
    task_description: str
    dataset: List[Dict[str, Any]]
    step_number: int
    max_steps: int
    last_action: Optional[str] = None
    last_action_error: Optional[str] = None
    progress: float = 0.0


class Action(BaseModel):
    action_type: str  # "fix_nulls", "fix_types", "remove_duplicates", "normalize", "done"
    column: Optional[str] = None
    method: Optional[str] = None
    value: Optional[Any] = None
    rows: Optional[List[int]] = None


class Reward(BaseModel):
    score: float
    partial_scores: Dict[str, float]
    message: str
