# -*- coding: utf-8 -*-
"""ssl.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1zzmews9E8PX11hYbg6Gs_KfpCn3jL48t
"""

import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def preprocess_input(x):
    x = x / 127.5 - 1  # [0, 255] -> [-1, 1]
    return x

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    horizontal_flip=True
)
val_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

# 現在の作業ディレクトリを取得
base_dir = os.getcwd()

# データディレクトリへのパスを設定
train_dir = os.path.join(base_dir, 'content/train')
validation_dir = os.path.join(base_dir, 'content/validation')

# ディレクトリが存在するか確認し、なければエラーを表示
if not os.path.isdir(train_dir):
    raise FileNotFoundError(f"トレーニングデータのディレクトリが見つかりません: {train_dir}")
if not os.path.isdir(validation_dir):
    raise FileNotFoundError(f"検証データのディレクトリが見つかりません: {validation_dir}")

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(256, 256),
    batch_size=32,
    class_mode='input'
)

validation_generator = val_datagen.flow_from_directory(
    validation_dir,
    target_size=(256, 256),
    batch_size=32,
    class_mode='input'
)

import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt

def build_generator():
    inputs = tf.keras.Input(shape=[256, 256, 3])

    down1 = layers.Conv2D(64, 4, strides=2, padding='same')(inputs)
    down1 = layers.LeakyReLU()(down1)

    up1 = layers.Conv2DTranspose(64, 4, strides=2, padding='same')(down1)
    up1 = layers.ReLU()(up1)

    outputs = layers.Conv2D(3, 1, activation='tanh')(up1)
    return tf.keras.Model(inputs, outputs)

generator = build_generator()
generator.summary()

generator.compile(optimizer='adam', loss='mae')

from tensorflow.keras.callbacks import EarlyStopping

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True
)

history = generator.fit(
    train_generator,
    epochs=100,
    validation_data=validation_generator,
    callbacks=[early_stopping]
)

print("train_generator:", train_generator)
print("Data preview:", next(iter(train_generator), "No data in generator"))

def generate_image(model, input_image):
    prediction = model.predict(np.expand_dims(input_image, axis=0))
    prediction = (prediction[0] + 1) / 2
    return prediction

# ジェネレータからデータを取得
test_batch = next(iter(validation_generator))
test_images = test_batch[0]

# テスト用の画像を取得
test_image = test_images[0]
generated_image = generate_image(generator, test_image)

plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.title('Original Image')
plt.imshow((test_image + 1) / 2)
plt.axis('off')

plt.subplot(1,2,2)
plt.title('Generated Image (Supervised)')
plt.imshow(generated_image)
plt.axis('off')

plt.show()

plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

generator.save('generator_model.h5')