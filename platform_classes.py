
import pandas as pd
import numpy as np

## TODO - make classes for other exchanges (Coinbase, Ledger, etc)

class CoinBasePro(object):

    '''Cleans and sets up transaction data provided by CoinbasePro'''

    def __init__(self, original_df):

        self.original_df = original_df


    def setup_new_df(self):

        self.working_df = self.original_df.drop(columns = ['portfolio','transfer id','trade id','order id'])
        self.working_df = self.working_df[['time','transaction_type','asset_type','amount','balance','source']]
        new_df = pd.DataFrame(columns = ['time','transaction_type','asset_type','spotprice','amount','balance','asset_type_2','amount_2','balance_2','asset_type_usd','usd_amount','usd_balance','asset_type_coin','coin_amount','coin_balance','source'])

        return new_df


    def make_new_df(self, new_df):

        skip_next_idx = 0
        for idx in range(len(self.working_df)):

            if skip_next_idx:
                skip_next_idx = 0
                continue

            new_df = new_df.append(self.working_df.loc[self.working_df.index[idx]])
            if idx == (len(self.working_df)-1):
                self.dollar_or_coin(new_df, idx)
                continue

            if self.working_df['time'][idx]==self.working_df['time'][idx+1] and self.working_df['transaction_type'][idx]=='match' and self.working_df['transaction_type'][idx+1]=='match':
                new_df['asset_type_2'][idx] = self.working_df['asset_type'][idx+1]
                new_df['amount_2'][idx] = self.working_df['amount'][idx+1]
                new_df['balance_2'][idx] = self.working_df['balance'][idx+1]
                new_df['transaction_type'][idx] = new_df['asset_type'][idx]+'to'+new_df['asset_type_2'][idx]

                if new_df['asset_type'][idx] == 'USD':
                    new_df['asset_type_usd'][idx] = new_df['asset_type'][idx]
                    new_df['usd_amount'][idx] = new_df['amount'][idx]
                    new_df['usd_balance'][idx] = new_df['balance'][idx]
                    new_df['asset_type_coin'][idx] = new_df['asset_type_2'][idx]
                    new_df['coin_amount'][idx] = new_df['amount_2'][idx]
                    new_df['coin_balance'][idx] = new_df['balance_2'][idx]
                    new_df['spotprice'][idx] = abs(new_df['amount'][idx]/new_df['amount_2'][idx])
                else:
                    new_df['asset_type_usd'][idx] = new_df['asset_type_2'][idx]
                    new_df['usd_amount'][idx] = new_df['amount_2'][idx]
                    new_df['usd_balance'][idx] = new_df['balance_2'][idx]
                    new_df['asset_type_coin'][idx] = new_df['asset_type'][idx]
                    new_df['coin_amount'][idx] = new_df['amount'][idx]
                    new_df['coin_balance'][idx] = new_df['balance'][idx]
                    new_df['spotprice'][idx] = abs(new_df['amount_2'][idx]/new_df['amount'][idx])

                skip_next_idx = 1

            else:
                
                self.dollar_or_coin(new_df, idx)

        self.full_df = new_df.reset_index(drop = True)


    def dollar_or_coin(self, new_df, idx):

        if self.working_df['asset_type'][idx]=='USD':
            new_df['asset_type_usd'][idx] = self.working_df['asset_type'][idx]
            new_df['usd_amount'][idx] = self.working_df['amount'][idx]
            new_df['usd_balance'][idx] = self.working_df['balance'][idx]
        else:
            new_df['asset_type_coin'][idx] = self.working_df['asset_type'][idx]
            new_df['coin_amount'][idx] = self.working_df['amount'][idx]
            new_df['coin_balance'][idx] = self.working_df['balance'][idx]

        return new_df


    def fix_coin_balance(self, df):

        for idx in range(len(df)):

            if (df['transaction_type'][idx]=='fee') and (np.isnan(df['coin_balance'][idx])):
                
                df['coin_balance'][idx] = df['coin_balance'][idx-1]

        return df


    def clean_df(self):

        df = self.full_df[['time','transaction_type','spotprice','usd_amount','usd_balance','asset_type_coin','coin_amount','coin_balance']]

        # We can ignore fees from capital gains calculations I think
        ignore_transactions = ['deposit','withdrawal','fee']
        df = df[~df['transaction_type'].isin(ignore_transactions)]

        df= df.reset_index(drop = True)

        df = self.fix_coin_balance(df)

        return df