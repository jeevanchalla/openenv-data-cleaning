from typing import Any, Dict, List
import re
from datetime import datetime


# ── helpers ──────────────────────────────────────────────────────────────────

def _has_duplicates(dataset: List[Dict]) -> bool:
    seen = []
    for row in dataset:
        r = {k: v for k, v in row.items() if k != "id"}
        if r in seen:
            return True
        seen.append(r)
    return False


def _any_null(dataset: List[Dict], column: str) -> bool:
    return any(row.get(column) is None for row in dataset)


def _all_float(dataset: List[Dict], column: str) -> bool:
    for row in dataset:
        v = row.get(column)
        if v is None:
            continue
        try:
            float(v)
        except (TypeError, ValueError):
            return False
    return True


def _all_uppercase(dataset: List[Dict], column: str) -> bool:
    return all(
        isinstance(row.get(column), str) and row[column] == row[column].upper()
        for row in dataset
    )


def _all_titlecase(dataset: List[Dict], column: str) -> bool:
    return all(
        isinstance(row.get(column), str) and row[column] == row[column].title()
        for row in dataset
    )


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _all_iso_date(dataset: List[Dict], column: str) -> bool:
    return all(
        isinstance(row.get(column), str) and _DATE_RE.match(row[column])
        for row in dataset
    )


def _no_null_id(dataset: List[Dict], column: str) -> bool:
    return all(row.get(column) is not None for row in dataset)


# ── graders ──────────────────────────────────────────────────────────────────

def grade_easy(dataset: List[Dict[str, Any]], goals_achieved: Dict[str, bool]) -> Dict:
    scores = {}

    # 1. No duplicates
    scores["remove_duplicates"] = 0.0 if _has_duplicates(dataset) else 1.0

    # 2. No null ages
    scores["fill_nulls_age"] = 0.0 if _any_null(dataset, "age") else 1.0

    total = sum(scores.values()) / len(scores)
    return {
        "score": round(total, 4),
        "partial_scores": scores,
        "message": _message(scores),
    }


def grade_medium(dataset: List[Dict[str, Any]], goals_achieved: Dict[str, bool]) -> Dict:
    scores = {}

    scores["remove_duplicates"] = 0.0 if _has_duplicates(dataset) else 1.0
    scores["fill_nulls_revenue"] = 0.0 if _any_null(dataset, "revenue") else 1.0
    scores["fix_types_revenue"] = 1.0 if _all_float(dataset, "revenue") else 0.0
    scores["normalize_country"] = 1.0 if _all_uppercase(dataset, "country") else 0.0

    total = sum(scores.values()) / len(scores)
    return {
        "score": round(total, 4),
        "partial_scores": scores,
        "message": _message(scores),
    }


def grade_hard(dataset: List[Dict[str, Any]], goals_achieved: Dict[str, bool]) -> Dict:
    scores = {}

    scores["remove_duplicates"] = 0.0 if _has_duplicates(dataset) else 1.0
    scores["remove_null_ids"] = 1.0 if _no_null_id(dataset, "employee_id") else 0.0
    scores["fill_nulls_salary"] = 0.0 if _any_null(dataset, "salary") else 1.0
    scores["fix_date_format"] = 1.0 if _all_iso_date(dataset, "join_date") else 0.0
    scores["normalize_department"] = 1.0 if _all_titlecase(dataset, "department") else 0.0

    total = sum(scores.values()) / len(scores)
    return {
        "score": round(total, 4),
        "partial_scores": scores,
        "message": _message(scores),
    }


def _message(scores: Dict[str, float]) -> str:
    passed = [k for k, v in scores.items() if v >= 1.0]
    failed = [k for k, v in scores.items() if v < 1.0]
    parts = []
    if passed:
        parts.append(f"Passed: {', '.join(passed)}")
    if failed:
        parts.append(f"Failed: {', '.join(failed)}")
    return " | ".join(parts)


GRADERS = {
    "task_easy":   grade_easy,
    "task_medium": grade_medium,
    "task_hard":   grade_hard,
}


def grade(task_id: str, dataset: List[Dict], goals_achieved: Dict[str, bool]) -> Dict:
    if task_id not in GRADERS:
        raise ValueError(f"No grader for task_id: {task_id}")
    return GRADERS[task_id](dataset, goals_achieved)
