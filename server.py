#!/usr/bin/env python3
"""MEOK AI Labs — workout-planner-ai-mcp MCP Server. Generate personalized workout plans by goal and equipment."""

import json
from datetime import datetime, timezone
from collections import defaultdict

from mcp.server.fastmcp import FastMCP
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

_progress = defaultdict(list)

EXERCISE_DB = {
    "chest": {
        "barbell": [
            {"name": "Barbell Bench Press", "sets": 4, "reps": "8-12", "rest": 90, "difficulty": "intermediate"},
            {"name": "Incline Barbell Press", "sets": 3, "reps": "8-10", "rest": 90, "difficulty": "intermediate"},
        ],
        "dumbbell": [
            {"name": "Dumbbell Bench Press", "sets": 4, "reps": "8-12", "rest": 75, "difficulty": "beginner"},
            {"name": "Dumbbell Flyes", "sets": 3, "reps": "10-15", "rest": 60, "difficulty": "beginner"},
            {"name": "Incline Dumbbell Press", "sets": 3, "reps": "8-12", "rest": 75, "difficulty": "intermediate"},
        ],
        "bodyweight": [
            {"name": "Push-ups", "sets": 3, "reps": "15-20", "rest": 45, "difficulty": "beginner"},
            {"name": "Diamond Push-ups", "sets": 3, "reps": "10-15", "rest": 45, "difficulty": "intermediate"},
            {"name": "Decline Push-ups", "sets": 3, "reps": "12-15", "rest": 45, "difficulty": "intermediate"},
        ],
    },
    "back": {
        "barbell": [
            {"name": "Barbell Rows", "sets": 4, "reps": "8-12", "rest": 90, "difficulty": "intermediate"},
            {"name": "Deadlift", "sets": 3, "reps": "5-8", "rest": 120, "difficulty": "advanced"},
        ],
        "dumbbell": [
            {"name": "Dumbbell Rows", "sets": 3, "reps": "10-12", "rest": 60, "difficulty": "beginner"},
            {"name": "Reverse Flyes", "sets": 3, "reps": "12-15", "rest": 45, "difficulty": "beginner"},
        ],
        "bodyweight": [
            {"name": "Pull-ups", "sets": 3, "reps": "6-12", "rest": 90, "difficulty": "intermediate"},
            {"name": "Inverted Rows", "sets": 3, "reps": "10-15", "rest": 60, "difficulty": "beginner"},
            {"name": "Superman Hold", "sets": 3, "reps": "30s hold", "rest": 30, "difficulty": "beginner"},
        ],
    },
    "legs": {
        "barbell": [
            {"name": "Barbell Squat", "sets": 4, "reps": "6-10", "rest": 120, "difficulty": "intermediate"},
            {"name": "Romanian Deadlift", "sets": 3, "reps": "8-12", "rest": 90, "difficulty": "intermediate"},
        ],
        "dumbbell": [
            {"name": "Goblet Squat", "sets": 3, "reps": "10-15", "rest": 60, "difficulty": "beginner"},
            {"name": "Dumbbell Lunges", "sets": 3, "reps": "10 each", "rest": 60, "difficulty": "beginner"},
            {"name": "Dumbbell Step-ups", "sets": 3, "reps": "10 each", "rest": 60, "difficulty": "beginner"},
        ],
        "bodyweight": [
            {"name": "Bodyweight Squats", "sets": 3, "reps": "15-20", "rest": 45, "difficulty": "beginner"},
            {"name": "Lunges", "sets": 3, "reps": "12 each", "rest": 45, "difficulty": "beginner"},
            {"name": "Glute Bridges", "sets": 3, "reps": "15-20", "rest": 30, "difficulty": "beginner"},
            {"name": "Wall Sits", "sets": 3, "reps": "30-45s", "rest": 45, "difficulty": "beginner"},
        ],
    },
    "shoulders": {
        "barbell": [
            {"name": "Overhead Press", "sets": 4, "reps": "6-10", "rest": 90, "difficulty": "intermediate"},
        ],
        "dumbbell": [
            {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": "8-12", "rest": 75, "difficulty": "beginner"},
            {"name": "Lateral Raises", "sets": 3, "reps": "12-15", "rest": 45, "difficulty": "beginner"},
            {"name": "Front Raises", "sets": 3, "reps": "10-12", "rest": 45, "difficulty": "beginner"},
        ],
        "bodyweight": [
            {"name": "Pike Push-ups", "sets": 3, "reps": "8-12", "rest": 60, "difficulty": "intermediate"},
            {"name": "Arm Circles", "sets": 2, "reps": "20 each direction", "rest": 30, "difficulty": "beginner"},
        ],
    },
    "core": {
        "bodyweight": [
            {"name": "Plank", "sets": 3, "reps": "30-60s", "rest": 30, "difficulty": "beginner"},
            {"name": "Bicycle Crunches", "sets": 3, "reps": "20", "rest": 30, "difficulty": "beginner"},
            {"name": "Mountain Climbers", "sets": 3, "reps": "20", "rest": 30, "difficulty": "beginner"},
            {"name": "Leg Raises", "sets": 3, "reps": "12-15", "rest": 30, "difficulty": "intermediate"},
            {"name": "Russian Twists", "sets": 3, "reps": "20", "rest": 30, "difficulty": "beginner"},
        ],
        "dumbbell": [
            {"name": "Weighted Plank", "sets": 3, "reps": "30-45s", "rest": 45, "difficulty": "intermediate"},
            {"name": "Dumbbell Woodchops", "sets": 3, "reps": "12 each", "rest": 45, "difficulty": "intermediate"},
        ],
    },
}

GOAL_CONFIGS = {
    "strength": {"sets_mult": 1.2, "rep_range": "low", "rest_mult": 1.3, "muscles": ["chest", "back", "legs", "shoulders"]},
    "muscle_building": {"sets_mult": 1.0, "rep_range": "medium", "rest_mult": 1.0, "muscles": ["chest", "back", "legs", "shoulders", "core"]},
    "fat_loss": {"sets_mult": 0.8, "rep_range": "high", "rest_mult": 0.7, "muscles": ["chest", "back", "legs", "core"]},
    "endurance": {"sets_mult": 0.7, "rep_range": "high", "rest_mult": 0.5, "muscles": ["legs", "core", "back"]},
    "general_fitness": {"sets_mult": 1.0, "rep_range": "medium", "rest_mult": 1.0, "muscles": ["chest", "back", "legs", "shoulders", "core"]},
}

mcp = FastMCP("workout-planner-ai", instructions="Create workout plans, track progress, suggest exercises, and calculate training volume.")


@mcp.tool()
def create_workout(goal: str = "general_fitness", equipment: list[str] = [], difficulty: str = "beginner", duration_minutes: int = 45, api_key: str = "") -> str:
    """Create a complete workout plan based on goal, equipment, and difficulty level."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    eq = [e.lower() for e in equipment] if equipment else ["bodyweight"]
    goal_key = goal.lower().replace(" ", "_") if goal.lower().replace(" ", "_") in GOAL_CONFIGS else "general_fitness"
    config = GOAL_CONFIGS[goal_key]

    workout_exercises = []
    total_time = 5  # warmup
    for muscle in config["muscles"]:
        if muscle not in EXERCISE_DB:
            continue
        muscle_exercises = EXERCISE_DB[muscle]
        added = 0
        for eq_type in eq:
            if eq_type in muscle_exercises and added < 2:
                for ex in muscle_exercises[eq_type]:
                    if difficulty == "beginner" and ex["difficulty"] == "advanced":
                        continue
                    if total_time > duration_minutes - 5:
                        break
                    exercise = dict(ex)
                    exercise["muscle_group"] = muscle
                    adj_rest = round(ex["rest"] * config["rest_mult"])
                    exercise["rest"] = adj_rest
                    est_time = ex["sets"] * 1.5 + ex["sets"] * (adj_rest / 60)
                    total_time += est_time
                    workout_exercises.append(exercise)
                    added += 1
                    if added >= 2:
                        break

    return json.dumps({
        "goal": goal_key,
        "difficulty": difficulty,
        "equipment": eq,
        "warmup": {"exercise": "Light cardio (jumping jacks, jogging in place)", "duration": "5 minutes"},
        "exercises": workout_exercises,
        "cooldown": {"exercise": "Static stretching - hold each stretch 20-30 seconds", "duration": "5 minutes"},
        "total_exercises": len(workout_exercises),
        "estimated_duration": f"{round(total_time)} minutes",
        "target_duration": f"{duration_minutes} minutes",
    }, indent=2)


@mcp.tool()
def track_progress(user_id: str, exercise: str, weight: float = 0, reps: int = 0, sets: int = 0, notes: str = "", api_key: str = "") -> str:
    """Log a workout entry and view progress history for a given exercise."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    entry = {
        "exercise": exercise,
        "weight": weight,
        "reps": reps,
        "sets": sets,
        "volume": round(weight * reps * sets, 1),
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    key = f"{user_id}:{exercise.lower()}"
    _progress[key].append(entry)
    history = _progress[key]

    # Calculate trends
    volumes = [e["volume"] for e in history]
    trend = "improving" if len(volumes) >= 2 and volumes[-1] > volumes[0] else \
            "declining" if len(volumes) >= 2 and volumes[-1] < volumes[0] else "stable"

    max_weight = max(e["weight"] for e in history) if history else 0
    total_volume = sum(e["volume"] for e in history)

    return json.dumps({
        "logged": entry,
        "history_count": len(history),
        "trend": trend,
        "personal_best_weight": max_weight,
        "total_lifetime_volume": round(total_volume, 1),
        "last_5_sessions": [{"weight": e["weight"], "reps": e["reps"], "volume": e["volume"]} for e in history[-5:]],
    }, indent=2)


@mcp.tool()
def suggest_exercises(muscle_group: str, equipment: list[str] = [], difficulty: str = "beginner", count: int = 5, api_key: str = "") -> str:
    """Suggest exercises for a specific muscle group filtered by equipment and difficulty."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    eq = [e.lower() for e in equipment] if equipment else ["bodyweight", "dumbbell", "barbell"]
    muscle = muscle_group.lower()

    if muscle not in EXERCISE_DB:
        available = list(EXERCISE_DB.keys())
        return json.dumps({"error": f"Unknown muscle group: {muscle}", "available_groups": available})

    exercises = []
    for eq_type in eq:
        if eq_type in EXERCISE_DB[muscle]:
            for ex in EXERCISE_DB[muscle][eq_type]:
                diff_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
                if diff_order.get(ex["difficulty"], 0) <= diff_order.get(difficulty, 0):
                    exercise = dict(ex)
                    exercise["equipment"] = eq_type
                    exercises.append(exercise)

    exercises = exercises[:count]

    return json.dumps({
        "muscle_group": muscle,
        "difficulty": difficulty,
        "equipment_filter": eq,
        "exercises": exercises,
        "total_found": len(exercises),
    }, indent=2)


@mcp.tool()
def calculate_volume(exercises: list[dict], api_key: str = "") -> str:
    """Calculate total training volume and per-muscle breakdown. Each item needs 'name', 'muscle_group', 'weight', 'reps', 'sets'."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    total_volume = 0
    total_sets = 0
    total_reps = 0
    muscle_volumes = defaultdict(float)
    muscle_sets = defaultdict(int)
    exercise_details = []

    for ex in exercises:
        weight = ex.get("weight", 0)
        reps = ex.get("reps", 0)
        sets = ex.get("sets", 0)
        volume = weight * reps * sets
        muscle = ex.get("muscle_group", "unknown")

        total_volume += volume
        total_sets += sets
        total_reps += reps * sets
        muscle_volumes[muscle] += volume
        muscle_sets[muscle] += sets

        exercise_details.append({
            "name": ex.get("name", "Unknown"),
            "muscle_group": muscle,
            "weight": weight,
            "reps": reps,
            "sets": sets,
            "volume": round(volume, 1),
        })

    # Assess volume adequacy per muscle
    assessments = {}
    for muscle, sets_count in muscle_sets.items():
        if sets_count >= 15:
            assessments[muscle] = "high volume - watch for overtraining"
        elif sets_count >= 10:
            assessments[muscle] = "optimal volume for hypertrophy"
        elif sets_count >= 6:
            assessments[muscle] = "moderate - good for maintenance"
        else:
            assessments[muscle] = "low volume - consider adding sets"

    return json.dumps({
        "total_volume": round(total_volume, 1),
        "total_sets": total_sets,
        "total_reps": total_reps,
        "exercises": exercise_details,
        "volume_by_muscle": {k: round(v, 1) for k, v in muscle_volumes.items()},
        "sets_by_muscle": dict(muscle_sets),
        "assessments": assessments,
        "unit": "kg x reps x sets",
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
