# -*- coding: utf-8 -*-
"""anomaly_detection_NSL_KDD.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Z8AHb2qzHzd5ISjOog_2RLjfYnr9eSVD
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc
from sklearn.ensemble import StackingClassifier

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid")

file_path_full_training_set = 'KDDTrain+.txt'
file_path_test = 'KDDTest+.txt'

df = pd.read_csv(file_path_full_training_set)
test_df = pd.read_csv(file_path_test)

columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack', 'level']
df.columns = columns
test_df.columns = columns

df['attack_flag'] = df['attack'].apply(lambda a: 0 if a == 'normal' else 1)
test_df['attack_flag'] = test_df['attack'].apply(lambda a: 0 if a == 'normal' else 1)

features_to_encode = ['protocol_type', 'service', 'flag']
encoded = pd.get_dummies(df[features_to_encode])
test_encoded = pd.get_dummies(test_df[features_to_encode])

to_fit = encoded.join(df[['duration', 'src_bytes', 'dst_bytes']])
test_set = test_encoded.join(test_df[['duration', 'src_bytes', 'dst_bytes']])

binary_y = df['attack_flag']
test_binary_y = test_df['attack_flag']

binary_train_X, binary_val_X, binary_train_y, binary_val_y = train_test_split(to_fit, binary_y, test_size=0.6)

base_classifiers = [
    ('lr', LogisticRegression()),
    ('knn', KNeighborsClassifier()),
    ('rf', RandomForestClassifier()),
    ('svc', SVC(probability=True)),
    ('xgb', XGBClassifier())
]

final_rf = RandomForestClassifier()
stacking_clf = StackingClassifier(estimators=base_classifiers, final_estimator=final_rf)

stacking_clf.fit(binary_train_X, binary_train_y)
stacking_binary_predictions = stacking_clf.predict(binary_val_X)

base_rf_score = accuracy_score(binary_val_y, stacking_binary_predictions)
print("Binary Classification Accuracy:", base_rf_score)

accuracy_scores = cross_val_score(stacking_clf, binary_train_X, binary_train_y, cv=5)
print("Cross-validated Accuracy Scores:", accuracy_scores)

stacking_binary_predictions = stacking_clf.predict(binary_val_X)

precision = precision_score(binary_val_y, stacking_binary_predictions)
recall = recall_score(binary_val_y, stacking_binary_predictions)
f1 = f1_score(binary_val_y, stacking_binary_predictions)

print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)

metrics = ['Precision', 'Recall', 'F1 Score']
values = [precision, recall, f1]

plt.figure(figsize=(8, 5))
ax = sns.barplot(x=metrics, y=values, color="blue")

for i, v in enumerate(values):
    ax.text(i, v + 0.02, f"{v:.2f}", color='black', ha='center')

plt.title('Model Performance Metrics')
plt.ylabel('Score')
plt.ylim(0, 1.1)
plt.show()

conf_matrix = confusion_matrix(binary_val_y, stacking_binary_predictions)
print("Confusion Matrix:\n", conf_matrix)

labels = ['Negative', 'Positive']

plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()

stacking_binary_probabilities = stacking_clf.predict_proba(binary_val_X)[:, 1]

fpr, tpr, thresholds = roc_curve(binary_val_y, stacking_binary_probabilities)

auc_score = auc(fpr, tpr)
print("AUC Score:", auc_score)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label='ROC curve (AUC = %0.2f)' % auc_score)
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()
