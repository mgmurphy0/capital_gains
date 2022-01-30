## Executable to calculate capital gains. Includes functions to calculate capital gains in different ways.
# 
# TODO: Update to deal with long term vs short term gains/losses
#

import os
import pandas as pd
import numpy as np
from update_doc_data import fix_time, fix_asset_type, fix_transaction_type, fix_amount_col
from platform_classes import CoinBasePro


def fifo_tax(df):

    df['available_to_sell'] = df['coin_amount']

    df['available_to_sell'].loc[np.isnan(df['available_to_sell'])] = 0

    mask = df['coin_amount']<0
    df.available_to_sell[mask] = 0

    df['capital_gains'] = 0

    for x in range(len(df)):
        # if asset was sold:
        if df['coin_amount'][x] < 0:

            # Returns the index going from zero to x that first has a value for available_to_sell for the same coin as selling
            counter = next((i for i, count in enumerate(df.available_to_sell) if count and (df.asset_type_coin[x]==df.asset_type_coin[i])), None)

            sell = df['coin_amount'][x]

            print(f'Selling {sell} {df.asset_type_coin[x]}')
            while abs(sell) > 0:
                if abs(sell) < df['available_to_sell'][counter]:
                    df['available_to_sell'][counter] = sell + df['available_to_sell'][counter]
                    df['capital_gains'][x] = (abs(sell)*df['spotprice'][x])\
                        - (df['spotprice'][counter]*abs(sell))\
                            + df['capital_gains'][x] 
                    sell = 0
                else:
                    df['capital_gains'][x] = (df['available_to_sell'][counter]*df['spotprice'][x])\
                        - (df['spotprice'][counter]*df['available_to_sell'][counter])\
                            + df['capital_gains'][x]
                    sell = sell + df['available_to_sell'][counter]
                    df['available_to_sell'][counter] = 0
                    counter = next((i for i, count in enumerate(df.available_to_sell) if count and (df.asset_type_coin[x]==df.asset_type_coin[i])), None)
            #print(f"{df['time'][x]} - Capital Gains for sell transaction of {abs(df['coin_amount'][x])} {df.asset_type_coin[x]} was {df['capital_gains'][x]}")
    print(f"FIFO - Total capital gains is {df['capital_gains'].sum()}")

    return df['capital_gains'].sum()


def hifo_tax(df):

    df['available_to_sell'] = df['coin_amount']

    df['available_to_sell'].loc[np.isnan(df['available_to_sell'])] = 0

    mask = df['coin_amount']<0
    df.available_to_sell[mask] = 0

    df['capital_gains'] = 0

    for x in range(len(df)):
        if df['coin_amount'][x] < 0:

            # Creat high to low transaction dataframe using only the dates up to the sell transaction date, and sorting by date. Do not include capital gains column
            high_to_low_transactions = df.loc[(df['asset_type_coin']==df.asset_type_coin[x])].iloc[:x, 0:-1].sort_values(by=['spotprice'], ascending=False)

            # Returns the index going from high to low transaction value that first has a value for available_to_sell
            counter = next((high_to_low_transactions.index.values[i] for i, count in enumerate(high_to_low_transactions.available_to_sell) if count), None)

            sell = df['coin_amount'][x]
            while abs(sell) > 0:
                if abs(sell) < df['available_to_sell'][counter]:
                    df['available_to_sell'][counter] = sell + df['available_to_sell'][counter]
                    df['capital_gains'][x] = (abs(sell)*df['spotprice'][x])\
                        - (df['spotprice'][counter]*abs(sell))\
                            + df['capital_gains'][x] 
                    sell = 0
                    
                else:
                    df['capital_gains'][x] = (df['available_to_sell'][counter]*df['spotprice'][x])\
                        - (df['spotprice'][counter]*df['available_to_sell'][counter])\
                            + df['capital_gains'][x]
                    sell = sell + df['available_to_sell'][counter]
                    df['available_to_sell'][counter] = 0
                    high_to_low_transactions['available_to_sell'][counter] = 0
                    counter = next((high_to_low_transactions.index.values[i] for i, count in enumerate(high_to_low_transactions.available_to_sell) if count), None)
            #print(f"{df['time'][x]} - Capital Gains for sell transaction of {abs(df['coin_amount'][x])} {df.asset_type_coin[x]} was {df['capital_gains'][x]}")
    print(f"HIFO - Total capital gains is {df['capital_gains'].sum()}")

    return df['capital_gains'].sum()


