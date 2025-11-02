import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Input, Conv2D, DepthwiseConv2D, BatchNormalization, Activation, AveragePooling2D, Dropout, SeparableConv2D, Reshape, Conv1D, Add, LayerNormalization, GlobalAveragePooling1D, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.utils import Sequence

# ------------------- Configuration -------------------
#processed_dir = 'G:\My Drive\dreamt_dataset\processed'  # Path to your preprocessed normalized data in Google Drive
processed_dir = r'G:\My Drive\dreamt_dataset\processed'

train_subjects = [f"S{str(i).zfill(3)}" for i in range(2, 27) if i not in [22, 23]]
val_subjects = [f"S{str(i).zfill(3)}" for i in range(27, 35)]

batch_size = 32
window_size = 128
num_classes = 7
input_shape = (window_size, 30, 1)  # Must match your preprocessed data shape

# ------------------- Data Generator -------------------
class EEGBatchGenerator(Sequence):
    def __init__(self, subject_list, processed_dir, batch_size=32, shuffle=True, num_classes=7, window_size=128, overlap=0):
        self.subject_list = subject_list
        self.processed_dir = processed_dir
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.num_classes = num_classes
        self.window_size = window_size
        self.overlap = overlap
        self.step_size = window_size - overlap

        self._calculate_window_indices()
        self.on_epoch_end()

    def _calculate_window_indices(self):
        self.window_indices = []
        for subj in self.subject_list:
            y_path = os.path.join(self.processed_dir, f"{subj}_y.npy")
            y = np.load(y_path, allow_pickle=True)
            num_samples = len(y)
            num_windows = (num_samples - self.window_size) // self.step_size + 1
            for i in range(num_windows):
                start_index = i * self.step_size
                self.window_indices.append((subj, start_index))

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.window_indices)

    def __len__(self):
        return int(np.floor(len(self.window_indices) / self.batch_size))

    def __getitem__(self, batch_index):
        batch_window_indices = self.window_indices[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        X_batch, y_batch = self.__data_generation(batch_window_indices)
        return X_batch, y_batch

    def __data_generation(self, batch_window_indices):
        X_batch = np.empty((self.batch_size, self.window_size, 30, 1))
        y_batch = np.empty((self.batch_size, self.num_classes), dtype=int)

        label_map = {'W':0, 'N1':1, 'N2':2, 'N3':3, 'R':4, 'P':5, 'Missing':6, 'nan':6}

        for i, (subj, start_index) in enumerate(batch_window_indices):
            X = np.load(os.path.join(self.processed_dir, f"{subj}_X_norm.npy"))
            y = np.load(os.path.join(self.processed_dir, f"{subj}_y.npy"), allow_pickle=True)
            end_index = start_index + self.window_size
            X_window = X[start_index:end_index, :]
            window_label = y[end_index - 1]

            if window_label not in label_map:
                X_batch[i] = np.zeros((self.window_size, 30, 1))
                y_batch[i] = np.zeros(self.num_classes)
                continue

            X_batch[i] = X_window[:, :, np.newaxis]
            label_int = label_map[window_label]
            y_batch[i] = tf.keras.utils.to_categorical(label_int, self.num_classes)

        return X_batch, y_batch

# ------------------- Model Definition -------------------
def EEGNet(input_shape, dropoutRate=0.5):
    inputs = Input(shape=input_shape)
    x = Conv2D(16, (1, 64), padding='same', use_bias=False)(inputs)
    x = BatchNormalization()(x)
    x = DepthwiseConv2D((input_shape[1], 1), use_bias=False, depth_multiplier=2, padding='valid')(x)
    x = BatchNormalization()(x)
    x = Activation('elu')(x)
    x = AveragePooling2D((1, 4))(x)
    x = Dropout(dropoutRate)(x)
    x = SeparableConv2D(32, (1, 16), padding='same', use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('elu')(x)
    x = AveragePooling2D((1, 7))(x)
    x = Dropout(dropoutRate)(x)
    x = Reshape((-1, 32))(x)
    model = Model(inputs=inputs, outputs=x)
    return model

def TCN_Block(x, filters, kernel_size, dilation_rate, dropout_rate=0.1):
    conv1 = Conv1D(filters, kernel_size, padding='causal', dilation_rate=dilation_rate, activation='relu')(x)
    conv1 = LayerNormalization()(conv1)
    conv1 = Dropout(dropout_rate)(conv1)
    conv2 = Conv1D(filters, kernel_size, padding='causal', dilation_rate=dilation_rate, activation='relu')(conv1)
    conv2 = LayerNormalization()(conv2)
    conv2 = Dropout(dropout_rate)(conv2)
    if x.shape[-1] != filters:
        x = Conv1D(filters, 1, padding='same')(x)
    out = Add()([conv2, x])
    out = Activation('relu')(out)
    return out

def build_combined_model(input_shape, num_classes):
    eeg_model = EEGNet(input_shape)
    tcn_input = eeg_model.output
    tcn = TCN_Block(tcn_input, 64, 3, 1)
    tcn = TCN_Block(tcn, 64, 3, 2)
    tcn = TCN_Block(tcn, 64, 3, 4)
    x = GlobalAveragePooling1D()(tcn)
    x = Dropout(0.5)(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=eeg_model.input, outputs=outputs)
    return model

# ------------------- Training -------------------
def setup_gpu():
    K.clear_session()
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"Using GPU: {[gpu.name for gpu in gpus]}")
    else:
        print("GPU not found, using CPU.")

def main():
    setup_gpu()
    train_gen = EEGBatchGenerator(train_subjects, processed_dir, batch_size=batch_size,
                                  window_size=window_size, shuffle=True, num_classes=num_classes)
    val_gen = EEGBatchGenerator(val_subjects, processed_dir, batch_size=batch_size,
                                window_size=window_size, shuffle=False, num_classes=num_classes)

    model = build_combined_model(input_shape, num_classes)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ModelCheckpoint('best_sleep_model.h5', monitor='val_accuracy', save_best_only=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    ]

    model.fit(train_gen, validation_data=val_gen, epochs=20, callbacks=callbacks, verbose=1)

if __name__ == "__main__":
    main()
