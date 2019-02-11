#
# Chapter 8, Example 3
#

import numpy as np
import tensorflow as tf
import pylab

import os
if not os.path.isdir('figures'):
    print('creating the figures folder')
    os.makedirs('figures')

n_in = 8
n_hidden = 5
n_out = 3
n_steps = 64
n_seqs = 16

n_iters = 25000
lr = 0.0001


seed = 10
np.random.seed(seed)
tf.set_random_seed(seed)


# generate training data
x_train = np.random.rand(n_seqs, n_steps, n_in)
y_train = np.random.randint(size=(n_seqs, n_steps), low=0, high=n_out)
y_train_ = np.zeros([n_seqs, n_steps, n_out])
for i in range(n_seqs):
    for j in range(n_steps):
        y_train_[i, j, y_train[i, j]] = 1 

# build the model
x = tf.placeholder(tf.float32,[None, n_steps, n_in])
y = tf.placeholder(tf.float32, [None, n_steps, n_out])
init_state = tf.placeholder(tf.float32, [None, n_hidden])
                

U = tf.Variable(tf.truncated_normal([n_in, n_hidden], stddev=1/np.sqrt(n_in)))
V = tf.Variable(tf.truncated_normal([n_hidden, n_out], stddev=1/np.sqrt(n_hidden)))
W = tf.Variable(tf.truncated_normal([n_hidden, n_hidden], stddev=1/np.sqrt(n_hidden)))
b = tf.Variable(tf.zeros([n_hidden]))
c = tf.Variable(tf.zeros([n_out]))


h = init_state
ys = []
for i, x_ in enumerate(tf.split(x, n_steps, axis = 1)):
    h = tf.tanh(tf.matmul(tf.squeeze(x_), U) + tf.matmul(h, W) + b)
    u_ = tf.matmul(h, V) + c
    ys.append(u_)

y_ = tf.stack(ys, axis=1)
cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(labels=y, logits=y_)
cross_entropy = tf.reduce_mean(cross_entropy)

train_op = tf.train.AdamOptimizer(lr).minimize(loss=cross_entropy)

sess = tf.Session()
sess.run(tf.global_variables_initializer())

state = np.zeros([n_seqs, n_hidden])
loss = []
for i in range(n_iters):

    sess.run(train_op, {x:x_train, y: y_train_, init_state: state})
    loss.append(sess.run(cross_entropy, {x:x_train, y: y_train_, init_state: state}))

    if not i % 100:
        print('iter:%d, cost: %g'%(i, loss[i]))


pylab.figure()
pylab.plot(range(n_iters), loss)
pylab.savefig('./figures/8.3a_1.png')

pred = sess.run(y_, {x:x_train, y: y_train_, init_state: state})
pred_ = np.zeros([n_seqs, n_steps])
for i in range(n_seqs):
    for j in range(n_steps):
        pred_[i, j] = np.argmax(pred[i,j])
        
pylab.figure(figsize=(4, 2))
for i in range(8):
    ax = pylab.subplot(4, 2, i+1)
    pylab.axis('off')
    ax.plot(range(n_steps), y_train[i])
    ax.plot(range(n_steps), pred_[i])
    pylab.savefig('./figures/8.3a_2.png')
    
pylab.show()

        




