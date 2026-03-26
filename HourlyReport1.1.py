import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

DATA_FILE = "data.csv"

# ---------------------------
# INIT FILE
# ---------------------------
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "vessel","date","shift","hour",
        "cr1_d","cr1_l","cr2_d","cr2_l",
        "cr3_d","cr3_l","cr4_d","cr4_l",
        "docked","first_lift","last_lift"
    ])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# ---------------------------
# HOURS
# ---------------------------
DAY_HOURS = ["06-07","07-08","08-09","09-10",
             "10-11","11-12","12-13","13-14",
             "14-15","15-16","16-17","17-18"]

NIGHT_HOURS = ["18-19","19-20","20-21","21-22",
               "22-23","23-00","00-01","01-02",
               "02-03","03-04","04-05","05-06"]

# ---------------------------
# NAV
# ---------------------------
menu = st.sidebar.radio("Menu", ["Input","Input View","Report","History"])

# ===========================
# INPUT
# ===========================
if menu == "Input":
    st.title("🚢 Input")

    vessel = st.text_input("Vessel")
    date = st.date_input("Date")
    shift = st.selectbox("Shift", ["DAY","NIGHT"])

    hours = DAY_HOURS if shift == "DAY" else NIGHT_HOURS
    hour = st.selectbox("Hour", hours)

    st.subheader("Crane Input")

    def crane(label):
        col1, col2 = st.columns(2)
        d = col1.number_input(f"{label} Discharge", 0)
        l = col2.number_input(f"{label} Load", 0)
        return d, l

    cr1_d, cr1_l = crane("CR1")
    cr2_d, cr2_l = crane("CR2")
    cr3_d, cr3_l = crane("CR3")
    cr4_d, cr4_l = crane("CR4")

    st.subheader("Other Info")

    docked = st.text_input("Docked (e.g 12-03-26 02:00)")
    first_lift = st.text_input("First Lift")
    last_lift = st.text_input("Last Lift")

    if st.button("Save"):
        new = pd.DataFrame([{
            "vessel": vessel,
            "date": str(date),
            "shift": shift,
            "hour": hour,
            "cr1_d": cr1_d,"cr1_l": cr1_l,
            "cr2_d": cr2_d,"cr2_l": cr2_l,
            "cr3_d": cr3_d,"cr3_l": cr3_l,
            "cr4_d": cr4_d,"cr4_l": cr4_l,
            "docked": docked,
            "first_lift": first_lift,
            "last_lift": last_lift
        }])

        df = pd.concat([df, new], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success("Saved")

# ===========================
# INPUT VIEW
# ===========================
elif menu == "Input View":
    st.title("📋 Input Data")
    st.dataframe(df)

# ===========================
# REPORT
# ===========================
elif menu == "Report":

    st.title("📊 Vessel Report")

    date = st.date_input("Date")
    shift = st.selectbox("Shift", ["DAY","NIGHT"])

    data = df[(df["date"] == str(date)) & (df["shift"] == shift)]

    hours = DAY_HOURS if shift == "DAY" else NIGHT_HOURS

    # Build hourly rows
    rows = []

    for h in hours:
        row = data[data["hour"] == h]

        if not row.empty:
            r = row.iloc[0]
            cr1 = r["cr1_d"] + r["cr1_l"]
            cr2 = r["cr2_d"] + r["cr2_l"]
            cr3 = r["cr3_d"] + r["cr3_l"]
            cr4 = r["cr4_d"] + r["cr4_l"]
        else:
            cr1 = cr2 = cr3 = cr4 = 0

        total = cr1 + cr2 + cr3 + cr4
        rows.append({"TIME":h,"CR1":cr1,"CR2":cr2,"CR3":cr3,"CR4":cr4,"TOTAL":total})

    report = pd.DataFrame(rows)

    # ---------------------------
    # INSERT 4 HOUR TOTALS
    # ---------------------------
    def add_total_block(df, start, end, label):
        block = df.iloc[start:end]
        total_row = block[["CR1","CR2","CR3","CR4","TOTAL"]].sum()
        total_row["TIME"] = label
        return total_row

    if shift == "DAY":
        t1 = add_total_block(report,0,4,"06-10 TOTAL")
        t2 = add_total_block(report,4,8,"10-14 TOTAL")
        t3 = add_total_block(report,8,12,"14-18 TOTAL")

        report = pd.concat([
            report.iloc[0:4],
            pd.DataFrame([t1]),
            report.iloc[4:8],
            pd.DataFrame([t2]),
            report.iloc[8:12],
            pd.DataFrame([t3])
        ])

    else:
        t1 = add_total_block(report,0,4,"18-22 TOTAL")
        t2 = add_total_block(report,4,8,"22-02 TOTAL")
        t3 = add_total_block(report,8,12,"02-06 TOTAL")

        report = pd.concat([
            report.iloc[0:4],
            pd.DataFrame([t1]),
            report.iloc[4:8],
            pd.DataFrame([t2]),
            report.iloc[8:12],
            pd.DataFrame([t3])
        ])

    # GRAND TOTAL
    grand = report[~report["TIME"].str.contains("TOTAL")][["CR1","CR2","CR3","CR4","TOTAL"]].sum()
    grand["TIME"] = "GRAND TOTAL"

    report = pd.concat([report, pd.DataFrame([grand])])

    st.dataframe(report)

# ===========================
# HISTORY
# ===========================
elif menu == "History":
    st.title("📁 History")
    st.dataframe(df)