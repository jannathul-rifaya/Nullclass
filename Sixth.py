# KPI values
avg_price = 950
avg_discount = 40
avg_rating = 3.8
# Display KPIs
print("Average Price: ", avg_price)
print("Average Discount:", avg_discount, "%")
print("Average Rating:", avg_rating)
# Simple business logic check
if avg_discount > 30 and avg_rating < 4:
    print("\nInsight: High discounts are not translating into high customer satisfaction.")