import yfinance as yf 
import pandas as pd 
 
stock = yf.download('YNDX', start='2021-01-01', end='2024-12-31') 
stock[['Close', 'Volume']].to_csv('data/yandex_stock.csv') 
print(f"Загружено {len(stock)} записей") 
