# 📘 **F1 Lap Time Prediction & Telemetry Analytics Dashboard**

A **machine learning–powered F1 lap time prediction and telemetry analytics dashboard**, built using **FastF1**, **LightGBM**, and **Streamlit**.
This project processes real Formula 1 telemetry, weather, and timing data to generate insights, analyze driver performance, visualize telemetry, and predict lap times using a trained LightGBM model.

---

# 🏎️ **Overview**

This repository contains:

✔ A full Streamlit dashboard
✔ Machine learning pipeline for predicting F1 lap times
✔ Tools to generate datasets from FastF1
✔ Feature engineering notebooks
✔ EDA notebooks
✔ Final trained ML model (LightGBM)
✔ Raw + processed datasets

---

# 📁 **Project Structure**

```
project-root/
│
├── app.py
├── f1.py
│
├── data_generation.ipynb
├── intial_data_analysis.ipynb
├── calculate_new_features.ipynb
├── model.ipynb
│
├── data/
│   ├── f1_ml_laps_dataset.csv
│   └── final_f1_ml_laps_dataset.csv
│
├── models/
│   └── laptime_best_model.pkl
│
└── README.md
```

---

# 📄 **File-by-File Explanation**


---

## **1️⃣ data_generation.ipynb — Dataset Creation Notebook**

This notebook retrieves real 2023 Formula 1 season data using **FastF1** and constructs the initial dataset.

Includes:

* Loading sessions (practice/qualifying/race)
* Extracting laps, telemetry, weather, and timing
* Merging into structured rows
* Cleaning and formatting
* Exporting initial CSVs into `/data`

Output → `data/*.csv`

---

## **2️⃣ intial_data_analysis.ipynb — Exploratory Data Analysis**

This notebook performs EDA on the generated dataset.

Includes:

* Data quality checks
* Correlation analysis
* Outlier detection
* Lap time distributions
* Driver/team comparisons
* Feature relationships
* Identifying missing/incorrect values

Used to validate the data before engineering and modeling.

---

## **3️⃣ calculate_new_features.ipynb — Feature Engineering Notebook**

This notebook creates **additional engineered features** to improve model performance.

Examples:

* Speed statistics (`speed_mean`, `speed_std`, `speed_q1`, `speed_q3`, etc.)
* Throttle/brake statistics
* Gear change counts
* DRS-related metrics (`drs_time_seconds`, `drs_active_pct`, etc.)
* Tyre life, stint information
* Weather transformations
* Rolling averages
* Track status indicators

Exports updated feature-rich datasets into `/data`.

---

## **4️⃣ model.ipynb — Machine Learning Model Training**

This is the main ML pipeline notebook.

Contains:

* Loading final dataset
* Train/test split
* Preprocessing pipeline (`ColumnTransformer`)
* OneHotEncoding of driver/team/compound
* Scaling numeric features
* Training multiple models:

  * RandomForest
  * LightGBM (final)
* Evaluation:

  * MAE
  * RMSE
  * R²
* SHAP feature importance
* Exporting trained model:

Output → `models/laptime_best_model.pkl`

This model is used inside `app.py` for predictions.

---

## **5️⃣ /data Folder — All Dataset Files**

Contains:

* Raw CSVs created from `data_generation.ipynb`
* Intermediate versions with additional features
* Cleaned & engineered datasets
* **final_f1_....csv** → the dataset used in training the LightGBM model

This folder is **required** for reproducibility and notebook execution.

---

## **6️⃣ /models Folder — Trained ML Models**

Contains:

### `laptime_best_model.pkl`

A fully trained LightGBM model pipeline:

* Preprocessor (`ColumnTransformer`)
* Encoders, Imputers, Scalers
* LightGBM Regressor
* Expects 74 engineered features
* Used by Streamlit in the dashboard for predictions

---

## **app.py — Streamlit Dashboard Application**

Provides an interactive dashboard with:

### **Telemetry**

* Speed vs distance
* Throttle & brake
* Gear usage
* RPM
* Lap times

### **Tyre Strategy**

* Stint visualizer per driver

### **Circuit Map**

* GPS-based lap trace colored by speed

### **Track Status**

* Green/yellow/SC/VSC/red status timeline
* Race control messages

### **Session Info**

* Weather summary
* Circuit details
* Driver summary
* Pit stop history

### **Model & Lap Time Prediction**

* Comparison metrics (RandomForest vs LightGBM)
* LightGBM feature importance
* Prediction interface using `key=value` input system

---

## **f1.py — FastF1 Helper Module**

Contains wrapper functions:

* `load_session_data()` – loads any F1 session
* `get_drivers_in_session()` – returns driver list
* `get_fastest_lap()` – returns fastest lap for a driver
* `get_telemetry_data()` – returns telemetry **with X/Y GPS** for lap path

Used to keep `app.py` clean and modular.

---

# 🚀 **How to Run the Project**

## **1. Install Dependencies**

You do *not* have a requirements.txt, so install manually:

### Using pip:

```
pip install streamlit fastf1 lightgbm scikit-learn pandas numpy matplotlib joblib
```

### Or using conda:

```
conda install -c conda-forge fastf1 lightgbm streamlit matplotlib scikit-learn=1.4.0
pip install joblib
```

## **2. Run the Streamlit App**

From project root:

```
streamlit run app.py
```

The dashboard will start at:

```
http://localhost:8501
```

---

## **3. Run the Notebooks**

Open them normally:

```
jupyter notebook
```

or via VSCode/JupyterLab.

---

# 🧠 **Lap Time Prediction (How It Works)**

The model uses:

* 36 numeric features (lap, sector times, speed stats, weather, throttle/brake stats, drs metrics, tyre metrics…)
* 38 OHE categorical features (driver, team, compound)
* Total: **74 features**

To predict a lap time, paste into the Model tab:

```
driver=VER
team=Red Bull Racing
compound=SOFT
lap_number=14
sector_1_time=30.412
sector_2_time=39.015
sector_3_time=24.087
position=3
track_status=1
is_pit_lap=0
air_temp=28.5
track_temp=42.1
humidity=47.0
wind_speed=5.3
wind_dir=182
pressure=1012.4
speed_mean=221.8
speed_max=319.7
speed_min=78.3
speed_std=14.9
speed_q1=206.2
speed_q3=234.9
speed_range=241.4
throttle_mean=82.7
throttle_std=9.5
throttle_pct_full=63.4
brake_mean=18.4
brake_std=6.2
brake_pct_braking=31.1
rpm_mean=11080
rpm_max=12540
rpm_std=780.2
gear_changes=37
gear_min=2
drs_activations=11
drs_active_pct=29.7
drs_time_seconds=4.18
stint=2
tyre_life=6
fresh_tyre=0

...
```

The app outputs predicted lap time in seconds.
