# interface.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# PAGE SETUP 
st.set_page_config(page_title="Restaurant Analytics Dashboard", page_icon="🍽️", layout="wide")

#  LOAD DATA 
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\HP\OneDrive\Desktop\Project ADS\REST ORDER ANALYSIS\restaurant_orders_350rows_realistic.csv")
    df["OrderTime"] = pd.to_datetime(df["OrderTime"], dayfirst=True, errors="coerce")

    # clean customer id
    if "CustomerID" in df.columns:
        df["CustomerID"] = df["CustomerID"].astype(str).str.strip()
    return df

df = load_data()

#  WELCOME PAGE 
if "customer_name" not in st.session_state:
    st.session_state.customer_name = None

if st.session_state.customer_name is None:
    st.title("👋 Welcome to Restaurant Analytics Dashboard")
    st.write("This dashboard helps you explore restaurant order insights like **most ordered items** and **peak order hours**.")

    name_input = st.text_input("Enter your name to continue:")
    if st.button("Proceed"):
        if name_input.strip():
            st.session_state.customer_name = name_input.strip()
            st.success(f"Welcome, {st.session_state.customer_name}! 🎉")
            st.rerun()
        else:
            st.warning("Please enter a valid name to continue.")

else:
    # 🔓 Logout (styled & at top)
    st.sidebar.markdown("### 🔓 Account")
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.customer_name = None
        st.rerun()

    st.sidebar.markdown("---")

    # SIDEBAR MENU
    st.sidebar.header("📌 Navigation")
    page = st.sidebar.selectbox(
        "Select View",
        [
            "🔍 Search Customer Orders",
            "⭐ Most Ordered Items",
            "⏰ Peak Order Hours",
            "📦 Order Channel Analysis",
        ]
    )

    # Global date filter
    min_date = df["OrderTime"].min().date()
    max_date = df["OrderTime"].max().date()
    date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[(df["OrderTime"].dt.date >= start_date) & (df["OrderTime"].dt.date <= end_date)]
    else:
        df_filtered = df.copy()

    # PAGE 1: CUSTOMER SEARCH
    if page == "🔍 Search Customer Orders":
        st.title(f"🔍 Search Orders by Customer ID, {st.session_state.customer_name}")

        if "CustomerID" not in df.columns:
            st.error("Column 'CustomerID' not found in dataset.")
        else:
            customer_ids = sorted(df["CustomerID"].dropna().unique().tolist())
            selected_id = st.selectbox("Select Customer ID", customer_ids)

            result = df_filtered[df_filtered["CustomerID"] == selected_id]

            if result.empty:
                st.warning(f"No records found for Customer ID: {selected_id}")
            else:
                st.success(f"Showing orders for Customer ID: {selected_id}")
                st.dataframe(result)

    # PAGE 2: MOST ORDERED ITEMS
    elif page == "⭐ Most Ordered Items":
        st.title(f"⭐ Top Ordered Items, {st.session_state.customer_name}")

        if "Quantity" not in df.columns or "ItemName" not in df.columns:
            st.error("Required columns missing (ItemName / Quantity).")
        else:
            # ✅ CATEGORY FILTER (this is what was missing)
            if "Category" in df_filtered.columns:
                categories = ["All"] + sorted(df_filtered["Category"].dropna().unique().tolist())
                selected_cat = st.selectbox("Filter by Food Category", categories)

                if selected_cat == "All":
                    df_items = df_filtered.copy()
                else:
                    df_items = df_filtered[df_filtered["Category"] == selected_cat]
            else:
                # if Category column somehow missing, fall back to all data
                df_items = df_filtered.copy()

            # same logic, but now uses df_items (filtered by category)
            item_counts = df_items.groupby("ItemName")["Quantity"].sum().sort_values(ascending=False)

            if item_counts.empty:
                st.warning("No items found for this category and date range.")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
                item_counts.head(10).plot(kind="bar", ax=ax)
                ax.set_ylabel("Total Quantity Ordered")
                ax.set_title("Top 10 Most Ordered Items")
                plt.xticks(rotation=45)
                st.pyplot(fig)

    # PAGE 3: PEAK ORDER HOURS
    elif page == "⏰ Peak Order Hours":
        st.title(f"⏰ Peak Order Hours, {st.session_state.customer_name}")

        if len(date_range) != 2:
            st.warning("Please select a valid date range to continue.")
        else:
            df_peak = df_filtered.copy()
            df_peak["Hour"] = df_peak["OrderTime"].dt.hour
            peak_counts = df_peak.groupby("Hour")["OrderID"].count()

            if peak_counts.empty:
                st.warning("No data found for selected date range.")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
                peak_counts.plot(kind="line", marker="o", ax=ax)
                ax.set_xlabel("Hour of Day")
                ax.set_ylabel("Number of Orders")
                ax.set_title("Peak Order Times (Hourly)")
                st.pyplot(fig)

    # PAGE 4: ORDER CHANNEL ANALYSIS
    elif page == "📦 Order Channel Analysis":
        st.title(f"📦 Order Channel Analysis, {st.session_state.customer_name}")

        if "OrderChannel" not in df.columns:
            st.error("Column 'OrderChannel' not found in dataset.")
        else:
            channel_counts = df_filtered["OrderChannel"].value_counts()

            if channel_counts.empty:
                st.warning("No data available for selected date range.")
            else:
                st.subheader("Orders by Channel")

                fig, ax = plt.subplots(figsize=(8, 5))
                channel_counts.plot(kind="bar", ax=ax)
                ax.set_ylabel("Number of Orders")
                ax.set_title("Orders by Channel (Online / Dine-in / Takeaway)")
                plt.xticks(rotation=0)
                st.pyplot(fig)

                st.write("Channel-wise Order Summary:")
                st.dataframe(
                    channel_counts.reset_index().rename(
                        columns={"index": "Channel", "OrderChannel": "Total Orders"}
                    )
                )
