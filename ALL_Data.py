import pandas as pd

low = pd.read_csv('./Data/Low_Data/Processed_Data/processed_low_data.csv')
high = pd.read_csv('./Data/High_Data/Processed_Data/processed_high_data.csv')

# print(low.head())
# print(high.head())

all = pd.concat([low, high]).reset_index()
all = all.drop(columns=['index'])

# print(all)

all.to_csv('./Data/ALL_data.csv', index=False, encoding='utf-8-sig')