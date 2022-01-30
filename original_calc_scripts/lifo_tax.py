## Last in First out (LIFO) Tax Strategy
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
transactions['capital_gains'] = 0

mask = transactions['transaction_units']<0
transactions.available_to_sell[mask] = 0

for x in range(len(transactions)):
    if transactions['transaction_units'][x] < 0:

        # Returns the index going from x to zero that first has a value for available_to_sell
        counter = next((i for i, count in enumerate(transactions.available_to_sell[x::-1]) if count), None)
        print(x,counter)

        sell = transactions['transaction_units'][x]
        while abs(sell) > 0:
            if abs(sell) < transactions['available_to_sell'][x-counter]:
                #print((transactions['available_to_sell'][x-counter],transactions['available_to_sell'][x]))
                transactions['available_to_sell'][x-counter] = sell + transactions['available_to_sell'][x-counter]
                transactions['capital_gains'][x] = (abs(sell)*transactions['transaction_price'][x])\
                    - (transactions['transaction_price'][x-counter]*abs(sell))\
                        + transactions['capital_gains'][x] 
                sell = 0
            else:
                #print((transactions['available_to_sell'][x-counter],transactions['available_to_sell'][x]))
                transactions['capital_gains'][x] = (transactions['available_to_sell'][x-counter]*transactions['transaction_price'][x])\
                    - (transactions['transaction_price'][x-counter]*transactions['available_to_sell'][x-counter])\
                        + transactions['capital_gains'][x]
                sell = sell + transactions['available_to_sell'][x-counter]
                transactions['available_to_sell'][x-counter] = 0
                if transactions['available_to_sell'][x-counter-1] > 0:
                    counter += 1
                    print(x,counter)
                else:
                    counter = next((i for i, count in enumerate(transactions.available_to_sell[x::-1]) if count), None)
                    print(x,counter)
        #print(f"{transactions['date'][x]} - Capital Gains for sell transaction of {abs(transactions['transaction_units'][x])} was {transactions['capital_gains'][x]}")
print(transactions)
print(f"Total capital gains is {transactions['capital_gains'].sum()}")