# 트레인데이터 수집

import pandas as pd
import random

data = pd.read_csv('./Data/ALL_data.csv')
# print(data)

select_ratio = 0.7

# 3점 이하 모으기
neg_data = data[data['별점']<=3]

# 랜덤하게 70% 추출
random.seed(42)
neg_data_rd = neg_data.sample(frac=select_ratio)

print(f'총 부정 데이터: {len(neg_data)}\n'
      f'30% 추출 부정 데이터: {len(neg_data_rd)}\n{neg_data_rd}')


# 4점 이상 모으기
pos_data = data[data['별점']>=4]

# 랜덤하게 70% 추출
random.seed(42)
pos_data_rd = pos_data.sample(frac=select_ratio)

print(f'총 긍정 데이터: {len(pos_data)}\n'
      f'30% 추출 긍정 데이터: {len(pos_data_rd)}\n{pos_data_rd}')

train_data = []

train_data = pd.concat([neg_data_rd, pos_data_rd], axis=0)
print(f'학습 데이터: \n{train_data}')

train_data.to_csv('./Data/train_data.csv', index=False, encoding='utf-8-sig')