import FinanceDataReader as fdr
import pandas as pd
import json

def collect_stocks():
    print("Gathering Market Data...")

    # --- 1. Fetch Korean Markets ---
    print("Fetching KRX main list...")
    df_krx = fdr.StockListing('KRX')
    
    # FDR sometimes uses 'Code' instead of 'Symbol'. Let's normalize it.
    if 'Code' in df_krx.columns:
        df_krx = df_krx.rename(columns={'Code': 'Symbol'})
        
    # Fetch the secondary "Description" list to get the Sector data
    print("Fetching KRX descriptions for sectors...")
    try:
        df_desc = fdr.StockListing('KRX-DESC')
        if 'Code' in df_desc.columns:
            df_desc = df_desc.rename(columns={'Code': 'Symbol'})
        
        # Look for 'Sector' or 'Industry' depending on the library version
        sector_col = 'Sector' if 'Sector' in df_desc.columns else 'Industry' if 'Industry' in df_desc.columns else None
        
        # Merge the Sector data into our main list
        if sector_col:
            df_krx = pd.merge(df_krx, df_desc[['Symbol', sector_col]], on='Symbol', how='left')
            df_krx = df_krx.rename(columns={sector_col: 'Sector'})
    except Exception as e:
        print(f"Notice: Could not fetch detailed sectors: {e}")

    # Safety Net: Ensure all required columns exist before filtering
    for col in ['Symbol', 'Name', 'Sector', 'Market']:
        if col not in df_krx.columns:
            df_krx[col] = 'Unknown'

    df_krx = df_krx[['Symbol', 'Name', 'Sector', 'Market']]
    df_krx.columns = ['symbol', 'name', 'sector', 'market']

    # --- 2. Fetch US Markets (S&P 500) ---
    print("Fetching S&P 500...")
    df_sp500 = fdr.StockListing('S&P500')
    
    # Safety Net for S&P 500
    for col in ['Symbol', 'Name', 'Sector']:
        if col not in df_sp500.columns:
            df_sp500[col] = 'Unknown'
            
    df_sp500['Market'] = 'S&P500'
    df_sp500 = df_sp500[['Symbol', 'Name', 'Sector', 'Market']]
    df_sp500.columns = ['symbol', 'name', 'sector', 'market']

    # --- 3. Fetch broader US Markets (NYSE) ---
    print("Fetching NYSE...")
    df_nyse = fdr.StockListing('NYSE')
    
    # Safety Net for NYSE
    for col in ['Symbol', 'Name']:
        if col not in df_nyse.columns:
            df_nyse[col] = 'Unknown'
            
    df_nyse['Sector'] = 'General NYSE'
    df_nyse['Market'] = 'NYSE'
    df_nyse = df_nyse[['Symbol', 'Name', 'Sector', 'Market']]
    df_nyse.columns = ['symbol', 'name', 'sector', 'market']

    # --- 4. Combine all ---
    print("Merging databases...")
    full_list = pd.concat([df_krx, df_sp500, df_nyse], ignore_index=True)

    # --- 5. Data Cleaning ---
    full_list = full_list.dropna(subset=['name'])
    full_list['sector'] = full_list['sector'].fillna('Other')

    # --- 6. Save as JSON ---
    result = full_list.to_dict(orient='records')
    with open('stocks.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"Success! Collected and saved {len(result)} stocks.")

if __name__ == "__main__":
    collect_stocks()
