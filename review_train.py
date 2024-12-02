import pandas as pd

data = pd.read_csv('Data/processed_data.csv')
# print(data)

not_pos_data = data[(data['별점']<=3) & (data['별점']>0)]
print(f'긍정이 아닌 데이터: \n{not_pos_data}')

pos_data = data[data['별점']==5]
# print(pos_data)

random_pos_data = pos_data.sample(n=1147)
print(f'긍정 데이터: \n{random_pos_data}')

train_data = []

train_data = pd.concat([not_pos_data, random_pos_data], axis=0)
print(f'학습 데이터: \n{train_data}')

train_data.to_csv('./train_data.csv', index=False, encoding='utf-8-sig')