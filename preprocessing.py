import os
import shutil
import random
import hashlib
import time
import stat
from PIL import Image

# ==========================================
# CONFIG
# ==========================================
BASE_DIR = os.getcwd()
DATASET_DIR = os.path.join(BASE_DIR, "Dataset", "IMG_CLASSES")
SPLIT_DIR = os.path.join(BASE_DIR, "Final_Skin_Split")

TRAIN_RATIO = 0.75
VAL_RATIO = 0.15

random.seed(42)

# ==========================================
# SAFE DELETE FUNCTION (Windows Fix)
# ==========================================
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# ==========================================
# STEP 1 — REMOVE EXACT DUPLICATES & CORRUPT
# ==========================================
print("Cleaning dataset (Exact duplicate removal)...")

hashes = {}
removed_duplicates = 0
removed_corrupt = 0

for cls in os.listdir(DATASET_DIR):
    cls_path = os.path.join(DATASET_DIR, cls)

    if not os.path.isdir(cls_path):
        continue

    for file in os.listdir(cls_path):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(cls_path, file)

            try:
                # Verify image
                img = Image.open(path)
                img.verify()

                # Compute file hash
                with open(path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()

                if file_hash in hashes:
                    os.remove(path)
                    removed_duplicates += 1
                else:
                    hashes[file_hash] = path

            except:
                os.remove(path)
                removed_corrupt += 1

print("Duplicates removed:", removed_duplicates)
print("Corrupt removed:", removed_corrupt)

# ==========================================
# STEP 2 — SPLIT FIRST (NO BALANCING)
# ==========================================
print("\nSplitting dataset (75/15/10)...")

TRAIN_DIR = os.path.join(SPLIT_DIR, "train")
VAL_DIR   = os.path.join(SPLIT_DIR, "val")
TEST_DIR  = os.path.join(SPLIT_DIR, "test")

# Delete old split safely
if os.path.exists(SPLIT_DIR):
    shutil.rmtree(SPLIT_DIR, onerror=remove_readonly)
    time.sleep(1)

os.makedirs(TRAIN_DIR)
os.makedirs(VAL_DIR)
os.makedirs(TEST_DIR)

for cls in os.listdir(DATASET_DIR):
    cls_path = os.path.join(DATASET_DIR, cls)
    if not os.path.isdir(cls_path):
        continue

    images = [
        f for f in os.listdir(cls_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    random.shuffle(images)

    total = len(images)
    train_count = int(TRAIN_RATIO * total)
    val_count = int(VAL_RATIO * total)

    train_files = images[:train_count]
    val_files   = images[train_count:train_count+val_count]
    test_files  = images[train_count+val_count:]

    for split_dir, files in zip(
        [TRAIN_DIR, VAL_DIR, TEST_DIR],
        [train_files, val_files, test_files]
    ):
        class_split_path = os.path.join(split_dir, cls)
        os.makedirs(class_split_path, exist_ok=True)

        for f in files:
            shutil.copy(
                os.path.join(cls_path, f),
                os.path.join(class_split_path, f)
            )

print("Split completed.")

# ==========================================
# STEP 3 — BALANCE ONLY TRAIN SET
# ==========================================
print("\nBalancing TRAIN set only...")

class_counts = {}
max_count = 0

for cls in os.listdir(TRAIN_DIR):
    cls_path = os.path.join(TRAIN_DIR, cls)
    count = len(os.listdir(cls_path))
    class_counts[cls] = count
    max_count = max(max_count, count)

print("\nTrain Distribution Before Balancing:")
for cls, count in class_counts.items():
    print(cls, "→", count)

print("\nBalancing each train class to:", max_count)

# Oversample only training classes
for cls in os.listdir(TRAIN_DIR):
    cls_path = os.path.join(TRAIN_DIR, cls)
    images = os.listdir(cls_path)

    while len(os.listdir(cls_path)) < max_count:
        img = random.choice(images)
        src = os.path.join(cls_path, img)

        new_name = f"aug_{random.randint(100000,999999)}_{img}"
        dst = os.path.join(cls_path, new_name)

        shutil.copy(src, dst)

print("Train set balanced successfully!")

# ==========================================
# FINAL DISTRIBUTION
# ==========================================
print("\nFinal Distribution:")

for split in ["train", "val", "test"]:
    print(f"\n{split.upper()}")
    split_path = os.path.join(SPLIT_DIR, split)
    for cls in os.listdir(split_path):
        count = len(os.listdir(os.path.join(split_path, cls)))
        print(cls, "→", count)

print("\nFinal dataset saved at:", SPLIT_DIR)