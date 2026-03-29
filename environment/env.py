import copy
import statistics
from typing import Any, Dict, List, Optional, Tuple

from environment.models import Action, Observation, Reward
from environment.tasks import get_task
from environment.graders import grade

MAX_STEPS = 20


class DataCleaningEnv:
    def __init__(self, task_id: str = "task_easy"):
        self.task_id = task_id
        self._task: Dict[str, Any] = {}
        self._dataset: List[Dict[str, Any]] = []
        self._step_number: int = 0
        self._done: bool = False
        self._goals_achieved: Dict[str, bool] = {}
        self._last_action: Optional[str] = None
        self._last_error: Optional[str] = None
        self._cumulative_reward: float = 0.0

    # ── public API ────────────────────────────────────────────────────────────

    def reset(self) -> Observation:
        self._task = get_task(self.task_id)
        self._dataset = copy.deepcopy(self._task["dataset"])
        self._step_number = 0
        self._done = False
        self._goals_achieved = {k: False for k in self._task["goals"]}
        self._last_action = None
        self._last_error = None
        self._cumulative_reward = 0.0
        return self._make_observation()

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        if self._done:
            return self._make_observation(), 0.0, True, {"info": "Episode already done"}

        self._step_number += 1
        self._last_error = None
        self._last_action = action.action_type

        # ── dispatch action ──────────────────────────────────────────────────
        try:
            if action.action_type == "done":
                self._done = True
            elif action.action_type == "remove_duplicates":
                self._action_remove_duplicates()
            elif action.action_type == "fix_nulls":
                self._action_fix_nulls(action.column, action.method, action.value)
            elif action.action_type == "fix_types":
                self._action_fix_types(action.column, action.method)
            elif action.action_type == "normalize":
                self._action_normalize(action.column, action.method)
            elif action.action_type == "remove_rows":
                self._action_remove_rows(action.column, action.method)
            else:
                self._last_error = f"Unknown action_type: {action.action_type}"
        except Exception as exc:
            self._last_error = str(exc)

        # ── grade current state ──────────────────────────────────────────────
        result = grade(self.task_id, self._dataset, self._goals_achieved)
        score: float = result["score"]

        # partial reward = improvement over cumulative reward so far
        step_reward = max(0.0, score - self._cumulative_reward)
        self._cumulative_reward = max(self._cumulative_reward, score)

        # small penalty for errors
        if self._last_error:
            step_reward -= 0.05

        # penalty for running out of steps without finishing
        if self._step_number >= MAX_STEPS and not self._done:
            self._done = True
            step_reward -= 0.1

        step_reward = round(max(-1.0, step_reward), 4)
        obs = self._make_observation(progress=score)

        info = {
            "grader": result,
            "cumulative_reward": self._cumulative_reward,
            "step_reward": step_reward,
        }
        return obs, step_reward, self._done, info

    def state(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "step_number": self._step_number,
            "done": self._done,
            "dataset": copy.deepcopy(self._dataset),
            "cumulative_reward": self._cumulative_reward,
            "goals_achieved": copy.deepcopy(self._goals_achieved),
        }

    # ── actions ───────────────────────────────────────────────────────────────

    def _action_remove_duplicates(self):
        seen = []
        unique = []
        for row in self._dataset:
            r = {k: v for k, v in row.items() if k not in ("id", "employee_id")}
            if r not in seen:
                seen.append(r)
                unique.append(row)
        self._dataset = unique

    def _action_fix_nulls(self, column: Optional[str], method: Optional[str], value: Any):
        if not column:
            raise ValueError("fix_nulls requires 'column'")
        method = method or "value"
        if method == "mean":
            nums = [r[column] for r in self._dataset if r.get(column) is not None]
            fill = statistics.mean(nums) if nums else 0
        elif method == "median":
            nums = [r[column] for r in self._dataset if r.get(column) is not None]
            fill = statistics.median(nums) if nums else 0
        elif method == "value":
            fill = value if value is not None else 0
        else:
            raise ValueError(f"Unknown method for fix_nulls: {method}")
        for row in self._dataset:
            if row.get(column) is None:
                row[column] = fill

    def _action_fix_types(self, column: Optional[str], method: Optional[str]):
        if not column:
            raise ValueError("fix_types requires 'column'")
        method = method or "float"
        for row in self._dataset:
            v = row.get(column)
            if v is None:
                continue
            try:
                if method == "float":
                    row[column] = float(v)
                elif method == "int":
                    row[column] = int(float(v))
                elif method == "str":
                    row[column] = str(v)
            except (ValueError, TypeError):
                row[column] = None

    def _action_normalize(self, column: Optional[str], method: Optional[str]):
        if not column:
            raise ValueError("normalize requires 'column'")
        method = method or "upper"
        for row in self._dataset:
            v = row.get(column)
            if not isinstance(v, str):
                continue
            if method == "upper":
                row[column] = v.upper()
            elif method == "lower":
                row[column] = v.lower()
            elif method == "title":
                row[column] = v.title()
            elif method == "date_iso":
                row[column] = _parse_date_to_iso(v)
            else:
                raise ValueError(f"Unknown normalize method: {method}")

    def _action_remove_rows(self, column: Optional[str], method: Optional[str]):
        if not column:
            raise ValueError("remove_rows requires 'column'")
        if method == "null":
            self._dataset = [r for r in self._dataset if r.get(column) is not None]
        else:
            raise ValueError(f"Unknown remove_rows method: {method}")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _make_observation(self, progress: float = 0.0) -> Observation:
        return Observation(
            task_id=self.task_id,
            task_description=self._task.get("description", ""),
            dataset=copy.deepcopy(self._dataset),
            step_number=self._step_number,
            max_steps=MAX_STEPS,
            last_action=self._last_action,
            last_action_error=self._last_error,
            progress=progress,
        )


# ── date parser ───────────────────────────────────────────────────────────────

_DATE_FORMATS = [
    "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d",
    "%d/%m/%Y", "%m-%d-%Y",
]


def _parse_date_to_iso(value: str) -> str:
    for fmt in _DATE_FORMATS:
        try:
            from datetime import datetime
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return value  # return as-is if unparseable
