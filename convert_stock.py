import pandas as pd 
 
df = pd.read_csv("yandex_stock.csv") 
 
print("Колонки:", df.columns.tolist()) 
 
df_clean = df[["Date", "Price", "Vol."]].copy() 
df_clean.columns = ["date", "close", "volume"] 
 
df_clean["date"] = pd.to_datetime(df_clean["date"]).dt.strftime("%Y-%m-%d") 
df_clean = df_clean.sort_values("date") 
 
df_clean.to_csv("data/yandex_stock.csv", index=False) 
 
print(f"✅ Готово! Записей: {len(df_clean)}") 
