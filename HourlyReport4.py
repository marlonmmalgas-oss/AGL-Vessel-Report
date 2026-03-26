import streamlit as st

st.set_page_config(layout="wide")

# -----------------------
# STYLE (EXCEL LOOK)
# -----------------------
st.markdown("""
<style>
.report-box {
    border: 3px solid black;
    padding: 20px;
}
.title {
    text-align:center;
    font-size:24px;
    font-weight:bold;
}
.center {
    text-align:center;
}
.blue {
    background:#2f5597;
    color:white;
    padding:6px;
    text-align:center;
}
.yellow {
    background:#ffff00;
    padding:6px;
    text-align:center;
}
.cell {
    border:1px solid black;
    text-align:center;
    padding:6px;
}
.small {
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# INPUT SECTION
# -----------------------
st.markdown("## INPUT")

c1,c2,c3,c4 = st.columns(4)

date = c1.date_input("Date")
shift = c2.selectbox("Shift", ["DAY","NIGHT"])
first_lift = c3.text_input("First Lift", "1815")
last_lift = c4.text_input("Last Lift", "0525")

# AUTO HOURS
def gen_hours(shift):
    start = 6 if shift=="DAY" else 18
    return [f"{(start+i)%24:02d}00-{(start+i+1)%24:02d}00" for i in range(12)]

hours = gen_hours(shift)
selected_hour = st.selectbox("Select Hour", hours)

# 4-HOUR AUTO
def get_block(h):
    s = int(h[:2])
    start = (s//4)*4
    end = start+4
    return f"{start:02d}00-{end:02d}00"

four_hour = get_block(selected_hour)

# CRANE INPUT
st.markdown("### CRANE INPUT")
cols = st.columns(3)

data = {}
for i,cr in enumerate(["CR1","CR2","CR3"]):
    with cols[i]:
        st.markdown(f"**{cr}**")
        d = st.number_input("Discharge",0,key=f"d{cr}")
        l = st.number_input("Load",0,key=f"l{cr}")
        data[cr] = [d,l]

# STORAGE
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
cranes = ["CR1","CR2","CR3"]

split = {c:[0,0] for c in cranes}
hourly = {c:[0,0] for c in cranes}
block = {c:[0,0] for c in cranes}

for r in st.session_state.records:
    for c in cranes:
        split[c][0]+=r["data"][c][0]
        split[c][1]+=r["data"][c][1]

        if r["hour"]==selected_hour:
            hourly[c]=r["data"][c]

        if r["block"]==four_hour:
            block[c][0]+=r["data"][c][0]
            block[c][1]+=r["data"][c][1]

remaining = {c:[split[c][0]-hourly[c][0],split[c][1]-hourly[c][1]] for c in cranes}

# TOTALS
total_d = sum(split[c][0] for c in cranes)
total_l = sum(split[c][1] for c in cranes)
total_moves = total_d + total_l

# -----------------------
# REPORT DISPLAY
# -----------------------
st.markdown("---")

main, chart = st.columns([4,1])

with main:
    st.markdown('<div class="report-box">', unsafe_allow_html=True)

    st.markdown('<div class="title">HOURLY REPORT</div>', unsafe_allow_html=True)
    st.markdown('<div class="center">AGL Terminal A Berth</div>', unsafe_allow_html=True)
    st.markdown('<div class="center"><b>MSC ADA F</b></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="small">
    Docked on 2026-01-25 @ 2315<br>
    {date}<br>
    First Lift @ {first_lift}<br>
    Last Lift @ {last_lift}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="yellow">{selected_hour}</div>', unsafe_allow_html=True)

    # HEADERS
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown("")
    c2.markdown('<div class="blue">Split Total</div>', unsafe_allow_html=True)
    c3.markdown('<div class="yellow">Hourly Totals</div>', unsafe_allow_html=True)
    c4.markdown('<div class="blue">Remaining</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown("")
    c2.markdown('<div class="blue">Discharge | Load</div>', unsafe_allow_html=True)
    c3.markdown('<div class="yellow">Discharge | Load</div>', unsafe_allow_html=True)
    c4.markdown('<div class="blue">Discharge | Load</div>', unsafe_allow_html=True)

    # ROWS
    for c in cranes:
        c1,c2,c3,c4 = st.columns(4)

        c1.markdown(f'<div class="cell">Crane {c[-1]}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="blue">{split[c][0]} | {split[c][1]}</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="yellow">{hourly[c][0]} | {hourly[c][1]}</div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="blue">{remaining[c][0]} | {remaining[c][1]}</div>', unsafe_allow_html=True)

    # TOTAL BLOCK
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="blue">Total Units Remaining</div>
    <div class="cell">0 | 0 | 0</div>

    <div class="blue">Total Units Done</div>
    <div class="cell">{total_d} | {total_l} | {total_moves}</div>

    <div class="yellow"><b>Total Units Done 12hrs</b><br>{total_d} | {total_l} | {total_moves}</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="small">
    TOTAL MOVES INCLUDE SHIFTS + HATCH COVERS<br>
    TARGET IS SUBJECT TO CHANGE<br>
    TARGET IS EFFECTED BY MAJOR DELAYS
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# ACTUAL VS TARGET (RIGHT)
# -----------------------
with chart:
    st.markdown("### ACTUAL VS TARGET")

    target = st.number_input("Target", 0, value=95)

    st.bar_chart({
        "Actual":[total_moves],
        "Target":[target]
    })

# -----------------------
# 4 HOURLY REPORT
# -----------------------
st.markdown("---")
st.markdown("## 4 HOURLY REPORT")

st.markdown(f'<div class="yellow">{four_hour}</div>', unsafe_allow_html=True)

for c in cranes:
    st.write(f"{c} → {block[c][0]} | {block[c][1]}")