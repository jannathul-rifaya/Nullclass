import matplotlib.pyplot as plt

# Sample data
price = [100, 200, 300, 400, 500, 600, 700, 800]
discount = [5, 10, 8, 15, 12, 18, 20, 25]

# Create scatter plot
plt.scatter(price, discount)

# Labels and title
plt.xlabel("Price")
plt.ylabel("Discount (%)")
plt.title("Discount vs Price Range")

# Show plot
plt.show()
