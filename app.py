
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from database import session, Expense, User, SavingsGoal, Budget
import io
import bcrypt


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_password(password):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, hashed_password):

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "user_id" not in st.session_state:

    st.session_state.user_id = None


if "username" not in st.session_state:

    st.session_state.username = ""


# =========================================================
# LOGIN / REGISTER
# =========================================================

if not st.session_state.logged_in:

    st.title("💰 Smart Expense Tracker")

    st.write(
        "Manage your expenses smarter and easier."
    )

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Register"
        ]
    )

    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

        st.subheader(
            "🔐 Login to Your Account"
        )

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            if not login_email or not login_password:

                st.error(
                    "Please enter email and password."
                )

            else:

                user = (
                    session.query(User)
                    .filter_by(
                        email=login_email.strip()
                    )
                    .first()
                )

                if user is None:

                    st.error(
                        "Account not found. Please register first."
                    )

                else:

                    try:

                        password_correct = verify_password(
                            login_password,
                            user.password
                        )

                    except Exception:

                        password_correct = False

                    if password_correct:

                        st.session_state.logged_in = True

                        st.session_state.user_id = user.id

                        st.session_state.username = user.username

                        st.success(
                            "Login successful! 🎉"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Incorrect password."
                        )


    # =====================================================
    # REGISTER
    # =====================================================

    with register_tab:

        st.subheader(
            "📝 Create New Account"
        )

        register_username = st.text_input(
            "Username",
            key="register_username"
        )

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            type="primary",
            use_container_width=True
        ):

            if not register_username:

                st.error(
                    "Please enter a username."
                )

            elif not register_email:

                st.error(
                    "Please enter an email."
                )

            elif not register_password:

                st.error(
                    "Please enter a password."
                )

            elif len(register_password) < 6:

                st.error(
                    "Password must contain at least 6 characters."
                )

            elif register_password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                existing_email = (
                    session.query(User)
                    .filter_by(
                        email=register_email.strip()
                    )
                    .first()
                )

                existing_username = (
                    session.query(User)
                    .filter_by(
                        username=register_username.strip()
                    )
                    .first()
                )

                if existing_email:

                    st.error(
                        "An account with this email already exists."
                    )

                elif existing_username:

                    st.error(
                        "Username already exists."
                    )

                else:

                    try:

                        encrypted_password = hash_password(
                            register_password
                        )

                        new_user = User(
                            username=register_username.strip(),
                            email=register_email.strip(),
                            password=encrypted_password
                        )

                        session.add(
                            new_user
                        )

                        session.commit()

                        st.success(
                            "Account created successfully! "
                            "You can now login."
                        )

                    except Exception as e:

                        session.rollback()

                        st.error(
                            f"Registration failed: {e}"
                        )


# =========================================================
# MAIN APPLICATION
# =========================================================

