import os
import pandas as pd
import numpy as np

dataset_dir = r"G:\My Drive\dreamt_dataset\physionet.org\files\dreamt\2.1.0\data_100Hz"
processed_dir = r"G:\My Drive\dreamt_dataset\processed"

os.makedirs(processed_dir, exist_ok=True)

subjects_to_process = [f"S{str(i).zfill(3)}" for i in range(24, 35)]

def already_processed(subject_id, processed_path):
    x_file = os.path.join(processed_path, f"{subject_id}_X.npy")
    y_file = os.path.join(processed_path, f"{subject_id}_y.npy")
    return os.path.exists(x_file) and os.path.exists(y_file)

def process_and_save(subject_ids, src_path, dst_path):
    for subj in subject_ids:
        if already_processed(subj, dst_path):
            print(f"{subj} already processed, skipping...")
            continue
        file_path = os.path.join(src_path, f"{subj}_PSG_df_updated.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            X = df.drop(['TIMESTAMP', 'Sleep_Stage'], axis=1).values
            y = df['Sleep_Stage'].values
            np.save(os.path.join(dst_path, f"{subj}_X.npy"), X)
            np.save(os.path.join(dst_path, f"{subj}_y.npy"), y)
            print(f"Processed and saved data for {subj}")
        else:
            print(f"Warning: File {file_path} missing, skipping...")

process_and_save(subjects_to_process, dataset_dir, processed_dir)

all_subjects = [i for i in range(2, 35) if i not in [22, 23]]
split_ratio = 0.8
split_index = int(len(all_subjects) * split_ratio)
train_subject_ids = all_subjects[:split_index]
val_subject_ids = all_subjects[split_index:]
train_subjects = [f"S{str(i).zfill(3)}" for i in train_subject_ids]
val_subjects = [f"S{str(i).zfill(3)}" for i in val_subject_ids]

def compute_norm_stats_incremental(subjects, processed_path):
    count = 0
    mean = 0
    M2 = 0
    for subj in subjects:
        X = np.load(os.path.join(processed_path, f"{subj}_X.npy"))
        n = X.shape[0]
        count_new = count + n
        mean_new = (mean * count + np.sum(X, axis=0)) / count_new
        M2_new = M2 + np.sum((X - mean)**2, axis=0) + count * n * (mean - mean_new)**2 / count_new
        mean = mean_new
        M2 = M2_new
        count = count_new
    variance = M2 / count
    std = np.sqrt(variance) + 1e-8
    return mean, std

mean_std_file = os.path.join(processed_dir, "train_norm_stats.npz")

if os.path.exists(mean_std_file):
    stats = np.load(mean_std_file)
    mean_train = stats['mean']
    std_train = stats['std']
else:
    mean_train, std_train = compute_norm_stats_incremental(train_subjects, processed_dir)
    np.savez(mean_std_file, mean=mean_train, std=std_train)

def normalize_data(subjects, processed_path, mean, std):
    for subj in subjects:
        norm_path = os.path.join(processed_path, f"{subj}_X_norm.npy")
        if os.path.exists(norm_path):
            print(f"Normalization already done for {subj}, skipping.")
            continue
        X_path = os.path.join(processed_path, f"{subj}_X.npy")
        X = np.load(X_path)
        X_norm = (X - mean) / std
        np.save(norm_path, X_norm)
        print(f"Normalized data saved for {subj}")

normalize_data(train_subjects, processed_dir, mean_train, std_train)
normalize_data(val_subjects, processed_dir, mean_train, std_train)
