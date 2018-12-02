# -- coding: utf-8 --
import tensorflow as tf
import numpy as np
import LSTM.Bi_LSTM as Bi_LSTM
import LSTM.Word2Vec as Word2Vec
from konlpy.tag import Okt
from eunjeon import Mecab

W2V = Word2Vec.Word2Vec()
mecab = Mecab()
okt = Okt()
Batch_size = 1
Vector_size = 300
Maxseq_length = 2000  ## Max length of training data
learning_rate = 0.001
lstm_units = 128
num_class = 4
keep_prob = 1.0
tf.reset_default_graph()
X = tf.placeholder(tf.float32, shape=[None, Maxseq_length, Vector_size], name='X')
Y = tf.placeholder(tf.float32, shape=[None, num_class], name='Y')
seq_len = tf.placeholder(tf.int32, shape=[None])

BiLSTM = Bi_LSTM.Bi_LSTM(lstm_units, num_class, keep_prob)

with tf.variable_scope("loss", reuse=tf.AUTO_REUSE):
    logits = BiLSTM.logits(X, BiLSTM.W, BiLSTM.b, seq_len)
    loss, optimizer = BiLSTM.model_build(logits, Y, learning_rate)

prediction = tf.nn.softmax(logits)

saver = tf.train.Saver()
init = tf.global_variables_initializer()
modelName = "Jupyter/BiLSTM_mecab_morphs_eqaul_4/BiLSTM_model.ckpt"

sess = tf.Session()
sess.run(init)
saver.restore(sess, modelName)

def classify(jss):
    okt = Okt()
    #tokens = okt.nouns(jss)
    tokens = mecab.nouns(jss)
    embedding = W2V.Convert2Vec('data/word2vec_mecab_morphs2.model', tokens)
    zero_pad = W2V.Zero_padding(embedding, Batch_size, Maxseq_length, Vector_size)
    global sess
    result = sess.run(tf.argmax(prediction,1), feed_dict = {X: zero_pad , seq_len: [len(tokens)] } )
    # print(sess.run(prediction, feed_dict = {X: zero_pad , seq_len: [len(tokens)] } ) )
    if result == 0:
        return '기타'
    elif result == 1:
        return '재무'
    elif result == 2:
        return '응용프로그래밍'
    elif result == 3:
        return '응용프로그래밍'
    elif result == 4:
        return '인사'
    elif result == 5:
        return '서버·시스템'
    elif result == 6:
        return '응용프로그래밍'

