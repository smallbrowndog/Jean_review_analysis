import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

bold = {'weight': 'bold'}

data_path = '../Data/ALL_data.csv'
dataset = pd.read_csv(data_path).dropna(axis=0)

# 브랜드 별 리뷰 개수 세기
a = dataset['브랜드'].value_counts(ascending=False)

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

plt.figure(figsize=(10, 6))
bar = plt.bar(a.index, a, color='#6495ED')
# 각 막대 위에 값 표시하기
for rect in bar:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2.0, height, '%.0f' % height, ha='center', va='bottom', size=12)

plt.xticks(rotation = 0)
plt.xlabel('브랜드', fontdict=bold)
plt.ylabel('리뷰 개수', fontdict=bold)
plt.title('브랜드 별 리뷰 수')
plt.savefig('brand_count.jpg')
plt.show()


# 리뷰 평점 분포표
dataset_r = dataset['별점'].value_counts()

plt.figure(figsize=(10, 6))
bar = plt.bar(dataset_r.index, dataset_r, color='#6495ED')
plt.xlabel('리뷰 평점', fontdict=bold)
plt.ylabel('인원수', fontdict=bold)
plt.title('리뷰 평점 분포표')

for rect in bar:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2.0, height, '%.0f' % height, ha='center', va='bottom', size=12)

plt.savefig('rating_count.jpg')
plt.show()


# 글자 수 분포표
dataset_t = dataset['리뷰'].str.len()

text_length_counts = dataset_t.value_counts()

plt.figure(figsize=(10, 6))
plt.hist(dataset_t, bins=60, color='#6495ED', edgecolor='black')
plt.xlabel('글자 길이', fontdict=bold)
plt.ylabel('리뷰수', fontdict=bold)
plt.title('글자수 분포표')
plt.savefig('review_len_count.jpg')
plt.show()


# 긍정 부정 분포표
dataset['긍정_부정'] = 0

# 4,5점일때 1 / 1,2,3점일때 0 값 부여
dataset.loc[dataset['별점'] > 3, '긍정_부정'] = 1
def combine_2rd_columns(col_1, col_2):
    result = col_1
    if not pd.isna(col_2):
        result += " " + str(col_2)
    return result

dataset_p_n = dataset['긍정_부정'].value_counts()

plt.figure(figsize=(10, 6))
# plt.hist(fin_df['rating'], bins=len(c_fin_df), edgecolor='black')
bar = plt.bar(dataset_p_n.index, dataset_p_n, color='#6495ED')

plt.xlabel('긍, 부정 구분', fontdict=bold)
plt.ylabel('인원수', fontdict=bold)
plt.xticks([0, 1], labels=['부정', '긍정'])
plt.title('리뷰 긍부정 분포표')

for rect in bar:
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2.0, height, '%.0f' % height, ha='center', va='bottom', size=12)

plt.savefig('pos_neg_count.jpg')
plt.show()