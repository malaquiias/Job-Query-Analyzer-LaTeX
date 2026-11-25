"""Compara uma query (perfil de vaga ideal) com vagas de Engenheiro de Dados.

Usa TF-IDF e similaridade de cosseno para ranquear as vagas de dois grupos
(São Paulo e Remotas) e gera um relatório em LaTeX/PDF com os resultados.

Uso:
    python analise.py                       # pede a query no terminal
    python analise.py --query "data engineer with python and sql"
"""

import argparse
import os
import re
import sys

import numpy as np
import pandas as pd
from pylatex import Command, Document, NoEscape, Section, Subsection
from pylatex.utils import bold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CAMINHO_PASTA = os.path.dirname(os.path.abspath(__file__))
NOME_ARQUIVO_CSV_INPUT = "engenheiro_de_dados_6k.csv"
NOME_ARQUIVO_SAIDA = "relatorio_analise_query"

COLUNA_TEXTO = "job_description"
COLUNA_LOCAL = "formatted_location"
TOP_K = 3
K_RUIDO = 10  # quantas posições do topo olhar para medir o efeito das cópias


def carregar_dados(caminho_csv):
    """Lê o CSV e remove as vagas sem descrição."""
    df = pd.read_csv(caminho_csv, encoding="utf-8", encoding_errors="replace")
    faltando = {COLUNA_TEXTO, COLUNA_LOCAL} - set(df.columns)
    if faltando:
        raise ValueError(f"colunas não encontradas no CSV: {sorted(faltando)}")
    return df.dropna(subset=[COLUNA_TEXTO])


def remover_duplicatas(df):
    """Remove linhas repetidas em duas etapas e devolve o DataFrame limpo e as contagens.

    1. Mesmo ``job_id``: a mesma vaga extraída mais de uma vez.
    2. Mesma descrição: vagas diferentes publicadas com o texto idêntico
       (ex.: uma empresa que repete o anúncio em várias cidades).
    """
    contagens = {"total": len(df)}
    if "job_id" in df.columns:
        df = df.drop_duplicates(subset="job_id")
    contagens["sem_id_repetido"] = len(df)
    df = df.drop_duplicates(subset=COLUNA_TEXTO)
    contagens["sem_texto_repetido"] = len(df)
    return df, contagens


def separar_grupos(df):
    """Divide as vagas em São Paulo e Remotas."""
    df_sp = df[df[COLUNA_LOCAL].str.contains("São Paulo", case=False, na=False)]
    if "work_remote_allowed" in df.columns:
        df_remote = df[df["work_remote_allowed"] == True]  # noqa: E712 (coluna pode ter NaN)
    else:
        df_remote = df[df[COLUNA_LOCAL].str.contains("Remoto|Remote", case=False, na=False)]
    return df_sp, df_remote


def ranquear(query_text, df_grupo, k=TOP_K):
    """Devolve as ``k`` vagas do grupo mais similares à query.

    A query e as descrições do grupo formam um corpus; o TF-IDF é ajustado nesse
    corpus e a similaridade de cosseno é calculada entre a query e cada vaga.
    """
    corpus = [query_text] + df_grupo[COLUNA_TEXTO].tolist()
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, min_df=2, norm="l2")
    tfidf = vectorizer.fit_transform(corpus)
    if tfidf[0].nnz == 0:
        raise ValueError(
            "nenhuma palavra da query está no vocabulário das vagas. "
            "Tente um texto mais descritivo, em inglês."
        )

    sim = cosine_similarity(tfidf[0], tfidf[1:])[0]
    resultado = df_grupo.assign(
        similaridade=sim,
        angulo=np.degrees(np.arccos(np.clip(sim, -1.0, 1.0))),
    )
    return resultado.sort_values("similaridade", ascending=False).head(k)


