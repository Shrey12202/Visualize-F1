# 📘 **F1 Lap Time Prediction & In-Race Strategy Analytics**

A **machine learning–driven Formula 1 lap time prediction and strategy analytics project**, focused on **realistic in-race decision support**.

This project uses historical race data (telemetry, weather, tyre state, and lap context) to **predict the next lap time for a driver**, enabling analysis of tyre degradation, pace trends, and pit strategy under real-world constraints.

---

## 🏎️ **Project Objective**

### **Primary Goal**

Predict the **next lap time** for a driver during a live race using **only information available up to the current lap**.

This framing mirrors real F1 race operations, where teams must:

* Make strategy calls sequentially
* Evaluate undercut / overcut windows
* Monitor tyre degradation
* Decide pit timing under uncertainty

Lap time is treated as the **foundational performance metric**, rather than predicting finishing position directly.

---

## 📊 **Key Features**

✔ Real race lap-level data (2022–2023)
✔ Season-aware modeling
✔ Temporal train/test split (last 2023 race held out)
✔ Physics-inspired feature engineering
✔ Multiple ML models (RandomForest, XGBoost)
✔ Strategy-focused notebooks (tyre modeling with/without fuel)
✔ Reproducible notebooks + Streamlit dashboard

---

## 📁 **Project Structure**

```
visualize_f1/
│
├── app.py                          # Streamlit dashboard
├── f1.py                           # FastF1 helper utilities
│
├── data/
│   ├── f1_ml_laps_dataset.csv
│   ├── f1_2022_races.csv
│   └── final_f1_ml_laps_dataset.csv
│
├── models/
│   └── laptime_best_model.pkl
│
├── cache/                          # FastF1 cache
│
├── trial/                          # Experimental notebooks
├── try/
│
├── intial_data_analysis.ipynb
├── f1_lap_prediction_MULTIYEAR_Final.ipynb
├── tyre_strategy_withfuel.ipynb
├── tyre_strategy_withoutfuel.ipynb
│
└── README.md
```

---

## 📄 **Notebook Overview**

### **1️⃣ intial_data_analysis.ipynb**

Exploratory data analysis:

* Lap time distributions
* Driver & team comparisons
* Weather effects
* Outlier detection
* Data quality checks

---

### **2️⃣ f1_lap_prediction_MULTIYEAR_Final.ipynb**

**Core modeling notebook**

Includes:

* Feature engineering (lags, rolling stats, weather deltas)
* Physics-based features (speed/rpm drops, lap progress)
* Season-aware data preparation
* One-hot encoding for categorical variables
* Scaling for tree-boosting models
* Model training:

  * RandomForest
  * XGBoost (tuned)
* Evaluation:

  * MAE
  * RMSE
  * R²
  * MAPE
* Final model selection

---

### **3️⃣ tyre_strategy_withfuel.ipynb**

Strategy modeling including:

* Fuel effects
* Tyre degradation curves
* Stint-based pace evolution
* Pit stop impact analysis

---

### **4️⃣ tyre_strategy_withoutfuel.ipynb**

Same framework as above but isolates **pure tyre effects** by excluding fuel load.

Used to compare degradation patterns independently.

---

## 🤖 **Modeling Approach**

### **Target**

`target_next_lap` → lap time of lap *t+1*

### **Key Feature Categories**

* **Lag features**: previous lap times
* **Rolling features**: recent pace trends
* **Tyre features**: stint, tyre life, compound
* **Telemetry summaries**: speed, throttle, brake, RPM
* **Weather**: track & air temperature, wind, humidity
* **Race context**: position, pit lap, track status
* **Season**: captures regulation & performance shifts

---

## ⏱️ **Train–Test Strategy**

To prevent data leakage and maintain realism:

* **Training data**: all races except the final 2023 race
* **Test data**: **last race of the 2023 season**
* No random splits
* No future-lap leakage

This ensures performance reflects **true forward-looking prediction**.

---

## 📈 **Current Model Performance **

| Model        | MAE (sec) | RMSE (sec) | R²      |
| ------------ | --------- | ---------- | ------  |
| RandomForest | 0.9487    | 1.5867     | 0.8555  |
| GradBoost    | 0.8690    | 1.638      | 0.8460  |
| XGBoost      | 0.7446    | 1.3287     | 0.8987  |


> Performance is realistic given the inherent noise and stochasticity of race conditions.

---

## 🖥️ **Streamlit Dashboard (`app.py`)**

The dashboard provides:

### Telemetry Visualization

* Speed vs distance
* Throttle & brake traces
* RPM & gear usage
* Circuit maps

### Tyre Strategy

* Stint visualizations
* Tyre age vs lap time trends

### Lap Time Prediction

* Interactive prediction interface
* Uses trained model from `/models`
* Designed for scenario analysis

Run with:

```bash
streamlit run app.py
```

---

## ⚙️ **How to Run**

### Install Dependencies

```bash
pip install pandas numpy scikit-learn xgboost streamlit fastf1 matplotlib joblib
```

### Run Notebooks

```bash
jupyter notebook
```

### Run App

```bash
streamlit run app.py
```

---

## 🔮 **Future Improvements**

* Per-compound models (Soft / Medium / Hard)
* Bayesian uncertainty estimates
* Online updating during live races
* Strategy simulation engine (undercut/overcut)

