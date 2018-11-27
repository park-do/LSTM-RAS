# -*- coding: utf-8 -*-
import time
import os
import tensorflow as tf
import numpy as np
import LSTM.Bi_LSTM as Bi_LSTM
import LSTM.Word2Vec as Word2Vec
import pandas as pd
from konlpy.tag import Okt

class Bi_LSTM_train:

    def __init__(self):
        okt = Okt()

    def load_data(self, dir):
        self.df = pd.read_csv(dir, index_col=0, engine='python', encoding='utf8')

        # 데이터 섞기
        df = self.df.reset_index().drop(columns={'index'})
        rows = np.random.choice(df.index.values, len(df), replace=False)
        sampled_df = df.loc[rows]
        self.df = sampled_df

        self.data = []
        print('txt divided by nouns...')
        i = 0
        for txt in df.jss:
            i += 1
            self.data.append(self.okt.nouns(txt))
            if i % 100 == 0:
                print(i / len(df.jss) * 100, '% processing')
        print('txt divide complete')
        self.labels = self.df.label

    def word_embedding(self, model="../data/word2vec_okt_nouns.model"):
        self.W2V = Word2Vec.Word2Vec()

        dataset = int(len(self.data) * 0.7)
        # 70% train, 30% test
        self.train_X = self.data[:dataset]
        self.train_Y = self.labels[:dataset]
        self.test_X = self.data[dataset:]
        self.test_Y = self.labels[dataset:]

        # TODO category3를 category로 고치자
        self.num_class = len(self.df.category3.unique())

        # 벡터로 바꾸기
        self.train_X_ = self.W2V.Convert2Vec(model, self.train_X)
        self.test_X_ = self.W2V.Convert2Vec(model, self.test_X)
        self.train_Y_ = self.W2V.One_hot(self.train_Y)
        self.test_Y_ = self.W2V.One_hot(self.test_Y)

    def train(self, model_dir='./Bidirectional_LSTM'):
        # 파라미터 셋팅======================================================
        Batch_size = 32
        Total_size = len(self.train_X)
        Vector_size = 300  # 모델의 워드벡터 사이즈
        train_seq_length = [len(x) for x in self.train_X]
        test_seq_length = [len(x) for x in self.test_X]
        Maxseq_length = max(max(train_seq_length), max(test_seq_length))
        learning_rate = 0.001
        lstm_units = 128
        num_class = self.num_class
        training_epochs = 4
        # ===================================================================

        # 그래프 만들기
        config = tf.ConfigProto()
        tf.reset_default_graph()

        X = tf.placeholder(tf.float32, shape=[None, Maxseq_length, Vector_size], name='X')
        Y = tf.placeholder(tf.float32, shape=[None, num_class], name='Y')
        seq_len = tf.placeholder(tf.int32, shape=[None])
        keep_prob = tf.placeholder(tf.float32, shape=None)

        BiLSTM = Bi_LSTM.Bi_LSTM(lstm_units, num_class, keep_prob)

        with tf.variable_scope("loss", reuse=tf.AUTO_REUSE):
            logits = BiLSTM.logits(X, BiLSTM.W, BiLSTM.b, seq_len)
            loss, optimizer = BiLSTM.model_build(logits, Y, learning_rate)
        prediction = tf.nn.softmax(logits)
        correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(Y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

        total_batch = int(len(self.train_X) / Batch_size)
        test_batch = int(len(self.test_X) / Batch_size)

        modelName = model_dir + '/BiLSTM_model.ckpt'
        saver = tf.train.Saver()

        train_acc = []
        train_loss = []
        test_acc = []
        test_loss = []


        # 학습
        with tf.Session(config=config) as sess:
            init = tf.global_variables_initializer()
            start_time = time.time()
            sess.run(init)
            train_writer = tf.summary.FileWriter(model_dir, sess.graph)
            merged = BiLSTM.graph_build()

            for epoch in range(training_epochs):

                avg_acc, avg_loss = 0., 0.
                mask = np.random.permutation(len(self.train_X_))
                self.train_X_ = self.train_X_[mask]
                self.train_Y_ = self.train_Y_[mask]

                for step in range(total_batch):
                    train_batch_X = self.train_X_[step * Batch_size: step * Batch_size + Batch_size]
                    train_batch_Y = self.train_Y_[step * Batch_size: step * Batch_size + Batch_size]
                    batch_seq_length = train_seq_length[step * Batch_size: step * Batch_size + Batch_size]

                    train_batch_X = self.W2V.Zero_padding(train_batch_X, Batch_size, Maxseq_length, Vector_size)

                    sess.run(optimizer, feed_dict={X: train_batch_X, Y: train_batch_Y, seq_len: batch_seq_length})
                    # Compute average loss
                    loss_ = sess.run(loss, feed_dict={X: train_batch_X, Y: train_batch_Y, seq_len: batch_seq_length,
                                                      keep_prob: 0.75})
                    avg_loss += loss_ / total_batch

                    acc = sess.run(accuracy, feed_dict={X: train_batch_X, Y: train_batch_Y, seq_len: batch_seq_length,
                                                        keep_prob: 0.75})
                    avg_acc += acc / total_batch
                    print(
                        "epoch : {:02d} step : {:04d} loss = {:.6f} accuracy= {:.6f}".format(epoch + 1, step + 1, loss_,
                                                                                             acc))

                summary = sess.run(merged, feed_dict={BiLSTM.loss: avg_loss, BiLSTM.acc: avg_acc})
                train_writer.add_summary(summary, epoch)

                t_avg_acc, t_avg_loss = 0., 0.
                print(avg_loss, avg_acc)
                print("Test cases, could take few minutes")

                for step in range(test_batch):
                    test_batch_X = self.test_X_[step * Batch_size: step * Batch_size + Batch_size]
                    test_batch_Y = self.test_Y_[step * Batch_size: step * Batch_size + Batch_size]
                    batch_seq_length = test_seq_length[step * Batch_size: step * Batch_size + Batch_size]

                    test_batch_X = self.W2V.Zero_padding(test_batch_X, Batch_size, Maxseq_length, Vector_size)

                    # Compute average loss
                    loss2 = sess.run(loss, feed_dict={X: test_batch_X, Y: test_batch_Y, seq_len: batch_seq_length,
                                                      keep_prob: 1.0})
                    t_avg_loss += loss2 / test_batch

                    t_acc = sess.run(accuracy, feed_dict={X: test_batch_X, Y: test_batch_Y, seq_len: batch_seq_length,
                                                          keep_prob: 1.0})
                    t_avg_acc += t_acc / test_batch

                print("<Train> Loss = {:.6f} Accuracy = {:.6f}".format(avg_loss, avg_acc))
                print("<Test> Loss = {:.6f} Accuracy = {:.6f}".format(t_avg_loss, t_avg_acc))
                train_loss.append(avg_loss)
                train_acc.append(avg_acc)
                test_loss.append(t_avg_loss)
                test_acc.append(t_avg_acc)
            # epoch end
        train_loss = pd.DataFrame({"train_loss": train_loss})
        train_acc = pd.DataFrame({"train_acc": train_acc})
        test_loss = pd.DataFrame({"test_loss": test_loss})
        test_acc = pd.DataFrame({"test_acc": test_acc})
        df = pd.concat([train_loss, train_acc, test_loss, test_acc], axis=1)
        df.to_csv(model_dir + "/loss_accuracy.csv", sep=",", index=False)

        train_writer.close()
        duration = time.time() - start_time
        minute = int(duration / 60)
        second = int(duration) % 60
        print("%dminutes %dseconds" % (minute, second))
        save_path = saver.save(sess, modelName)

        print('save_path', save_path)
