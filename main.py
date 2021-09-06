import binance
import pandas as pd
import math
import pytz
import time
from secret import Secret
from datetime import datetime, timedelta

class BinanceUtils:

    @staticmethod
    def get_binance_client() -> binance.Client:
        
        return binance.Client(
            Secret.API_KEY, # Your API key here
            Secret.SECRET_KEY # Your secret key here
            )

    @staticmethod
    def is_valid_interval(interval) -> bool:

        client = BinanceUtils.get_binance_client()
        
        SUPPORTED_INTERVALS = [
            client.KLINE_INTERVAL_1MINUTE,
            client.KLINE_INTERVAL_5MINUTE,
            client.KLINE_INTERVAL_15MINUTE,
            client.KLINE_INTERVAL_30MINUTE,
            client.KLINE_INTERVAL_1HOUR,
            client.KLINE_INTERVAL_4HOUR,
            client.KLINE_INTERVAL_1DAY,
            client.KLINE_INTERVAL_1WEEK,
            client.KLINE_INTERVAL_1MONTH
        ]
        
        if interval in SUPPORTED_INTERVALS:
            return True
        return False

    @staticmethod
    def convert_interval_to_timedelta(interval) -> timedelta:
    
        interval_converter = {
            "1m": timedelta(minutes=1),
            "5m": timedelta(minutes=5),
            "15m": timedelta(minutes=15),
            "30m": timedelta(minutes=30),
            "1h": timedelta(hours=1),
            "4h": timedelta(hours=4),
            "1d": timedelta(days=1),
            "1w": timedelta(weeks=1),
            "1M": timedelta(weeks=4)
        }
        
        return interval_converter[interval]

    @staticmethod
    def get_number_of_candles_between_datetimes(interval, start_datetime, end_datetime):
    
        if BinanceUtils.is_valid_interval(interval) and start_datetime < end_datetime:
            
            interval_period = BinanceUtils.convert_interval_to_timedelta(interval)
            
            datetime_diff = end_datetime - start_datetime
            
            return datetime_diff / interval_period
            
        else:
            raise Exception("Invalid interval")

    @staticmethod
    def convert_timestamp_to_utc_string(timestamp):
        return datetime.utcfromtimestamp(timestamp / 1000)


def get_candle_data_between_datetimes(symbol: str, interval: str, first_datetime: datetime, last_datetime: datetime):
    
    cols = ["timestamp","open","high","low","close","volume","Close time",
        "Quote asset volume","Number of trades","Taker buy base asset volume",
       "Taker buy quote asset volume", "..."]
    limit = 500
    client = BinanceUtils.get_binance_client()
    
    number_of_expected_datapoints = math.ceil(BinanceUtils.get_number_of_candles_between_datetimes(interval, first_datetime, last_datetime))
    api_calls = math.ceil(number_of_expected_datapoints / 500)
    
    print(f"Expected: {number_of_expected_datapoints} datapoints required to fill date range.")
    print(f"Requires {api_calls} API calls to complete the requirement.")
    print(f"Request should take approximately {api_calls * 1.25}s")
    
    if BinanceUtils.is_valid_interval(interval) and first_datetime < last_datetime:
        
        if number_of_expected_datapoints < limit:
            limit = number_of_expected_datapoints

        data = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        
        df = pd.DataFrame(data, columns=cols)
        
        oldest_candle_timestamp = data[0][0] # Keep track of the oldest candle received
        
        while len(df) < number_of_expected_datapoints:
            
            # The oldest timestamp becomes the LAST of the next requested datetime interval
            next_last_datetime = BinanceUtils.convert_timestamp_to_utc_string(oldest_candle_timestamp)
            next_first_datetime = next_last_datetime - (BinanceUtils.convert_interval_to_timedelta(interval) * 500)

            # Convert to utc string form for Binance
            next_first_timestamp = str(next_first_datetime.replace(tzinfo=pytz.UTC))
            next_end_timestamp = str(next_last_datetime.replace(tzinfo=pytz.UTC))

            # Get next 500 data points
            new_data = client.get_historical_klines(symbol, interval, next_first_timestamp, next_end_timestamp)
            
            if (new_data[-1][0] == data[0][0]): # Assure that the timestamps match

                del new_data[-1]
                
            else:
                
                raise Exception("Timestamp error")

            new_df = pd.DataFrame(new_data, columns=cols)

            frames = [new_df, df]
            
            df = pd.concat(frames)
            df = df.reset_index(drop=True)
            
            oldest_candle_timestamp = new_data[0][0]
            data = new_data
            
            print(f"{(len(df) / number_of_expected_datapoints) * 100}%")
            
            time.sleep(1)
        
        print("Completed")
        return df      
        
    