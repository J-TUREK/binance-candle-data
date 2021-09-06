# binance-candle-data

A small utility class used for fetching large amounts of historic candlestick data from the Binance API.

### Setup:

#### Requirements:
```
import binance
import pandas as pd
import math
import pytz
import time
from datetime import datetime, timedelta

# Binance Api keys:
class Secret:
    API_KEY = "your_api_key"
    SECRET_KEY = "your_secret_key"
```

### Functionality:

Calculate the number of API calls required to generate the required data:
```
LIMIT = 500 # The Binance API request limit per call is 500

number_of_datapoints = BinanceUtils.get_number_of_candles_between_datetimes(interval, start_datetime, end_datetime)

number_of_calls = math.ceil(number_of_datapoints / LIMIT)

print("Shit, that's a lot of calls")
```
Generate a pandas DataFrame and save the result as a csv using pandas built-in method
```
# Example case:

first_datetime = datetime(2018, 1, 1, 0, 0)
last_datetime = datetime.utcnow()
interval = "4h"
symbol = "BTCUSDT"

x = get_candle_data_between_datetimes(symbol, interval, first_datetime, last_datetime)

>>> Expected: 8070 datapoints required to fill date range.
>>> Requires 17 API calls to complete the requirement.
>>> Request should take approximately 21.25s

x.to_csv(f"{symbol}{interval}{str(first_datetime)}{str(last_datetime)}")
```
