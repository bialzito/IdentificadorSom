"""
treinador_svm.py
Versão simplificada — sem t-SNE.

Treina e avalia um modelo SVM com MFCCs extraídos
pelo 'extrator_features.py', compatível com o projetosom.py.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix

# ======================================
# CONFIGURAÇÕES
# ======================================
ARQUIVO_ENTRADA = r"C:\Users\ninho\Desktop\codigosom\features_passaros.csv"
MAP_LABELS = {1: "sabia", 2: "bemtevi"}  # Igual ao projetosom.py
CATEGORIAS = ["bemtevi", "sabia"]

# ======================================
# CARREGAR DADOS
# ======================================
print(f"Carregando dados de {ARQUIVO_ENTRADA}...")
data = pd.read_csv(ARQUIVO_ENTRADA)

# Filtra apenas as classes desejadas
data = data[data['label'].isin(MAP_LABELS.keys())].copy()

# Converte labels numéricas para texto (iguais ao projetosom.py)
data["classe_str"] = data["label"].map(MAP_LABELS)

# Garante a ordem das colunas
feature_cols = [f"mfcc_{i}" for i in range(13)]
data = data[feature_cols + ["classe_str"]]

X = data[feature_cols].values
y = data["classe_str"].values

# ======================================
# DIVISÃO TREINO/TESTE (igual ao projetosom.py)
# ======================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalização
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ======================================
# TREINAMENTO
# ======================================
print("\nTreinando modelo SVM...")
modelo = SVC(kernel='rbf', gamma='scale', C=1)
modelo.fit(X_train, y_train)

# ======================================
# AVALIAÇÃO
# ======================================
y_pred = modelo.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nAcurácia no conjunto de teste: {acc * 100:.2f}%")

# Matriz de confusão
plt.figure(figsize=(5,4))
cm = confusion_matrix(y_test, y_pred, labels=CATEGORIAS)
sns.heatmap(cm, annot=True, cmap="Blues",
            xticklabels=CATEGORIAS, yticklabels=CATEGORIAS, fmt='d')
plt.title("Matriz de Confusão - SVM")
plt.xlabel("Predito")
plt.ylabel("Real")
plt.show()
