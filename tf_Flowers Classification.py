
# importing libraries 

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import cv2 
import os


data_dir = r'E:\Project\Machine Learing\paid\flowers' # include here your data dir instead of mine

categories = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips'] # we have 5 categories of flowers
data_dir # checking whether my dir works properly or or not


# making a dictionary name data to keep my images with label
data = []

# I use this function to test my whether image path is valid or not. Thats the reason I plot the image by calling it from make_data() 
def show_img(image):
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title('image1')
    plt.show()
    

def make_data():
    for category in categories:
        path = os.path.join(data_dir, category) # .../flowers/daisy
        label = categories.index(category)

        for img_name in os.listdir(path):
            image_path = os.path.join(path, img_name)
            image = cv2.imread(image_path)
            # to test your image just call show_img() and pass the image i.e. show_img(image)
            try:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (224, 224))
                image = np.array(image, dtype = np.float32) # converting image into numpy array
                
                data.append([image, label])
                
            except Exception as e:
                pass
        print(len(data))
                
    
make_data()

# check total number of photos 
len(data)

np.random.shuffle(data) # shuffle your data

features = []
labels = []

for img, label in data:
    features.append(img)
    labels.append(label)


# conver fetures and labels into numpy array
features = np.array(features, dtype=np.float32)
labels = np.array(labels, dtype=np.float32)

# feature scaling 

features = features / 255.0

from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(features, labels, test_size=0.1)

# Data Augmentation
from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Learning Rate Schedule
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-5)

# Early Stopping
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)


input_layer = tf.keras.layers.Input([224, 224, 3])
conv1 = tf.keras.layers.Conv2D(filters = 32, 
                                      kernel_size = (5, 5), 
                                      padding = 'same', 
                                      activation = 'relu')(input_layer)

pool1 =tf.keras.layers.MaxPooling2D(pool_size = (2, 2))(conv1)

conv2 = tf.keras.layers.Conv2D(filters = 64, 
                                      kernel_size = (3, 3), 
                                      padding = 'same', 
                                      activation = 'relu')(pool1)


pool2 =tf.keras.layers.MaxPooling2D(pool_size = (2, 2), strides = (2, 2))(conv2)

conv3 = tf.keras.layers.Conv2D(filters = 96, 
                                      kernel_size = (3, 3), 
                                      padding = 'same', 
                                      activation = 'relu')(pool2)

pool3 =tf.keras.layers.MaxPooling2D(pool_size = (2, 2), strides = (2, 2))(conv3)

conv4 = tf.keras.layers.Conv2D(filters = 96, 
                                      kernel_size = (3, 3), 
                                      padding = 'same', 
                                      activation = 'relu')(pool3)

pool4 =tf.keras.layers.MaxPooling2D(pool_size = (2, 2), strides = (2, 2))(conv4)

fltn = tf.keras.layers.Flatten()(pool4)

# dn1 = tf.keras.layers.Dense(512, activation = 'relu')(fltn)
dn2 = tf.keras.layers.Dense(128, activation = 'relu')(fltn)
out = tf.keras.layers.Dense(5, activation = 'softmax')(dn2)

model  = tf.keras.Model(input_layer, out)

from tensorflow.keras.optimizers import Adam
# Compile the model
model.compile(optimizer=Adam(learning_rate=1e-4),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])


# Fit the model using training data

history = model.fit(datagen.flow(X_train, Y_train, batch_size=32),
                    epochs=30,
                    validation_data=(X_test, Y_test),
                    callbacks=[reduce_lr, early_stop])


# saving my model for future uses
model.save('mymodel.h5')

# loading my model

model = tf.keras.models.load_model('mymodel.h5')

# evaluting the model 
model.evaluate(X_test, Y_test, verbose=1)

# make prefdiciton on Testing data 

prediction = model.predict(X_test)

plt.figure(figsize=(10, 7))

for i in range(10):
    plt.subplot(2, 5, i + 1)
    plt.imshow(X_test[i])
    
    actual_label = categories[int(Y_test[i])]  # Convert float32 to int
    predicted_label = categories[np.argmax(prediction[i])]
    
    plt.xlabel('Actual: ' + actual_label + '\nPredicted: ' + predicted_label)
    plt.xticks([])

plt.show()

# Plot training history
plt.figure(figsize=(8, 4))

# Plot Accuracy
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

# Plot Loss
plt.figure(figsize=(8, 4))

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()
