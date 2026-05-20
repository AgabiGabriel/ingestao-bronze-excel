import pandas as pd
import os

# ==============================================================================
# CONFIGURAÇÕES DO PIPELINE (PREENCHA COM OS SEUS DADOS)
# ==============================================================================
DIRETORIO_ORIGEM = "/seu/caminho/no/lakehouse/Files/sua_pasta_de_origem/"
CATALOGO_DESTINO = "seu_catalogo"   # Ex: nome_do_lakehouse
SCHEMA_DESTINO   = "dbo"            # Padrão no Fabric, ou seu schema personalizado
PREFIXO_TABELA   = "brz_"           # Prefixo para identificar a camada Bronze
MODO_ESCRITA     = "overwrite"      # 'overwrite' para sobrescrever ou 'append' para anexar
# ==============================================================================

# Lista todos os arquivos presentes no diretório configurado
arquivos_na_pasta = os.listdir(DIRETORIO_ORIGEM)

for arquivo in arquivos_na_pasta:
    
    # Isola o processamento estritamente para arquivos do Excel
    if arquivo.endswith(".xlsx"):
        print(f"Iniciando processamento do arquivo: {arquivo}...")
        
        # Consolida o caminho completo do arquivo atual
        caminho_arquivo = os.path.join(DIRETORIO_ORIGEM, arquivo)
        
        # 1. LEITURA ESTRITA: Força todas as colunas como string (dtype=str)
        # Evita que o Pandas trunque zeros à esquerda de IDs ou códigos textuais.
        df_pandas = pd.read_excel(caminho_arquivo, dtype=str)
        
        # 2. LIMPEZA: Remove linhas fantasma (completamente vazias no fim do Excel)
        df_pandas = df_pandas.dropna(how='all')
        
        # 3. TRATAMENTO: Substitui valores nulos (NaN) por strings vazias
        # Garante consistência de tipos na conversão para o ecossistema Spark.
        df_pandas = df_pandas.fillna("")
        
        # Normaliza o tipo dos cabeçalhos das colunas como string para o motor do Spark
        df_pandas.columns = df_pandas.columns.astype(str)
        
        # 4. CONVERSÃO: Transforma o DataFrame local do Pandas em Spark DataFrame distribuído
        df_spark = spark.createDataFrame(df_pandas)
        
        # 5. NOMENCLATURA: Trata o nome do arquivo para o padrão de tabela SQL (snake_case)
        nome_limpo_tabela = arquivo.replace(".xlsx", "").lower()
        nome_final_tabela = f"{PREFIXO_TABELA}{nome_limpo_tabela}"
        
        # 6. PERSISTÊNCIA: Grava os dados no catálogo de dados no formato Delta Lake
        caminho_tabela_catalogo = f"{CATALOGO_DESTINO}.{SCHEMA_DESTINO}.{nome_final_tabela}"
        
        print(f"Gravando dados na tabela Delta: {caminho_tabela_catalogo}...")
        
        # Linha de gravação (Remova o '#' para ativar no seu ambiente de produção)
        # df_spark.write.format("delta").mode(MODO_ESCRITA).saveAsTable(caminho_tabela_catalogo)
        
        print(f"Sucesso: Tabela '{nome_final_tabela}' integrada de forma resiliente.\n")