import pandas as pd
from datetime import datetime, timedelta

data = pd.read_csv('Data/Original_Data/all_reviews.csv')
print(data.info())

# 기준 날짜 (24.11.26)
today = datetime.strptime('24.11.26', '%y.%m.%d')

# '작성일' 열을 처리하여 날짜로 변경
def adjust_date(row):
    if '일 전' in row:
        # 'n일 전'에서 n 값 추출
        days_ago = int(row.split('일 전')[0])
        # 오늘 날짜에서 n일을 뺀 날짜 계산
        return (today - timedelta(days=days_ago)).strftime('%y.%m.%d')
    else:
        return row  # 'n일 전'이 아닌 다른 날짜는 그대로 유지

# '작성일' 열에 대해 날짜 조정
data['작성일'] = data['작성일'].apply(adjust_date)

print(data)

data_process = data.drop_duplicates(['리뷰'])
print(data_process.info())

data_process.to_csv('processed_data.csv', index=False, encoding='utf-8-sig')
