"""
treinar_modelo_final.py
-----------------------
Carrega 100% dos dados de features (com augmentation e SK),
treina o modelo SVM vencedor (com os melhores hiperparâmetros)
e salva o modelo final ("o cérebro") num ficheiro .joblib.
"""

import pandas as pd
import os
import joblib  # Para salvar o modelo
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline # Vamos usar um Pipeline!

# ======================================
# CONFIGURAÇÕES
# ======================================
ARQUIVO_ENTRADA = os.path.join(os.getcwd(), "features_passaros_AUG_SK.csv")
ARQUIVO_SAIDA_MODELO = os.path.join(os.getcwd(), "svm_passaros_v1.joblib")
MAP_LABELS = {1: "sabia", 2: "bemtevi"}

# ======================================
# PARÂMETROS VENCEDORES DO GRIDSEARCHCV
# (Já inseridos a partir dos seus resultados)
# ======================================
PARAMETROS_SVM = {
    'C': 10,
    'gamma': 'scale',
    'kernel': 'rbf',
    'probability': True  # Importante para prever probab.
}

# ======================================
# CARREGAR DADOS
# ======================================
print(f"Carregando 100% dos dados de {ARQUIVO_ENTRADA}...")
if not os.path.exists(ARQUIVO_ENTRADA):
    print(f"!!! ERRO: Arquivo de features não encontrado: {ARQUIVO_ENTRADA}")
    print("Por favor, execute o script 'extrator_features.py' (com augmentation) primeiro.")
    exit()
    
data = pd.read_csv(ARQUIVO_ENTRADA)

data = data[data['label'].isin(MAP_LABELS.keys())].copy()
data["classe_str"] = data["label"].map(MAP_LABELS)

excluir_cols = ['label', 'classe_str', 'arquivo_origem']
feature_cols = [col for col in data.columns if col not in excluir_cols]

# Prepara 100% dos dados
X_final = data[feature_cols].values
y_final = data["classe_str"].values

print(f"Total de {len(y_final)} amostras carregadas para o treino final.")
print(f"Usando {len(feature_cols)} features (ex: 91).")

# ======================================
# TREINAMENTO FINAL (COM PIPELINE)
# ======================================
# Usar um "Pipeline" é a forma correta.
# Ele junta o Normalizador (Scaler) + o Modelo (SVM) num
# único objeto. Isso evita erros de normalização no futuro.

print("\nCriando pipeline final (StandardScaler + SVM)...")

# O "pipeline" diz:
# 1. 'scaler': Sempre normalize os dados
# 2. 'svm': Depois, aplique o SVM
pipeline_final = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(**PARAMETROS_SVM)) # Desempacota os parâmetros
])

print("Iniciando treinamento final com 100% dos dados...")
# Aqui, ele normaliza E treina, tudo de uma vez.
pipeline_final.fit(X_final, y_final)

# ======================================
# SALVAR O MODELO
# ======================================
print(f"\nTreinamento concluído! Salvando modelo em {ARQUIVO_SAIDA_MODELO}")
joblib.dump(pipeline_final, ARQUIVO_SAIDA_MODELO)

print("\n--- SUCESSO ---")
print("O seu modelo final ('o cérebro') está salvo!")
print(f"Pode agora carregar '{ARQUIVO_SAIDA_MODELO}' em outro app para fazer previsões.")