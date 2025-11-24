import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import style
import fastf1
import pandas as pd
import numpy as np
import joblib

from f1 import (
    load_session_data,
    get_drivers_in_session,
    get_fastest_lap,
    get_telemetry_data
)

# ========================
# 🎨 Set Page Config + Enhanced Dark Theme
# ========================
st.set_page_config(
    page_title="🏎️ F1 Insights: Live Race Analytics",
    layout="wide",
    page_icon="🏎️"
)

# 🖤 Enhanced Dark Theme Styling
st.markdown(
    """
    <style>
        .main {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .css-16huue1, .css-qbe2hs, p {
            color: #FAFAFA !important;
        }
        .stButton > button {
            background-color: #e10600;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
            border: none;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #b30000;
            color: white;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #FAFAFA !important;
        }
        .graph-container {
            background-color: #1A1A1A;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border: 1px solid #333;
        }
        .placeholder {
            background-color: #1A1A1A;
            border: 2px dashed #444;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            color: #888;
            margin: 20px 0;
        }
        .info-card {
            background-color: #1A1A1A;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border: 1px solid #333;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Set Matplotlib to Dark Background
style.use('dark_background')


@st.cache_resource
def load_laptime_model():
    """
    Load the trained lap time prediction pipeline (preprocessor + model).
    Expects a joblib file at models/laptime_best_model.pkl
    """
    try:
        model = joblib.load("models/laptime_best_model.pkl")
        return model
    except Exception as e:
        st.error(f"⚠️ Could not load lap time model: {e}")
        return None


# ========================
# 🏎️ App Title
# ========================
st.title("🏎️ F1 Insights: Live Race Analytics")

# ========================
# 🛠 Main Controls Section
# ========================
st.markdown("### 📋 Select Session Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    season = st.selectbox("🏆 Season (Year)", list(range(2018, 2024))[::-1])

with col2:
    session_name = st.selectbox("🏁 Session Type", ["FP1", "FP2", "FP3", "Q", "R"])

with col3:
    races = fastf1.get_event_schedule(season)
    gp_list = races['EventName'].tolist()
    selected_gp = st.selectbox("🏎️ Grand Prix", gp_list)

# Load button
if st.button("🚀 Load Session Data", type="primary"):
    with st.spinner("Loading session data..."):
        session = load_session_data(season, selected_gp, session_name)
        st.session_state.session_data = session
        st.session_state.selected_gp = selected_gp
        st.session_state.session_name = session_name
        st.session_state.season = season
        st.success(f"✅ {session.event['EventName']} {session_name} data loaded successfully!")

# ========================
# 📊 Driver Analytics (Only show when data is loaded)
# ========================
if "session_data" in st.session_state and st.session_state.session_data:
    session = st.session_state.session_data

    # Driver selection
    st.markdown("### 🏎️ Driver Selection")
    drivers = get_drivers_in_session(session)
    selected_driver = st.selectbox("👤 Select Driver", drivers)

    if selected_driver:
        fastest_lap = get_fastest_lap(session, selected_driver)

        if fastest_lap is not None:
            # Driver Info Card
            driver_info = session.get_driver(selected_driver)
            # Get classification info from session.results
            classification = getattr(session, 'results', None)
            final_position = total_time = points = status = 'N/A'
            if classification is not None and not classification.empty and 'Abbreviation' in classification.columns:
                driver_result = classification[classification['Abbreviation'].astype(str).str.strip() == str(selected_driver).strip()]
                if not driver_result.empty:
                    def safe_str(val):
                        if pd.isna(val) or val is None:
                            return 'N/A'
                        return str(val)

                    final_position = safe_str(driver_result['Position'].values[0])
                    total_time = safe_str(driver_result['Time'].values[0]) if 'Time' in driver_result.columns else 'N/A'
                    points = safe_str(driver_result['Points'].values[0]) if 'Points' in driver_result.columns else 'N/A'
                    status = safe_str(driver_result['Status'].values[0]) if 'Status' in driver_result.columns else 'N/A'

            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader(f"👤 {driver_info.get('FullName', selected_driver)}")
            st.markdown(f"""
            - 🏎 **Team**: {driver_info.get('TeamName', 'Unknown')}
            - 🔢 **Car Number**: {driver_info.get('PermanentNumber', 'N/A')}
            - 🏁 **Starting Grid**: {fastest_lap.get('GridPosition', 'N/A')}
            - 🎯 **Final Position**: {final_position}
            - ⏱ **Fastest Lap**: {fastest_lap['LapTime']}
            - ⏳ **Total Race Time / Status**: {total_time if status == 'Finished' or status == 'N/A' else status}
            - 🏆 **Points Scored**: {points}
            """)
            st.markdown('</div>', unsafe_allow_html=True)

            # Get driver laps and telemetry
            driver_laps = session.laps.pick_drivers(selected_driver)
            telemetry = get_telemetry_data(fastest_lap)

            # ========================
            # 📋 Tabs for all charts
            # ========================
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "Telemetry Graphs",
                "Tyre Strategy",
                "Circuit Map",
                "Track Status",
                "Session Info",
                "Model & Lap Time Prediction"
            ])

            # --- Tab 1: Telemetry Graphs ---
            with tab1:
                colA, colB, colC = st.columns(3)
                with colA:
                    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    st.subheader("🏃 Speed vs Distance")
                    fig1, ax1 = plt.subplots(figsize=(6, 4))
                    ax1.plot(telemetry['Distance'], telemetry['Speed'], label='Speed', linewidth=2)
                    ax1.set_xlabel("Distance (m)", color='white')
                    ax1.set_ylabel("Speed (km/h)", color='white')
                    ax1.set_title(f"{selected_driver} - Fastest Lap Speed", color='white', fontsize=12, fontweight='bold')
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig1)
                    st.markdown('</div>', unsafe_allow_html=True)

                with colB:
                    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    st.subheader("🦶 Throttle & Brake vs Distance")
                    fig2, ax2 = plt.subplots(figsize=(6, 4))
                    ax2.plot(telemetry['Distance'], telemetry['Throttle'], label='Throttle (%)', linewidth=2)
                    ax2.plot(telemetry['Distance'], telemetry['Brake'], label='Brake (%)', linewidth=2)
                    ax2.set_xlabel("Distance (m)", color='white')
                    ax2.set_ylabel("Percentage", color='white')
                    ax2.set_title(f"{selected_driver} - Throttle & Brake", color='white', fontsize=12, fontweight='bold')
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig2)
                    st.markdown('</div>', unsafe_allow_html=True)

                with colC:
                    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    st.subheader("⚙️ Gear vs Distance")
                    fig3, ax3 = plt.subplots(figsize=(6, 4))
                    ax3.plot(telemetry['Distance'], telemetry['nGear'], label='Gear', linewidth=2, marker='o', markersize=4)
                    ax3.set_xlabel("Distance (m)", color='white')
                    ax3.set_ylabel("Gear", color='white')
                    ax3.set_title(f"{selected_driver} - Gear Changes", color='white', fontsize=12, fontweight='bold')
                    ax3.legend()
                    ax3.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig3)
                    st.markdown('</div>', unsafe_allow_html=True)

                # Second row: RPM and Lap Times
                colD, colE, _ = st.columns(3)
                with colD:
                    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    st.subheader("🎛 RPM vs Distance")
                    fig4, ax4 = plt.subplots(figsize=(6, 4))
                    ax4.plot(telemetry['Distance'], telemetry['RPM'], label='RPM', linewidth=2)
                    ax4.set_xlabel("Distance (m)", color='white')
                    ax4.set_ylabel("RPM", color='white')
                    ax4.set_title(f"{selected_driver} - Engine RPM", color='white', fontsize=12, fontweight='bold')
                    ax4.legend()
                    ax4.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig4)
                    st.markdown('</div>', unsafe_allow_html=True)

                with colE:
                    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    st.subheader("⏱ Lap Times Progression")
                    fig5, ax5 = plt.subplots(figsize=(6, 4))
                    lap_times = driver_laps['LapTime'].dt.total_seconds()
                    ax5.plot(driver_laps['LapNumber'], lap_times, marker='o', linestyle='-', linewidth=2, markersize=6)
                    ax5.set_xlabel("Lap Number", color='white')
                    ax5.set_ylabel("Lap Time (s)", color='white')
                    ax5.set_title(f"{selected_driver} - Lap Times", color='white', fontsize=12, fontweight='bold')
                    ax5.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig5)
                    st.markdown('</div>', unsafe_allow_html=True)

            # --- Tab 2: Tyre Strategy ---
            with tab2:
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                st.subheader("🛞 Tyre Strategy (Stint Visualization)")
                stints = driver_laps[['Stint', 'Compound', 'LapNumber']]
                stints = stints.groupby(['Stint', 'Compound']).min().reset_index()
                fig_stints, ax_stints = plt.subplots(figsize=(10, 2))
                compound_colors = {
                    'SOFT': 'red',
                    'MEDIUM': 'yellow',
                    'HARD': 'white',
                    'INTERMEDIATE': 'green',
                    'WET': 'blue'
                }
                for _, row in stints.iterrows():
                    color = compound_colors.get(str(row['Compound']).upper(), 'gray')
                    ax_stints.barh(
                        y=row['Compound'],
                        width=len(driver_laps[driver_laps['Stint'] == row['Stint']]),
                        left=row['LapNumber'],
                        edgecolor='black',
                        color=color
                    )
                ax_stints.set_xlabel("Lap Number")
                ax_stints.set_ylabel("Tyre Compound")
                ax_stints.set_title(f"{selected_driver} - Tyre Stint Strategy")
                st.pyplot(fig_stints)
                st.markdown('</div>', unsafe_allow_html=True)

            # --- Tab 3: Circuit Map ---
            with tab3:
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                st.subheader("🗺️ Circuit Map (Lap Path or Track Outline)")
                # Try to plot lap path if X/Y available, else fallback to circuit outline
                if all(col in telemetry.columns for col in ['X', 'Y', 'Speed']):
                    x = telemetry['X']
                    y = telemetry['Y']
                    speed = telemetry['Speed']
                    fig_map, ax_map = plt.subplots(figsize=(8, 8))
                    sc = ax_map.scatter(x, y, c=speed, s=2, marker='o')
                    ax_map.set_aspect('equal', 'box')
                    ax_map.set_xlabel("X")
                    ax_map.set_ylabel("Y")
                    ax_map.set_title(f"{selected_driver} - Lap Path Colored by Speed")
                    cbar = plt.colorbar(sc, ax=ax_map, orientation='vertical', pad=0.01)
                    cbar.set_label('Speed (km/h)')
                    ax_map.set_facecolor('#181818')
                    fig_map.patch.set_facecolor('#181818')
                    st.pyplot(fig_map)
                else:
                    # Fallback: plot circuit outline
                    try:
                        circuit_info = session.get_circuit_info()
                        if hasattr(circuit_info, 'center_line'):
                            center_line = circuit_info.center_line
                            x = center_line.x
                            y = center_line.y
                            fig_outline, ax_outline = plt.subplots(figsize=(8, 8))
                            ax_outline.plot(x, y, linewidth=2)
                            ax_outline.set_aspect('equal', 'box')
                            ax_outline.set_xlabel("X")
                            ax_outline.set_ylabel("Y")
                            ax_outline.set_title(f"{session.event['EventName']} - Circuit Outline")
                            ax_outline.set_facecolor('#181818')
                            fig_outline.patch.set_facecolor('#181818')
                            st.pyplot(fig_outline)
                        else:
                            st.warning("No circuit outline data available for this event.")
                    except Exception as e:
                        st.warning(f"No positional (X, Y) telemetry or circuit outline data available. Circuit map cannot be displayed. ({e})")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- Tab 4: Track Status ---
            with tab4:
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                st.subheader("🚦 Track Status Timeline")
                try:
                    track_status = session.track_status
                    if not track_status.empty and all(col in track_status.columns for col in ["Time", "EndTime", "Status"]):
                        # Map status codes to labels/colors
                        status_map = {
                            1: ("Green", "#00FF00"),
                            2: ("Yellow", "#FFFF00"),
                            3: ("SC", "#FFA500"),
                            4: ("VSC", "#00FFFF"),
                            5: ("Red", "#FF0000")
                        }
                        plotted = False
                        fig_ts, ax_ts = plt.subplots(figsize=(10, 2))
                        for code, (label, color) in status_map.items():
                            periods = track_status[(track_status['Status'] == code) & track_status['EndTime'].notnull()]
                            for _, row in periods.iterrows():
                                ax_ts.axvspan(row['Time'], row['EndTime'], color=color, alpha=0.5, label=label)
                                plotted = True
                        if plotted:
                            ax_ts.set_xlabel("Session Time")
                            ax_ts.set_yticks([])
                            ax_ts.set_title("Track Status Timeline")
                            handles, labels = ax_ts.get_legend_handles_labels()
                            by_label = dict(zip(labels, handles))
                            ax_ts.legend(by_label.values(), by_label.keys(), loc='upper right')
                            st.pyplot(fig_ts)
                        else:
                            st.info("No track status changes recorded for this session.")
                    else:
                        st.info("No track status data available for this session.")
                except Exception as e:
                    st.write(f"Could not display track status: {e}")

                st.subheader("📢 Race Control Messages")
                try:
                    rcm = session.race_control_messages
                    if not rcm.empty:
                        show_cols = [col for col in ["Time", "Category", "Message", "Flag"] if col in rcm.columns]
                        st.dataframe(rcm[show_cols])
                    else:
                        st.write("No race control messages available.")
                except Exception as e:
                    st.write(f"Could not display race control messages: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- Tab 5: Session Info ---
            with tab5:
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                st.subheader("📋 Session Info, Circuit, Driver Summary & Pit Stops")
                # Show session info
                st.write("**Event:**", session.event['EventName'])
                st.write("**Session:**", session_name)
                st.write("**Date:**", session.event['EventDate'])
                st.write("**Location:**", session.event['Location'])
                st.write("**Country:**", session.event['Country'])

                # Weather data (show min/max for key columns)
                try:
                    weather = session.weather_data
                    st.write("**Weather Data (range):**")
                    for col, label, unit in [
                        ("AirTemp", "Air Temp", "°C"),
                        ("TrackTemp", "Track Temp", "°C"),
                        ("Humidity", "Humidity", "%"),
                        ("WindSpeed", "Wind Speed", "km/h"),
                        ("WindDirection", "Wind Direction", "°"),
                        ("Pressure", "Pressure", "hPa")
                    ]:
                        if col in weather.columns:
                            min_val = weather[col].min()
                            max_val = weather[col].max()
                            st.write(f"- {label}: {min_val:.1f}{unit} to {max_val:.1f}{unit}")
                        else:
                            st.write(f"- {label}: Not available")
                except Exception:
                    st.write("No weather data available for this session.")

                # Circuit info
                try:
                    circuit_info = session.get_circuit_info()
                    st.write("**Circuit Name:**", getattr(circuit_info, 'name', 'N/A'))
                    st.write("**Circuit Location:**", getattr(circuit_info, 'location', 'N/A'))
                    st.write("**Circuit Length (km):**", getattr(circuit_info, 'length', 'N/A'))
                    st.write("**Number of Turns:**", getattr(circuit_info, 'number_of_corners', 'N/A'))
                except Exception:
                    st.write("No circuit info available for this event.")

                # Driver Race Summary
                st.subheader("📋 Driver Race Summary")
                num_laps = len(driver_laps)
                top_speed = telemetry['Speed'].max() if 'Speed' in telemetry else 'N/A'
                tyre_changes = driver_laps['Compound'].nunique() if 'Compound' in driver_laps else 'N/A'
                pit_stops_count = driver_laps['PitInTime'].notnull().sum()

                overtakes = None
                if 'Position' in driver_laps.columns:
                    pos_changes = driver_laps['Position'].diff().fillna(0)
                    overtakes = int((pos_changes != 0).sum())

                st.markdown(f"""
                - 🏎 **Number of Laps Completed**: {num_laps}
                - 🛞 **Tyre Compounds Used**: {driver_laps['Compound'].unique().tolist()}
                - 🔄 **Number of Tyre Changes**: {tyre_changes}
                - 🛠 **Pit Stops**: {pit_stops_count}
                - 🚀 **Top Speed**: {top_speed:.1f} km/h
                - 🏁 **Final Position**: {final_position}
                - ⏳ **Total Race Time / Status**: {total_time if status == 'Finished' or status == 'N/A' else status}
                - 🏆 **Points Scored**: {points}
                {(f'- 🔢 **Estimated Overtakes**: {overtakes}' if overtakes is not None else '')}
                """)

                # Pit Stop Details (all columns)
                pit_stops = driver_laps[driver_laps['PitInTime'].notnull()].copy()
                if not pit_stops.empty:
                    st.subheader("⛽ Pit Stop Details (All Columns)")
                    for col in pit_stops.columns:
                        if pd.api.types.is_timedelta64_dtype(pit_stops[col]):
                            pit_stops[col] = pit_stops[col].apply(
                                lambda x: str(x).split(' days ')[-1][:-3] if pd.notnull(x) else ""
                            )
                        elif pd.api.types.is_datetime64_any_dtype(pit_stops[col]):
                            pit_stops[col] = pit_stops[col].dt.strftime('%H:%M:%S.%f').str[:-3]
                        else:
                            pit_stops[col] = pit_stops[col].astype(str)
                    st.dataframe(pit_stops)
                else:
                    st.write("🚫 No pit stops recorded for this session.")
                st.markdown('</div>', unsafe_allow_html=True)

            # --- Tab 6: Model & Lap Time Prediction ---
            with tab6:
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                st.subheader("🤖 Model Performance & Lap Time Prediction")

                model_pipe = load_laptime_model()

                if model_pipe is None:
                    st.warning("Lap time model could not be loaded from `models/laptime_best_model.pkl`.")
                else:
                    st.markdown("### 🏆 Model Comparison Summary")

                    # Static metrics from your notebook (RandomForest vs LightGBM)
                    metrics_df = pd.DataFrame([
                        {
                            "Model": "RandomForest",
                            "MAE": 0.194212,
                            "RMSE": 0.825694,
                            "R²": 0.996111,
                            "Accuracy": 0.996320,
                            "F1": 0.996380,
                            "AUC": 0.999912,
                        },
                        {
                            "Model": "LightGBM (Selected)",
                            "MAE": 0.266628,
                            "RMSE": 0.663674,
                            "R²": 0.997488,
                            "Accuracy": 0.994622,
                            "F1": 0.994715,
                            "AUC": 0.999896,
                        },
                    ])

                    st.dataframe(metrics_df, use_container_width=True)

                    colb1, colb2, colb3 = st.columns(3)
                    with colb1:
                        st.metric("Best Model", "LightGBM")
                    with colb2:
                        st.metric("RMSE (LightGBM)", f"{0.663674:.3f}")
                    with colb3:
                        st.metric("R² (LightGBM)", f"{0.997488:.3f}")

                    st.info(
                        "LightGBM is used as the final model (saved in `models/laptime_best_model.pkl`) "
                        "because it achieves the best RMSE and R² on your evaluation set."
                    )

                    # Feature importance (LightGBM)
                    st.markdown("### 📈 Top Feature Importances (LightGBM)")

                    try:
                        pre = model_pipe.named_steps.get("pre", None)
                        base_model = model_pipe.named_steps.get("model", None)

                        if (pre is not None) and (base_model is not None) and hasattr(base_model, "feature_importances_"):
                            try:
                                feature_names = pre.get_feature_names_out()
                            except Exception:
                                feature_names = np.array(
                                    [f"feature_{i}" for i in range(len(base_model.feature_importances_))]
                                )

                            imp_df = pd.DataFrame({
                                "feature": feature_names,
                                "importance": base_model.feature_importances_
                            }).sort_values("importance", ascending=False)

                            top_n = 20
                            top_imp = imp_df.head(top_n).iloc[::-1]  # reverse for nicer barh

                            fig_imp, ax_imp = plt.subplots(figsize=(8, 6))
                            ax_imp.barh(top_imp["feature"], top_imp["importance"])
                            ax_imp.set_xlabel("Importance")
                            ax_imp.set_title(f"Top {top_n} Features (LightGBM)")
                            ax_imp.grid(True, axis="x", alpha=0.3)
                            plt.tight_layout()
                            st.pyplot(fig_imp)
                        else:
                            st.warning(
                                "Could not access `pre` and `model` steps or feature importances. "
                                "Make sure the saved pipeline has steps named `'pre'` and `'model'`."
                            )
                    except Exception as e:
                        st.error(f"Error while computing feature importances: {e}")

                    # Lap time prediction from user input
                    st.markdown("---")
                    st.markdown("### 🔮 Predict Lap Time")

                    st.write(
                        "Enter lap features as `key=value`, one per line. "
                        "Keys must match the **raw** feature names used when training "
                        "(before preprocessing). For example:\n\n"
                        "**Numeric features:**\n"
                        "`lap_number, sector_1_time, sector_2_time, sector_3_time, position, track_status,`\n"
                        "`is_pit_lap, air_temp, track_temp, humidity, wind_speed, wind_dir, pressure,`\n"
                        "`speed_mean, speed_max, throttle_mean, brake_mean, rpm_mean, rpm_max,`\n"
                        "`drs_activations, speed_min, speed_std, speed_q1, speed_q3, speed_range,`\n"
                        "`throttle_std, throttle_pct_full, brake_std, brake_pct_braking, rpm_std,`\n"
                        "`gear_changes, gear_min, drs_active_pct, drs_time_seconds, stint, tyre_life, fresh_tyre`\n\n"
                        "**Categorical features:**\n"
                        "`driver, team, compound`\n\n"
                        "Example input:\n"
                        "`driver=VER`\n"
                        "`team=Red Bull Racing`\n"
                        "`compound=SOFT`\n"
                        "`lap_number=12`\n"
                        "`sector_1_time=30.512`\n"
                        "`sector_2_time=38.921`\n"
                        "`sector_3_time=24.134`\n"
                        "`track_temp=41.5`\n"
                        "`air_temp=28.0`\n"
                        "`tyre_life=7`\n"
                        "`drs_time_seconds=4.2`"
                    )

                    user_kv_text = st.text_area(
                        "Lap features (key=value per line)",
                        height=260,
                        placeholder=(
                            "driver=VER\n"
                            "team=Red Bull Racing\n"
                            "compound=SOFT\n"
                            "lap_number=12\n"
                            "sector_1_time=30.512\n"
                            "sector_2_time=38.921\n"
                            "sector_3_time=24.134\n"
                            "position=3\n"
                            "track_status=1\n"
                            "is_pit_lap=0\n"
                            "air_temp=28.0\n"
                            "track_temp=41.5\n"
                            "humidity=45.0\n"
                            "wind_speed=5.2\n"
                            "wind_dir=180\n"
                            "pressure=1013.0\n"
                            "speed_mean=220.5\n"
                            "speed_max=320.8\n"
                            "throttle_mean=82.3\n"
                            "brake_mean=18.7\n"
                            "rpm_mean=11000\n"
                            "rpm_max=12500\n"
                            "drs_activations=12\n"
                            "speed_min=80.2\n"
                            "speed_std=15.3\n"
                            "speed_q1=205.0\n"
                            "speed_q3=235.0\n"
                            "speed_range=240.6\n"
                            "throttle_std=10.5\n"
                            "throttle_pct_full=60.0\n"
                            "brake_std=5.7\n"
                            "brake_pct_braking=32.0\n"
                            "rpm_std=800.0\n"
                            "gear_changes=38\n"
                            "gear_min=2\n"
                            "drs_active_pct=30.0\n"
                            "drs_time_seconds=4.2\n"
                            "stint=2\n"
                            "tyre_life=7\n"
                            "fresh_tyre=0"
                        ),
                        key="lap_pred_kv",
                    )

                    if st.button("🚀 Predict Lap Time", key="predict_laptime_btn"):
                        if not user_kv_text.strip():
                            st.warning("Please provide at least one `key=value` pair.")
                        else:
                            feature_dict = {}
                            for line in user_kv_text.splitlines():
                                line = line.strip()
                                if not line or "=" not in line:
                                    continue
                                key, val = line.split("=", 1)
                                key = key.strip()
                                val = val.strip()

                                # Try casting to float; otherwise leave as string (for categoricals)
                                try:
                                    num_val = float(val)
                                    feature_dict[key] = num_val
                                except ValueError:
                                    feature_dict[key] = val

                            if not feature_dict:
                                st.warning("No valid `key=value` pairs were parsed.")
                            else:
                                input_df = pd.DataFrame([feature_dict])

                                st.write("Parsed features sent to the model:")
                                st.dataframe(input_df)

                                try:
                                    y_pred = model_pipe.predict(input_df)[0]
                                    st.success(f"Predicted Lap Time: **{y_pred:.3f} seconds**")
                                except Exception as e:
                                    st.error(f"Model could not predict with these inputs: {e}")
                                    st.info(
                                        "Check that the feature names and types match those used in training "
                                        "(same raw column names as in your notebook before preprocessing)."
                                    )

                st.markdown('</div>', unsafe_allow_html=True)
