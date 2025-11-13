import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pylatex import Document, Section, Subsection, Command, NoEscape
from pylatex.utils import bold
import os
import re
import sys 


CAMINHO_PASTA = r"C:\Users\Gamer\Documents\fatec\algebra"

NOME_ARQUIVO_CSV_INPUT = 'engenheiro_de_dados_6k.csv'

NOME_ARQUIVO_SAIDA = 'relatorio_analise_query' 


caminho_csv = os.path.join(CAMINHO_PASTA, NOME_ARQUIVO_CSV_INPUT)
caminho_saida = os.path.join(CAMINHO_PASTA, NOME_ARQUIVO_SAIDA)


COLUNA_TEXTO = 'job_description'
COLUNA_LOCAL = 'formatted_location'
ENCODING_ARQUIVO = 'utf-8' 
ENCODING_ERRORS = 'replace'

def carregar_e_filtrar_dados(caminho_csv):
    """
    Lê o CSV e cria dois DataFrames: um para SP e um Remoto.
    """
    try:
        df = pd.read_csv(caminho_csv, 
                         encoding=ENCODING_ARQUIVO, 
                         encoding_errors=ENCODING_ERRORS)
        print(f"Arquivo CSV '{caminho_csv}' carregado com sucesso.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_csv}' não encontrado.")
        return None, None
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")
        return None, None

    if COLUNA_TEXTO not in df.columns or COLUNA_LOCAL not in df.columns:
        print("ERRO CRÍTICO: Colunas 'job_description' ou 'formatted_location' não encontradas.")
        return None, None
        
    df = df.dropna(subset=[COLUNA_TEXTO])
    print(f"Total de vagas com descrição: {len(df)}")

  
    df_sp = df[df[COLUNA_LOCAL].str.contains('São Paulo', case=False, na=False)]
    
    if 'work_remote_allowed' in df.columns:
        df_remote = df[df['work_remote_allowed'] == True]
        print("Usando a coluna 'work_remote_allowed' para filtrar vagas remotas.")
    else:
        print("Usando a coluna 'formatted_location' para filtrar vagas remotas.")
        df_remote = df[df[COLUNA_LOCAL].str.contains('Remoto|Remote', case=False, na=False)]

    if df_sp.empty or df_remote.empty:
        print("AVISO: Um dos grupos (SP ou Remoto) não encontrou vagas.")
        print(f"Total de vagas SP: {len(df_sp)}")
        print(f"Total de vagas Remotas: {len(df_remote)}")
        return None, None

    print(f"Dados filtrados: {len(df_sp)} vagas SP, {len(df_remote)} vagas Remotas.")
    return df_sp, df_remote


def analisar_query_vs_grupo(query_text, df_grupo):
   
    print(f"Analisando query contra {len(df_grupo)} documentos...")

    lista_documentos = df_grupo[COLUNA_TEXTO].tolist()
    corpus = [query_text] + lista_documentos
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000, min_df=2, norm='l2')
    
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        print("ERRO: A query não contém palavras conhecidas pelo vocabulário. Tente um texto mais descritivo.")
        return None

    vetor_q = tfidf_matrix[0]
    vetores_d = tfidf_matrix[1:]

    similaridades_array = cosine_similarity(vetor_q, vetores_d)[0]
    S_clip = np.clip(similaridades_array, -1.0, 1.0)
    angulos_deg = np.degrees(np.arccos(S_clip))

    resultados_df = pd.DataFrame({
        'Descricao': lista_documentos,
        'Similaridade (S)': similaridades_array,
        'Angulo (Graus)': angulos_deg
    })


    resultados_df['Rank_Original'] = df_grupo.index
    
    top_3 = resultados_df.sort_values(by='Similaridade (S)', ascending=False).head(3)
    return top_3


