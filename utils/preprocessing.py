import pandas as pd
import numpy as np
import joblib


#Features used for clustering (they match the ones train_model.py)
CLUSTER_FEATURES = [
    "Age", "Weight (kg)", "Height (m)", "Max_BPM", "Avg_BPM",
    "Resting_BPM", "Session_Duration (hours)", "Calories_Burned",
    "Fat_Percentage", "Water_Intake (liters)",
    "Workout_Frequency (days/week)", "Experience_Level", "BMI"
]


def preprocess_user_input(user_data: dict) -> np.ndarray:
    """
    Convert user quiz answers into a feature vector for the KMeans model.
    
    Since we don't have all physiological data from the user (e.g., Max_BPM, Fat_Percentage),
    we estimate them based on typical ranges for the user's profile.
    
    Args:
        user_data: Dictionary with user quiz responses.
    
    Returns:
        Scaled feature array ready for model.predict().
    """
    bmi = user_data["weight_kg"] / (user_data["height_m"] ** 2)
    exp = user_data["experience_level"]

    #estimate missing physiological metrics based on experience and age
    estimated_max_bpm = 220 - user_data["age"]
    estimated_avg_bpm = estimated_max_bpm * (0.6 + exp * 0.05)
    estimated_resting_bpm = 80 - exp * 5
    estimated_fat_pct = 25 - exp * 3 if user_data["gender"] == "Male" else 30 - exp * 3
    estimated_calories = (user_data["session_duration"] * 300) + (exp * 100)

    features = pd.DataFrame([[
        user_data["age"],
        user_data["weight_kg"],
        user_data["height_m"],
        estimated_max_bpm,
        estimated_avg_bpm,
        estimated_resting_bpm,
        user_data["session_duration"],
        estimated_calories,
        estimated_fat_pct,
        user_data["water_intake"],
        user_data["workout_frequency"],
        exp,
        bmi
    ]], columns=CLUSTER_FEATURES)

    scaler = joblib.load("model/scaler.pkl") #since the model was trained with scaled data, it's better to scale user inputs
    features = scaler.transform(features)

    return features


def get_cluster_summary(df: pd.DataFrame, cluster: int, model) -> dict:
    """
    Get summary statistics for a specific cluster.
    
    Args:
        df: Full dataset.
        cluster: Cluster label assigned to the user.
        model: Trained KMeans model.
    
    Returns:
        Dictionary with cluster stats.
    """
    #Predict clusters for all data points
    try:
        numeric_df = df[CLUSTER_FEATURES].dropna()
        labels = model.predict(numeric_df.values)
        df_clustered = numeric_df.copy()
        df_clustered["Cluster"] = labels

        cluster_data = df_clustered[df_clustered["Cluster"] == cluster]

        if len(cluster_data) == 0:
            #Fallback
            return {
                "avg_calories": 400,
                "avg_bpm": 140,
                "common_workout": "Mix",
                "cluster_size": 0
            }

        return {
            "avg_calories": cluster_data["Calories_Burned"].mean(),
            "avg_bpm": cluster_data["Avg_BPM"].mean(),
            "cluster_size": len(cluster_data)
        }
    except Exception as e:
        print(f"Error computing cluster summary: {e}")
        return {
            "avg_calories": 400,
            "avg_bpm": 140,
            "common_workout": "Mix",
            "cluster_size": 0
        }
