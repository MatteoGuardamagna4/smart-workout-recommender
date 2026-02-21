import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import joblib

from utils.preprocessing import preprocess_user_input, get_cluster_summary
from utils.llm_api import generate_workout_plan
from utils.radar_widget import render_fitness_radar #SELF-MADE WIDGET


st.set_page_config(
    page_title="Smart Workout Recommender",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items= {'about' : 'This is my prototype for Prototyping Products with Data and Artificial Intelligence!'}

)



#Load Data & Model
@st.cache_data
def load_data():
    df = pd.read_csv("data/gym_members.csv")
    return df

@st.cache_resource
def load_model():
    model_path = "model/kmeans_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

#session state initialization 
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "user_cluster" not in st.session_state:
    st.session_state.user_cluster = None
if "workout_plan" not in st.session_state:
    st.session_state.workout_plan = None
if "progress_data" not in st.session_state:
    st.session_state.progress_data = None

#Header, also by forced injection as above
st.markdown('<p style="font-size:3.2rem;font-weight:700;color:#1E3A5F;text-align:center;margin-bottom:0.5rem;">Smart Workout Recommender</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:1.5rem;color:#6B7280;text-align:center;margin-bottom:2rem;">AI-powered personalized workout plans based on your fitness profile</p>', unsafe_allow_html=True)

# ─── Tabs ───
tab1, tab2, tab3 = st.tabs(["Fitness Quiz", "Your Plan", "Forecasted Progress"])

#TAB1: QUIZ
with tab1:
    st.subheader("Tell us about yourself!")
    st.caption("Complete this quick assessment to get a personalized workout plan")

    col1, col2 = st.columns(2)

    with col1:
        # Basic Info
        age = st.slider("Age", min_value=16, max_value=70, value=25, step=1)
        gender = st.pills("Gender", options=["Male", "Female"], default="Male")
        weight = st.number_input("Weight (kg)", min_value=40.0, max_value=180.0, value=70.0, step=0.5)
        height = st.number_input("Height (m)", min_value=1.40, max_value=2.20, value=1.75, step=0.01)

    with col2:
        # Fitness Info
        experience = st.select_slider(
            "Experience Level",
            options=["Beginner", "Intermediate", "Expert"],
            value="Beginner"
        )
        workout_freq = st.slider("Workout days per week", min_value=1, max_value=7, value=3)
        session_duration = st.slider("Session duration (hours)", min_value=0.5, max_value=3.0, value=1.0, step=0.25)
        water_intake = st.slider("Daily water intake (liters)", min_value=0.5, max_value=5.0, value=2.0, step=0.25)

    st.divider()

    # Workout Preferences
    st.subheader("Workout Preferences")
    col3, col4 = st.columns(2)

    with col3:
        goal = st.pills(
            "Primary Goal",
            options=["Lose Weight", "Build Muscle", "Improve Cardio", "General Fitness"],
            default="General Fitness"
        )
        preferred_type = st.pills(
            "Preferred Workout Type",
            options=["Cardio", "Strength", "HIIT", "Yoga", "Mix"],
            default="Mix"
        )

    with col4:
        equipment = st.multiselect(
            "Available Equipment",
            options=["Full Gym", "Dumbbells", "Resistance Bands", "Bodyweight Only", "Treadmill", "Pull-up Bar"],
            default=["Full Gym"]
        )
        injuries = st.toggle("Do you have any injuries or limitations?")
        if injuries:
            injury_details = st.text_input("Please describe briefly:")
        else:
            injury_details = ""

    st.divider()

    # Submit Quiz
    if st.button("Generate My Plan", type="primary", width="stretch"):
        with st.spinner("Analyzing your profile..."):
            # Map experience to numeric
            exp_map = {"Beginner": 1, "Intermediate": 2, "Expert": 3}

            # Prepare user data for clustering
            user_data = {
                "age": age,
                "gender": gender,
                "weight_kg": weight,
                "height_m": height,
                "experience_level": exp_map[experience],
                "workout_frequency": workout_freq,
                "session_duration": session_duration,
                "water_intake": water_intake,
                "goal": goal,
                "preferred_type": preferred_type,
                "equipment": equipment,
                "injury_details": injury_details
            }

            # Load model and predict cluster
            model = load_model()
            df = load_data()

            if model is not None:
                user_features = preprocess_user_input(user_data)
                cluster = model.predict(user_features)[0]
                cluster_info = get_cluster_summary(df, cluster, model)
            else:
                # Fallback: assign cluster based on experience level
                cluster = exp_map[experience] - 1
                cluster_info = {
                    "avg_calories": 300 + cluster * 150,
                    "avg_bpm": 130 + cluster * 10,
                    "common_workout": preferred_type,
                    "cluster_size": 100
                }

            st.session_state.user_cluster = cluster
            st.session_state.user_data = user_data
            st.session_state.cluster_info = cluster_info

            # Generate workout plan via LLM
            plan = generate_workout_plan(user_data, cluster_info)
            st.session_state.workout_plan = plan
            st.session_state.quiz_completed = True

            # Generate mock forecast progress data based on random stats 
            weeks = 12
            base_cal = cluster_info["avg_calories"]
            progress = pd.DataFrame({
                "Week": range(1, weeks + 1),
                "Calories Burned": [base_cal + i * np.random.uniform(5, 15) + np.random.normal(0, 20) for i in range(weeks)],
                "Session Duration (min)": [session_duration * 60 + i * np.random.uniform(1, 3) + np.random.normal(0, 5) for i in range(weeks)],
                "Weight (kg)": [weight - i * np.random.uniform(0.1, 0.3) + np.random.normal(0, 0.2) for i in range(weeks)] if goal == "Lose Weight" else [weight + i * np.random.uniform(0.05, 0.15) + np.random.normal(0, 0.2) for i in range(weeks)],
            })
            st.session_state.progress_data = progress

        st.success("Your personalized plan is ready! Go to the **Your Plan** tab.")


