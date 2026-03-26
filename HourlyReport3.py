import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("MARLON AGL TERMINAL REPORT")

# -------------------------
# SHIFT + AUTO HOURS
# -------------------------
shift = st.sidebar.selectbox("Shift", ["DAY", "NIGHT"])

def generate_hours(shift):
    hours = []
    if shift == "DAY":
        start = 6
    else:
        start = 18

    for i in range(12):
        h1 = (start + i) % 24
        h2 = (start + i + 1) % 24
        hours.append(f"{h1:02d}00-{h2:02d}00")
    return hours

time_slots = generate_hours(shift)

selected_time = st.sidebar.selectbox("Select Hour", time_slots)

# -------------------------
# AUTO 4-HOUR BLOCK
# -------------------------
def get_4hour_block(time_range):
    start = int(time_range[:2])
    block_start = (start // 4) * 4
    block_end = block_start + 4
    return f"{block_start:02d}00-{block_end:02d}00"

four_hour_block = get_4hour_block(selected_time)

st.subheader(f"Hourly: {selected_time}")
st.subheader(f"4-Hour Block: {four_hour_block}")

# -------------------------
# INPUT
# -------------------------
st.sidebar.subheader("CRANE INPUT")

data = {}
for cr in ["CR1", "CR2", "CR3"]:
    d = st.sidebar.number_input(f"{cr} Discharge", 0, key=f"d_{cr}")
    l = st.sidebar.number_input(f"{cr} Load", 0, key=f"l_{cr}")
    data[cr] = {"Discharge": d, "Load": l}

# -------------------------
# STORAGE
# -------------------------
if "records" not in st.session_state:
    st.session_state.records = []

if st.sidebar.button("Save Entry"):
    st.session_state.records.append({
        "shift": shift,
        "time": selected_time,
        "block": four_hour_block,
        "data": data
    })

records = st.session_state.records

# -------------------------
# CALCULATIONS
# -------------------------
cranes = ["CR1", "CR2", "CR3"]

split_totals = {cr:[0,0] for cr in cranes}
hourly = {cr:[0,0] for cr in cranes}
four_hour = {cr:[0,0] for cr in cranes}

for r in records:
    for cr in cranes:
        # TOTAL (Split)
        split_totals[cr][0] += r["data"][cr]["Discharge"]
        split_totals[cr][1] += r["data"][cr]["Load"]

        # HOURLY
        if r["time"] == selected_time:
            hourly[cr][0] = r["data"][cr]["Discharge"]
            hourly[cr][1] = r["data"][cr]["Load"]

        # 4-HOURLY
        if r["block"] == four_hour_block:
            four_hour[cr][0] += r["data"][cr]["Discharge"]
            four_hour[cr][1] += r["data"][cr]["Load"]

# Remaining
remaining = {}
for cr in cranes:
    remaining[cr] = [
        split_totals[cr][0] - hourly[cr][0],
        split_totals[cr][1] - hourly[cr][1]
    ]

# -------------------------
# DISPLAY (MATCH YOUR EXCEL STRUCTURE)
# -------------------------
st.markdown("## HOURLY REPORT")

for cr in cranes:
    st.write(f"### {cr}")
    col1, col2, col3 = st.columns(3)

    col1.metric("Split Total", f"D:{split_totals[cr][0]} | L:{split_totals[cr][1]}")
    col2.metric("Hourly", f"D:{hourly[cr][0]} | L:{hourly[cr][1]}")
    col3.metric("Remaining", f"D:{remaining[cr][0]} | L:{remaining[cr][1]}")

st.markdown("---")

st.markdown("## 4 HOURLY REPORT")

for cr in cranes:
    st.write(f"{cr} → D:{four_hour[cr][0]} | L:{four_hour[cr][1]}")

# -------------------------
# TOTALS
# -------------------------
total_d = sum(split_totals[cr][0] for cr in cranes)
total_l = sum(split_totals[cr][1] for cr in cranes)

st.markdown("---")
st.subheader("TOTALS")
st.write(f"Discharge: {total_d}")
st.write(f"Load: {total_l}")
st.write(f"Total Moves: {total_d + total_l}")