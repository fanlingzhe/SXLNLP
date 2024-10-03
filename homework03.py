import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

class TorchModel(nn.Module):
    def  __init__(self, vector_dim, sentence_length, vocab):
        super(TorchModel, self).__init__()
        self.embedding = nn.Embedding(len(vocab), vector_dim)
        self.rnn = nn.RNN(vector_dim, vector_dim, batch_first = True)
        self.classify = nn.Linear(vector_dim, sentence_length + 1)
        self.loss = nn.functional.cross_entropy


    def forward(self, x, y=None):
        x= self.embedding(x)
        rnn_out, hidden = self.rnn(x)
        x = rnn_out[:, -1, :]

        y_pred = self.classify(x)
        if y is not None:
            loss = self.loss(y_pred, y)
        else:
            return y_pred

def build_vocab():
    chars = "abcdefghijk"
    vocab = {"pad": 0}
    for index, char in enumerate(chars):
        vocab[char] = index + 1
    vocab["unk"] = len(vocab)
    return vocab

def build_sample(vocab, sentence_length):
    x = random.sample(list(vocab.keys()), sentence_length)
    if "a" in x:
        y = x.index("a")
    else:
        y = sentence_length
    x = [vocab.get(word,vocab['unk']) for word in x]
    return x, y

def build_dataset(sample_size, vocab, sentence_length):
    dataset_x = []
    dataset_y = []
    for i in range(sample_size):
        x, y = build_sample(vocab, sentence_length)
        dataset_x.append(x)
        dataset_y.append(y)
    return torch.LongTensor(dataset_x), torch.LongTensor(dataset_y)


#建立模型
def build_model(vocab, char_dim, sentence_length):
    model = TorchModel(char_dim, sentence_length, vocab)
    return model


def evaluate(model, vocab, sample_length):
    model.eval()
    x, y = build_dataset(200, vocab, sample_length)
    print("本次预测集中共有%d个样本" % (len(y)))
    correct, wrong = 0, 0
    with torch.no_grad():
        y_pred = model(x)
        for y_p, y_t in zip(y_pred, y):
            if int(torch.argmax(y_p)) == int(y_t):
                correct += 1
            else:
                wrong += 1
    print("正确预测个数: %d, 正确率: %f"% (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)

def main():
    epoch_num = 20
    batch_size = 40
    train_sample = 1000
    char_dim = 30
    sentence_length = 10
    learning_rate = 0.001
    vocab = build_vocab()
    model = build_model(vocab, char_dim, sentence_length)
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch in range(int(train_sample / batch_size)):
            x, y = build_dataset(batch_size, vocab, sentence_length)  # 构造一组训练样本
            optim.zero_grad()  # 梯度归零
            loss = model(x, y)  # 计算loss
            loss.backward()  # 计算梯度
            optim.step()  # 更新权重
            watch_loss.append(loss.item())
        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model, vocab, sentence_length)  # 测试本轮模型结果
        log.append([acc, np.mean(watch_loss)])
    # 画图
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    # 保存模型
    torch.save(model.state_dict(), "model.pth")
    return