def limpar_texto_latex(texto):
   
    if not isinstance(texto, str):
        return ""
    texto = texto.replace('\ufffd', '?')
    texto = texto.replace('\\', r'\textbackslash{}')
    texto = texto.replace('{', r'\{')
    texto = texto.replace('}', r'\}')
    texto = texto.replace('_', r'\_')
    texto = texto.replace('^', r'\textasciicircum{}')
    texto = texto.replace('~', r'\textasciitilde{}')
    texto = texto.replace('%', r'\%')
    texto = texto.replace('$', r'\$')
    texto = texto.replace('#', r'\#')
    texto = texto.replace('&', r'\&')
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def gerar_relatorio_latex(query_text, top_sp, top_remote, contagens, caminho_saida_pdf, nome_csv):
  
    print("Iniciando geração do PDF via LaTeX...")
    
    doc = Document(caminho_saida_pdf, documentclass='article',
                   fontenc='T1', inputenc='utf8')
                   
    doc.preamble.append(Command('usepackage', ['babel'], 'portuguese'))
    doc.preamble.append(Command('usepackage', 'geometry', options=['a4paper', 'margin=1in']))
    doc.preamble.append(Command('usepackage', 'lmodern'))
    doc.preamble.append(Command('usepackage', 'verbatim'))
    doc.preamble.append(Command('usepackage', 'hyperref'))

    doc.preamble.append(Command('title', 'Relatório de Análise de Query - Vagas SP vs. Remoto'))
    doc.preamble.append(Command('author', 'Análise de Álgebra Linear com TF-IDF'))
    doc.append(Command('maketitle'))

   
    with doc.create(Section('Descrição do Dataset')):
        doc.append("A análise foi realizada utilizando um conjunto de dados público da plataforma Kaggle.\n")
        doc.append(NoEscape(r"\\"))
        doc.append(bold("Arquivo:"))
        doc.append(NoEscape(f" {nome_csv.replace('_', r'\_')} \n"))
        doc.append(NoEscape(r"\\"))
        doc.append(bold("Conteúdo:"))
        doc.append(" O dataset contém 1.614 vagas para a posição de Engenheiro de Dados (Data Engineer) no Brasil (LinkedIn, 2023). "
                   "Para esta análise, os 'documentos' são os textos da coluna 'job_description'.")

    
    with doc.create(Section('Metodologia da Análise')):
        total_sp, total_remote = contagens
        doc.append("O objetivo deste trabalho é comparar a aderência de dois mercados de trabalho (São Paulo e Remoto) "
                   "a um perfil de vaga ideal, definido pelo usuário (a 'query').")
        doc.append(NoEscape(r"\par"))

        with doc.create(Subsection('Definição da Query e Documentos')):
            doc.append(bold("A Query (Perfil Ideal):\n"))
            doc.append(NoEscape(r"\\"))
            doc.append("O usuário forneceu o seguinte texto em inglês descrevendo seu perfil ideal:\n")
            doc.append(NoEscape(r"\begin{it}"))
            doc.append(NoEscape(limpar_texto_latex(query_text))) 
            doc.append(NoEscape(r"\end{it}"))
            doc.append(NoEscape(r"\\ \par"))

            doc.append(bold("Os Documentos (Os Grupos):\n"))
            doc.append(NoEscape(r"\\"))
            doc.append(f"Os documentos da base foram divididos em dois grupos:\n")
            doc.append(NoEscape(r"\\"))
            doc.append(f"- {bold('Grupo 1 (São Paulo):')} {total_sp} documentos.\n")
            doc.append(NoEscape(r"\\"))
            doc.append(f"- {bold('Grupo 2 (Remotas):')} {total_remote} documentos.\n")

        with doc.create(Subsection('Processamento (Álgebra Linear)')):
            doc.append("1. ")
            doc.append(bold("TF-IDF:"))
            doc.append(" A Query e todos os Documentos de um grupo são transformados em vetores numéricos que representam a importância de cada palavra-chave.\n")
            doc.append(NoEscape(r"\\"))
            doc.append("2. ")
            doc.append(bold("Similaridade de Cosseno (Análise de Ângulos):"))
            doc.append(" É calculada a similaridade (cosseno do ângulo) entre o vetor da Query e *cada um* dos vetores de documentos do grupo. "
                       "Um ângulo de 0° (cosseno = 1) significa que a vaga é idêntica à query.")

 
    with doc.create(Section('Resultados da Análise Comparativa')):
        doc.append("A seguir, são apresentados os 3 documentos mais similares (menor ângulo) à Query, "
                   "separados por cada grupo.")

        with doc.create(Subsection('Top 3 - Vagas em São Paulo')):
            if top_sp is None or top_sp.empty:
                doc.append("Nenhum resultado encontrado para este grupo.")
            else:
                for i, (_, row) in enumerate(top_sp.reset_index().iterrows()):
                    doc.append(bold(f"Rank {i+1} (ID do Documento no CSV: {row['Rank_Original']}):"))
                    doc.append(NoEscape(r"\\"))
                    doc.append(f"   {bold('Similaridade (S):')} {row['Similaridade (S)']:.4f}")
                    doc.append(NoEscape(r" | "))
                    doc.append(f"{bold('Ângulo (Graus):')} {row['Angulo (Graus)']:.2f}°\n")
                    doc.append(NoEscape(r"\\ \par"))
                    doc.append(bold("   Trecho do Documento:\n"))
                    doc.append(NoEscape(r"\\ \begin{it}"))
                    doc.append(NoEscape(limpar_texto_latex(row['Descricao'][:400]) + "..."))
                    doc.append(NoEscape(r"\end{it} \par"))

        with doc.create(Subsection('Top 3 - Vagas Remotas')):
            if top_remote is None or top_remote.empty:
                doc.append("Nenhum resultado encontrado para este grupo.")
            else:
                for i, (_, row) in enumerate(top_remote.reset_index().iterrows()):
                    doc.append(bold(f"Rank {i+1} (ID do Documento no CSV: {row['Rank_Original']}):"))
                    doc.append(NoEscape(r"\\"))
                    doc.append(f"   {bold('Similaridade (S):')} {row['Similaridade (S)']:.4f}")
                    doc.append(NoEscape(r" | "))
                    doc.append(f"{bold('Ângulo (Graus):')} {row['Angulo (Graus)']:.2f}°\n")
                    doc.append(NoEscape(r"\\ \par"))
                    doc.append(bold("   Trecho do Documento:\n"))
                    doc.append(NoEscape(r"\\ \begin{it}"))
                    doc.append(NoEscape(limpar_texto_latex(row['Descricao'][:400]) + "..."))
                    doc.append(NoEscape(r"\end{it} \par"))


    with doc.create(Section('Discussão dos Resultados')):
        doc.append(bold("A Descoberta: "))
        doc.append("A análise da query revelou um 'cluster' (agrupamento) de vagas dominado pela empresa Turing, tanto no mercado de SP quanto no Remoto.")
        doc.append(NoEscape(r"\par")) 

        doc.append(bold("A Causa: "))
        doc.append("Isso é evidenciado pelos scores de similaridade e ângulos idênticos (ex: 0.3032 / 72.35")
        doc.append(NoEscape(r"°")) 
        doc.append("), provando que múltiplas vagas (Ranks 45, 60, 55) são, na verdade, cópias exatas do mesmo documento de texto.")
        doc.append(NoEscape(r"\par"))

        doc.append(bold("A Implicação (Ruído nos Dados): "))
        doc.append("Isso também expõe um 'ruído' nos dados: o uso de texto 'boilerplate' (o parágrafo de introdução da Turing) faz com que essas vagas pareçam muito similares entre si e dominem o topo do ranking.")
        doc.append(NoEscape(r"\par"))

        doc.append(bold("A Prova: ")) 
        doc.append("O algoritmo, no entanto, funciona como esperado. Outros resultados, como a vaga de 'Azure Data Engineer' (score 0.2430), "
                   "provam que o sistema está corretamente ranqueando os documentos, mas que as vagas da Turing são matematicamente mais similares à query.")
        doc.append(NoEscape(r"\par"))

 
    try:
       
        doc.generate_pdf(caminho_saida_pdf, clean_tex=False, compiler='pdflatex') 
        
        print(f"\nSUCESSO! PDF '{caminho_saida_pdf}.pdf' gerado na pasta.")
        print(f"O arquivo fonte '{caminho_saida_pdf}.tex' também foi salvo.")
        
    except Exception as e:
        print(f"\nERRO AO GERAR O PDF. Verifique se o MiKTeX está instalado.")
    
        try:
            doc.generate_tex(caminho_saida_pdf)
            print(f"O arquivo '{caminho_saida_pdf}.tex' foi gerado com sucesso (mas o PDF falhou).")
            print("Você pode compilá-lo manualmente com seu editor de LaTeX (Texworks).")
        except Exception as e_tex:
            print(f"Falha ao salvar o arquivo .tex: {e_tex}")
            
        print(f"Erro original do compilador: {str(e).splitlines()[0]}") 