def copias_no_topo(query_text, df_grupo_bruto, k=K_RUIDO):
    """Quantas das ``k`` primeiras posições, sem limpar os dados, são cópias de outra."""
    topo = ranquear(query_text, df_grupo_bruto, k)
    return k - topo[COLUNA_TEXTO].nunique()


def limpar_texto_latex(texto):
    """Escapa os caracteres especiais do LaTeX e junta espaços repetidos."""
    if not isinstance(texto, str):
        return ""
    trocas = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "_": r"\_",
        "^": r"\textasciicircum{}",
        "~": r"\textasciitilde{}",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "&": r"\&",
    }
    texto = texto.replace("�", "?")
    texto = "".join(trocas.get(c, c) for c in texto)
    return re.sub(r"\s+", " ", texto).strip()


def escrever_top(doc, titulo, top):
    """Escreve uma subseção com o top-k de um grupo."""
    with doc.create(Subsection(titulo)):
        for posicao, (indice, row) in enumerate(top.iterrows(), start=1):
            cargo = limpar_texto_latex(row.get("title")) or "Cargo não informado"
            empresa = limpar_texto_latex(row.get("company_name")) or "empresa não informada"
            doc.append(NoEscape(rf"\textbf{{{posicao}. {cargo}}} ({empresa}, linha {indice} do CSV)\\"))
            doc.append(NoEscape(
                rf"Similaridade: {row['similaridade']:.4f} \quad "
                rf"Ângulo: {row['angulo']:.2f}\textdegree\\"
            ))
            trecho = limpar_texto_latex(row[COLUNA_TEXTO][:400])
            doc.append(NoEscape(rf"\textit{{{trecho}...}}\par\medskip"))


