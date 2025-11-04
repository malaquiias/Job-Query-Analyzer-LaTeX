# 🚀 Job Query Analyzer (com LaTeX)

[](https://www.python.org/downloads/)
[](https://scikit-learn.org/)
[](https://www.latex-project.org/)

Um script Python que analisa a similaridade de vagas de emprego usando TF-IDF e gera automaticamente um relatório formal em LaTeX.

Este projeto foi desenvolvido como trabalho para a disciplina de **Álgebra Linear**, aplicando modelos de espaço vetorial (TF-IDF) e similaridade de cosseno para uma análise de dados do mundo real.

-----

## 📖 Índice

  * [🎯 Sobre o Projeto](https://www.google.com/search?q=%23-sobre-o-projeto)
  * [🛠️ Tecnologias Utilizadas](https://www.google.com/search?q=%23-tecnologias-utilizadas)
  * [✨ Funcionalidades](https://www.google.com/search?q=%23-funcionalidades)
  * [🔬 Metodologia (Como Funciona)](https://www.google.com/search?q=%23-metodologia-como-funciona)
  * [🏁 Começando (Instalação e Uso)](https://www.google.com/search?q=%23-come%C3%A7ando-instala%C3%A7%C3%A3o-e-uso)
      * [Pré-requisitos](https://www.google.com/search?q=%23pr%C3%A9-requisitos)
      * [Instalação](https://www.google.com/search?q=%23instala%C3%A7%C3%A3o)
      * [Executando](https://www.google.com/search?q=%23executando)
  * [📈 Análise e Descobertas](https://www.google.com/search?q=%23-an%C3%A1lise-e-descobertas)

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

  * Carrega um grande dataset de vagas do Kaggle.
  * Filtra os dados em dois grupos de análise (SP vs. Remoto).
  * Solicita interativamente uma "query" (perfil de vaga) ao usuário via terminal.
  * Aplica a vetorização TF-IDF para criar um espaço vetorial de palavras-chave.
  * Calcula a Similaridade de Cosseno (o ângulo) entre a query e todos os documentos.
  * Identifica os 3 documentos Top 3 mais similares em cada grupo.
  * **Gera automaticamente um relatório `relatorio_analise_query.pdf` e o código-fonte `relatorio_analise_query.tex`** com os resultados e a análise.

## 🔬 Metodologia (Como Funciona)

O fluxo de análise do script segue 5 etapas principais:

1.  **Carregar Dados:** O arquivo `engenheiro_de_dados_6k.csv` é lido com o Pandas.
2.  **Filtrar Grupos:** O DataFrame é dividido em dois: `df_sp` (vagas contendo "São Paulo" na localização) e `df_remote` (vagas com `work_remote_allowed == True`).
3.  **Obter Query:** O script pausa e pede ao usuário para digitar o perfil de vaga ideal.
4.  **Vetorizar (TF-IDF):** Para cada grupo, um "corpus" (coleção de textos) é criado, contendo a *query* e as *descrições das vagas* daquele grupo. O `TfidfVectorizer` transforma esse corpus em uma matriz de vetores.
5.  **Calcular Similaridade (Ângulos):** O script extrai o vetor da query (índice 0 da matriz) e os vetores das vagas (índice 1 em diante). A `cosine_similarity` é usada para calcular o cosseno do ângulo entre a query e cada vaga.
6.  **Gerar Relatório:** Os resultados do Top 3 de cada grupo, junto com os metadados da análise (contagem de vagas, a query, etc.), são passados para a biblioteca `PyLaTeX`, que escreve o arquivo `.tex` e chama o compilador `pdflatex` (do MiKTeX) para gerar o `.pdf` final.

## 📈 Análise e Descobertas

Uma descoberta chave da análise (detalhada no relatório gerado) foi a identificação de um "ruído" significativo nos dados:

> **A Descoberta:** A análise da query revelou um 'cluster' (agrupamento) de vagas dominado pela empresa Turing, tanto no mercado de SP quanto no Remoto.
>
> **A Causa:** Isso é evidenciado pelos scores de similaridade e ângulos idênticos (ex: 0.3032 / 72.35°), provando que múltiplas vagas (Ranks 45, 60, 55) são, na verdade, cópias exatas do mesmo documento de texto.
>
> **A Implicação (Ruído nos Dados):** Isso também expõe um 'ruído' nos dados: o uso de texto 'boilerplate' (o parágrafo de introdução da Turing) faz com que essas vagas pareçam muito similares entre si e dominem o topo do ranking.
>
> **A Prova:** O algoritmo, no entanto, funciona como esperado. Outros resultados, como a vaga de 'Azure Data Engineer' (score 0.2430), provam que o sistema está corretamente ranqueando os documentos.