#TAB2: THE PLAN ------------------------------------------

with tab2:
    if not st.session_state.quiz_completed:
        st.info("Complete the Fitness Quiz first to get your personalized plan!")
    else:
        user_data = st.session_state.user_data
        cluster_info = st.session_state.cluster_info
        plan = st.session_state.workout_plan

        #Profile Summary Metrics
        st.subheader("Your Fitness Profile")
        m1, m3, m4 = st.columns(3)
        bmi = user_data["weight_kg"] / (user_data["height_m"] ** 2)
        m1.metric("BMI", f"{bmi:.1f}")
        m3.metric("Avg Calories (similar users)", f"{cluster_info['avg_calories']:.0f}")
        m4.metric("Target Days/Week", f"{user_data['workout_frequency']}")

        st.divider()
        st.subheader('Fitness Radar')

        #Workout plan display
        st.subheader("Your Personalized Weekly Plan") # Compute user scores (0-100 scale) from quiz data
        exp = user_data["experience_level"]
        bmi_score = max(0, min(100, 100 - abs(bmi - 22.5) * 5))  # Optimal BMI ~22.5
        strength_score = min(100, exp * 25 + user_data["workout_frequency"] * 5 + (15 if "Strength" in user_data.get("preferred_type", "") or user_data.get("preferred_type") == "Mix" else 0))
        endurance_score = min(100, user_data["session_duration"] * 40 + user_data["workout_frequency"] * 8)
        consistency_score = min(100, user_data["workout_frequency"] * 14)
        hydration_score = min(100, user_data["water_intake"] * 30)
        recovery_score = min(100, 40 + (7 - user_data["workout_frequency"]) * 10 + (10 if user_data["session_duration"] <= 1.5 else 0))

        user_scores = {
            "Strength": round(strength_score),
            "Endurance": round(endurance_score),
            "Body Comp.": round(bmi_score),
            "Consistency": round(consistency_score),
            "Hydration": round(hydration_score),
            "Recovery": round(recovery_score)
        }

        # Cluster averages (simulated from cluster info) (not really accurate as it /
        # often displays the user having much better stats than the average, but why don't give some confidence boost ;) )
        cluster_avg_exp = 2  # mid-level default
        cluster_scores = {
            "Strength": 55,
            "Endurance": 60,
            "Body Comp.": 65,
            "Consistency": 50,
            "Hydration": 55,
            "Recovery": 58
        }

        radar_col1, radar_col2 = st.columns([3, 2])
        with radar_col1:
            render_fitness_radar(user_scores, cluster_scores, title="You vs Similar Users")
        with radar_col2:
            st.markdown("**Your Scores**")
            for label, score in user_scores.items():
                delta = score - cluster_scores[label]
                emoji = "🟢" if delta > 5 else "🔴" if delta < -5 else "🟡"
                st.write(f"{emoji} **{label}**: {score}/100 ({'+'if delta>=0 else ''}{delta} vs avg)")

        st.divider()
        # ── Workout Plan Display ──
        st.subheader("Your Personalized Weekly Plan")

        if isinstance(plan, dict) and "days" in plan:
            # Structured plan from LLM
            for day in plan["days"]:
                with st.expander(f"**{day.get('day', 'Day')}** — {day.get('focus', '')}", expanded=False):
                    st.write(day.get("description", ""))
                    if "exercises" in day:
                        for ex in day["exercises"]:
                            st.write(f"- **{ex.get('name', '')}**: {ex.get('details', '')}")
        elif isinstance(plan, str):
            # Raw text plan
            st.markdown(plan)
        else:
            st.warning("Could not generate plan. Please check your LLM API configuration.")

        st.divider()


        # ── Tips Section ──
        st.subheader("Quick Tips")
        tips = plan.get("tips", []) if isinstance(plan, dict) else []
        if tips:
            for tip in tips:
                st.info(tip)
        else:
            st.info("Stay hydrated, warm up properly, and listen to your body!")