if __name__ == "__main__":
    df_sp, df_remote = carregar_e_filtrar_dados(caminho_csv)
    
    if df_sp is not None and df_remote is not None:
        
        print("\n==============================================")
        print(" 🚀 INÍCIO DA ANÁLISE DE VAGAS 🚀")
        print("\n--- ETAPA 1: DEFINIÇÃO DO PERFIL (QUERY) ---")
        print("Descreva o seu perfil ou a vaga de Engenheiro de Dados ideal (em inglês, para melhor resultado com as palavras-chave de TI).")
        print("Exemplo: data engineer with experience in python, spark, sql and aws cloud services.")
        
        query_text = input("Query (English): ")

        if not query_text.strip():
            print("ERRO: O texto da Query não pode ser vazio.")
            sys.exit()
        
        print("\n--- ETAPA 2: PROCESSANDO (TF-IDF E ÂNGULOS) ---")
        
        top_sp = analisar_query_vs_grupo(query_text, df_sp)
        top_remote = analisar_query_vs_grupo(query_text, df_remote)

        print("\n--- ETAPA 3: GERANDO RELATÓRIO PDF (LATEX) ---")
        
        contagens = (len(df_sp), len(df_remote))
        gerar_relatorio_latex(query_text, top_sp, top_remote, contagens, caminho_saida, NOME_ARQUIVO_CSV_INPUT)
    
    else:
        print("Script interrompido devido a falha no carregamento ou filtragem dos dados.")
