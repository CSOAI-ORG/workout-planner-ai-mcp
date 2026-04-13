from mcp.server.fastmcp import FastMCP

mcp = FastMCP("workout-planner")

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> dict:
    """Calculate BMI."""
    bmi = weight_kg / (height_m ** 2)
    category = (
        "underweight" if bmi < 18.5 else
        "normal" if bmi < 25 else
        "overweight" if bmi < 30 else
        "obese"
    )
    return {"bmi": round(bmi, 2), "category": category}

@mcp.tool()
def calculate_one_rep_max(weight: float, reps: int, formula: str = "epley") -> dict:
    """Estimate 1RM."""
    if reps <= 0:
        return {"error": "Reps must be > 0"}
    if formula == "epley":
        one_rm = weight * (1 + reps / 30)
    elif formula == "brzycki":
        one_rm = weight / (1.0278 - 0.0278 * reps)
    else:
        return {"error": "Unsupported formula. Use epley or brzycki"}
    return {"one_rep_max": round(one_rm, 2), "formula": formula}

@mcp.tool()
def suggest_workout_split(days_per_week: int) -> dict:
    """Suggest a workout split."""
    splits = {
        1: ["Full body"],
        2: ["Upper body", "Lower body"],
        3: ["Push", "Pull", "Legs"],
        4: ["Upper", "Lower", "Upper", "Lower"],
        5: ["Chest", "Back", "Legs", "Shoulders", "Arms"],
        6: ["Push", "Pull", "Legs", "Push", "Pull", "Legs"],
    }
    plan = splits.get(days_per_week, splits[3])
    return {"days_per_week": days_per_week, "split": plan}

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
