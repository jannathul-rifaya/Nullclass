import pandas as pd
import matplotlib.pyplot as plt

# Sample dataset
data = {
    "Scraping_Date": pd.date_range("2024-01-01", periods=7, freq="D"),
    "Discount": [10, 15, 20, 18, 25, 22, 30]
}

df = pd.DataFrame(data)
# Group by date to calculate average discount
avg_discount = df.groupby("Scraping_Date")["Discount"].mean()

# Line chart
plt.plot(avg_discount.index, avg_discount.values, marker='o')
plt.xlabel("Scraping Date")
plt.ylabel("Average Discount (%)")
plt.title("Average Discount Trend Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()