import matplotlib.pyplot as plt

# 로그 파일 경로
log_file_path = '../train.csv'

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# epoch, 학습 정확도, 검증 정확도, 학습 손실을 저장할 리스트
epochs = []
train_accuracies = []
val_accuracies = []
train_losses = []

# 로그 파일 읽기
with open(log_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        if 'Epoch' in line:
            # epoch 추출
            epoch = int(line.split()[1])  # 'Epoch 1 of 4'에서 1을 추출
            epochs.append(epoch)
        elif '학습 정확도' in line:
            # 학습 정확도 추출
            train_accuracy = float(line.split(':')[1].strip())
            train_accuracies.append(train_accuracy)
        elif '검증 정확도' in line:
            # 검증 정확도 추출
            val_accuracy = float(line.split(':')[1].strip())
            val_accuracies.append(val_accuracy)
        elif '평균 학습 오차' in line:
            # 학습 손실 추출
            train_loss = float(line.split(':')[1].strip())
            train_losses.append(train_loss)

plt.figure(figsize=(10, 6))

plt.plot(epochs, train_accuracies, marker='o', color='b', label='학습 Accuracy')
plt.plot(epochs, val_accuracies, marker='o', color='g', label='검증 Accuracy')

for i in range(len(epochs)):
    plt.text(epochs[i], train_accuracies[i], f'{train_accuracies[i]:.2f}',
             ha='center', va='bottom', fontsize=10)
    plt.text(epochs[i], val_accuracies[i], f'{val_accuracies[i]:.2f}',
             ha='center', va='bottom', fontsize=10)

plt.title('Epoch별 Accuracy')
plt.xlabel('Epoch')
plt.ylabel('정확도')
plt.ylim(0, 1)
plt.xticks(epochs)
plt.grid()
plt.legend()
plt.savefig('train_val_accuracy.jpg')  # 그래프 저장
plt.show()

plt.figure(figsize=(10, 6))

plt.plot(epochs, train_losses, marker='o', color='r', label='Train Loss')

for i in range(len(epochs)):
    plt.text(epochs[i], train_losses[i], f'{train_losses[i]:.2f}',
             ha='center', va='bottom', fontsize=10)

plt.title('Epoch별 loss')
plt.xlabel('Epoch')
plt.ylabel('loss')
plt.ylim(0, max(train_losses) * 1.1)  # 손실의 최대값에 약간 여유를 두기
plt.xticks(epochs)
plt.grid()
plt.savefig('train_loss.jpg')
plt.show()
