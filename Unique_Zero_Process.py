import pandas as pd

data = pd.read_csv('Data/Row_Data/all_row_reviews.csv')
print(data.info())

# 0점 제거
Zero_process = data[data['별점'] != 0]
Zero_process.reset_index(inplace=True)

print(Zero_process.info())

# <br> 제거
Zero_process.loc[:, '리뷰'] = Zero_process['리뷰'].str.replace('<br>', ' ', regex=True)
Zero_process = Zero_process.drop(columns=['index'])

print(Zero_process.info())

# 중복 값 제거
Zero_process = Zero_process.drop_duplicates(subset=['리뷰'])
Zero_process.reset_index(inplace=True)

print(Zero_process.info())


