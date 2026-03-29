"""
OpenEnv Data Cleaning — Baseline Inference Script
Uses gpt-4-turbo via OpenAI client to run an agent against all 3 tasks.
"""

import json
import os
import sys

from openai import OpenAI

# ── config ────────────────────────────────────────────────────────────────────

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN",     "")          # OpenAI key here
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", HF_TOKEN)

MAX_STEPS   = 15
TEMPERATURE = 0.2
MAX_TOKENS  = 512
FALLBACK_ACTION = json.dumps({"action_type": "done"})

# ── import env directly (no HTTP server needed for inference) ─────────────────

sys.path.insert(0, os.path.dirname(__file__))
from environment.env import DataCleaningEnv
from environment.models import Action
from environment.tasks import list_tasks

client = OpenAI(api_key=OPENAI_API_KEY, base_url=API_BASE_URL)

# ── prompts ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a data cleaning agent. You will be given a dataset and a task description.
Your job is to clean the dataset by issuing actions one at a time.

Available actions (respond ONLY with valid JSON, no markdown):

1. Remove duplicate rows:
   {"action_type": "remove_duplicates"}

2. Fill null values in a column:
   {"action_type": "fix_nulls", "column": "<col>", "method": "mean|median|value", "value": <optional>}

3. Convert column to a data type:
   {"action_type": "fix_types", "column": "<col>", "method": "float|int|str"}

4. Normalize string column:
   {"action_type": "normalize", "column": "<col>", "method": "upper|lower|title|date_iso"}

5. Remove rows where a column is null:
   {"action_type": "remove_rows", "column": "<col>", "method": "null"}

6. Signal task complete:
   {"action_type": "done"}

Rules:
- Output ONLY a single JSON object. No explanation, no markdown.
- After all cleaning steps are done, output {"action_type": "done"}.
- If the last action had an error, try a different approach.
"""


def build_user_prompt(obs: dict) -> str:
    return f"""Task: {obs['task_description']}

Current dataset:
{json.dumps(obs['dataset'], indent=2)}

Step: {obs['step_number']} / {obs['max_steps']}
Last action: {obs.get('last_action', 'none')}
Last error:  {obs.get('last_action_error') or 'none'}
Progress:    {obs.get('progress', 0.0):.2f}

What is your next action?"""


def parse_action(text: str) -> Action:
    """Extract JSON from model response and parse into Action."""
    text = text.strip()
    # strip markdown fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(l for l in lines if not l.startswith("```")).strip()
    try:
        data = json.loads(text)
        return Action(**data)
    except Exception:
        return Action(action_type="done")


# ── agent loop ────────────────────────────────────────────────────────────────

def run_task(task_id: str) -> float:
    print(f"\n{'='*60}")
    print(f"  Task: {task_id}")
    print(f"{'='*60}")

    env = DataCleaningEnv(task_id=task_id)
    obs_obj = env.reset()
    obs = obs_obj.model_dump()

    total_reward = 0.0
    final_score  = 0.0

    for step in range(1, MAX_STEPS + 1):
        user_content = build_user_prompt(obs)

        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_content},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            response_text = completion.choices[0].message.content or FALLBACK_ACTION
        except Exception as exc:
            print(f"  [Step {step}] API error: {exc}. Using fallback.")
            response_text = FALLBACK_ACTION

        action = parse_action(response_text)
        print(f"  Step {step:02d}: {action.action_type}"
              + (f" | col={action.column} method={action.method}" if action.column else ""))

        obs_obj, reward, done, info = env.step(action)
        obs = obs_obj.model_dump()
        total_reward += reward
        final_score   = info["grader"]["score"]

        print(f"          reward={reward:+.4f} | score={final_score:.4f} | done={done}")
        if obs.get("last_action_error"):
            print(f"          ERROR: {obs['last_action_error']}")

        if done:
            break

    print(f"\n  Final score : {final_score:.4f}")
    print(f"  Total reward: {total_reward:+.4f}")
    print(f"  Grader detail: {info['grader']['message']}")
    return final_score


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    if not OPENAI_API_KEY:
        print("ERROR: Set OPENAI_API_KEY (or HF_TOKEN) environment variable.")
        sys.exit(1)

    tasks = list_tasks()
    scores = {}

    for task_id in tasks:
        score = run_task(task_id)
        scores[task_id] = score

    print(f"\n{'='*60}")
    print("  BASELINE RESULTS")
    print(f"{'='*60}")
    for task_id, score in scores.items():
        bar = "█" * int(score * 20)
        print(f"  {task_id:<15} {score:.4f}  {bar}")
    avg = sum(scores.values()) / len(scores)
    print(f"  {'AVERAGE':<15} {avg:.4f}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
