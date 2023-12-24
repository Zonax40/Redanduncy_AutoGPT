---------------------------
Question: Plot a chart of their stock price change YTD and save to stock_price_ytd.png.
Answer:
Step 1: Import necessary libraries and data

In the first step, we need to import the necessary libraries to carry out the task. We will be using the pandas library to manipulate the data and the matplotlib library to plot the chart. Additionally, we need to load the stock price data from a CSV file.

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load the stock price data from a CSV file
df = pd.read_csv('stock_data.csv')
```

Step 2: Data preprocessing

Next, we need to preprocess the data to extract the year-to-date (YTD) stock price change. To do this, we will filter the data for the current year and calculate the percentage change in the stock price.

```python
# Filter the data for the current year
current_year = pd.Timestamp.now().year
df = df[df['Date'].dt.year == current_year]

# Calculate the percentage change in stock price
df['Price Change YTD'] = df['Close'].pct_change() * 100
```

Step 3: Plotting and saving the chart

Now, we can plot the chart of the stock price change YTD using the matplotlib library. We will set the x-axis as the dates and the y-axis as the percentage change in stock price. Finally, we will save the chart as a PNG file named "stock_price_ytd.png".

```python
# Plot the chart
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Price Change YTD'])
plt.xlabel('Date')
plt.ylabel('Percentage Change')
plt.title('Stock Price Change YTD')
plt.grid()

# Save the chart as a PNG file
plt.savefig('stock_price_ytd.png')
```

And that's it! You have successfully plotted a chart of the stock price change YTD and saved it as "stock_price_ytd.png".
---------------------------
