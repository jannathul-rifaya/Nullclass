import pandas as pd

# Sample dataset
data = {
    "Discount": [5, 10, 20, 30, 40, 50, 60],
    "Rating": [4.2, 4.1, 4.0, 3.9, 4.0, 3.8, 3.9]
}

df = pd.DataFrame(data)
print(df)
# Calculate correlation
correlation = df["Discount"].corr(df["Rating"])
print("Correlation between Discount and Rating:", correlation)