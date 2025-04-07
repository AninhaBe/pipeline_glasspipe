# Importa as bibliotecas necessárias: pandas para trabalhar com os dados,
# datetime para usar a data atual, os e glob para localizar o arquivo mais recente
import pandas as pd
from datetime import datetime
import os
import glob

# Define uma função chamada processar_silver que transforma os dados brutos em dados limpos e padronizados
def processar_silver():
    # Define o caminho onde estão os arquivos CSV brutos do bronze
    pasta_bronze = "data/bronze/extracao"

    # Busca todos os arquivos CSV da pasta
    arquivos_csv = glob.glob(os.path.join(pasta_bronze, "empresas_*.csv"))

    # Se não encontrar nenhum arquivo, para tudo
    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado em bronze.")
        return

    # Ordena os arquivos por nome (por padrão de data no nome) e pega o mais recente
    arquivos_csv.sort(reverse=True)
    caminho_mais_recente = arquivos_csv[0]

    print(f"Lendo arquivo mais recente: {caminho_mais_recente.replace(os.sep, '/')}")

    # Lê o arquivo CSV para um DataFrame
    df = pd.read_csv(caminho_mais_recente)

    # Remove espaços antes/depois dos nomes das empresas
    df['nome'] = df['nome'].astype(str).str.strip()

    # Substitui vírgula por ponto e converte as notas para float
    df['nota'] = df['nota'].astype(str).str.replace(',', '.').astype(float)

    # Adiciona uma coluna com a data da transformação (data de ingestão)
    df['data_ingestao'] = pd.to_datetime('today').normalize()

    # Cria a pasta silver se não existir
    pasta_silver = "data/silver"
    os.makedirs(pasta_silver, exist_ok=True)

    # Define o caminho final do arquivo parquet
    caminho_parquet = os.path.join(pasta_silver, "empresas.parquet")

    # Salva o DataFrame como parquet
    df.to_parquet(caminho_parquet, index=False)

    # Mostra os primeiros registros e mensagem final
    print(df.head())
    print(f"\nArquivo Parquet salvo em: {caminho_parquet}")
    print(f"Total de registros processados: {len(df)}")

# Executa a função se o arquivo for chamado diretamente
if __name__ == "__main__":
    processar_silver()
