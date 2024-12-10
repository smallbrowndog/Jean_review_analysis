import MeCab
import pandas as pd

stop_word_list = ['모드나인','토피','페이탈리즘','브랜디드','무신사스탠다드']

def extract_noun(text):
    t = MeCab.Tagger()
    parsed = t.parse(text)
    nouns = []
    for line in parsed.split('\n'):
        if line == 'EOS' or line == '':
            break
        word, features = line.split('\t')
        pos = features.split(',')[0]
        if pos == 'NNG' or pos == 'NNP':
            if len(word) >= 2:
                if word not in stop_word_list:
                    nouns.append(word)
    return nouns

data_path = 'Data/ratings_result.csv'
dataset = pd.read_csv(data_path).dropna(axis=0)

pos_text = list(dataset[dataset['예측 별점'] == 1]['리뷰'].values)
neg_text = list(dataset[dataset['예측 별점'] == 0]['리뷰'].values)

print(neg_text[:3])

processed_texts = [extract_noun(doc) for doc in neg_text]

print(processed_texts[:3])

from gensim import corpora
from gensim.models import LdaModel

dictionary= corpora.Dictionary(processed_texts)
print(f'전체 명사의 수: {len(dictionary)}')

# 5개 이하는 제거, 1000개 중 50퍼센트 이상의 문장에서 나온 단어는 빼기(영화 등 일반적인 단어를 제외하기 위해서)
# 내가 쓸때는 no_above는 0.5 ~ 0.7 로 조정 가능
# 지나치게 일반적인 단어가 있을때는 차후에 불용어로 처리할 수 있다.
dictionary.filter_extremes(no_below=10, no_above=0.5)
print(f'전체 명사의 수에서 필터를 적용한 개수: {len(dictionary)}')
print(dictionary.token2id)

# with open('dict_neg_text.txt', 'w', encoding='utf-8') as f:
#     for token, id in dictionary.token2id.items():
#         f.write(f'{token}\t{id}\n')

# 단어의 숫자와 빈도수를 표현하는것
corpus = [dictionary.doc2bow(text) for text in processed_texts]
print(corpus[:3])

num_topics = 10

lda_model = LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=num_topics,
    random_state=2024
)

for idx, topic in lda_model.print_topics(num_words=5):
    print(f'토픽 #{idx+1}: {topic}')