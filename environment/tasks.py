from typing import Any, Dict, List


TASKS = {
    "task_easy": {
        "id": "task_easy",
        "description": (
            "Clean a small customer dataset. "
            "Remove duplicate rows and fill missing 'age' values with the column mean. "
            "Signal done when complete."
        ),
        "difficulty": "easy",
        "dataset": [
            {"id": 1, "name": "Alice",   "age": 30,   "email": "alice@example.com"},
            {"id": 2, "name": "Bob",     "age": None, "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "age": 25,   "email": "charlie@example.com"},
            {"id": 4, "name": "Bob",     "age": None, "email": "bob@example.com"},   # duplicate
            {"id": 5, "name": "Diana",   "age": 35,   "email": "diana@example.com"},
        ],
        "goals": {
            "remove_duplicates": True,
            "fill_nulls_age": True,
        },
    },

    "task_medium": {
        "id": "task_medium",
        "description": (
            "Clean a sales dataset. "
            "Fix null values in 'revenue' with 0, convert 'revenue' column to float, "
            "remove duplicate rows, and normalize 'country' values to uppercase. "
            "Signal done when complete."
        ),
        "difficulty": "medium",
        "dataset": [
            {"id": 1, "product": "Widget A", "revenue": "1500.50", "country": "usa"},
            {"id": 2, "product": "Widget B", "revenue": None,       "country": "UK"},
            {"id": 3, "product": "Widget C", "revenue": "3200.00", "country": "canada"},
            {"id": 4, "product": "Widget B", "revenue": None,       "country": "UK"},   # duplicate
            {"id": 5, "product": "Widget D", "revenue": "750.25",  "country": "india"},
            {"id": 6, "product": "Widget E", "revenue": "bad_val", "country": "usa"},
        ],
        "goals": {
            "remove_duplicates": True,
            "fill_nulls_revenue": True,
            "fix_types_revenue": True,
            "normalize_country": True,
        },
    },

    "task_hard": {
        "id": "task_hard",
        "description": (
            "Clean a complex HR dataset. "
            "Tasks: (1) Remove duplicate employee records. "
            "(2) Fill missing 'salary' with column median. "
            "(3) Convert 'join_date' to a standard format YYYY-MM-DD. "
            "(4) Normalize 'department' to title case. "
            "(5) Remove rows where 'employee_id' is null. "
            "Signal done when complete."
        ),
        "difficulty": "hard",
        "dataset": [
            {"employee_id": "E001", "name": "John",  "salary": 75000, "department": "engineering", "join_date": "01/15/2020"},
            {"employee_id": "E002", "name": "Sara",  "salary": None,  "department": "MARKETING",   "join_date": "2021-03-22"},
            {"employee_id": "E003", "name": "Mike",  "salary": 90000, "department": "Sales",       "join_date": "03-10-2019"},
            {"employee_id": None,   "name": "Ghost", "salary": 50000, "department": "engineering", "join_date": "2022-07-01"},  # null id
            {"employee_id": "E001", "name": "John",  "salary": 75000, "department": "engineering", "join_date": "01/15/2020"},  # duplicate
            {"employee_id": "E004", "name": "Lucy",  "salary": 62000, "department": "hr",          "join_date": "15-08-2023"},
            {"employee_id": "E005", "name": "Tom",   "salary": 81000, "department": "ENGINEERING", "join_date": "2020/11/30"},
        ],
        "goals": {
            "remove_duplicates": True,
            "fill_nulls_salary": True,
            "fix_date_format": True,
            "normalize_department": True,
            "remove_null_ids": True,
        },
    },
}


def get_task(task_id: str) -> Dict[str, Any]:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id: {task_id}. Choose from {list(TASKS.keys())}")
    import copy
    return copy.deepcopy(TASKS[task_id])


def list_tasks() -> List[str]:
    return list(TASKS.keys())
