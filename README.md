# Workout Planner Ai

> By [MEOK AI Labs](https://meok.ai) — Create workout plans, track progress, suggest exercises, and calculate training volume.

MEOK AI Labs — workout-planner-ai-mcp MCP Server. Generate personalized workout plans by goal and equipment.

## Installation

```bash
pip install workout-planner-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install workout-planner-ai-mcp
```

## Tools

### `create_workout`
Create a complete workout plan based on goal, equipment, and difficulty level.

**Parameters:**
- `goal` (str)
- `equipment` (str)
- `difficulty` (str)
- `duration_minutes` (int)

### `track_progress`
Log a workout entry and view progress history for a given exercise.

**Parameters:**
- `user_id` (str)
- `exercise` (str)
- `weight` (float)
- `reps` (int)
- `sets` (int)
- `notes` (str)

### `suggest_exercises`
Suggest exercises for a specific muscle group filtered by equipment and difficulty.

**Parameters:**
- `muscle_group` (str)
- `equipment` (str)
- `difficulty` (str)
- `count` (int)

### `calculate_volume`
Calculate total training volume and per-muscle breakdown. Each item needs 'name', 'muscle_group', 'weight', 'reps', 'sets'.

**Parameters:**
- `exercises` (str)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/workout-planner-ai-mcp](https://github.com/CSOAI-ORG/workout-planner-ai-mcp)
- **PyPI**: [pypi.org/project/workout-planner-ai-mcp](https://pypi.org/project/workout-planner-ai-mcp/)

## License

MIT — MEOK AI Labs
