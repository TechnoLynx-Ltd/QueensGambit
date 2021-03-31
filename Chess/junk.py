import numpy as np
import tensorflow.compat.v1 as tf
# import tensorflow as tf
# from tensorflow.keras import Model
# from tensorflow.keras.layers import Conv2D, Flatten, Dense

if False:
    class MyModel(Model):
        def __init__(self):
            super(MyModel, self).__init__()
            self.conv1 = Conv2D(32, 3, activation='relu')
            self.flatten = Flatten()
            self.d1 = Dense(128, activation='relu')
            self.d2 = Dense(10)

        def call(self, x):
            x = self.conv1(x)
            x = self.flatten(x)
            x = self.d1(x)
            return self.d2(x)


    a = np.ones((2, 3), dtype=np.float32)
    b = Dense(10)(a)
    pass

    # model = MyModel()

a = tf.placeholder(tf.float32, [])
b = tf.constant(1.0)
c = tf.add(a, b)

with tf.compat.v1.Session() as sess:
    print(sess.run(c))