def gerar_relatorio(query_text, resultados, contagens, caminho_saida, nome_csv):
    """Monta o documento LaTeX e tenta compilar o PDF."""
    doc = Document(caminho_saida, documentclass="article", fontenc="T1", inputenc="utf8")
    doc.preamble.append(Command("usepackage", "babel", options="portuguese"))
    doc.preamble.append(Command("usepackage", "geometry", options=["a4paper", "margin=1in"]))
    doc.preamble.append(Command("usepackage", "hyperref"))
    doc.preamble.append(Command("title", "Relatório de Análise de Query - Vagas SP vs. Remoto"))
    doc.preamble.append(Command("author", "Análise de Álgebra Linear com TF-IDF"))
    doc.append(Command("maketitle"))

    nome_csv_tex = limpar_texto_latex(nome_csv)
    removidas_id = contagens["total"] - contagens["sem_id_repetido"]
    removidas_texto = contagens["sem_id_repetido"] - contagens["sem_texto_repetido"]

    with doc.create(Section("Descrição do Dataset")):
        doc.append(NoEscape(
            rf"Dataset público do Kaggle com vagas de Engenheiro de Dados no Brasil "
            rf"(LinkedIn, 2023), arquivo \texttt{{{nome_csv_tex}}}. "
            rf"Os documentos são os textos da coluna \texttt{{job\_description}}.\par"
        ))
        with doc.create(Subsection("Limpeza: vagas duplicadas")):
            doc.append(NoEscape(
                rf"O arquivo tem {contagens['total']} linhas com descrição. "
                rf"{removidas_id} são a mesma vaga (mesmo \texttt{{job\_id}}) extraída mais de uma vez, "
                rf"e outras {removidas_texto} são vagas diferentes com o texto idêntico. "
                rf"Depois de remover as duas, restam {contagens['sem_texto_repetido']} descrições únicas, "
                rf"que são as usadas no ranking.\par"
            ))

    with doc.create(Section("Metodologia")):
        doc.append(NoEscape(r"\textbf{Query (perfil ideal):} \textit{"
                            + limpar_texto_latex(query_text) + r"}\par\medskip"))
        doc.append(NoEscape(
            rf"\textbf{{Grupos:}} São Paulo ({len(resultados['sp']['grupo'])} vagas) e "
            rf"Remotas ({len(resultados['remoto']['grupo'])} vagas).\par\medskip"
        ))
        doc.append(NoEscape(
            r"\textbf{TF-IDF:} a query e as vagas de cada grupo viram vetores com o peso de cada "
            r"palavra. \textbf{Similaridade de cosseno:} mede o ângulo entre o vetor da query e o "
            r"de cada vaga; ângulo de 0\textdegree{} (cosseno 1) seria um texto idêntico.\par"
        ))

    with doc.create(Section(f"Resultados: top {TOP_K} de cada grupo")):
        escrever_top(doc, "Vagas em São Paulo", resultados["sp"]["top"])
        escrever_top(doc, "Vagas Remotas", resultados["remoto"]["top"])

    with doc.create(Section("Discussão")):
        melhor_sp = resultados["sp"]["top"]["similaridade"].max()
        melhor_rem = resultados["remoto"]["top"]["similaridade"].max()
        grupo_melhor = "São Paulo" if melhor_sp >= melhor_rem else "Remotas"
        doc.append(NoEscape(
            rf"Para esta query, a vaga mais aderente está no grupo \textbf{{{grupo_melhor}}} "
            rf"(similaridade {max(melhor_sp, melhor_rem):.4f}, contra "
            rf"{min(melhor_sp, melhor_rem):.4f} no outro grupo).\par\medskip"
        ))
        doc.append(NoEscape(
            rf"\textbf{{Efeito das duplicatas:}} sem a limpeza, das {K_RUIDO} primeiras posições "
            rf"{resultados['sp']['copias']} seriam cópias de outra vaga em São Paulo e "
            rf"{resultados['remoto']['copias']} nas Remotas. Cópias têm exatamente o mesmo score, "
            r"então ocupam o topo do ranking sem trazer informação nova.\par"
        ))

    try:
        doc.generate_pdf(caminho_saida, clean_tex=False, compiler="pdflatex")
        print(f"\nPDF gerado: {caminho_saida}.pdf (fonte em {caminho_saida}.tex)")
    except Exception as e:  # pdflatex ausente ou erro de compilação
        doc.generate_tex(caminho_saida)
        print(f"\nNão foi possível gerar o PDF ({str(e).splitlines()[0]}).")
        print(f"O arquivo {caminho_saida}.tex foi salvo; compile com pdflatex.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--query", help="perfil de vaga ideal, em inglês")
    parser.add_argument("--csv", default=os.path.join(CAMINHO_PASTA, NOME_ARQUIVO_CSV_INPUT))
    args = parser.parse_args()

    df_bruto = carregar_dados(args.csv)
    df, contagens = remover_duplicatas(df_bruto)
    print(f"{contagens['total']} vagas no CSV -> {contagens['sem_texto_repetido']} descrições únicas.")

    query_text = args.query
    if not query_text:
        print("Descreva a vaga de Engenheiro de Dados ideal, em inglês.")
        print("Exemplo: data engineer with experience in python and sql")
        query_text = input("Query: ")
    if not query_text.strip():
        sys.exit("ERRO: a query não pode ser vazia.")

    resultados = {}
    grupos_limpos = dict(zip(("sp", "remoto"), separar_grupos(df)))
    grupos_brutos = dict(zip(("sp", "remoto"), separar_grupos(df_bruto)))
    for nome, grupo in grupos_limpos.items():
        if grupo.empty:
            sys.exit(f"ERRO: o grupo '{nome}' não tem vagas.")
        resultados[nome] = {
            "grupo": grupo,
            "top": ranquear(query_text, grupo),
            "copias": copias_no_topo(query_text, grupos_brutos[nome]),
        }

    gerar_relatorio(
        query_text,
        resultados,
        contagens,
        os.path.join(CAMINHO_PASTA, NOME_ARQUIVO_SAIDA),
        os.path.basename(args.csv),
    )


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"ERRO: {e}")
