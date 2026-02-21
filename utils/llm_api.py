import json
import os

#CONFIGURATION
#Set your preferred config  "groq" or "mock"
LLM_PROVIDER ="groq"  # Change to "mock" to sperimentate with mock data and don't want to consume API calls/Tokens


def generate_workout_plan(user_data: dict, cluster_info: dict) -> dict:
    """
    Generate a personalized weekly workout plan using an LLM.
    
    Args:
        user_data: User profile from quiz.
        cluster_info: Stats from the user's assigned cluster.
    
    Returns:
        Structured plan as a dict with keys: "days", "tips".
    """
    prompt = _build_prompt(user_data, cluster_info)

    if LLM_PROVIDER == "groq":
        return _call_groq(prompt)
    else:
        return _mock_plan(user_data)


def _build_prompt(user_data: dict, cluster_info: dict) -> str:
    """Build a detailed prompt for the LLM."""
    return f"""You are a professional fitness coach. Generate a personalized weekly workout plan (Monday to Sunday) in JSON format.

User Profile:
- Age: {user_data['age']}, Gender: {user_data['gender']}
- Weight: {user_data['weight_kg']}kg, Height: {user_data['height_m']}m
- Experience: Level {user_data['experience_level']} (1=beginner, 3=expert)
- Goal: {user_data['goal']}
- Preferred workout type: {user_data['preferred_type']}
- Available equipment: {', '.join(user_data['equipment'])}
- Workout frequency: {user_data['workout_frequency']} days/week
- Session duration: {user_data['session_duration']} hours
- Injuries/limitations: {user_data['injury_details'] or 'None'}

Similar Users Profile (from data analysis):
- Average calories burned per session: {cluster_info['avg_calories']:.0f}
- Average heart rate during workout: {cluster_info['avg_bpm']:.0f} BPM
- Cluster size: {cluster_info['cluster_size']} similar users

Respond ONLY with valid JSON in this exact format:
{{
    "days": [
        {{
            "day": "Monday",
            "focus": "Upper Body Strength",
            "description": "Brief description of the session",
            "exercises": [
                {{"name": "Bench Press", "details": "3 sets x 10 reps @ moderate weight"}},
                {{"name": "Dumbbell Rows", "details": "3 sets x 12 reps"}}
            ]
        }}
    ],
    "tips": [
        "Tip 1 for the user",
        "Tip 2 for the user"
    ]
}}

Include rest days based on the user's frequency. Make it specific and actionable."""


# ═══════════════════════════════════════════
# PROVIDER IMPLEMENTATIONS
# ═══════════════════════════════════════════

def _call_groq(prompt: str) -> dict:
    """
    Call the Groq API.  
    """
    try:
        from groq import Groq

        client = Groq(api_key="INSERT VALID KEY") #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or your preferred model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Groq API error: {e}")
        return _mock_plan({})


# ═══════════════════════════════════════════
# MOCK PLAN (for development without API key)
# ═══════════════════════════════════════════

def _mock_plan(user_data: dict) -> dict:
    """
    Returns a hardcoded sample plan for development/testing.
    Replace with real LLM calls in production.
    """
    goal = user_data.get("goal", "General Fitness")
    freq = user_data.get("workout_frequency", 3)

    days_plan = [
        {"day": "Monday", "focus": "Upper Body Strength", "description": "Focus on chest, shoulders, and triceps.",
         "exercises": [
             {"name": "Bench Press", "details": "3 sets x 10 reps"},
             {"name": "Overhead Press", "details": "3 sets x 8 reps"},
             {"name": "Tricep Dips", "details": "3 sets x 12 reps"},
             {"name": "Lateral Raises", "details": "3 sets x 15 reps"}
         ]},
        {"day": "Tuesday", "focus": "Rest / Active Recovery", "description": "Light stretching or a 20-min walk.",
         "exercises": [
             {"name": "Foam Rolling", "details": "15 minutes full body"},
             {"name": "Light Walking", "details": "20-30 minutes"}
         ]},
        {"day": "Wednesday", "focus": "Lower Body", "description": "Focus on quads, hamstrings, and glutes.",
         "exercises": [
             {"name": "Squats", "details": "4 sets x 8 reps"},
             {"name": "Romanian Deadlifts", "details": "3 sets x 10 reps"},
             {"name": "Leg Press", "details": "3 sets x 12 reps"},
             {"name": "Calf Raises", "details": "3 sets x 15 reps"}
         ]},
        {"day": "Thursday", "focus": "Rest", "description": "Full rest day. Stay hydrated.", "exercises": []},
        {"day": "Friday", "focus": "Full Body HIIT", "description": "High-intensity circuit training.",
         "exercises": [
             {"name": "Burpees", "details": "3 rounds x 45 sec"},
             {"name": "Kettlebell Swings", "details": "3 rounds x 45 sec"},
             {"name": "Mountain Climbers", "details": "3 rounds x 45 sec"},
             {"name": "Box Jumps", "details": "3 rounds x 45 sec"}
         ]},
        {"day": "Saturday", "focus": "Cardio & Core", "description": "Cardiovascular endurance + ab work.",
         "exercises": [
             {"name": "Running / Cycling", "details": "30-40 minutes moderate intensity"},
             {"name": "Plank", "details": "3 sets x 60 sec"},
             {"name": "Russian Twists", "details": "3 sets x 20 reps"}
         ]},
        {"day": "Sunday", "focus": "Rest / Yoga", "description": "Active recovery with flexibility work.",
         "exercises": [
             {"name": "Yoga Flow", "details": "30-45 minutes"},
             {"name": "Stretching", "details": "15 minutes"}
         ]}
    ]

    tips = [
        f" Based on your goal ({goal}), focus on progressive overload each week.",
        " Aim for at least 2L of water on training days.",
        " Get 7-9 hours of sleep for optimal recovery.",
        f" With {freq} training days/week, make sure to space out intense sessions."
    ]

    return {"days": days_plan, "tips": tips}