else:

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.title(
        "💰 Smart Expense Tracker"
    )

    st.sidebar.success(
        f"Welcome, {st.session_state.username}! 👋"
    )

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user_id = None

        st.session_state.username = ""

        st.rerun()

    st.sidebar.divider()

    st.sidebar.header(
        "Menu"
    )

    menu = st.sidebar.selectbox(
        "Select an option",
        [
            "Dashboard",
            "Add Expense",
            "Analytics",
            "Budget",
            "Edit Expense",
            "Delete Expense",
            "Export Reports",
            "Smart Insights",
            "🎯 Savings Goals",
            "🤖 AI Financial Advisor"
        ]
    )


    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "Dashboard":

        st.header(
            "📊 Expense Dashboard"
        )

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .all()
        )

        if expenses:

            data = []

            for expense in expenses:

                data.append({
                    "ID": expense.id,
                    "Date": expense.date,
                    "Category": expense.category,
                    "Description": expense.description,
                    "Amount": expense.amount
                })

            df = pd.DataFrame(data)

            total = df["Amount"].sum()

            count = len(df)

            average = df["Amount"].mean()

            highest = df["Amount"].max()

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💰 Total Spent",
                    f"₹{total:,.2f}"
                )

            with col2:

                st.metric(
                    "🧾 Transactions",
                    count
                )

            with col3:

                st.metric(
                    "📊 Average Expense",
                    f"₹{average:,.2f}"
                )

            with col4:

                st.metric(
                    "⬆️ Highest Expense",
                    f"₹{highest:,.2f}"
                )

            st.divider()

            # -------------------------------------------------
            # BUDGET ALERT ON DASHBOARD
            # -------------------------------------------------

            today = date.today()

            budget_record = (
                session.query(Budget)
                .filter_by(
                    user_id=st.session_state.user_id,
                    month=today.month,
                    year=today.year
                )
                .first()
            )

            if budget_record:

                monthly_budget = float(
                    budget_record.amount
                )

                df["Date"] = pd.to_datetime(
                    df["Date"]
                )

                current_month_df = df[
                    (df["Date"].dt.month == today.month)
                    &
                    (df["Date"].dt.year == today.year)
                ]

                monthly_spending = (
                    current_month_df["Amount"].sum()
                )

                if monthly_budget > 0:

                    budget_percentage = (
                        monthly_spending
                        / monthly_budget
                    ) * 100

                    if monthly_spending > monthly_budget:

                        st.error(
                            f"🚨 **Budget Exceeded!** "
                            f"You have spent "
                            f"₹{monthly_spending:,.2f} "
                            f"out of your "
                            f"₹{monthly_budget:,.2f} budget."
                        )

                    elif budget_percentage >= 80:

                        st.warning(
                            f"⚠️ **Budget Alert:** "
                            f"You have used "
                            f"{budget_percentage:.1f}% "
                            f"of your monthly budget."
                        )

                    else:

                        st.success(
                            f"🟢 Budget Status: "
                            f"{budget_percentage:.1f}% used."
                        )

            st.subheader(
                "🧾 Recent Expenses"
            )

            recent_df = (
                df.tail(10)
                .iloc[::-1]
            )

            st.dataframe(
                recent_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No expenses added yet. "
                "Go to Add Expense to get started."
            )


    # =====================================================
    # ADD EXPENSE
    # =====================================================

    elif menu == "Add Expense":

        st.header(
            "➕ Add New Expense"
        )

        expense_date = st.date_input(
            "Date",
            value=date.today()
        )

        category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Shopping",
                "Bills",
                "Education",
                "Entertainment",
                "Health",
                "Other"
            ]
        )

        description = st.text_input(
            "Description"
        )

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=1.0
        )

        if st.button(
            "Add Expense",
            type="primary"
        ):

            if amount <= 0:

                st.error(
                    "Please enter an amount greater than 0."
                )

            else:

                try:

                    new_expense = Expense(
                        date=expense_date,
                        category=category,
                        description=description,
                        amount=float(amount),
                        user_id=st.session_state.user_id
                    )

                    session.add(
                        new_expense
                    )

                    session.commit()

                    st.success(
                        "Expense added successfully! 🎉"
                    )

                except Exception as e:

                    session.rollback()

                    st.error(
                        f"Error adding expense: {e}"
                    )


    # =====================================================
    # ANALYTICS
    # =====================================================

    elif menu == "Analytics":

        st.header(
            "📊 Expense Analytics"
        )

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .all()
        )

        if not expenses:

            st.info(
                "Add some expenses first to see analytics."
            )

        else:

            data = []

            for expense in expenses:

                data.append({
                    "ID": expense.id,
                    "Date": expense.date,
                    "Category": expense.category,
                    "Description": expense.description,
                    "Amount": expense.amount
                })

            df = pd.DataFrame(data)

            df["Date"] = pd.to_datetime(
                df["Date"]
            )

            st.subheader(
                "🔍 Filter Expenses"
            )

            filter_type = st.radio(
                "Choose filter type",
                [
                    "All Expenses",
                    "Select Month",
                    "Custom Date Range"
                ],
                horizontal=True
            )

            filtered_df = df.copy()

            if filter_type == "Select Month":

                months = sorted(
                    df["Date"]
                    .dt
                    .to_period("M")
                    .unique(),
                    reverse=True
                )

                selected_month = st.selectbox(
                    "Select Month",
                    months
                )

                filtered_df = df[
                    df["Date"]
                    .dt
                    .to_period("M")
                    == selected_month
                ]

            elif filter_type == "Custom Date Range":

                min_date = df["Date"].min().date()

                max_date = df["Date"].max().date()

                selected_range = st.date_input(
                    "Select Date Range",
                    value=(
                        min_date,
                        max_date
                    ),
                    min_value=min_date,
                    max_value=max_date
                )

                if len(selected_range) == 2:

                    start_date = pd.Timestamp(
                        selected_range[0]
                    )

                    end_date = pd.Timestamp(
                        selected_range[1]
                    )

                    filtered_df = df[
                        (df["Date"] >= start_date)
                        &
                        (df["Date"] <= end_date)
                    ]

            if filtered_df.empty:

                st.warning(
                    "No expenses found for the selected period."
                )

            else:

                total = filtered_df["Amount"].sum()

                count = len(filtered_df)

                average = filtered_df["Amount"].mean()

                highest = filtered_df["Amount"].max()

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "💰 Total Spending",
                        f"₹{total:,.2f}"
                    )

                with col2:

                    st.metric(
                        "🧾 Transactions",
                        count
                    )

                with col3:

                    st.metric(
                        "📊 Average Expense",
                        f"₹{average:,.2f}"
                    )

                with col4:

                    st.metric(
                        "⬆️ Highest Expense",
                        f"₹{highest:,.2f}"
                    )

                st.divider()

                st.subheader(
                    "📊 Category-wise Spending"
                )

                category_data = (
                    filtered_df
                    .groupby("Category")["Amount"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )

                st.bar_chart(
                    category_data
                )

                st.subheader(
                    "🥧 Spending Distribution"
                )

                fig, ax = plt.subplots()

                ax.pie(
                    category_data,
                    labels=category_data.index,
                    autopct="%1.1f%%",
                    startangle=90
                )

                ax.set_title(
                    "Expenses by Category"
                )

                st.pyplot(fig)

                plt.close(fig)

                st.subheader(
                    "📈 Daily Spending Trend"
                )

                daily_data = (
                    filtered_df
                    .groupby("Date")["Amount"]
                    .sum()
                )

                st.line_chart(
                    daily_data
                )

                highest_category = category_data.idxmax()

                highest_amount = category_data.max()

                st.info(
                    f"💡 Your highest spending category is "
                    f"**{highest_category}** "
                    f"with **₹{highest_amount:,.2f}**."
                )

                st.subheader(
                    "📋 Filtered Expenses"
                )

                display_df = filtered_df.copy()

                display_df["Date"] = (
                    display_df["Date"].dt.date
                )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )


    # =====================================================
    # BUDGET + ALERTS
    # =====================================================

    elif menu == "Budget":

        st.header(
            "💰 Monthly Budget"
        )

        st.write(
            "Set your monthly spending limit and monitor "
            "your financial health."
        )

        today = date.today()

        current_month = today.month
        current_year = today.year

        budget_record = (
            session.query(Budget)
            .filter_by(
                user_id=st.session_state.user_id,
                month=current_month,
                year=current_year
            )
            .first()
        )

        if budget_record:

            current_budget = float(
                budget_record.amount
            )

        else:

            current_budget = 10000.0

        # -------------------------------------------------
        # SET BUDGET
        # -------------------------------------------------

        st.subheader(
            "💰 Set Monthly Budget"
        )

        budget = st.number_input(
            "Monthly Budget",
            min_value=0.0,
            value=current_budget,
            step=500.0
        )

        if st.button(
            "💾 Save Budget",
            type="primary"
        ):

            try:

                if budget_record:

                    budget_record.amount = float(
                        budget
                    )

                else:

                    new_budget = Budget(
                        month=current_month,
                        year=current_year,
                        amount=float(budget),
                        user_id=st.session_state.user_id
                    )

                    session.add(
                        new_budget
                    )

                session.commit()

                st.success(
                    "✅ Monthly budget saved successfully!"
                )

                st.rerun()

            except Exception as e:

                session.rollback()

                st.error(
                    f"Could not save budget: {e}"
                )

        st.divider()

        # -------------------------------------------------
        # GET EXPENSES
        # -------------------------------------------------

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .all()
        )

        monthly_spending = 0.0

        if expenses:

            for expense in expenses:

                if (
                    expense.date.month == current_month
                    and
                    expense.date.year == current_year
                ):

                    monthly_spending += float(
                        expense.amount
                    )

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        remaining = (
            float(budget)
            - monthly_spending
        )

        if budget > 0:

            percentage = (
                monthly_spending
                / float(budget)
            ) * 100

        else:

            percentage = 0

        # -------------------------------------------------
        # METRICS
        # -------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "💰 Monthly Budget",
                f"₹{budget:,.2f}"
            )

        with col2:

            st.metric(
                "💸 Spent This Month",
                f"₹{monthly_spending:,.2f}"
            )

        with col3:

            st.metric(
                "💵 Remaining",
                f"₹{remaining:,.2f}"
            )

        st.divider()

        # -------------------------------------------------
        # PROGRESS
        # -------------------------------------------------

        st.subheader(
            "📊 Budget Usage"
        )

        progress = (
            min(
                monthly_spending / float(budget),
                1.0
            )
            if budget > 0
            else 0
        )

        st.progress(
            progress
        )

        st.write(
            f"**{percentage:.1f}%** of your monthly budget used."
        )

        # -------------------------------------------------
        # ALERTS
        # -------------------------------------------------

        st.subheader(
            "🔔 Budget Alerts"
        )

        if budget <= 0:

            st.warning(
                "⚠️ Please set a monthly budget to activate alerts."
            )

        elif monthly_spending > budget:

            exceeded_amount = (
                monthly_spending - budget
            )

            st.error(
                f"🚨 **Budget Exceeded!**\n\n"
                f"You have exceeded your monthly budget by "
                f"**₹{exceeded_amount:,.2f}**."
            )

            st.write(
                "💡 Try reducing unnecessary spending "
                "for the rest of the month."
            )

        elif percentage >= 90:

            st.error(
                f"🔴 **Critical Alert!**\n\n"
                f"You have used **{percentage:.1f}%** "
                "of your monthly budget."
            )

            st.write(
                f"Only **₹{remaining:,.2f}** remains."
            )

        elif percentage >= 80:

            st.warning(
                f"🟡 **Warning!**\n\n"
                f"You have already used **{percentage:.1f}%** "
                "of your monthly budget."
            )

            st.write(
                f"Only **₹{remaining:,.2f}** remains. "
                "Consider reducing unnecessary expenses."
            )

        elif percentage >= 50:

            st.info(
                f"🔵 You have used **{percentage:.1f}%** "
                "of your monthly budget."
            )

        else:

            st.success(
                f"🟢 Great! You have used only "
                f"**{percentage:.1f}%** of your budget."
            )

        # -------------------------------------------------
        # LARGE EXPENSE ALERT
        # -------------------------------------------------

        if expenses:

            average_expense = (
                sum(
                    float(expense.amount)
                    for expense in expenses
                )
                / len(expenses)
            )

            large_expenses = []

            for expense in expenses:

                if (
                    expense.date.month == current_month
                    and
                    expense.date.year == current_year
                    and
                    float(expense.amount)
                    > average_expense * 2
                ):

                    large_expenses.append(
                        expense
                    )

            if large_expenses:

                st.divider()

                st.subheader(
                    "💸 Large Expense Alert"
                )

                st.warning(
                    "The following expenses are unusually "
                    "high compared with your average expense:"
                )

                for expense in large_expenses:

                    st.write(
                        f"• **₹{expense.amount:,.2f}** — "
                        f"{expense.category} — "
                        f"{expense.description or 'No description'}"
                    )

        # -------------------------------------------------
        # DAILY SPENDING ALERT
        # -------------------------------------------------

        today_spending = 0.0

        for expense in expenses:

            if expense.date == today:

                today_spending += float(
                    expense.amount
                )

        if today_spending > 0 and budget > 0:

            daily_limit = (
                float(budget) / 30
            )

            if today_spending > daily_limit * 1.5:

                st.divider()

                st.warning(
                    f"⚠️ **High Daily Spending**\n\n"
                    f"You spent **₹{today_spending:,.2f}** today. "
                    f"Your approximate daily budget is "
                    f"**₹{daily_limit:,.2f}**."
                )

        # -------------------------------------------------
        # FINANCIAL TIP
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "💡 Financial Tip"
        )

        if percentage >= 90:

            st.write(
                "Try using a **needs vs wants** approach. "
                "Prioritize essential expenses until the "
                "month ends."
            )

        elif percentage >= 80:

            st.write(
                "You are getting close to your budget limit. "
                "Avoid unnecessary purchases for the next few days."
            )

        elif percentage >= 50:

            st.write(
                "You are halfway through your budget. "
                "Continue tracking your expenses carefully."
            )

        else:

            st.write(
                "Your spending is currently under control. "
                "Keep maintaining this habit! 🎉"
            )


    # =====================================================
    # EDIT EXPENSE
    # =====================================================

    elif menu == "Edit Expense":

        st.header(
            "✏️ Edit Expense"
        )

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .order_by(
                Expense.id.desc()
            )
            .all()
        )

        if not expenses:

            st.info(
                "No expenses available to edit."
            )

        else:

            expense_ids = [
                expense.id
                for expense in expenses
            ]

            selected_id = st.selectbox(
                "Select Expense ID",
                expense_ids
            )

            selected_expense = session.get(
                Expense,
                selected_id
            )

            if selected_expense:

                edited_date = st.date_input(
                    "Date",
                    value=selected_expense.date
                )

                categories = [
                    "Food",
                    "Transport",
                    "Shopping",
                    "Bills",
                    "Education",
                    "Entertainment",
                    "Health",
                    "Other"
                ]

                category_index = (
                    categories.index(
                        selected_expense.category
                    )
                    if selected_expense.category in categories
                    else 0
                )

                edited_category = st.selectbox(
                    "Category",
                    categories,
                    index=category_index
                )

                edited_description = st.text_input(
                    "Description",
                    value=selected_expense.description or ""
                )

                edited_amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(
                        selected_expense.amount
                    ),
                    step=1.0
                )

                if st.button(
                    "💾 Save Changes",
                    type="primary"
                ):

                    if edited_amount <= 0:

                        st.error(
                            "Amount must be greater than 0."
                        )

                    else:

                        try:

                            selected_expense.date = edited_date

                            selected_expense.category = edited_category

                            selected_expense.description = edited_description

                            selected_expense.amount = float(
                                edited_amount
                            )

                            session.commit()

                            st.success(
                                "Expense updated successfully!"
                            )

                            st.rerun()

                        except Exception as e:

                            session.rollback()

                            st.error(
                                f"Update failed: {e}"
                            )


    # =====================================================
    # DELETE EXPENSE
    # =====================================================

    elif menu == "Delete Expense":

        st.header(
            "🗑️ Delete Expense"
        )

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .order_by(
                Expense.id.desc()
            )
            .all()
        )

        if not expenses:

            st.info(
                "No expenses available to delete."
            )

        else:

            expense_ids = [
                expense.id
                for expense in expenses
            ]

            selected_id = st.selectbox(
                "Select Expense ID",
                expense_ids
            )

            selected_expense = session.get(
                Expense,
                selected_id
            )

            if selected_expense:

                st.write(
                    f"**Date:** {selected_expense.date}"
                )

                st.write(
                    f"**Category:** {selected_expense.category}"
                )

                st.write(
                    f"**Description:** "
                    f"{selected_expense.description or 'No description'}"
                )

                st.write(
                    f"**Amount:** ₹{selected_expense.amount:,.2f}"
                )

                st.warning(
                    "⚠️ This expense will be permanently deleted."
                )

                confirm_delete = st.checkbox(
                    "I confirm that I want to delete this expense."
                )

                if st.button(
                    "🗑️ Delete Expense",
                    type="primary"
                ):

                    if not confirm_delete:

                        st.error(
                            "Please confirm deletion first."
                        )

                    else:

                        try:

                            session.delete(
                                selected_expense
                            )

                            session.commit()

                            st.success(
                                "Expense deleted successfully!"
                            )

                            st.rerun()

                        except Exception as e:

                            session.rollback()

                            st.error(
                                f"Delete failed: {e}"
                            )


    # =====================================================
    # EXPORT REPORTS
    # =====================================================

    elif menu == "Export Reports":

        st.header(
            "📥 Export Reports"
        )

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .order_by(
                Expense.id.desc()
            )
            .all()
        )

        if not expenses:

            st.info(
                "No expenses available to export."
            )

        else:

            data = []

            for expense in expenses:

                data.append({
                    "ID": expense.id,
                    "Date": expense.date,
                    "Category": expense.category,
                    "Description": expense.description,
                    "Amount": expense.amount
                })

            df = pd.DataFrame(data)

            total = df["Amount"].sum()

            st.metric(
                "💰 Total Amount",
                f"₹{total:,.2f}"
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            csv_data = df.to_csv(
                index=False
            )

            st.download_button(
                "📄 Download CSV",
                data=csv_data,
                file_name="expense_report.csv",
                mime="text/csv",
                type="primary"
            )

            try:

                excel_buffer = io.BytesIO()

                with pd.ExcelWriter(
                    excel_buffer,
                    engine="openpyxl"
                ) as writer:

                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Expenses"
                    )

                st.download_button(
                    "📊 Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name="expense_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception:

                st.warning(
                    "Excel export requires openpyxl."
                )


    # =====================================================
    # SMART INSIGHTS
    # =====================================================

    elif menu == "Smart Insights":

        st.header(
            "🤖 Smart Expense Insights"
        )

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .order_by(
                Expense.date
            )
            .all()
        )

        if not expenses:

            st.info(
                "Add some expenses first to generate insights."
            )

        else:

            data = []

            for expense in expenses:

                data.append({
                    "Date": expense.date,
                    "Category": expense.category,
                    "Amount": float(expense.amount)
                })

            df = pd.DataFrame(data)

            df["Date"] = pd.to_datetime(
                df["Date"]
            )

            total_spending = df["Amount"].sum()

            transaction_count = len(df)

            average_transaction = df["Amount"].mean()

            category_totals = (
                df.groupby("Category")["Amount"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            highest_category = category_totals.idxmax()

            highest_category_amount = category_totals.max()

            daily_spending = (
                df.groupby("Date")["Amount"]
                .sum()
                .sort_index()
            )

            average_daily_spending = (
                daily_spending.mean()
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💰 Total Spending",
                    f"₹{total_spending:,.2f}"
                )

            with col2:

                st.metric(
                    "📊 Average Transaction",
                    f"₹{average_transaction:,.2f}"
                )

            with col3:

                st.metric(
                    "📅 Daily Average",
                    f"₹{average_daily_spending:,.2f}"
                )

            with col4:

                st.metric(
                    "🧾 Transactions",
                    transaction_count
                )

            st.divider()

            st.subheader(
                "💡 Spending Insights"
            )

            st.info(
                f"🏆 Your highest spending category is "
                f"**{highest_category}** "
                f"with **₹{highest_category_amount:,.2f}**."
            )

            st.subheader(
                "📈 Spending Trend"
            )

            st.line_chart(
                daily_spending
            )

            st.subheader(
                "📊 Category Analysis"
            )

            st.bar_chart(
                category_totals
            )

            if len(category_totals) > 0:

                highest_percentage = (
                    highest_category_amount
                    / total_spending
                ) * 100

                if highest_percentage >= 40:

                    st.warning(
                        f"⚠️ {highest_category} represents "
                        f"{highest_percentage:.1f}% of your spending. "
                        "Consider reducing this category."
                    )

                else:

                    st.success(
                        "✅ Your spending is reasonably distributed."
                    )

            monthly_spending = (
                df.assign(
                    Month=(
                        df["Date"]
                        .dt
                        .to_period("M")
                        .astype(str)
                    )
                )
                .groupby("Month")["Amount"]
                .sum()
            )

            st.subheader(
                "📅 Monthly Spending"
            )

            st.bar_chart(
                monthly_spending
            )

            if len(monthly_spending) >= 2:

                current_month = monthly_spending.iloc[-1]

                previous_month = monthly_spending.iloc[-2]

                if previous_month > 0:

                    change = (
                        (
                            current_month
                            - previous_month
                        )
                        / previous_month
                    ) * 100

                    if change > 0:

                        st.warning(
                            f"📈 Spending increased by "
                            f"**{change:.1f}%** compared with "
                            "the previous month."
                        )

                    elif change < 0:

                        st.success(
                            f"📉 Spending decreased by "
                            f"**{abs(change):.1f}%** compared with "
                            "the previous month."
                        )


    # =====================================================
    # SAVINGS GOALS
    # =====================================================

    elif menu == "🎯 Savings Goals":

        st.header(
            "🎯 Savings Goals"
        )

        st.write(
            "Create financial goals and track your savings progress."
        )

        st.subheader(
            "➕ Create New Goal"
        )

        goal_name = st.text_input(
            "Goal Name",
            placeholder="Example: New Laptop"
        )

        target_amount = st.number_input(
            "Target Amount",
            min_value=1.0,
            step=500.0
        )

        target_date = st.date_input(
            "Target Date",
            min_value=date.today()
        )

        if st.button(
            "🎯 Create Goal",
            type="primary"
        ):

            if not goal_name.strip():

                st.error(
                    "Please enter a goal name."
                )

            else:

                try:

                    new_goal = SavingsGoal(
                        name=goal_name.strip(),
                        target_amount=float(target_amount),
                        saved_amount=0.0,
                        target_date=target_date,
                        user_id=st.session_state.user_id
                    )

                    session.add(
                        new_goal
                    )

                    session.commit()

                    st.success(
                        "🎉 Savings goal created successfully!"
                    )

                    st.rerun()

                except Exception as e:

                    session.rollback()

                    st.error(
                        f"Could not create goal: {e}"
                    )

        st.divider()

        goals = (
            session.query(SavingsGoal)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .order_by(
                SavingsGoal.id.desc()
            )
            .all()
        )

        if not goals:

            st.info(
                "You haven't created any savings goals yet."
            )

        else:

            st.subheader(
                "💰 My Savings Goals"
            )

            for goal in goals:

                st.markdown("---")

                st.subheader(
                    f"🎯 {goal.name}"
                )

                target = float(
                    goal.target_amount
                )

                saved = float(
                    goal.saved_amount or 0
                )

                remaining = max(
                    target - saved,
                    0
                )

                percentage = (
                    saved / target
                ) * 100 if target > 0 else 0

                progress = min(
                    saved / target,
                    1.0
                ) if target > 0 else 0

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "🎯 Target",
                        f"₹{target:,.2f}"
                    )

                with col2:

                    st.metric(
                        "💰 Saved",
                        f"₹{saved:,.2f}"
                    )

                with col3:

                    st.metric(
                        "💵 Remaining",
                        f"₹{remaining:,.2f}"
                    )

                st.write(
                    f"**Progress: {percentage:.1f}%**"
                )

                st.progress(
                    progress
                )

                st.write(
                    f"📅 Target Date: **{goal.target_date}**"
                )

                with st.expander(
                    "💵 Add Savings"
                ):

                    saving_amount = st.number_input(
                        "Amount to Add",
                        min_value=1.0,
                        step=100.0,
                        key=f"saving_{goal.id}"
                    )

                    if st.button(
                        "➕ Add Money",
                        key=f"add_{goal.id}"
                    ):

                        if saved >= target:

                            st.info(
                                "🎉 This goal is already completed!"
                            )

                        elif saving_amount > remaining:

                            st.error(
                                f"You only need ₹{remaining:,.2f} "
                                "to complete this goal."
                            )

                        else:

                            try:

                                goal.saved_amount = (
                                    saved + saving_amount
                                )

                                session.commit()

                                st.success(
                                    "💰 Savings added successfully!"
                                )

                                st.rerun()

                            except Exception as e:

                                session.rollback()

                                st.error(
                                    f"Could not add savings: {e}"
                                )

                if saved >= target:

                    st.success(
                        "🏆 Goal Completed! Congratulations! 🎉"
                    )

                else:

                    days_remaining = (
                        goal.target_date
                        - date.today()
                    ).days

                    if days_remaining < 0:

                        st.warning(
                            "⚠️ Target date has passed."
                        )

                    elif days_remaining == 0:

                        st.warning(
                            "⏰ Your target date is today!"
                        )

                    else:

                        st.info(
                            f"📅 {days_remaining} days remaining"
                        )

                        monthly_required = (
                            remaining
                            / max(
                                days_remaining / 30,
                                1
                            )
                        )

                        st.write(
                            f"💡 Try saving approximately "
                            f"**₹{monthly_required:,.2f} per month** "
                            "to reach your goal on time."
                        )

                with st.expander(
                    "🗑️ Delete Goal"
                ):

                    confirm_goal_delete = st.checkbox(
                        "I want to permanently delete this goal.",
                        key=f"confirm_delete_{goal.id}"
                    )

                    if st.button(
                        "🗑️ Delete Goal",
                        key=f"delete_goal_{goal.id}"
                    ):

                        if not confirm_goal_delete:

                            st.error(
                                "Please confirm deletion first."
                            )

                        else:

                            try:

                                session.delete(
                                    goal
                                )

                                session.commit()

                                st.success(
                                    "Goal deleted successfully."
                                )

                                st.rerun()

                            except Exception as e:

                                session.rollback()

                                st.error(
                                    f"Could not delete goal: {e}"
                                )


    # =====================================================
    # AI FINANCIAL ADVISOR
    # =====================================================

    elif menu == "🤖 AI Financial Advisor":

        st.header(
            "🤖 AI Financial Advisor"
        )

        st.write(
            "Your personal financial assistant analyzes "
            "your spending, budget, and savings goals."
        )

        expenses = (
            session.query(Expense)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .all()
        )

        goals = (
            session.query(SavingsGoal)
            .filter_by(
                user_id=st.session_state.user_id
            )
            .all()
        )

        if not expenses:

            st.info(
                "💡 Add some expenses first so the advisor "
                "can analyze your financial behavior."
            )

        else:

            data = []

            for expense in expenses:

                data.append({
                    "Date": expense.date,
                    "Category": expense.category,
                    "Amount": float(expense.amount)
                })

            df = pd.DataFrame(data)

            df["Date"] = pd.to_datetime(
                df["Date"]
            )

            total_spending = (
                df["Amount"].sum()
            )

            transaction_count = len(df)

            average_expense = (
                df["Amount"].mean()
            )

            category_totals = (
                df.groupby("Category")["Amount"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            highest_category = (
                category_totals.idxmax()
            )

            highest_category_amount = (
                category_totals.max()
            )

            highest_category_percentage = (
                highest_category_amount
                / total_spending
            ) * 100

            today = date.today()

            current_month_df = df[
                (df["Date"].dt.month == today.month)
                &
                (df["Date"].dt.year == today.year)
            ]

            current_month_spending = (
                current_month_df["Amount"].sum()
            )

            # -------------------------------------------------
            # FINANCIAL SUMMARY
            # -------------------------------------------------

            st.subheader(
                "📊 Your Financial Summary"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💰 Total Spending",
                    f"₹{total_spending:,.2f}"
                )

            with col2:

                st.metric(
                    "📅 This Month",
                    f"₹{current_month_spending:,.2f}"
                )

            with col3:

                st.metric(
                    "📊 Average Expense",
                    f"₹{average_expense:,.2f}"
                )

            with col4:

                st.metric(
                    "🧾 Transactions",
                    transaction_count
                )

            st.divider()

            # -------------------------------------------------
            # FINANCIAL HEALTH
            # -------------------------------------------------

            st.subheader(
                "❤️ Financial Health"
            )

            health_score = 100

            if highest_category_percentage > 50:

                health_score -= 25

            elif highest_category_percentage > 40:

                health_score -= 15

            elif highest_category_percentage > 30:

                health_score -= 5

            if goals:

                completed_goals = sum(
                    1
                    for goal in goals
                    if goal.saved_amount >= goal.target_amount
                )

                if completed_goals > 0:

                    health_score += 5

            health_score = max(
                0,
                min(
                    health_score,
                    100
                )
            )

            if health_score >= 80:

                st.success(
                    f"🟢 Excellent financial health — "
                    f"Score: **{health_score}/100**"
                )

            elif health_score >= 60:

                st.warning(
                    f"🟡 Good, but there is room for improvement — "
                    f"Score: **{health_score}/100**"
                )

            else:

                st.error(
                    f"🔴 Your spending needs attention — "
                    f"Score: **{health_score}/100**"
                )

            st.divider()

            # -------------------------------------------------
            # PERSONALIZED ADVICE
            # -------------------------------------------------

            st.subheader(
                "💡 Personalized Financial Advice"
            )

            if highest_category_percentage >= 40:

                st.warning(
                    f"⚠️ **Reduce {highest_category} spending**\n\n"
                    f"{highest_category} represents "
                    f"**{highest_category_percentage:.1f}%** "
                    f"of your total expenses. Try setting a "
                    f"weekly limit for this category."
                )

            else:

                st.success(
                    "✅ Your spending is reasonably distributed "
                    "across categories."
                )

            if average_expense > 1000:

                st.info(
                    f"💡 Your average transaction is "
                    f"**₹{average_expense:,.2f}**. "
                    "Consider reviewing large purchases before "
                    "making them."
                )

            # -------------------------------------------------
            # SAVINGS ADVICE
            # -------------------------------------------------

            if not goals:

                st.info(
                    "🎯 You don't have a savings goal yet. "
                    "Create one in **🎯 Savings Goals** to "
                    "start building a savings habit."
                )

                savings_percentage = 0

            else:

                total_target = sum(
                    float(goal.target_amount)
                    for goal in goals
                )

                total_saved = sum(
                    float(goal.saved_amount or 0)
                    for goal in goals
                )

                total_remaining = max(
                    total_target - total_saved,
                    0
                )

                savings_percentage = (
                    total_saved / total_target
                ) * 100 if total_target > 0 else 0

                st.info(
                    f"🎯 You have saved "
                    f"**₹{total_saved:,.2f}** toward your goals "
                    f"out of **₹{total_target:,.2f}** "
                    f"({savings_percentage:.1f}%)."
                )

                if savings_percentage < 25:

                    st.warning(
                        "💡 Your savings progress is still below "
                        "25%. Consider saving a fixed amount "
                        "every week or month."
                    )

                elif savings_percentage >= 75:

                    st.success(
                        "🏆 Excellent savings progress! "
                        "You are close to completing your goals."
                    )

            # -------------------------------------------------
            # RECOMMENDED BUDGET
            # -------------------------------------------------

            st.subheader(
                "💰 Recommended Budget"
            )

            recommended_budget = (
                current_month_spending * 1.10
                if current_month_spending > 0
                else 10000
            )

            st.write(
                f"Based on your current spending, a reasonable "
                f"starting monthly budget would be approximately "
                f"**₹{recommended_budget:,.0f}**."
            )

            st.caption(
                "This is an estimate based on your recorded "
                "expenses, not professional financial advice."
            )

            # -------------------------------------------------
            # TOP CATEGORIES
            # -------------------------------------------------

            st.subheader(
                "🏆 Top Spending Categories"
            )

            top_categories = (
                category_totals
                .head(3)
            )

            for category_name, amount in top_categories.items():

                category_percentage = (
                    amount
                    / total_spending
                ) * 100

                st.write(
                    f"**{category_name}** — "
                    f"₹{amount:,.2f} "
                    f"({category_percentage:.1f}%)"
                )

            st.bar_chart(
                top_categories
            )

            # -------------------------------------------------
            # RECOMMENDATIONS
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "🧠 Advisor Recommendations"
            )

            recommendations = []

            if highest_category_percentage >= 40:

                recommendations.append(
                    f"Reduce your {highest_category} spending."
                )

            if average_expense > 1000:

                recommendations.append(
                    "Review high-value purchases before spending."
                )

            if not goals:

                recommendations.append(
                    "Create a savings goal and contribute regularly."
                )

            elif savings_percentage < 25:

                recommendations.append(
                    "Increase your savings contribution."
                )

            recommendations.append(
                "Review your expenses at the end of every week."
            )

            recommendations.append(
                "Keep tracking every expense for more accurate insights."
            )

            for index, recommendation in enumerate(
                recommendations,
                start=1
            ):

                st.write(
                    f"**{index}.** {recommendation}"
                )

            st.success(
                "🎯 Keep tracking your expenses consistently. "
                "Small improvements can make a big difference over time!"
            )
