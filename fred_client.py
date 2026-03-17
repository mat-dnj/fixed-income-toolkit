'''
This module aims to pull live US treasury data from the FRED API,
If you don't have a FRED API key, get yours here: https://fred.stlouisfed.org/docs/api/api_key.html,
Then run the command: export fred_api_key = 'enter your key here' 
'''
import os 
import requests
import pandas as pd
from datetime import datetime, timedelta


# Fred series ID for each treasury maturity
treasury_series = {
    '1M': 'DGS1MO',
    '3M': 'DGS3MO',
    '6M': 'DGS6MO',
    '1Y': 'DGS1',
    '2Y': 'DGS2',
    '3Y': 'DGS3',
    '5Y': 'DGS5',
    '7Y': 'DGS7',
    '10Y': 'DGS10',
    '20Y': 'DGS20',
    '30Y': 'DGS30',
}


fred_url = "https://api.stlouisfed.org/fred/series/observations"


def get_api_key(api_key):
    """
    get api key from argument of environment variable
    """
    key = api_key or os.environ.get('fred_api_key', '')
    if not key:
        raise ValueError(
            " no fred api key found\n"
            'get one at https://fred.stlouisfed.org/docs/api/api_key.html\n'
            'then run: export fred_api_key = "enter your key here"'
        )
    return key

def get_treasury_curve(start='2019-01-01', end=None, api_key=None):
    """
    downlad full UST yield curve from fred and returns a dataframe where each row is a trading day and each col is a maturity
    """
    api_key = get_api_key(api_key)
    end = end or datetime.today().strftime('%Y-%m-%d')
    
    print('downloading treasury yield from Fred...')
    all_series = {}
    for maturity, series_id in treasury_series.items():
        print(f' {maturity}', end='', flush=True)

        params = {
            'series_id': series_id,
            'api_key': api_key,
            'file_type': 'json',
            'observation_start': start,
            'observation_end': end
        }
        response = requests.get(fred_url, params=params, timeout=10)
    
        if response.status_code != 200:
            print(f'error fetching the {series_id}: status {response.status_code}')
            continue

        observations = response.json().get('observations', [])
        data = {
            obs['date']: float(obs['value'])
            for obs in observations
            if obs['value']!= '.'
        }

        s = pd.Series(data, dtype=float)
        s.index = pd.to_datetime(s.index)
        all_series[maturity] = s.sort_index()
        print()

    curve = pd.DataFrame(all_series)

    # make colum order go from short to long maturity
    ordered = ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y','7Y', '10Y', '20Y', '30Y']
    curve = curve[[c for c in ordered if c in curve.columns]] # this line check if specific maturity exists and add it to the dataframe, otherwise it skips it
    curve.index.name = 'date'

    print(f'Got {len(curve)} trading days from {curve.index[0].date()} to {curve.index[1].date()}')
    return curve


def get_latest_yields(api_key=None):
    """
    get the most recent available Treasury yield curve and returns a pandas Series. 
    use this to quickly check the curve or to price a bond
    """
    api_key= get_api_key(api_key)
    start = (datetime.today()-timedelta(days=10)).strftime('%Y-%m-%d') # look back 10days to make sure we hit a working business day 
    end = datetime.today().strftime('%Y-%m-%d')

    curve = get_treasury_curve(start=start, end=end, api_key=api_key)
    latest = curve.dropna(how='all').iloc[-1]

    print(f'latest Treasury yield ({latest.name.date()}):')
    for maturity, yield_values in latest.dropna().items():
        print(f'{maturity:} {yield_values:.3f}%')

    return latest

def get_curve_spreads(curve):
    """
    computes standards treasury yeild curve spread indicators
    2s10s / 3m10y / 5s30s
    """
    spreads = pd.DataFrame(index = curve.index)
    spreads['2s10s'] = (curve['10Y'] - curve['2Y']) * 100
    spreads['3m10y'] = (curve['10Y'] - curve['3M']) * 100
    spreads['5s30s'] = (curve['30Y'] - curve['5Y']) * 100
    return spreads.dropna()

# to do: maybe add SOFR data later for swap part
# also need to think about how to align US and EUR curves on the same dates cause they dont always have the same trading days
