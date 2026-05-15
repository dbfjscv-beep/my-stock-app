import FinanceDataReader as fdr
import pandas as pd
import json
import os

def collect_stocks():
    print("Gathering Market Data...")

    # 1. Fetch Korean Markets (KOSPI, KOSDAQ)
    # This returns: Symbol, Name, Sector, Industry, etc.
    df_krx = fdr.StockListing('KRX')
    df_krx = df_krx[['Code', 'Name', 'Sector', 'Market']]
    df_krx.columns = ['symbol', 'name', 'sector', 'market']

    # 2. Fetch US Markets (S&P 500)
    # S&P 500 is the best source for clean US Sector data
    df_sp500 = fdr.StockListing('S&P500')
    df_sp500 = df_sp500[['Symbol', 'Name', 'Sector']]
    df_sp500['market'] = 'S&P500'
    df_sp500.columns = ['symbol', 'name', 'sector', 'market']

    # 3. Fetch broader US Markets (NYSE)
    # Note: Broad NYSE sector data is sometimes sparse; we combine it
    df_nyse = fdr.StockListing('NYSE')
    df_nyse = df_nyse[['Symbol', 'Name']]
    df_nyse['sector'] = 'General NYSE'
    df_nyse['market'] = 'NYSE'
    df_nyse.columns = ['symbol', 'name', 'sector', 'market']

    # 4. Combine all into one massive list
    full_list = pd.concat([df_krx, df_sp500, df_nyse], ignore_index=True)

    # 5. Data Cleaning
    # Remove any stocks that don't have a name or sector to keep the app clean
    full_list = full_list.dropna(subset=['name'])
    full_list['sector'] = full_list['sector'].fillna('Other')

    # 6. Save as JSON (The Warehouse file)
    result = full_list.to_dict(orient='records')
    with open('stocks.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully collected {len(result)} stocks.")

if __name__ == "__main__":
    collect_stocks()
