import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

bold = {'weight': 'bold'}

data_path = '../Data/ALL_data.csv'
dataset = pd.read_csv(data_path).dropna(axis=0)

# 브랜드 별 리뷰 개수 세기
brands = dataset['브랜드'].unique()

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 서브플롯 설정 (2행 3열)
num_brands = len(brands)
rows = 2
cols = 3
fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(5 * cols, 5 * rows))

# 브랜드 수에 따른 서브플롯 조정
axes = axes.flatten()
for i in range(num_brands):
    ax = axes[i]
    brand = brands[i]

    brand_data = dataset[dataset['브랜드'] == brand]

    # 1~3점 부정, 4~5점 긍정
    negative_count = brand_data[(brand_data['별점'] >= 1) & (brand_data['별점'] <= 3)].shape[0]
    positive_count = brand_data[(brand_data['별점'] >= 4) & (brand_data['별점'] <= 5)].shape[0]

    # 그래프 그리기
    ax.bar(['부정', '긍정'], [negative_count, positive_count], color=['#FF6347', '#6495ED'])

    # 각 막대 위에 값 표시하기
    for j, count in enumerate([negative_count, positive_count]):
        ax.text(j, count, str(count), ha='center', va='bottom', size=12)

    ax.set_title(f'{brand} 브랜드 리뷰 분포', fontdict=bold)
    ax.set_xlabel('리뷰 유형', fontdict=bold)
    ax.set_ylabel('리뷰 개수', fontdict=bold)

# 마지막 서브플롯을 빈 그래프로 설정
if num_brands < rows * cols:
    axes[num_brands].axis('off')  # 축 끄기

# 레이아웃 조정
plt.tight_layout()

# 이미지 저장
plt.savefig('ALL_brands_review_Pos_Neg.jpg')
plt.show()
