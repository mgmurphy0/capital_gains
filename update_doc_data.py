'''Contains functions that are used to standardize data from transaction datasheets from different exchanges.'''

import pandas as pd
import datetime


def fix_time(df):

    time_vars = ['Timestamp','Operation Date','time']

    time_col = [col for col in df.columns for time_var in time_vars if time_var in col][0]

    fixed_time_df = df.rename(columns={time_col: 'time_old'})
    
    if fixed_time_df['source'][0] == 'Coinbase':
        time_list = [datetime.datetime.strptime(time,"%Y-%m-%dT%H:%M:%SZ") for time in fixed_time_df['time_old']]
    else:
        time_list = [datetime.datetime.strptime(time,"%Y-%m-%dT%H:%M:%S.%fZ") for time in fixed_time_df['time_old']]
    time = pd.DataFrame(time_list)
    fixed_time_df.insert(0, 'time', time)

    return fixed_time_df.drop(columns = ['time_old'])


def fix_asset_type(df):

    column_vars = ['Asset','amount/balance unit','Currency Ticker']

    asset_col = [col for col in df.columns for asset in column_vars if asset in col][0]

    return df.rename(columns={asset_col: 'asset_type'})


def fix_transaction_type(df):

    column_vars = ['Transaction Type','Operation Type','type']

    asset_col = [col for col in df.columns for trans_type in column_vars if trans_type in col][0]

    return df.rename(columns={asset_col: 'transaction_type'})


def fix_amount_col(df):

    column_vars = ['Quantity Transacted','Operation Amount','amount']

    amount_col = [col for col in df.columns for amount in column_vars if amount in col][0]

    fixed_amount_df = df.rename(columns={amount_col: 'amount_old'})
    fixed_amount_df['amount'] = fixed_amount_df['amount_old']

    return fixed_amount_df.drop(columns = ['amount_old'])


def fix_usd_asset_price(df):

    column_vars = ['Spot Price','Countervalue at Operation Date','type']

    asset_col = [col for col in df.columns for trans_type in column_vars if trans_type in col][0]

    return df.rename(columns={asset_col: 'transaction_type'})