## Highest in First out (HIFO) Tax Strategy
# This script was created to read data from a handmade sheet documenting transaction. Out-dated.
#
import pandas as pd
import os

#file_path = os.path.join('C:','Users','mgmur','OneDrive','Desktop','Life_Documents')

df = pd.read_csv('C:/Users/mgmur/OneDrive/Desktop/Life_Documents/Crypto_History.csv',skiprows=2,header=None)

cols_to_keep = [3,4,5,6]
transactions = df[cols_to_keep]
transactions.columns=['date','transaction_price','transaction_units','quantity_owned']
#transactions.reset_index(inplace = True, drop = True)

#transactions = transactions.iloc[1:,:]
#transactions.drop_index()

# Delete rows where transaction price is zero (stolen, gifted, etc)
transactions = transactions.loc[transactions['transaction_price'] != 0]
transactions = transactions.reset_index(drop = True)

transactions['available_to_sell'] = transactions['transaction_units']

mask = transactions['transaction_units']<0
transactions.available_to_sell[mask] = 0

transactions['capital_gains'] = 0

for x in range(len(transactions)):
    if transactions['transaction_units'][x] < 0:

        # Creat high to low transaction dataframe using only the dates up to the sell transaction date, and sorting by date. Do not include capital gains column
        high_to_low_transactions = transactions.iloc[:x, 0:-1].sort_values(by=['transaction_price'], ascending=False)

        # Returns the index going from high to low transaction value that first has a value for available_to_sell
        counter = next((high_to_low_transactions.index.values[i] for i, count in enumerate(high_to_low_transactions.available_to_sell) if count), None)

        sell = transactions['transaction_units'][x]
        while abs(sell) > 0:
            if abs(sell) < transactions['available_to_sell'][counter]:
                transactions['available_to_sell'][counter] = sell + transactions['available_to_sell'][counter]
                transactions['capital_gains'][x] = (abs(sell)*transactions['transaction_price'][x])\
                    - (transactions['transaction_price'][counter]*abs(sell))\
                        + transactions['capital_gains'][x] 
                sell = 0
                
            else:
                transactions['capital_gains'][x] = (transactions['available_to_sell'][counter]*transactions['transaction_price'][x])\
                    - (transactions['transaction_price'][counter]*transactions['available_to_sell'][counter])\
                        + transactions['capital_gains'][x]
                sell = sell + transactions['available_to_sell'][counter]
                transactions['available_to_sell'][counter] = 0
                high_to_low_transactions['available_to_sell'][counter] = 0
                counter = next((high_to_low_transactions.index.values[i] for i, count in enumerate(high_to_low_transactions.available_to_sell) if count), None)

print(transactions)
print(f"Total capital gains is {transactions['capital_gains'].sum()}")