import pandas as pd
import numpy as np
import requests
from datetime import date
from pandas.tseries.offsets import MonthEnd

def profit_summary():

    start_date = date(2020, 1, 1)
    end_date = date(2020, 10, 30)
    auth = ('cedwards@curioanalytics.com', 'Sloane2011')
    dates = pd.date_range(start=start_date, end=end_date, freq='MS').strftime('%Y%m')
    api_root = 'https://webservices.iso-ne.com/api/v1.1/'


    profit_summary = pd.DataFrame([])
    for insert_date in dates:
        try:
            # get auction results
            api_endpoint = '/ftrauctionresults/monthly/month/{}.json'
            url = api_root + api_endpoint.format(insert_date)
            resp = requests.get(url, auth=auth).json()
            record_path = ['FtrAuctionResults', 'FtrAuctionResult']
            df = pd.json_normalize(resp, record_path=record_path)
            df = df[df['BuySell'] == 'BUY']
            df = df[['AuctionName', 'CustomerName', 'ClassType', 'AwardFTRMW', 'AwardFTRPrice', 'SourceLocation.@LocId', 'SinkLocation.@LocId']]
            # df = df[[x for x in list(df) if not any(j in x for j in ['LocationType', '$', 'Buy', 'CustomerId'])]]
            df.columns = ['AuctionName', 'competitor_name', 'peak_type', 'mw', 'cp', 'source_id', 'sink_id']
            df['date_ms'] = pd.to_datetime(df['AuctionName'].apply(lambda x: x[-8:]), format='%Y %b').dt.date
            df['competitor_name'] = df['competitor_name'].apply(lambda x: x.split(' ')[0])
            df['peak_type'] = df['peak_type'].apply(lambda x: x.replace('PEAK', ''))
            df['cp'] = df['cp'] * df['mw']
            for col in ['sink_id', 'source_id']:
                df[col] = df[col].astype(int)
            df = df[['date_ms', 'competitor_name', 'peak_type', 'sink_id', 'source_id', 'mw', 'cp']]
            df_auctions = df.copy()

            # get cg
            api_endpoint = '/dayaheadlmpavgcongestion/month/{}.json'
            url = api_root + api_endpoint.format(insert_date)
            resp = requests.get(url, auth=auth).json()
            record_path = ['DayAheadLmpAvgCongestions', 'DayAheadLmpAvgCongestion']
            df = pd.json_normalize(resp, record_path=record_path)
            df = df[df['BeginDate'] == df['BeginDate'].max()]
            df.columns = ['BeginDate', 'ON', 'OFF', 'node_id', 'node_name']
            df['date_ms'] = pd.to_datetime(df['BeginDate'].apply(lambda x: x[:10])).dt.date
            df = pd.melt(df, id_vars=['date_ms', 'node_id'], value_vars=['ON', 'OFF'],
                             var_name='peak_type', value_name='cg_hourly')
            start = pd.to_datetime(insert_date, format='%Y%m').date()
            end = (start + MonthEnd(0)).date()
            weekdays = len([x for x in pd.date_range(start, end, freq='D') if x.weekday() <= 4])

            nerc_holiday_adj = 0
            if start.month in [5, 9, 11]:
                nerc_holiday_adj = 16
            if start.month == 1 and date(start.year, 1, 1).weekday() != 6:
                nerc_holiday_adj = 16
            if start.month == 7 and date(start.year, 7, 4).weekday() != 6:
                nerc_holiday_adj = 16
            if start.month == 12 and date(start.year, 12, 25).weekday() != 6:
                nerc_holiday_adj = 16

            on_hours = weekdays * 16 - nerc_holiday_adj
            off_hours = end.day * 24 - on_hours
            df['hours'] = np.where(df['peak_type'] =='ON', on_hours, off_hours)
            df['cg'] = df['cg_hourly'] * df['hours']
            df['node_id'] = df['node_id'].astype(int)
            df = df[['date_ms', 'peak_type', 'node_id', 'cg']]
            df_sink = df.copy()
            df_sink.columns = ['date_ms', 'peak_type', 'sink_id', 'sink_cg']
            df_source = df.copy()
            df_source.columns = ['date_ms', 'peak_type', 'source_id', 'source_cg']
            df = df_auctions.merge(df_sink)
            df = df.merge(df_source)

            df['cg'] = (df['sink_cg'] - df['source_cg']) * df['mw']
            df['profit'] = df['cg'] - df['cp']
            aggs = {'mw': 'sum', 'cg': 'sum', 'cp': 'sum', 'profit': 'sum'}
            df = df.groupby(['date_ms', 'competitor_name'], as_index=False).agg(aggs).round(0)
            profit_summary = profit_summary.append(df)

        except Exception as e:
            print(insert_date, e)

    return profit_summary
