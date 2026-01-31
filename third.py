import matplotlib.pyplot as plt

# Sample data
subcategory = ["Tablet", "Kettle", "Printer", "Mouse", "Toys"]
avg_price = [25000, 1500, 5000, 600, 800]
avg_rating = [3.8, 4.2, 3.5, 4.6, 4.0]

# Create figure and primary axis
fig, ax1 = plt.subplots()

# Bar chart for Average Price
ax1.bar(subcategory, avg_price)
ax1.set_xlabel("Subcategory")
ax1.set_ylabel("Average Price")

# Secondary axis for Average Rating
ax2 = ax1.twinx()
ax2.plot(subcategory, avg_rating, marker='o')
ax2.set_ylabel("Average Rating")

# Title
plt.title("Average Price vs Average Rating per Subcategory")

plt.show()