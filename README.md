# 🎧 Classificador de Sons com IA
> 🚧 **Status:** Projeto em desenvolvimento — novas funcionalidades e melhorias estão sendo implementadas continuamente.

Projeto desenvolvido em **Python 3.13.9** para **classificar sons automaticamente** (como pássaros ou outros áudios) usando **Inteligência Artificial**.  
O sistema utiliza **MFCCs** (Mel-Frequency Cepstral Coefficients) para extrair características do som e um **classificador SVM** para reconhecer padrões.

---

## 🎯 Objetivo

Criar um modelo de aprendizado de máquina capaz de **identificar sons diferentes** a partir de arquivos de áudio.  
O projeto pode ser expandido para novas categorias ou sensores IoT.

---

## ⚙️ Tecnologias Utilizadas

- **Python 3.13.9**  
- **Librosa** — extração de MFCCs (características de áudio)  
- **SoundFile** — leitura e gravação de arquivos `.wav`  
- **NumPy / Pandas** — manipulação de dados  
- **Scikit-learn** — treinamento e avaliação com SVM  
- **Matplotlib / Seaborn** — visualização e matriz de confusão  
- **Requests / OS** — automação e manipulação de diretórios  

---

## 🧠 Funcionamento do Projeto

1. **Extração de características (MFCCs):**  
   O script `extrator_features.py` percorre as pastas de áudio, extrai 13 coeficientes MFCC de cada som e salva em `features_passaros.csv`.

2. **Treinamento e avaliação:**  
   O script `treinador_svm.py` lê o CSV, divide em treino e teste, normaliza os dados e treina um modelo **SVM**.  
   Ao final, mostra a **acurácia** e a **matriz de confusão**.

3. **Execução automática (opcional):**  
   O script `rodar_no_github.py` baixa os áudios, executa a extração e depois treina o modelo automaticamente.

---

## 🧩 Instalação e Execução

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Rodar o projeto
```bash
python rodar_no_github.py
```

Ou, manualmente:

```bash
python extrator_features.py
python treinador_svm.py
```

---

## 👥 Equipe

| Integrante | Função | Responsabilidades |
|-------------|--------|-------------------|
| **Denival Biotto Filho** | Back End | Desenvolvimento principal do código e integração. |
| **Filipe Gomes Ferreira** | Back End | Processamento de áudio e testes. |
| **Filipy Tavares dos Santos** | Front End (HTML) | Estrutura da interface básica. |
| **Naum Calebe Félix Sarti** | Front End (Design) | Design visual do sistema. |
| **Luan Vitor Pereira Rocha** | IoT (Sensores) | Desenvolvimento do sensor acústico. |
| **Luiz Otávio Machado Seles** | IoT (Integração) | Comunicação entre sensores e backend. |
| **Pedro Azevedo Batista (Piphoka)** | Pesquisa / Apresentação | Pesquisa teórica e organização da apresentação. |
| **Rafael Magesto** | Modelo 3D | Criação do modelo físico do dispositivo. |
| **Luis Henrique da Silva** | Dados | Coleta e organização dos áudios. |

---

## 📦 Dependências (requirements.txt)

```txt
numpy==2.1.3
pandas==2.2.3
librosa==0.10.2.post1
soundfile==0.12.1
scikit-learn==1.5.2
matplotlib==3.9.2
seaborn==0.13.2
requests==2.32.3
```

---

## 🧾 Licença e Créditos

Projeto desenvolvido para fins **educacionais e experimentais**.  
Os áudios utilizados foram obtidos de repositórios públicos, incluindo o projeto [FilipyTav/IdentificadorSom](https://github.com/FilipyTav/IdentificadorSom).  
Todos os direitos reservados aos autores.

---

## 💡 Observações

- Certifique-se de estar utilizando o **Python 3.13.9**.  
- Os scripts criam automaticamente os arquivos necessários na primeira execução.  
- Para reproduzir resultados, mantenha o mesmo ambiente de dependências indicado acima.
