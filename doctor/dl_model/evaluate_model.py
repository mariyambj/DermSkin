import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

from torchvision import models, transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
    auc,
    accuracy_score
)
from sklearn.preprocessing import label_binarize

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------------------------------------------------------
# DATASET PATH
# -------------------------------------------------------

TEST_DIR = "../../Dataset/test"   # change if needed

IMG_SIZE = 224
BATCH_SIZE = 32

# -------------------------------------------------------
# TRANSFORMS
# -------------------------------------------------------

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485,0.456,0.406],
        [0.229,0.224,0.225]
    )
])

dataset = ImageFolder(TEST_DIR, transform=transform)

loader = DataLoader(
    dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class_names = dataset.classes
num_classes = len(class_names)

print("Class Order:", class_names)

# -------------------------------------------------------
# MODEL ARCHITECTURE
# -------------------------------------------------------

def build_model():

    model = models.densenet169(weights=None)

    model.classifier = nn.Sequential(
        nn.Dropout(0.5),
        nn.Linear(model.classifier.in_features,512),
        nn.BatchNorm1d(512),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(512,num_classes)
    )

    return model

# -------------------------------------------------------
# LOAD TRAINED MODEL
# -------------------------------------------------------

model = build_model()

model.load_state_dict(
    torch.load("best_densenet_mixup.pth", map_location=DEVICE)
)

model.to(DEVICE)
model.eval()

# -------------------------------------------------------
# PREDICTION LOOP
# -------------------------------------------------------

all_preds=[]
all_labels=[]
all_probs=[]

with torch.no_grad():

    for images,labels in loader:

        images = images.to(DEVICE)

        outputs = model(images)

        probs = torch.softmax(outputs,dim=1)

        preds = torch.argmax(outputs,dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.numpy())
        all_probs.extend(probs.cpu().numpy())

all_preds=np.array(all_preds)
all_labels=np.array(all_labels)
all_probs=np.array(all_probs)

# -------------------------------------------------------
# ACCURACY
# -------------------------------------------------------

acc = accuracy_score(all_labels,all_preds)

print("\nTest Accuracy:",acc)

# -------------------------------------------------------
# PRECISION RECALL F1
# -------------------------------------------------------

print("\nClassification Report\n")

print(
    classification_report(
        all_labels,
        all_preds,
        target_names=class_names
    )
)

# -------------------------------------------------------
# CONFUSION MATRIX WITH COUNTS
# -------------------------------------------------------

cm = confusion_matrix(all_labels,all_preds)

plt.figure(figsize=(10,8))

plt.imshow(cm, interpolation='nearest')
plt.title("Confusion Matrix")
plt.colorbar()

tick_marks = np.arange(num_classes)

plt.xticks(tick_marks,class_names,rotation=90)
plt.yticks(tick_marks,class_names)

# add numbers inside cells
thresh = cm.max()/2

for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(
            j,
            i,
            format(cm[i,j],'d'),
            horizontalalignment="center",
            color="white" if cm[i,j] > thresh else "black"
        )

plt.ylabel("Actual Label")
plt.xlabel("Predicted Label")

plt.tight_layout()
plt.show()

# -------------------------------------------------------
# ROC CURVE
# -------------------------------------------------------

y_bin = label_binarize(all_labels,classes=range(num_classes))

plt.figure()

for i in range(num_classes):

    fpr,tpr,_ = roc_curve(
        y_bin[:,i],
        all_probs[:,i]
    )

    roc_auc = auc(fpr,tpr)

    plt.plot(
        fpr,
        tpr,
        label=f"{class_names[i]} AUC={roc_auc:.2f}"
    )

plt.plot([0,1],[0,1],'k--')

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title("ROC Curve")

plt.legend()
plt.show()

# -------------------------------------------------------
# PRECISION RECALL CURVE
# -------------------------------------------------------

plt.figure()

for i in range(num_classes):

    precision,recall,_ = precision_recall_curve(
        y_bin[:,i],
        all_probs[:,i]
    )

    plt.plot(
        recall,
        precision,
        label=class_names[i]
    )

plt.xlabel("Recall")
plt.ylabel("Precision")

plt.title("Precision Recall Curve")

plt.legend()
plt.show()

# -------------------------------------------------------
# F1 SCORE CURVE
# -------------------------------------------------------

plt.figure()

for i in range(num_classes):

    precision,recall,thr = precision_recall_curve(
        y_bin[:,i],
        all_probs[:,i]
    )

    f1 = 2*(precision*recall)/(precision+recall+1e-8)

    plt.plot(thr,f1[:-1],label=class_names[i])

plt.xlabel("Threshold")
plt.ylabel("F1 Score")

plt.title("F1 Score Curve")

plt.legend()
plt.show()