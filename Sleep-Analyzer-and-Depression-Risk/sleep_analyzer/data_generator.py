# import tensorflow as tf
#
# gpus = tf.config.list_physical_devices('GPU')
# if gpus:
#     print(f"CUDA-enabled GPU(s) found: {gpus}")
# else:
#     print("No CUDA-enabled GPU detected. CUDA connection not established.")

from tensorflow.keras.utils import Sequence
import numpy as np
import os
import tensorflow as tf

label_map = {
    'W': 0,
    'N1': 1,
    'N2': 2,
    'N3': 3,
    'R': 4,
    'P': 5,
    'Missing': 6,
    'nan': 6
}
num_classes = len(set(label_map.values()))

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
        for i, (subj, start_index) in enumerate(batch_window_indices):
            X_path = os.path.join(self.processed_dir, f"{subj}_X_norm.npy")
            y_path = os.path.join(self.processed_dir, f"{subj}_y.npy")
            X = np.load(X_path, allow_pickle=True)
            y = np.load(y_path, allow_pickle=True)
            end_index = start_index + self.window_size
            X_window = X[start_index:end_index, :]
            window_label = y[end_index - 1]
            if window_label is None or (isinstance(window_label, float) and np.isnan(window_label)):
                X_batch[i] = np.zeros((self.window_size, 30, 1))
                y_batch[i] = np.zeros(self.num_classes)
                continue
            if window_label not in label_map:
                X_batch[i] = np.zeros((self.window_size, 30, 1))
                y_batch[i] = np.zeros(self.num_classes)
                continue
            X_window_reshaped = X_window[:, :, np.newaxis]
            label_int = label_map[window_label]
            y_cat = tf.keras.utils.to_categorical(label_int, self.num_classes)
            X_batch[i] = X_window_reshaped
            y_batch[i] = y_cat
        return X_batch, y_batch
