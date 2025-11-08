# Classificador de Sons com IA
> **Status:** Projeto em desenvolvimento — novas funcionalidades e melhorias estão sendo implementadas continuamente.

Projeto desenvolvido em **Python 3.13.9** para **classificar sons automaticamente** (como pássaros ou outros áudios) usando **Inteligência Artificial**.  
O sistema utiliza **MFCCs** (Mel-Frequency Cepstral Coefficients) para extrair características do som e um **classificador SVM** para reconhecer padrões.

---

## Objetivo

Criar um modelo de aprendizado de máquina capaz de **identificar sons diferentes** a partir de arquivos de áudio.  
O projeto pode ser expandido para novas categorias ou sensores IoT.

---

## Tecnologias Utilizadas

- **Python 3.13.9**  
- **Librosa** — extração de MFCCs (características de áudio)  
- **SoundFile** — leitura e gravação de arquivos `.wav`  
- **NumPy / Pandas** — manipulação de dados  
- **Scikit-learn** — treinamento e avaliação com SVM  
- **Matplotlib / Seaborn** — visualização e matriz de confusão  
- **Requests / OS** — automação e manipulação de diretórios  

---

## Funcionamento do Projeto

1. **Extração de características (MFCCs):**  
   O script `extrator_features.py` percorre as pastas de áudio, extrai 13 coeficientes MFCC de cada som e salva em `features_passaros.csv`.

2. **Treinamento e avaliação:**  
   O script `treinador_svm.py` lê o CSV, divide em treino e teste, normaliza os dados e treina um modelo **SVM**.  
   Ao final, mostra a **acurácia** e a **matriz de confusão**.

3. **Execução automática (opcional):**  
   O script `rodar_no_github.py` baixa os áudios, executa a extração e depois treina o modelo automaticamente.

---

## Instalação e Execução

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

## Equipe

| Integrante | Função |
|-------------|--------|
| **Denival Biotto Filho** | Back End (Desenvolvimento de Código) |
| **Filipe Gomes Ferreira** | Back End (Desenvolvimento de Código) |
| **Filipy Tavares dos Santos** | Front End (HTML) |
| **Naum Calebe Félix Sarti** | Front End (Design e Interface) |
| **Luan Vitor Pereira Rocha** | IoT (Desenvolvimento de Sensores e Coleta de Dados) |
| **Luiz Otávio Machado Seles** | IoT (Integração de Dispositivo) |
| **Pedro Azevedo Batista (Piphoka)** | Apresentação, Pesquisa Teórica e Integração |
| **Rafael Magesto** | Modelo 3D do IoT |
| **Luis Henrique da Silva** | Dados |

---

## Divisão de Trabalho

Embora a divisão de trabalho do nosso grupo seja organizada, é importante destacar que não há uma separação rígida de funções entre os membros.  
Trabalhamos de forma colaborativa e presencial, com a flexibilidade de desempenharmos várias funções conforme as demandas do projeto.  
Essa abordagem nos permite ser mais dinâmicos e eficientes, já que todos contribuem ativamente em diversas áreas, dependendo da necessidade do momento.  
De forma geral, entretanto, as tarefas foram divididas de acordo com a seguinte organização, que servirá como um guia para nossa execução.

| Integrante | Responsabilidade |
|-------------|------------------|
| **Denival Biotto Filho** | Desenvolver o código responsável pela identificação de sons, explorando diferentes métodos de aprendizado de máquina para melhorar a precisão do sistema. |
| **Filipe Gomes Ferreira** | Desenvolver o código responsável pela identificação de sons, focando em transformar o áudio em informações que o sistema possa entender e analisar. |
| **Filipy Tavares dos Santos** | Desenvolver a estrutura básica da interface. |
| **Naum Calebe Félix Sarti** | Criar design gráfico e interface do usuário para uma experiência intuitiva. |
| **Luan Vitor Pereira Rocha** | Desenvolver o sensor IoT e integrar a captura de dados acústicos com o sistema. |
| **Luiz Otávio Machado Seles** | Responsável pelo armazenamento dos dados e pelo envio ao backend. |
| **Pedro Azevedo Batista (Piphoka)** | Realizar pesquisa teórica sobre características dos sons (como brilho, textura, etc.) e coordenar a apresentação que os integrantes farão do projeto. |
| **Rafael Magesto** | Desenvolver o modelo 3D do dispositivo IoT utilizado no projeto. |
| **Luis Henrique da Silva** | Coletar dados de áudio e construir uma base de dados para o desenvolvimento e aprimoramento do sistema. |

---

## Dependências (requirements.txt)

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

## Licença e Créditos

Projeto desenvolvido para fins **educacionais e experimentais**.  
Os áudios utilizados foram obtidos de repositórios públicos, incluindo o projeto [FilipyTav/IdentificadorSom](https://github.com/FilipyTav/IdentificadorSom).  
Todos os direitos reservados aos autores.

---

## Observações

- Certifique-se de estar utilizando o **Python 3.13.9**.  
- Os scripts criam automaticamente os arquivos necessários na primeira execução.  
- Para reproduzir resultados, mantenha o mesmo ambiente de dependências indicado acima.
