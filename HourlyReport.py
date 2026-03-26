import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide")

# -------------------------------
# FILE STORAGE
# -------------------------------
DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "vessel","date","shift","hour",
        "cr1_d","cr1_l","cr2_d","cr2_l",
        "cr3_d","cr3_l","cr4_d","cr4_l",
        "docked","first_lift","last_lift"
    ])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# -------------------------------
# SHIFT HOURS
# -------------------------------
DAY_HOURS = [
    "06-07","07-08","08-09","09-10",
    "10-11","11-12","12-13","13-14",
    "14-15","15-16","16-17","17-18"
]

NIGHT_HOURS = [
    "18-19","19-20","20-21","21-22",
    "22-23","23-00","00-01","01-02",
    "02-03","03-04","04-05","05-06"
]

# -------------------------------
# SIDEBAR NAV
# -------------------------------
menu = st.sidebar.radio("Menu", ["Input", "Input View", "Report", "History"])

# -------------------------------
# INPUT SCREEN
# -------------------------------
if menu == "Input":
    st.title("🚢 Vessel Input")

    vessel = st.text_input("Vessel Name")
    date = st.date_input("Date")
    shift = st.selectbox("Shift", ["DAY","NIGHT"])

    hours = DAY_HOURS if shift == "DAY" else NIGHT_HOURS
    hour = st.selectbox("Hour", hours)

    st.subheader("Enter Crane Data")

    cols = st.columns(4)

    def crane_input(label, col):
        with col:
            d = st.number_input(f"{label} Discharge", 0)
            l = st.number_input(f"{label} Load", 0)
        return d, l

    cr1_d, cr1_l = crane_input("CR1", cols[0])
    cr2_d, cr2_l = crane_input("CR2", cols[1])
    cr3_d, cr3_l = crane_input("CR3", cols[2])
    cr4_d, cr4_l = crane_input("CR4", cols[3])

    st.subheader("Additional Info")

    docked = st.text_input("Docked (e.g. 12-03-26 02:00)")
    first_lift = st.text_input("First Lift")
    last_lift = st.text_input("Last Lift")

    if st.button("Save Entry"):
        new_row = pd.DataFrame([{
            "vessel": vessel,
            "date": str(date),
            "shift": shift,
            "hour": hour,
            "cr1_d": cr1_d, "cr1_l": cr1_l,
            "cr2_d": cr2_d, "cr2_l": cr2_l,
            "cr3_d": cr3_d, "cr3_l": cr3_l,
            "cr4_d": cr4_d, "cr4_l": cr4_l,
            "docked": docked,
            "first_lift": first_lift,
            "last_lift": last_lift
        }])

        df_new = pd.concat([df, new_row], ignore_index=True)
        df_new.to_csv(DATA_FILE, index=False)

        st.success("Saved!")

# -------------------------------
# INPUT VIEW
# -------------------------------
elif menu == "Input View":
    st.title("📋 Input Grid")

    st.dataframe(df)

# -------------------------------
# REPORT
# -------------------------------
elif menu == "Report":
    st.title("📊 Vessel Report")

    date = st.date_input("Select Date")
    shift = st.selectbox("Select Shift", ["DAY","NIGHT"])

    data = df[(df["date"] == str(date)) & (df["shift"] == shift)]

    hours = DAY_HOURS if shift == "DAY" else NIGHT_HOURS

    report = []

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

        report.append([h, cr1, cr2, cr3, cr4, total])

    report_df = pd.DataFrame(report, columns=["TIME","CR1","CR2","CR3","CR4","TOTAL"])

    st.dataframe(report_df)

    st.subheader("Totals")
    st.write("Grand Total:", report_df["TOTAL"].sum())

# -------------------------------
# HISTORY
# -------------------------------
elif menu == "History":
    st.title("📁 History")

    st.dataframe(df)