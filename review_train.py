# 트레인데이터 수집

import pandas as pd

data = pd.read_csv('./Data/ALL_data.csv')
# print(data)

not_pos_data = data[(data['별점']<=3) & (data['별점']>0)]
random_pos_data = not_pos_data.sample(n=1147)

# 조건에 맞는 인덱스 중 랜덤하게 30% 추출
random_not_pos_data = list(neg)
random.seed(42)
random.shuffle(neg)
# print(neg)

select_ratio = 0.3

neg = neg[:int(select_ratio * len(neg))]
selected_neg = project.iloc[neg]
print(selected_neg)

print(f'긍정이 아닌 데이터: \n{not_pos_data}')

pos_data = data[data['별점']==5]
# print(pos_data)
random_pos_data = pos_data.sample(n=1147)
print(f'긍정 데이터: \n{random_pos_data}')



train_data = []

train_data = pd.concat([not_pos_data, random_pos_data], axis=0)
print(f'학습 데이터: \n{train_data}')

train_data.to_csv('./Data/train_data.csv', index=False, encoding='utf-8-sig')