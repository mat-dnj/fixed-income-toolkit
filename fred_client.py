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
    '6M': 'DGS61MO',
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

def _get_api_key(api_key):
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

def _fetch_series(series_id, start, end, api_key):
    """
    fetch single time series from Fred and returns a pandas Series indexed by date, with values is pct
    """
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
        'observation_start': start,
        'observation_end': end
    }
    response = requests.get(fred_url, params=params, timeout=10)
    response.raise_for_status()

    observations = response.json().get('observations', [])

    data = {
        obs['date']: float(obs['value'])
        for obs in observations
        if obs['value']!= '.'
    }

    s = pd.Series(data, dtype=float)
    s.index = pd.to_datetime(s.index)
    return s.sort_index()

