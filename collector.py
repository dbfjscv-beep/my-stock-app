import FinanceDataReader as fdr
import pandas as pd
import json

# 번역기: 미국 섹터를 한국어 대응어로 변환
SECTOR_TRANSLATION = {
    'Information Technology': 'IT/기술',
    'Health Care': '헬스케어',
    'Financials': '금융',
    'Consumer Discretionary': '자유소비재',
    'Communication Services': '통신서비스',
    'Industrials': '산업재',
    'Consumer Staples': '필수소비재',
    'Energy': '에너지',
    'Utilities': '유틸리티',
    'Real Estate': '부동산',
    'Materials': '소재',
    'General NYSE': '미국 기타(NYSE)',
    'Unknown': '분류안됨',
    'Other': '기타'
}

def translate_sector(sector_name):
    return SECTOR_TRANSLATION.get(sector_name, sector_name)

def collect_stocks():
    print("시장 데이터 수집 중...")

    # 1. 한국 시장 수집
    df_krx = fdr.StockListing('KRX')
    if 'Code' in df_krx.columns:
        df_krx = df_krx.rename(columns={'Code': 'Symbol'})
        
    try:
        df_desc = fdr.StockListing('KRX-DESC')
        if 'Code' in df_desc.columns:
            df_desc = df_desc.rename(columns={'Code': 'Symbol'})
        sector_col = 'Sector' if 'Sector' in df_desc.columns else 'Industry' if 'Industry' in df_desc.columns else None
        if sector_col:
            df_krx = pd.merge(df_krx, df_desc[['Symbol', sector_col]], on='Symbol', how='left')
            df_krx = df_krx.rename(columns={sector_col: 'Sector'})
    except Exception as e:
        print(f"공지: 상세 섹터 정보를 가져오지 못했습니다: {e}")

    for col in ['Symbol', 'Name', 'Sector', 'Market']:
        if col not in df_krx.columns:
            df_krx[col] = '분류안됨'

    df_krx = df_krx[['Symbol', 'Name', 'Sector', 'Market']]
    df_krx.columns = ['symbol', 'name', 'sector', 'market']
    df_krx['sector'] = df_krx['sector'].fillna('분류안됨')

    # 2. 미국 시장 (S&P 500) - 번역 적용
    df_sp500 = fdr.StockListing('S&P500')
    for col in ['Symbol', 'Name', 'Sector']:
        if col not in df_sp500.columns:
            df_sp500[col] = '분류안됨'
    df_sp500['Market'] = 'S&P500'
    df_sp500 = df_sp500[['Symbol', 'Name', 'Sector', 'Market']]
    df_sp500.columns = ['symbol', 'name', 'sector', 'market']
    df_sp500['sector'] = df_sp500['sector'].apply(translate_sector)

    # 3. 미국 시장 (NYSE)
    df_nyse = fdr.StockListing('NYSE')
    for col in ['Symbol', 'Name']:
        if col not in df_nyse.columns:
            df_nyse[col] = '분류안됨'
    df_nyse['Sector'] = 'General NYSE'
    df_nyse['Market'] = 'NYSE'
    df_nyse = df_nyse[['Symbol', 'Name', 'Sector', 'Market']]
    df_nyse.columns = ['symbol', 'name', 'sector', 'market']
    df_nyse['sector'] = df_nyse['sector'].apply(translate_sector)

    # 4. 전체 데이터 병합
    full_list = pd.concat([df_krx, df_sp500, df_nyse], ignore_index=True)
    full_list = full_list.dropna(subset=['name'])

    # 5. JSON 저장
    result = full_list.to_dict(orient='records')
    with open('stocks.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"성공! 총 {len(result)}개의 종목을 저장했습니다.")

if __name__ == "__main__":
    collect_stocks()
