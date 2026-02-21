"""
Offline training script for KMeans clustering model.
I've run this once to generate the model file before launching the Streamlit app.

"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

#adding parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Config ───
DATA_PATH = "data/gym_members.csv"
MODEL_PATH = "model/kmeans_model.pkl"
SCALER_PATH = "model/scaler.pkl"
N_CLUSTERS = 4  #arbitrary choice

# Features to use for clustering
FEATURES = [
    "Age", "Weight (kg)", "Height (m)", "Max_BPM", "Avg_BPM",
    "Resting_BPM", "Session_Duration (hours)", "Calories_Burned",
    "Fat_Percentage", "Water_Intake (liters)",
    "Workout_Frequency (days/week)", "Experience_Level", "BMI"
]


def train():
    df = pd.read_csv(DATA_PATH)
    print(f"   Dataset shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")

    #Select features
    X = df[FEATURES].dropna()
    print(f"   Features shape after dropna: {X.shape}")

    #Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    #Train KMeans
    print(f" Training KMeans with {N_CLUSTERS} clusters...")
    model = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    model.fit(X_scaled)

    print(f"   Cluster sizes: {np.bincount(model.labels_)}")

    #Save model and scaler
    print(f" Saving model to {MODEL_PATH}...")
    joblib.dump(model, MODEL_PATH)
    print(f" Saving scaler to {SCALER_PATH}...")
    joblib.dump(scaler, SCALER_PATH)

    #Print cluster summaries
    print("\n Cluster Summaries:")
    df_features = X.copy()
    df_features["Cluster"] = model.labels_
    for c in range(N_CLUSTERS):
        cluster_data = df_features[df_features["Cluster"] == c]
        print(f"\n  Cluster {c} (n={len(cluster_data)}):")
        print(f"    Avg Age: {cluster_data['Age'].mean():.1f}")
        print(f"    Avg BMI: {cluster_data['BMI'].mean():.1f}")
        print(f"    Avg Calories: {cluster_data['Calories_Burned'].mean():.0f}")
        print(f"    Avg Experience: {cluster_data['Experience_Level'].mean():.1f}")
        print(f"    Avg Frequency: {cluster_data['Workout_Frequency (days/week)'].mean():.1f} days/week")

    


if __name__ == "__main__":
    train()
