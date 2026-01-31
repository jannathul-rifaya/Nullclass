import pandas as pd

# Sample data
data = {
    "Product Name": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    "Price": [100, 200, 150, 120, 180],
    "Discount": [0.6, 0.05, 0.3, 0.55, 0.08],
    "Rating": [4, 2, 3, 4.5, 1.8]
}

df = pd.DataFrame(data)
print(df)

# Save to Excel (no styling)
df.to_excel("products_no_formatting.xlsx", index=False)

print("Excel file saved without formatting as 'products_no_formatting.xlsx'")
