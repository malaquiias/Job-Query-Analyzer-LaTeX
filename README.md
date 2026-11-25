# 🚀 Job Query Analyzer (com LaTeX)

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-orange)
![LaTeX](https://img.shields.io/badge/LaTeX-PyLaTeX-008080)

Um script Python que analisa a similaridade de vagas de emprego usando TF-IDF e gera automaticamente um relatório formal em LaTeX.

Este projeto foi desenvolvido como trabalho para a disciplina de **Álgebra Linear**, aplicando modelos de espaço vetorial (TF-IDF) e similaridade de cosseno para uma análise de dados do mundo real.

-----

## 📖 Índice

  * [🎯 Sobre o Projeto](#-sobre-o-projeto)
  * [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
  * [✨ Funcionalidades](#-funcionalidades)
  * [🔬 Metodologia (Como Funciona)](#-metodologia-como-funciona)
  * [🏁 Como Executar](#-como-executar)
  * [📈 Análise e Descobertas](#-análise-e-descobertas)

-----

## 🎯 Sobre o Projeto

Este projeto tem como objetivo aplicar os conceitos de Álgebra Linear para analisar e comparar textos. O script recebe uma **"query"** (um perfil de vaga ideal) definida pelo usuário e a compara com dois grupos de "documentos" (descrições de vagas reais):

1.  **Grupo 1:** Vagas em São Paulo
2.  **Grupo 2:** Vagas Remotas

O algoritmo calcula a similaridade entre a query do usuário e cada vaga nos dois grupos, ranqueia os resultados e, por fim, gera um relatório completo em **`.pdf`** e **`.tex`** usando `PyLaTeX`, pronto para ser entregue.

## 🛠️ Tecnologias Utilizadas

  * **Python 3.9+**
  * **Pandas:** Para carregar e filtrar o dataset (`.csv`).
  * **Scikit-learn (sklearn):** Para a vetorização `TfidfVectorizer` e cálculo de `cosine_similarity`.
  * **Numpy:** Para operações matemáticas e angulares (`arccos`).
  * **PyLaTeX:** Para gerar dinamicamente o código-fonte `.tex` do relatório.
  * **MiKTeX / TeX Live:** (Dependência externa) O compilador LaTeX necessário para converter o `.tex` em `.pdf` automaticamente.

## ✨ Funcionalidades

  * Carrega o dataset de vagas do Kaggle (LinkedIn, 2023).
  * **Remove vagas duplicadas** em duas etapas: mesma vaga extraída mais de uma vez (`job_id`) e vagas com texto idêntico.
  * Filtra os dados em dois grupos de análise (SP vs. Remoto).
  * Recebe a "query" (perfil de vaga) pelo terminal ou pelo argumento `--query`.
  * Aplica TF-IDF e calcula a similaridade de cosseno (e o ângulo) entre a query e cada vaga.
  * Gera `relatorio_analise_query.pdf` e `.tex` com o top 3 de cada grupo e uma discussão **calculada a partir dos resultados** da query usada.

## 🔬 Metodologia (Como Funciona)

1.  **Carregar e limpar:** lê `engenheiro_de_dados_6k.csv` e remove as duplicatas.
2.  **Filtrar grupos:** `df_sp` (localização contém "São Paulo") e `df_remote` (`work_remote_allowed == True`).
3.  **Vetorizar (TF-IDF):** para cada grupo, o corpus é a query + as descrições do grupo.
4.  **Similaridade de cosseno:** compara o vetor da query (linha 0) com cada vaga e converte em ângulo (`arccos`).
5.  **Medir o ruído:** roda o mesmo ranking nos dados sem limpeza e conta quantas das 10 primeiras posições seriam cópias.
6.  **Gerar relatório:** monta o documento com `PyLaTeX` e compila com `pdflatex`.

## 🏁 Como Executar

Pré-requisitos: Python 3.9+ e uma distribuição LaTeX com `pdflatex` (MiKTeX ou TeX Live). Sem LaTeX, o script salva só o `.tex`.

```bash
pip install -r requirements.txt
python analise.py --query "data engineer with experience in python and sql"
```

Sem `--query`, o script pede o texto no terminal.

## 📈 Análise e Descobertas

**1. Mais da metade do dataset era duplicada.** Das 1.614 linhas, 812 são a mesma vaga extraída duas vezes (mesmo `job_id`) e outras 38 repetem o texto de outra vaga. Sobram **764 descrições únicas**.

**2. Sem limpar, as cópias dominam o topo.** Na primeira versão do trabalho, o ranking da query de exemplo trazia scores idênticos em posições seguidas (ex.: 0.2691 / 74.39° em duas vagas de SP). Eram cópias do mesmo texto. Medindo isso no código: sem a limpeza, das 10 primeiras posições, **5 seriam cópias em SP e 8 nas Remotas**.

**3. Texto padrão ("boilerplate") ainda pesa.** Mesmo depois da limpeza, o top 3 remoto é todo de vagas da Turing, cujos anúncios começam com o mesmo parágrafo de apresentação. O TF-IDF não diferencia esse parágrafo do conteúdo da vaga.

Resultado da query de exemplo (`data engineer with experience in python and sql`):

| Grupo | Vagas únicas | Melhor similaridade | Ângulo |
|---|---:|---:|---:|
| São Paulo | 363 | 0.1863 | 79.26° |
| Remotas | 86 | 0.3236 | 71.12° |

### Limitações e próximos passos

  * Quase-duplicatas (o mesmo anúncio com um cabeçalho diferente) não são removidas: o 2º e o 3º lugar de SP são a mesma vaga da Thomson Reuters. Dá para tratar com um limiar de similaridade entre as próprias vagas.
  * Parte dos textos do CSV original já vem com caracteres corrompidos (`�`).
  * `min_df=2` descarta palavras da query que não aparecem em pelo menos 2 documentos.
  * A query precisa estar em inglês por causa das *stop words*, mas parte das vagas está em português.

O arquivo `analise_dos_resultados.pdf` é a análise entregue na disciplina, feita sobre a primeira versão do script (antes da remoção de duplicatas).
