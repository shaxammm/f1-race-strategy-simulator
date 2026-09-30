"""Streamlit dashboard for the F1 Race Strategy Simulator (educational)."""
from __future__ import annotations

from dataclasses import replace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.analysis import run_monte_carlo
from src.models import Compound, RaceConfig, Stint, Strategy
from src.plots import (
    plot_lap_times,
    plot_race_time_distribution,
    plot_tyre_degradation,
)
from src.simulation import simulate_strategy
from src.weather import Weather

st.set_page_config(page_title="F1 Race Strategy Simulator", layout="wide")

PRESETS = {
    "Soft-Medium": [(Compound.SOFT, 0.35), (Compound.MEDIUM, 0.65)],
    "Medium-Hard": [(Compound.MEDIUM, 0.44), (Compound.HARD, 0.56)],
    "Soft-Medium-Soft": [
        (Compound.SOFT, 0.26), (Compound.MEDIUM, 0.47), (Compound.SOFT, 0.27),
    ],
}


def scale_preset(name: str, parts: list, n_laps: int) -> Strategy:
    """Scale a preset's stint fractions to the chosen race length."""
    laps = [max(1, round(frac * n_laps)) for _, frac in parts[:-1]]
    stints = [Stint(c, n) for (c, _), n in zip(parts, laps)]
    stints.append(Stint(parts[-1][0], n_laps - sum(laps)))
    return Strategy(name, tuple(stints))