def lifo_tax(df):

    df['available_to_sell'] = df['coin_amount']

    df['available_to_sell'].loc[np.isnan(df['available_to_sell'])] = 0

    mask = df['coin_amount']<0
    df.available_to_sell[mask] = 0

    df['capital_gains'] = 0

    for x in range(len(df)):
        if df['coin_amount'][x] < 0:

            # Returns the index going from x to zero that first has a value for available_to_sell
            last_to_first_df = df.iloc[x::-1]
            # because our data has reset indices before this function, .loc[x-i] is the same as .iloc[i] 
            counter = next((i for i, count in enumerate(last_to_first_df['available_to_sell']) if count and (df.asset_type_coin[x]==last_to_first_df['asset_type_coin'].loc[x-i])), None)

            sell = df['coin_amount'][x]
            while abs(sell) > 0:
                if abs(sell) < df['available_to_sell'][x-counter]:
                    #print((df['available_to_sell'][x-counter],df['available_to_sell'][x]))
                    df['available_to_sell'][x-counter] = sell + df['available_to_sell'][x-counter]
                    df['capital_gains'][x] = (abs(sell)*df['spotprice'][x])\
                        - (df['spotprice'][x-counter]*abs(sell))\
                            + df['capital_gains'][x] 
                    sell = 0
                else:
                    #print((df['available_to_sell'][x-counter],df['available_to_sell'][x]))
                    df['capital_gains'][x] = (df['available_to_sell'][x-counter]*df['spotprice'][x])\
                        - (df['spotprice'][x-counter]*df['available_to_sell'][x-counter])\
                            + df['capital_gains'][x]
                    sell = sell + df['available_to_sell'][x-counter]
                    df['available_to_sell'][x-counter] = 0
                    last_to_first_df = df.iloc[x::-1]
                    counter = next((i for i, count in enumerate(last_to_first_df['available_to_sell']) if count and (df.asset_type_coin[x]==last_to_first_df['asset_type_coin'].loc[x-i])), None)
            #print(f"{df['time'][x]} - Capital Gains for sell transaction of {abs(df['coin_amount'][x])} was {df['capital_gains'][x]}")
    #print(df)
    print(f"LIFO - Total capital gains is {df['capital_gains'].sum()}")

    return df['capital_gains'].sum()


if __name__ == "__main__":

    # File must be Excel document that contains sheets named after the exchange that they were provided by.
    file = 'C:/Users/mgmur/OneDrive/Desktop/Life_Documents/crypto_by_platform.xlsx'
    sheets = ['CoinbasePro'] #["Coinbase","Ledger","CoinbasePro"]

    data_xls = pd.read_excel(file, sheet_name = sheets, index_col=None)
    for sheet_name, df in data_xls.items():

        df['source'] = sheet_name
        df = fix_time(df)
        df = fix_asset_type(df)
        df = fix_transaction_type(df)
        df = fix_amount_col(df)

        if sheet_name == 'Coinbase':

            ## TODO: Finish developing

            coinbase = df
            continue

        if sheet_name == 'Ledger':

            ## TODO: Finish developing
            
            ledger = df
            continue

        if sheet_name == 'CoinbasePro':

            cbp = CoinBasePro(df)
            new_df = cbp.setup_new_df()
            cbp.make_new_df(new_df)

            ## TODO: Make sure to sort by date/time
            df = cbp.clean_df()

            continue

    fifo = fifo_tax(df)
    hifo = hifo_tax(df)
    lifo = lifo_tax(df)
    print(fifo)
    print(hifo)
    print(lifo)

