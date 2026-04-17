import streamlit as st
import pandas as pd
from datetime import date
import json
import os

st.set_page_config(page_title="BudgetBot", page_icon="💰")

# ---------- THEME ----------
theme_toggle = st.toggle("🌗 Dark Mode", value=True)

if theme_toggle:
    bg = "#0f172a"
    card = "#1e293b"
    text = "#ffffff"
    subtext = "#cbd5f5"
else:
    bg = "#f1f5f9"
    card = "#ffffff"
    text = "#111827"
    subtext = "#374151"

# ---------- STYLE (FULL FIX) ----------
st.markdown(f"""
<style>

/* App background */
.stApp {{
    background-color: {bg};
    color: {text};
}}

/* ALL TEXT FIX */
h1, h2, h3, h4, h5, h6, p, label, span {{
    color: {text} !important;
}}

/* Sidebar text fix */
section[data-testid="stSidebar"] * {{
    color: {text} !important;
}}

/* Radio buttons FIX */
.stRadio label {{
    color: {text} !important;
    font-weight: 500;
}}

/* Input fields */
.stTextInput input, .stNumberInput input {{
    background-color: {"#111827" if theme_toggle else "#ffffff"} !important;
    color: {text} !important;
    border-radius: 10px;
}}

/* Cards */
.card {{
    background-color: {card};
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 12px;
    color: {text};
}}

/* Buttons */
.stButton button {{
    height: 45px;
    border-radius: 10px;
    font-weight: bold;
}}

/* Dataframe */
.stDataFrame {{
    color: {text} !important;
}}

/* Fix alerts */
.stAlert {{
    color: black !important;
}}

</style>
""", unsafe_allow_html=True)

# ---------- FUNCTIONS ----------
def load_users():
    if os.path.exists("users.json"):
        return json.load(open("users.json"))
    return {}

def save_users(users):
    json.dump(users, open("users.json", "w"))

def save_data(data, file):
    json.dump(data, open(file, "w"))

users = load_users()

if "user" not in st.session_state:
    st.session_state.user = None

# ---------- LOGIN ----------
if st.session_state.user is None:

    st.markdown("<h2 style='text-align:center;'>💰 BudgetBot</h2>", unsafe_allow_html=True)

    mode = st.radio("", ["Login", "Register"], horizontal=True)

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if mode == "Login":
        if st.button("Login", use_container_width=True):
            if u in users and users[u]["password"] == p:
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        if st.button("Register", use_container_width=True):
            users[u] = {"password": p}
            save_users(users)
            st.success("Registered successfully")

# ---------- MAIN ----------
if st.session_state.user:

    user = st.session_state.user
    file = f"{user}_data.json"

    if os.path.exists(file):
        data = json.load(open(file))
        if isinstance(data, list):
            data = {"income": 0, "expenses": data}
    else:
        data = {"income": 0, "expenses": []}

    # HEADER
    col1, col2 = st.columns([4,1])
    with col1:
        st.markdown(f"### 👋 {user}")
    with col2:
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    # NAV
    menu = st.radio("", ["🏠 Dashboard", "➕ Add", "📋 Expenses"], horizontal=True)

    # INCOME
    income = st.number_input("Monthly Income", value=data["income"])
    data["income"] = income
    save_data(data, file)

    df = pd.DataFrame(data["expenses"])

    # ---------- DASHBOARD ----------
    if menu == "🏠 Dashboard":

        total = df["amount"].sum() if not df.empty else 0
        savings = income - total

        st.markdown("### Summary")

        st.markdown(f"<div class='card'>💸 Expense: ₹{total}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>💰 Savings: ₹{savings}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>📊 Entries: {len(df)}</div>", unsafe_allow_html=True)

        st.markdown("### Insights")

        if total > income:
            st.error("Spending is high")
        elif total > income * 0.7:
            st.warning("Spending is moderate")
        else:
            st.success("All good")

        st.markdown("### Recent Transactions")

        if not df.empty:
            st.dataframe(df.tail(3), use_container_width=True)
        else:
            st.info("No transactions")

    # ---------- ADD ----------
    elif menu == "➕ Add":

        st.markdown("### Add Expense")

        with st.form("form", clear_on_submit=True):
            name = st.text_input("Name")
            amount = st.number_input("Amount", min_value=0)
            cat = st.selectbox("Category", ["Fixed", "Optional", "Extra"])
            d = st.date_input("Date")

            if st.form_submit_button("Add"):
                data["expenses"].append({
                    "name": name,
                    "amount": amount,
                    "category": cat,
                    "date": str(d)
                })
                save_data(data, file)
                st.success("Added successfully")

    # ---------- EXPENSES ----------
    elif menu == "📋 Expenses":

        st.markdown("### Expenses")

        search = st.text_input("Search")

        filtered = data["expenses"]
        if search:
            filtered = [e for e in filtered if search.lower() in e["name"].lower()]

        if filtered:
            for i, exp in enumerate(filtered):

                st.markdown(f"""
                <div class='card'>
                <b>{exp['name']}</b><br>
                ₹{exp['amount']} | {exp['category']}<br>
                📅 {exp['date']}
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                if col1.button("Edit", key=f"edit{i}"):
                    st.session_state.edit_index = i

                if col2.button("Delete", key=f"del{i}"):
                    data["expenses"].remove(exp)
                    save_data(data, file)
                    st.rerun()

        else:
            st.info("No expenses found")