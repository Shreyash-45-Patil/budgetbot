import streamlit as st
import pandas as pd
import json
import os
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="SmartExpense Manager", page_icon="logo.png")

# ---------- SPLASH SCREEN ----------
if "loaded" not in st.session_state:
    st.session_state.loaded = False

if not st.session_state.loaded:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", width=220)
        st.markdown("<h1 style='text-align:center;'>SmartExpense Manager</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Loading...</p>", unsafe_allow_html=True)

        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

    st.session_state.loaded = True
    st.rerun()

# ---------- STYLE ----------
st.markdown("""
<style>
.fade {
    animation: fadeIn 0.5s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
.card {
    padding: 15px;
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

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

# ---------- LOGIN / REGISTER ----------
if st.session_state.user is None:

    # ✅ BIG CENTERED LOGO
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", width=220)  # 🔥 BIG LOGO
        st.markdown(
            "<h1 style='text-align:center; margin-top:10px;'>SmartExpense Manager</h1>",
            unsafe_allow_html=True
        )

    option = st.radio("", ["🔐 Login", "🆕 Register"], horizontal=True)
    users = load_users()

    # LOGIN
    if option == "🔐 Login":
        st.markdown("<div class='fade'>", unsafe_allow_html=True)

        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            users = load_users()

            if username in users and users[username]["password"] == password:
                st.session_state.user = username
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")

        st.markdown("</div>", unsafe_allow_html=True)

    # REGISTER
    else:
        st.markdown("<div class='fade'>", unsafe_allow_html=True)

        st.subheader("Register")

        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")

        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Register", use_container_width=True):
            users = load_users()

            if username in users:
                st.warning("User already exists")
            elif password != confirm:
                st.error("Passwords do not match")
            elif username == "" or password == "":
                st.warning("Fill all fields")
            else:
                users[username] = {"password": password}
                save_users(users)
                st.success("Registered successfully 🎉")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- MAIN ----------
if st.session_state.user:

    user = st.session_state.user
    file = f"{user}_data.json"

    # HEADER
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo.png", width=160)  # 🔥 bigger header logo
        st.markdown(
            "<h2 style='text-align:center;'>SmartExpense Manager</h2>",
            unsafe_allow_html=True
        )

    st.markdown(f"### 👋 Welcome, {user}")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

    menu = st.radio("", ["🏠 Dashboard", "➕ Add Expense", "📋 Expenses"], horizontal=True)

    # LOAD DATA
    if os.path.exists(file):
        data = json.load(open(file))
        if isinstance(data, list):
            data = {"income": 0, "expenses": data}
    else:
        data = {"income": 0, "expenses": []}

    income = st.number_input("Monthly Income", value=data["income"])
    data["income"] = income
    save_data(data, file)

    df = pd.DataFrame(data["expenses"])

    # DASHBOARD
    if menu == "🏠 Dashboard":
        st.markdown("<div class='fade'>", unsafe_allow_html=True)

        total = df["amount"].sum() if not df.empty else 0
        savings = income - total

        st.markdown(f"<div class='card'>💸 Expense: ₹{total}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>💰 Savings: ₹{savings}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='card'>📊 Entries: {len(df)}</div>", unsafe_allow_html=True)

        if total > income:
            st.error("Spending is high")
        elif total > income * 0.7:
            st.warning("Moderate spending")
        else:
            st.success("Good control")

        st.markdown("</div>", unsafe_allow_html=True)

    # ADD
    elif menu == "➕ Add Expense":

        with st.form("form", clear_on_submit=True):
            name = st.text_input("Expense Name")
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

    # EXPENSES
    elif menu == "📋 Expenses":

        search = st.text_input("Search")

        filtered = data["expenses"]
        if search:
            filtered = [e for e in filtered if search.lower() in e["name"].lower()]

        if filtered:
            for i, exp in enumerate(filtered):

                st.markdown(f"""
                <div class='card'>
                <b>{exp['name']}</b><br>
                ₹{exp['amount']} | {exp['category']}
                </div>
                """, unsafe_allow_html=True)

                if st.button("Delete", key=i):
                    data["expenses"].remove(exp)
                    save_data(data, file)
                    st.rerun()
        else:
            st.info("No expenses found")
