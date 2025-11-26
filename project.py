import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load dataset
df = pd.read_csv("restaurant_orders_350rows_realistic.csv")

# Step 2: Basic info
print("First 5 rows of data:\n", df.head())
print("\nColumns in dataset:", df.columns)
print("\nShape of dataset:", df.shape)

# Step 3: Analysis - Most Ordered Items
item_counts = df.groupby("ItemName")["Quantity"].sum().sort_values(ascending=False)

# Step 4: Visualization - Bar Chart
plt.figure(figsize=(10,6))
plt.bar(item_counts.index[:10], item_counts.values[:10], color="skyblue")  # top 10 items
plt.title("Top 10 Most Ordered Items")
plt.xlabel("Menu Items")
plt.ylabel("Total Quantity Ordered")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Ask user to enter a Customer ID
cust_id = input("\nEnter Customer ID to search: ")

# Check if entered ID exists in dataset
if cust_id in df["CustomerID"].astype(str).values:
    print("\n✅ Customer Found! Showing their orders:\n")
    print(df[df["CustomerID"].astype(str) == cust_id][["OrderID", "ItemName", "Quantity", "TotalPrice", "OrderTime"]])
else:
    print("\n❌ This Customer ID does not exist in the database.")