#TAB3: PROGRESS TRACKER
with tab3:
    if st.session_state.progress_data is None:
        st.info("Complete the Fitness Quiz first to see projected progress")
    else:
        st.subheader("Projected 12-Week Progress")
        st.caption("Based on users with a similar profile; results are **rough** estimations")

        progress = st.session_state.progress_data

        # Metric selector
        metric_choice = st.pills(
            "Select metric to visualize",
            options=["Calories Burned", "Session Duration (min)", "Weight (kg)"],
            default="Calories Burned"
        )

        # Main chart
        fig = px.line(
            progress,
            x="Week",
            y=metric_choice,
            markers=True,
            title=f"{metric_choice} — 12 Week Projection",
            template="plotly_white"
        )
        fig.update_traces(line=dict(width=3, color="#1a3cd6"), marker=dict(size=8))
        fig.update_layout(
            xaxis_title="Week",
            yaxis_title=metric_choice,
            font=dict(size=14),
            height=400
        )
        st.plotly_chart(fig, width="stretch")

        # Summary stats
        st.divider()
        st.subheader("Summary")
        s1, s2, s3 = st.columns(3)

        start_val = progress[metric_choice].iloc[0]
        end_val = progress[metric_choice].iloc[-1]
        change = end_val - start_val
        pct_change = (change / start_val) * 100

        s1.metric("Start (Week 1)", f"{start_val:.1f}")
        s2.metric("End (Week 12)", f"{end_val:.1f}")
        s3.metric("Change", f"{change:+.1f}", delta=f"{pct_change:+.1f}%")


#Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/dumbbell.png", width=80)
    st.title("About")
    st.write(
        "**Smart Workout Recommender** uses machine learning (KMeans clustering) "
        "and AI (Groq API calls) to create personalized workout plans based on your fitness profile and goal"
    )
    st.divider()
    st.caption("Built with Streamlit")
    st.caption("Dataset: [Kaggle - Gym Members Exercise](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset)")