def weather_effect_figure(cfg: RaceConfig, strategy: Strategy):
    """Lap times of one strategy under every weather scenario."""
    clean = replace(cfg, safety_car_prob=0.0)
    fig, ax = plt.subplots(figsize=(10, 5))
    for w in Weather:
        r = simulate_strategy(clean, strategy, noise_std_s=0.0, weather=w)
        ax.plot(np.arange(1, len(r.lap_times_s) + 1), r.lap_times_s, label=w.value)
    ax.set_xlabel("Lap")
    ax.set_ylabel("Lap time (s)")
    ax.set_title(f"Effect of weather ({strategy.name}, dry tyres only)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def comparison_figure(results: list):
    """Mean race time with +/- 1 std error bars."""
    fig, ax = plt.subplots(figsize=(8, 5))
    names = [r.strategy_name for r in results]
    ax.bar(names, [r.mean_s for r in results],
           yerr=[r.std_s for r in results], capsize=6, alpha=0.8)
    lo = min(r.mean_s - r.std_s for r in results)
    hi = max(r.mean_s + r.std_s for r in results)
    ax.set_ylim(lo - 20, hi + 20)
    ax.set_ylabel("Mean race time (s)")
    ax.set_title("Strategy comparison (error bars = 1 std)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    return fig


def show(fig) -> None:
    st.pyplot(fig)
    plt.close(fig)


# ---------------- Race Settings (sidebar) ----------------
st.sidebar.header("Race Settings")
n_laps = st.sidebar.slider("Number of laps", 30, 78, 57)
base_lap = st.sidebar.slider("Base lap time (s)", 70, 110, 90)
pit_loss = st.sidebar.slider("Pit-stop time loss (s)", 15, 30, 22)
track_temp = st.sidebar.slider("Track temperature (C)", 10, 55, 30)
sc_prob = st.sidebar.slider("Safety Car probability", 0.0, 1.0, 0.3, 0.05)
weather = Weather(st.sidebar.selectbox("Weather", [w.value for w in Weather]))
n_runs = st.sidebar.slider("Monte Carlo runs", 100, 3000, 500, 100)
seed = int(st.sidebar.number_input("Random seed", 0, 99999, 42))

try:
    cfg = RaceConfig(
        n_laps=n_laps, base_lap_time_s=float(base_lap), pit_loss_s=float(pit_loss),
        track_temp_c=float(track_temp), safety_car_prob=sc_prob,
    )
except ValueError as err:
    st.error(str(err))
    st.stop()

st.title("F1 Race Strategy Simulator")
st.caption("Simplified educational simulation. Not an official Formula 1 model.")

# ---------------- Strategy Builder ----------------
st.header("Strategy Builder")
chosen = st.multiselect("Preset strategies", list(PRESETS), default=list(PRESETS))
strategies = [scale_preset(n, PRESETS[n], n_laps) for n in chosen]

with st.expander("Add a custom strategy"):
    use_custom = st.checkbox("Include custom strategy")
    n_stints = st.selectbox("Number of stints", [2, 3, 4])
    compounds, stint_laps = [], []
    for i in range(n_stints):
        cols = st.columns(2)
        value = cols[0].selectbox(f"Stint {i + 1} tyre", [c.value for c in Compound], key=f"c{i}")
        compounds.append(Compound(value))
        if i < n_stints - 1:
            stint_laps.append(int(cols[1].number_input(
                f"Stint {i + 1} laps", 1, n_laps, max(1, n_laps // n_stints), key=f"l{i}")))
    remainder = n_laps - sum(stint_laps)
    if use_custom:
        if remainder < 1:
            st.error("Stints are longer than the race. Reduce the laps.")
        else:
            stint_laps.append(remainder)
            strategies.append(Strategy(
                "Custom", tuple(Stint(c, n) for c, n in zip(compounds, stint_laps))))

for s in strategies:
    text = " -> ".join(f"{st_.compound.value} ({st_.laps})" for st_ in s.stints)
    st.write(f"**{s.name}:** {text}")

# ---------------- Tabs ----------------
tab_sim, tab_res, tab_charts, tab_analysis = st.tabs(
    ["Simulation", "Results", "Charts", "Analysis"])

with tab_sim:
    st.write("Each strategy is simulated many times with random lap-time noise, "
             "track temperature and Safety Car events.")
    if st.button("Run simulation", type="primary"):
        if not strategies:
            st.warning("Choose at least one strategy.")
        else:
            with st.spinner("Simulating..."):
                mc = [run_monte_carlo(cfg, s, n_runs=n_runs, weather=weather, seed=seed)
                      for s in strategies]
            st.session_state["run"] = {
                "mc": mc, "cfg": cfg, "strategies": strategies, "weather": weather}
            st.success("Done. Open the Results, Charts and Analysis tabs.")

run = st.session_state.get("run")

with tab_res:
    if not run:
        st.info("Run the simulation first.")
    else:
        mc = run["mc"]
        default_thr = float(round(np.mean([r.mean_s for r in mc])))
        threshold = st.number_input("Time threshold (s)", value=default_thr, step=10.0)
        rows = [{
            "Strategy": r.strategy_name,
            "Pit stops": r.pit_stops,
            "Mean (s)": round(r.mean_s, 1),
            "Median (s)": round(r.median_s, 1),
            "Std (s)": round(r.std_s, 1),
            "Fastest (s)": round(r.fastest_s, 1),
            "Slowest (s)": round(r.slowest_s, 1),
            f"P(< {threshold:.0f} s)": f"{r.prob_below(threshold) * 100:.1f}%",
            "Risk: P95 - median (s)": round(
                float(np.percentile(r.race_times_s, 95) - r.median_s), 1),
        } for r in mc]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

with tab_charts:
    if not run:
        st.info("Run the simulation first.")
    else:
        r_cfg, r_strats = run["cfg"], run["strategies"]
        clean = replace(r_cfg, safety_car_prob=0.0)
        single = {s.name: simulate_strategy(clean, s, noise_std_s=0.0, weather=run["weather"])
                  for s in r_strats}
        st.subheader("Lap times and pit-stop locations")
        show(plot_lap_times(single, {s.name: s.pit_laps for s in r_strats}))
        st.subheader("Tyre degradation")
        show(plot_tyre_degradation(track_temp_c=r_cfg.track_temp_c))
        st.subheader("Race-time distribution (Monte Carlo)")
        show(plot_race_time_distribution(run["mc"]))
        st.subheader("Strategy comparison")
        show(comparison_figure(run["mc"]))
        st.subheader("Effect of weather")
        show(weather_effect_figure(r_cfg, r_strats[0]))

with tab_analysis:
    if not run:
        st.info("Run the simulation first.")
    else:
        mc = sorted(run["mc"], key=lambda r: r.mean_s)
        fastest, steadiest = mc[0], min(mc, key=lambda r: r.std_s)
        st.write(f"- Lowest **mean** race time: **{fastest.strategy_name}** "
                 f"({fastest.mean_s:.1f} s).")
        st.write(f"- Lowest **spread** (std): **{steadiest.strategy_name}** "
                 f"({steadiest.std_s:.1f} s).")
        if len(mc) > 1:
            gap = mc[1].mean_s - mc[0].mean_s
            st.write(f"- Gap between the two best means: {gap:.1f} s, compared with "
                     f"a typical spread of {fastest.std_s:.1f} s. "
                     "If the gap is small relative to the spread, the ranking is "
                     "not reliable.")
        st.write("Trade-off: a strategy with a lower mean is not automatically "
                 "better. More pit stops and softer tyres can change both the "
                 "average and the risk. Safety Car and weather add uncertainty "
                 "that the model only approximates.")
