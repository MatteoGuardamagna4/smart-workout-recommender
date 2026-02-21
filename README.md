# Smart Workout Recommender

AI-powered personalized workout plans based on your fitness profile.

## Features

- **Fitness Quiz** — Interactive assessment to capture your profile, goals, and preferences
- **Personalized Plan** — Weekly workout plan generated using ML clustering + LLM
- **Progress Tracker** — Projected 12-week progress visualization

## Tech Stack

- **Frontend**: Streamlit (tabs, pills, toggle, sliders, expanders, metrics)
- **ML Model**: KMeans clustering (scikit-learn) to group similar fitness profiles
- **AI Generation**: LLM API (Groq) for personalized plan generation
- **Visualization**: Plotly for interactive charts
- **Dataset**: [Kaggle - Gym Members Exercise Dataset](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset)

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Download the dataset
Download `gym_members_exercise_tracking.csv` from [Kaggle](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset) and place it in `data/gym_members.csv`.

### 3. (Optional) Configure LLM API
Set environment variables:
```bash
# For Groq:
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_key_here
```

Without an API key, the app uses a mock plan for demo purposes. (My personal API Key is in the moodle submission)

### 4. Run the app
```bash
streamlit run app.py
```

## Project Structure

```
smart-workout-recommender/
├── app.py                    # Main Streamlit application
├── model/
│   ├── train_model.py        # Offline clustering training script (pre-run)
│   ├── kmeans_model.pkl      # Trained model (pre-built, included in repo)
│   └── scaler.pkl            # Feature scaler (pre-built, included in repo)
├── utils/
│   ├── __init__.py
│   ├── preprocessing.py      # Feature engineering & cluster utils
│   ├── llm_api.py            # LLM wrapper (Groq)
│   └── radar_widget.py       # Custom radar chart Streamlit component
├── data/
│   └── gym_members.csv       # Dataset (not included in repo)
├── requirements.txt
└── README.md
```

## How It Works

1. **Quiz**: User answers questions about fitness level, goals, equipment, etc.
2. **Clustering**: User profile is matched to a cluster of similar gym members using KMeans
3. **Plan Generation**: An LLM generates a tailored weekly plan using the user's profile + cluster insights
4. **Progress**: Simulated 12-week projections based on similar users' data (Room fo future improvement: train a model to make better predictions)

## Streamlit Widgets Used

- `st.tabs` — Main navigation
- `st.pills` — Goal, gender, workout type selection
- `st.toggle` — Injury flag
- `st.select_slider` — Experience level
- `st.slider` — Age, frequency, duration
- `st.multiselect` — Equipment selection
- `st.expander` — Daily workout details
- `st.metric` — Profile summary cards
- `st.plotly_chart` — Interactive progress charts

---

*Built for PDAI Assignment 1 — Prototyping with Streamlit*
