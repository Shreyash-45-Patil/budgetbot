import streamlit as st
import pandas as pd
from datetime import date
import json
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="SmartExpense Manager", page_icon="💰")

# ---------- FUNCTIONS ----------
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def save_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ---------- SESSION ----------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------- LOGIN ----------
if st.session_state.user is None:

    st.markdown("<h2 style='text-align:center;'>💰 SmartExpense Manager</h2>", unsafe_allow_html=True)

    users = load_users()

    mode = st.radio("", ["Login", "Register"], horizontal=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # LOGIN
    if mode == "Login":
        if st.button("Login", use_container_width=True):

            users = load_users()

            if username in users and users[username]["password"] == password:
                st.session_state.user = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # REGISTER
    else:
        if st.button("Register", use_container_width=True):

            users = load_users()

            if username in users:
                st.warning("User already exists")
            else:
                users[username] = {"password": password}
                save_users(users)
                st.success("Registered successfully")

# ---------- MAIN ----------
if st.session_state.user:

    user = st.session_state.user
    file = f"{user}_data.json"

    # ---------- HEADER (YOUR VERSION) ----------
    st.markdown("<h2 style='text-align:center;'>💰 SmartExpense Manager</h2>", unsafe_allow_html=True)
    st.markdown(f"### 👋 Welcome to SmartExpense Manager, {user}")

    # LOGOUT
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # ---------- NAVIGATION ----------
    menu = st.radio("", ["🏠 Dashboard", "➕ Add", "📋 Expenses"], horizontal=True)

    # ---------- LOAD DATA ----------
    if os.path.exists(file):
        data = json.load(open(file))
        if isinstance(data, list):
            data = {"income": 0, "expenses": data}
    else:
        data = {"income": 0, "expenses": []}

    # ---------- INCOME ----------
    income = st.number_input("Monthly Income", value=data["income"])
    data["income"] = income
    save_data(data, file)

    df = pd.DataFrame(data["expenses"])

    # ---------- DASHBOARD ----------
    if menu == "🏠 Dashboard":

        total = df["amount"].sum() if not df.empty else 0
        savings = income - total

        st.subheader("Summary")

        st.metric("Expense", f"₹{total}")
        st.metric("Savings", f"₹{savings}")
        st.metric("Entries", len(df))

        st.subheader("Insights")

        if total > income:
            st.error("Spending is high")
        elif total > income * 0.7:
            st.warning("Spending is moderate")
        else:
            st.success("All good")

        st.subheader("Recent Transactions")

        if not df.empty:
            st.dataframe(df.tail(3), use_container_width=True)
        else:
            st.info("No transactions")

    # ---------- ADD ----------
    elif menu == "➕ Add":

        st.subheader("Add Expense")

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

        st.subheader("Expenses")

        search = st.text_input("Search")

        filtered = data["expenses"]
        if search:
            filtered = [e for e in filtered if search.lower() in e["name"].lower()]

        if filtered:
            for i, exp in enumerate(filtered):

                st.write(f"**{exp['name']}** - ₹{exp['amount']} ({exp['category']})")

                col1, col2 = st.columns(2)

                # EDIT
                if col1.button("Edit", key=f"edit{i}"):
                    st.info("Edit feature can be added here")

                # DELETE
                if col2.button("Delete", key=f"del{i}"):
                    data["expenses"].remove(exp)
                    save_data(data, file)
                    st.rerun()

        else:
            st.info("No expenses found")
