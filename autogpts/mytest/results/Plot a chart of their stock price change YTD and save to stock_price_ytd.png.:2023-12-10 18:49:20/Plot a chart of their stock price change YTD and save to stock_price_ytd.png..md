---------------------------
Question: Plot a chart of their stock price change YTD and save to stock_price_ytd.png.
Answer:
Step 1: Import necessary libraries and retrieve stock data.

```python
# Import the necessary libraries
import matplotlib.pyplot as plt
import pandas as pd

# Retrieve the stock data
stock_data = pd.read_csv('stock_data.csv')
```
In this step, we start by importing the required libraries, which in this case are `matplotlib.pyplot` for plotting the chart, and `pandas` for data manipulation. Then, we read the stock data from the CSV file using the `read_csv()` function and store it in the variable `stock_data`.
---------------------------
