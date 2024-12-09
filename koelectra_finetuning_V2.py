import pandas as pd
import numpy as np
from transformers import ElectraTokenizer, ElectraForSequenceClassification
from transformers import get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import TensorDataset, DataLoader, RandomSampler
import time
import datetime

train_data_path = "./Data/train_data.csv"
dataset = pd.read_csv(train_data_path, sep=',', encoding='utf-8').dropna(axis=0)
text = list(dataset['리뷰'].values)
label = dataset['별점'].values

# 클래스 레이블 변환
label_mapping = {1: 0, 2: 0, 3: 0, 5: 1}  # 1, 2, 3을 0으로 묶고, 5를 1으로 매핑
label = np.array([label_mapping[l] for l in label])
label = label.tolist()

# 데이터 확인하기
num_to_print = 3
print("\n\n*** 데이터 ***")
for j in range(num_to_print):
    print(f'text: {text[j][:20]}, \tlabel: {label[j]}')
print(f'\t * 학습 데이터의 수: {len(text)}')
print(f'\t * 부정 리뷰 수: {list(label).count(0)}')
print(f'\t * 긍정 리뷰 수: {list(label).count(1)}')


tokenizer = ElectraTokenizer.from_pretrained('koelectra-base-v3-discriminator')
inputs = tokenizer(text, truncation=True, max_length=256, add_special_tokens=True, padding="max_length")
input_ids = inputs['input_ids']
attention_mask = inputs['attention_mask']
print("\n\n*** 토큰화 ***")
for j in range(num_to_print):
    print(f'\n{j+1}번째 데이터')
    print(' ** 토큰 **')
    print(input_ids[j])
    print(' ** 어텐션 마스크 **')
    print(attention_mask[j])

train, validation, train_y, validation_y = train_test_split(input_ids, label, test_size=0.2, random_state=2024)
train_masks, validation_masks, _, _ = train_test_split(attention_mask, label, test_size=0.2, random_state=2024)

print('\n\n *** 데이터 분리 ***')
print(f'학습 데이터 수: {len(train)}')
print(f'검증 데이터 수: {len(validation)}')

batch_size = 32
train_inputs = torch.tensor(train)
train_labels = torch.tensor(train_y)
train_masks  = torch.tensor(train_masks)
train_data   = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

validation_inputs = torch.tensor(validation)
validation_labels = torch.tensor(validation_y)
validation_masks  = torch.tensor(validation_masks)
validation_data   = TensorDataset(validation_inputs, validation_masks, validation_labels)
validation_sampler = RandomSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = ElectraForSequenceClassification.from_pretrained('koelectra-base-v3-discriminator', num_labels=2)
model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-04, eps=1e-06, betas=(0.9, 0.999))

epoch = 4
scheduler = get_linear_schedule_with_warmup(optimizer,
                                            num_warmup_steps=0,
                                            num_training_steps=len(train_dataloader)*epoch)

for e in range(0, epoch):
    print(f'\n\nEpoch {e+1} of {epoch}')
    total_loss = 0
    model.train()

    for step, batch in enumerate(train_dataloader):
        batch_ids, batch_mask, batch_label = tuple(t.to(device) for t in batch)
        model.zero_grad()

        outputs = model(batch_ids, token_type_ids=None, attention_mask=batch_mask, labels=batch_label)
        loss = outputs.loss
        total_loss += loss.item()

        if step % 10 == 0 and not step ==0: print(f'step: {step}, \tloss: {loss.item()}')

        loss.backward()
        torch.nn.utils.clip_grad_norm(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

    avg_train_loss = total_loss / len(train_dataloader)
    print(f'평균 학습 오차 (loss): {avg_train_loss}')

    model.eval()
    train_loss, train_accuracy, train_steps = 0, 0, 0
    for batch in train_dataloader:
        batch_ids, batch_mask, batch_label = tuple(t.to(device) for t in batch)

        with torch.no_grad():
            outputs = model(batch_ids, token_type_ids=None, attention_mask=batch_mask)

        logits = outputs[0]
        logits = logits.cpu().numpy()
        label_ids = batch_label.cpu().numpy()

        pred_flat = np.argmax(logits, axis=1).flatten()
        label_flat = label_ids.flatten()
        train_accuracy_temp = np.sum(pred_flat == label_flat) / len(label_flat)
        train_accuracy += train_accuracy_temp
        train_steps += 1
    print(f'학습 정확도: {train_accuracy / train_steps}')

    eval_loss, eval_accuracy, eval_steps = 0, 0, 0
    for batch in validation_dataloader:
        batch_ids, batch_mask, batch_label = tuple(t.to(device) for t in batch)

        with torch.no_grad():
            outputs = model(batch_ids, token_type_ids=None, attention_mask=batch_mask)

        logits = outputs[0]
        logits = logits.cpu().numpy()
        label_ids = batch_label.cpu().numpy()

        pred_flat = np.argmax(logits, axis=1).flatten()
        label_flat = label_ids.flatten()
        eval_accuracy_temp = np.sum(pred_flat == label_flat) / len(label_flat)
        eval_accuracy += eval_accuracy_temp
        eval_steps += 1
    print(f'검증 정확도: {eval_accuracy/eval_steps}')

print('\n\n *** 모델 저장 ***')
save_path = 'koelectra_base_musinsa'
model.cpu()
for param in model.parameters():
    if not param.is_contiguous():
        param.data = param.data.contiguous()
model.save_pretrained(save_path, '.pt')
print('\n\n *** 끝 ***')