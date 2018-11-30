import tensorflow as tf
import numpy as np
import LSTM.Bi_LSTM as Bi_LSTM
import LSTM.Word2Vec as Word2Vec
from konlpy.tag import Okt

class Classifier:
    def __init__(self, model_name="models/Bidirectional_LSTM/BiLSTM_model.ckpt", Maxseq_length=1025, num_class=8):
        self.W2V = Word2Vec.Word2Vec()
        self.okt = Okt()

        # 파라미터 셋팅====================================================
        self.Batch_size = 1
        self.Vector_size = 300
        self.Maxseq_length = Maxseq_length  ## Max length of training data
        self.learning_rate = 0.001
        self.lstm_units = 128
        self.num_class = num_class
        self.keep_prob = 1.0
        # 파라미터 셋팅====================================================

        # 모델 리스토어
        saver = tf.train.Saver()
        tf.reset_default_graph()
        init = tf.global_variables_initializer()
        modelName = model_name
        self.sess = tf.Session()
        self.sess.run(init)
        print(model_name + 'model restoring...')
        saver.restore(self.sess, modelName)
        print('model restored')

        # 그래프 빌드
        tf.reset_default_graph()
        self.X = tf.placeholder(tf.float32, shape=[None, self.Maxseq_length, self.Vector_size], name='X')
        self.Y = tf.placeholder(tf.float32, shape=[None, self.num_class], name='Y')
        self.seq_len = tf.placeholder(tf.int32, shape=[None])

        self.BiLSTM = Bi_LSTM(self.lstm_units, num_class, self.keep_prob)

        with tf.variable_scope("loss", reuse=tf.AUTO_REUSE):
            self.logits = self.BiLSTM.logits(self.X, self.BiLSTM.W, self.BiLSTM.b, self.seq_len)
            self.loss, self.optimizer = self.BiLSTM.model_build(self.logits, self.Y, self.learning_rate)

        self.prediction = tf.nn.softmax(self.logits)

    # TODO W2V 모델 새로 만들어서 이름 고쳐놓기
    def classify(self, jss, w2vmodel='models/word2vec_okt_nouns.model'):
        tokens = self.okt.nouns(jss)
        embedding = self.W2V.Convert2Vec(w2vmodel, tokens)
        zero_pad = self.W2V.Zero_padding(embedding, self.Batch_size, self.Maxseq_length, self.Vector_size)
        result = self.sess.run(tf.argmax(prediction, 1), feed_dict={self.X: zero_pad, self.seq_len: [len(tokens)]})
        print(self.sess.run(prediction, feed_dict={self.X: zero_pad, self.seq_len: [len(tokens)]}))
        if result == 0:
            return '경영지원'
        elif result == 1:
            return '재무·금융'
        elif result == 2:
            return '생산·물류'
        elif result == 3:
            return '영업·마케팅'
        elif result == 4:
            return '인사'
        elif result == 5:
            return '통계'
        elif result == 6:
            return '서버·시스템'
        elif result == 7:
            return '응용프로그래밍'
