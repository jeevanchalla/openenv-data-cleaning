# 🧹 OpenEnv — Data Cleaning Environment

An [OpenEnv](https://github.com/openenv)-compliant environment where an AI agent learns to clean real-world tabular datasets by identifying and fixing data quality issues.

---

## 📌 Environment Description

Real-world data pipelines constantly struggle with dirty data — null values, duplicate records, wrong types, inconsistent formatting. This environment simulates exactly that challenge.

The agent receives a dataset and a task description, then issues a sequence of cleaning actions. A programmatic grader evaluates the result and provides partial-progress rewards at every step.

---

## 🗂️ Project Structure

```
openenv-data-cleaning/
├── inference.py          # Baseline agent script (mandatory name)
├── Dockerfile            # Container build
├── openenv.yaml          # OpenEnv spec metadata
├── requirements.txt
├── README.md
├── environment/
│   ├── __init__.py
│   ├── env.py            # DataCleaningEnv: step / reset / state
│   ├── tasks.py          # 3 task definitions
│   ├── graders.py        # Scoring functions (0.0 – 1.0)
│   └── models.py         # Pydantic typed models
└── server/
    └── main.py           # FastAPI server (port 7860)
```

---

## 🧩 Observation Space

| Field | Type | Description |
|---|---|---|
| `task_id` | string | Which task is active |
| `task_description` | string | Human-readable goal |
| `dataset` | list[dict] | Current state of the dataset |
| `step_number` | int | Current step |
| `max_steps` | int | Episode step limit (20) |
| `last_action` | string | Previous action type |
| `last_action_error` | string | Error from last action (if any) |
| `progress` | float | Current grader score 0.0–1.0 |

---

## ⚡ Action Space

| `action_type` | Required fields | Description |
|---|---|---|
| `remove_duplicates` | — | Remove duplicate rows |
| `fix_nulls` | `column`, `method` (`mean`/`median`/`value`), optional `value` | Fill null values |
| `fix_types` | `column`, `method` (`float`/`int`/`str`) | Convert column type |
| `normalize` | `column`, `method` (`upper`/`lower`/`title`/`date_iso`) | Normalize string format |
| `remove_rows` | `column`, `method` (`null`) | Remove rows with null in column |
| `done` | — | Signal episode complete |

---

## 📋 Tasks

### Task 1 — Easy: `task_easy`
**Goal:** Clean a small customer dataset.
- Remove duplicate rows
- Fill missing `age` values with the column mean

**Grader checks:** no duplicates, no null ages
**Max steps:** 20 | **Expected score:** 1.0 with 2 correct actions

---

### Task 2 — Medium: `task_medium`
**Goal:** Clean a sales dataset.
- Remove duplicates
- Fill null `revenue` with `0`
- Convert `revenue` column to `float`
- Normalize `country` to uppercase

**Grader checks:** 4 criteria, each worth 0.25
**Max steps:** 20 | **Expected score:** 0.75–1.0

---

### Task 3 — Hard: `task_hard`
**Goal:** Clean a complex HR dataset.
- Remove duplicate records
- Remove rows where `employee_id` is null
- Fill missing `salary` with column median
- Convert `join_date` to ISO format `YYYY-MM-DD`
- Normalize `department` to title case

**Grader checks:** 5 criteria, each worth 0.20
**Max steps:** 20 | **Expected score:** 0.60–1.0

---

## 🎯 Reward Function

- **Partial reward** at every step = improvement in grader score since last step
- **No reward** for steps that don't improve the score
- **−0.05 penalty** for actions that cause errors
- **−0.10 penalty** for hitting the step limit without calling `done`

---

## 🚀 Setup & Usage

### Local (Python)

```bash
git clone https://github.com/your-username/openenv-data-cleaning
cd openenv-data-cleaning
pip install -r requirements.txt

# Start the server
uvicorn server.main:app --host 0.0.0.0 --port 7860

# In another terminal — run baseline inference
export OPENAI_API_KEY=sk-...
python inference.py
```

### Docker

```bash
docker build -t openenv-data-cleaning .
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=sk-... \
  openenv-data-cleaning
```

### API Endpoints

```
POST /reset?task_id=task_easy       → initial observation
POST /step?task_id=task_easy        → step with action body
GET  /state?task_id=task_easy       → current env state
GET  /health                        → health check
GET  /tasks                         → list all task IDs
```

---

## 📊 Baseline Scores

Run with `gpt-4-turbo` at `temperature=0.2`:

| Task | Score |
|---|---|
| task_easy | 1.0000 |
| task_medium | 0.7500 |
| task_hard | 0.6000 |
| **Average** | **0.7833** |

---

## 🔧 Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `API_BASE_URL` | LLM API base URL (default: `https://api.openai.com/v1`) |
| `MODEL_NAME` | Model to use (default: `gpt-4-turbo`) |
| `HF_TOKEN` | Alias for API key on Hugging Face Spaces |

---

## ✅ OpenEnv Validation

```bash
pip install openenv-core
openenv validate
```

---

## 📄 License

MIT
