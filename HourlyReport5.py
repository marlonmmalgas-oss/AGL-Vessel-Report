import streamlit as st

st.set_page_config(layout="wide")

# -----------------------
# INPUT SECTION
# -----------------------
st.title("MARLON HOURLY REPORT")

c1,c2,c3,c4 = st.columns(4)
date = c1.date_input("Date")
shift = c2.selectbox("Shift", ["DAY","NIGHT"])
first_lift = c3.text_input("First Lift", "1815")
last_lift = c4.text_input("Last Lift", "0525")

# -----------------------
# HOURS
# -----------------------
def generate_hours(shift):
    start = 6 if shift=="DAY" else 18
    hours = []
    for i in range(12):
        h1 = (start + i) % 24
        h2 = (start + i + 1) % 24
        hours.append(f"{h1:02d}00-{h2:02d}00")
    return hours

hours = generate_hours(shift)
selected_hour = st.selectbox("Select Hour", hours)

# 4-hour block
def get_block(hour_str):
    h = int(hour_str[:2])
    start = (h//4)*4
    return f"{start:02d}00-{start+4:02d}00"

four_hour = get_block(selected_hour)

# -----------------------
# CRANE INPUT
# -----------------------
st.markdown("### CRANE INPUT")
cols = st.columns(3)
cranes = ["CR1","CR2","CR3"]
data = {}
for i, cr in enumerate(cranes):
    with cols[i]:
        st.markdown(f"**{cr}**")
        d = st.number_input("Discharge", 0, key=f"d{cr}")
        l = st.number_input("Load", 0, key=f"l{cr}")
        data[cr] = [d,l]

# -----------------------
# SESSION STATE STORAGE
# -----------------------
if "records" not in st.session_state:
    st.session_state.records = []

if st.button("Save Entry"):
    st.session_state.records.append({
        "hour": selected_hour,
        "block": four_hour,
        "data": data
    })

# -----------------------
# CALCULATIONS
# -----------------------
split = {c:[0,0] for c in cranes}
hourly = {c:[0,0] for c in cranes}
block = {c:[0,0] for c in cranes}

for r in st.session_state.records:
    for c in cranes:
        split[c][0] += r["data"][c][0]
        split[c][1] += r["data"][c][1]

        if r["hour"] == selected_hour:
            hourly[c] = r["data"][c]

        if r["block"] == four_hour:
            block[c][0] += r["data"][c][0]
            block[c][1] += r["data"][c][1]

remaining = {c:[split[c][0]-hourly[c][0], split[c][1]-hourly[c][1]] for c in cranes}

total_d = sum(split[c][0] for c in cranes)
total_l = sum(split[c][1] for c in cranes)
total_moves = total_d + total_l

# -----------------------
# REPORT HTML
# -----------------------
def render_report():
    rows = ""
    for c in cranes:
        rows += f"""
        <tr>
            <td>{c}</td>
            <td class="blue">{split[c][0]}</td>
            <td class="blue">{split[c][1]}</td>
            <td class="yellow">{hourly[c][0]}</td>
            <td class="yellow">{hourly[c][1]}</td>
            <td class="blue">{remaining[c][0]}</td>
            <td class="blue">{remaining[c][1]}</td>
        </tr>
        """
    html = f"""
    <style>
    table {{border-collapse: collapse; width:100%;}}
    td, th {{border:2px solid black; text-align:center; padding:6px;}}
    .blue {{background:#2f5597; color:white;}}
    .yellow {{background:#ffff00;}}
    .title {{font-size:20px; font-weight:bold; text-align:center;}}
    </style>

    <div class="title">HOURLY REPORT</div>
    <div style="text-align:center;">AGL Terminal A Berth</div>
    <div style="text-align:center;"><b>MSC ADA F</b></div>
    <br>
    <div class="small">
    Docked on 2026-01-25 @ 2315<br>
    {date}<br>
    First Lift @ {first_lift}<br>
    Last Lift @ {last_lift}
    </div>
    <br>

    <div class="yellow">{selected_hour}</div>
    <table>
        <tr>
            <th></th>
            <th colspan="2" class="blue">Split Total</th>
            <th colspan="2" class="yellow">Hourly</th>
            <th colspan="2" class="blue">Remaining</th>
        </tr>
        <tr>
            <th></th>
            <th class="blue">D</th>
            <th class="blue">L</th>
            <th class="yellow">D</th>
            <th class="yellow">L</th>
            <th class="blue">D</th>
            <th class="blue">L</th>
        </tr>
        {rows}
        <tr>
            <td><b>Total</b></td>
            <td class="blue">{total_d}</td>
            <td class="blue">{total_l}</td>
            <td class="yellow">-</td>
            <td class="yellow">-</td>
            <td class="blue">-</td>
            <td class="blue">-</td>
        </tr>
    </table>
    <br>
    <div class="yellow">
        Total Units Done 12hrs: {total_d} | {total_l} | {total_moves}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

render_report()

# -----------------------
# ACTUAL VS TARGET
# -----------------------
st.markdown("---")
st.markdown("### ACTUAL VS TARGET")
cols = st.columns([3,1])
with cols[1]:
    target = st.number_input("Target", 0, value=95)
    st.bar_chart({"Actual":[total_moves],"Target":[target]})

# -----------------------
# 4-HOURLY REPORT
# -----------------------
st.markdown("---")
st.markdown("## 4 HOURLY REPORT")
st.markdown(f'<div class="yellow">{four_hour}</div>', unsafe_allow_html=True)
for c in cranes:
    st.write(f"{c}: {block[c][0]} | {block[c][1]}")