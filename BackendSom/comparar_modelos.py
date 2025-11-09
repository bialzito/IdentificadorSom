"""
comparar_modelos.py (Versão 2.1 - Corrigida)
-------------------
Compara diferentes algoritmos de classificação (SVM, Árvore de Decisão,
Random Forest e Rede Neural MLP) usando GridSearchCV para encontrar
os melhores hiperparâmetros para cada um.

Usa o conjunto de features com estatísticas.
"""
#Antes de usar o código lembre de dar o comando pip install -r requirements.txt

import pandas as pd
import numpy as np # Necessário para o np.prod
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

# ======================================
# CONFIGURAÇÕES
# ======================================
ARQUIVO_ENTRADA = os.path.join(os.getcwd(), "features_passaros_AUG_SK.csv'")
ARQUIVO_SAIDA = os.path.join(os.getcwd(), "resultados_modelos.csv")
MAP_LABELS = {1: "sabia", 2: "bemtevi"}

# ======================================
# CARREGAR DADOS
# ======================================
if not os.path.exists(ARQUIVO_ENTRADA):
    raise FileNotFoundError(f"Arquivo de features não encontrado: {ARQUIVO_ENTRADA}")

print(f"Carregando dados de {ARQUIVO_ENTRADA}...")
data = pd.read_csv(ARQUIVO_ENTRADA)

data = data[data['label'].isin(MAP_LABELS.keys())].copy()
data["classe_str"] = data["label"].map(MAP_LABELS)

excluir_cols = ['label', 'classe_str', 'arquivo_origem']
feature_cols = [col for col in data.columns if col not in excluir_cols]

print(f"Encontradas {len(feature_cols)} features para o treinamento.")

X = data[feature_cols].values
y = data["classe_str"].values

# ======================================
# DIVISÃO TREINO/TESTE
# ======================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalização
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ======================================
# NOVA FUNÇÃO DE TREINAMENTO (com GridSearch)
# ======================================
def treinar_e_avaliar_grid(nome, grid_search_obj):
    """
    Executa o GridSearchCV, mede o tempo, e reporta
    os melhores parâmetros e a acurácia no conjunto de TESTE.
    """
    print(f"\n--- Iniciando Otimização para: {nome} ---")
    
    # --- LINHA CORRIGIDA ---
    # Em vez de ler 'cv_results_' (que ainda não existe),
    # calculamos as combinações a partir do 'param_grid' (que já existe).
    try:
        param_values = grid_search_obj.param_grid.values()
        combinations = int(np.prod([len(v) for v in param_values]))
        print(f"Testando {combinations} combinações...")
    except:
        # Fallback caso algo dê errado no cálculo
        print("Iniciando testes...")
    # --- FIM DA CORREÇÃO ---
    
    inicio = time.time()
    grid_search_obj.fit(X_train, y_train) # É AQUI QUE A MÁGICA (E A DEMORA) ACONTECE
    tempo_busca = time.time() - inicio
    
    # Pega o melhor modelo encontrado
    melhor_modelo = grid_search_obj.best_estimator_
    
    print(f"Melhores parâmetros encontrados: {grid_search_obj.best_params_}")
    
    # Avalia o *melhor modelo* no conjunto de TESTE
    inicio_pred = time.time()
    y_pred = melhor_modelo.predict(X_test)
    tempo_pred = time.time() - inicio_pred
    
    acc = accuracy_score(y_test, y_pred)
    
    print(f"Acurácia no TESTE (Otimizada): {acc * 100:.2f}% | "
          f"Tempo Total (Busca): {tempo_busca:.2f}s")
    
    return {
        "Modelo": nome,
        "Acurácia (%)": round(acc * 100, 2),
        "Tempo de Treino/Busca (s)": round(tempo_busca, 2),
        "Melhores Parâmetros": str(grid_search_obj.best_params_)
    }

# ======================================
# DEFINIÇÃO DOS "ESPAÇOS de BUSCA"
# ======================================
# Define os "botões" que o GridSearchCV vai testar
# n_jobs=-1 usa todos os núcleos do PC. cv=3 faz 3 "pastas" de validação
cv_folds = 3  # Use 3 para ser mais rápido, ou 5 para mais precisão
n_jobs = -1

# 1. SVM
params_svm = {
    'C': [1, 10, 100], 
    'gamma': ['scale', 0.1],
    'kernel': ['rbf'] # 'linear' tende a ser pior para dados complexos
}
grid_svm = GridSearchCV(SVC(probability=True), params_svm, n_jobs=n_jobs, cv=cv_folds)

# 2. Árvore de Decisão
params_tree = {
    'criterion': ['gini', 'entropy'], 
    'max_depth': [None, 10, 20, 30]
}
grid_tree = GridSearchCV(DecisionTreeClassifier(random_state=42), params_tree, n_jobs=n_jobs, cv=cv_folds)

# 3. Random Forest
params_rf = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 30],
    'criterion': ['gini', 'entropy']
}
grid_rf = GridSearchCV(RandomForestClassifier(random_state=42), params_rf, n_jobs=n_jobs, cv=cv_folds)

# 4. Rede Neural (MLP)
params_mlp = {
    'hidden_layer_sizes': [(50,), (100, 50), (100, 100)],
    'activation': ['relu', 'tanh'],
    'alpha': [0.0001, 0.001]
}
grid_mlp = GridSearchCV(MLPClassifier(max_iter=500, random_state=42), params_mlp, n_jobs=n_jobs, cv=cv_folds)

# Lista de todos os "trabalhos" de otimização
grids_para_rodar = {
    "SVM": grid_svm,
    "Árvore de Decisão": grid_tree,
    "Random Forest": grid_rf,
    "Rede Neural (MLP)": grid_mlp
}

resultados = []

print("\n=== INICIANDO OTIMIZAÇÃO DE HIPERPARÂMETROS (GridSearchCV) ===")
print(f"Atenção: Este processo vai demorar. (Usando {cv_folds} folds de validação)")

for nome, grid_obj in grids_para_rodar.items():
    resultado = treinar_e_avaliar_grid(nome, grid_obj) # Chama a nova função
    resultados.append(resultado)

# ======================================
# SALVAR RESULTADOS
# ======================================
df_resultados = pd.DataFrame(resultados)
df_resultados = df_resultados.sort_values(by="Acurácia (%)", ascending=False)
df_resultados.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")

print(f"\nResultados salvos em: {ARQUIVO_SAIDA}")
print("\n=== PLACAR FINAL (OTIMIZADO) ===")
print(df_resultados)

# ======================================
# GRÁFICO DE ACURÁCIA
# ======================================
plt.figure(figsize=(10, 6)) # Aumentei o tamanho
sns.barplot(data=df_resultados, x="Modelo", y="Acurácia (%)")
plt.title("Comparação de Acurácia (Modelos Otimizados)")
plt.ylim(0, 105)
for i, v in enumerate(df_resultados["Acurácia (%)"]):
    plt.text(i, v + 1, f"{v:.2f}%", ha='center', fontsize=10)
plt.tight_layout()
plt.show()