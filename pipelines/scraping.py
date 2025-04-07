# Importa o Playwright (modo síncrono), o pandas (pra manipular tabelas), time (pra pausas), datetime (pra nomear o arquivo) e os (pra criar pastas)
from playwright.sync_api import sync_playwright
import pandas as pd
import time
from datetime import datetime
import os

# Define uma função chamada scrape_glassdoor_empresas, que vai fazer todo o processo de raspagem.
def scrape_glassdoor_empresas():
    # Guarda o endereço da página do Glassdoor que lista as empresas que queremos raspar.
    base_url = "https://www.glassdoor.com.br/Avaliações/index.htm"
    
    # Cria uma lista vazia chamada empresas, onde vamos guardar os dados de cada empresa conforme formos raspando.
    empresas = []

    with sync_playwright() as p:
        # Inicie o Playwright agora, e me dê acesso ao controle dos navegadores (p.chromium, p.firefox, p.webkit) enquanto esse bloco estiver rodando
        browser = p.chromium.launch(headless=False)  # Abra o navegador Chrome de forma visível (modo não headless), pra gente ver o que tá acontecendo.
        page = browser.new_page()  # Abra uma nova aba
        page.goto(base_url)  # Vá para o site do Glassdoor onde estão listadas as empresas.

        while True:  # Rode enquanto tiver páginas com empresas
            page.wait_for_timeout(3000)  # Espera 3 segundos pra garantir que a página carregou direito

            # Pegue todos os blocos (cards) de empresas dessa página.
            cards = page.query_selector_all('div[data-test="employer-card"]')
            print(f"Coletando {len(cards)} empresas...")  # Mostre quantos foram encontrados.

            for card in cards:  # Dentro de cada card de empresa, procure o nome da empresa. Se achar, pegue o texto.
                try:
                    nome_elem = card.query_selector('div[data-test="employer-short-name"]')  # Seleciona o nome
                    nome = nome_elem.inner_text() if nome_elem else None

                    nota_elem = card.query_selector('div[class*="ratingWithText"]')  # Agora procure a nota de avaliação da empresa (tipo '4.2 ★'). Pegue só o número (4.2).
                    nota = nota_elem.inner_text().split()[0] if nota_elem else None

                    # Adicione essa empresa (nome + nota) à lista empresas.
                    empresas.append({
                        "nome": nome,
                        "nota": nota
                    })

                except Exception as e:  # Se der qualquer erro ao tentar extrair os dados de um card, mostra o erro no terminal e continua o scraping.
                    print(f"Erro no card: {e}")
                    continue

            # Tenta clicar no botão "Próxima página"
            try:
                next_button = page.query_selector('button[data-test="next-page"]')  # Se o botão existe e está habilitado, clique nele. Depois espere 3 segundos pra nova página carregar
                if next_button and next_button.is_enabled():
                    next_button.click()
                    page.wait_for_timeout(3000)
                else:
                    print("Fim da paginação.")  # Se não tem mais botão, quer dizer que acabou. Então encerre o loop.
                    break
            except:
                print("Botão 'next-page' não encontrado.")  # Se deu erro tentando achar o botão, encerre o scraping.
                break

        browser.close()  # Feche o navegador quando terminar tudo.

    # Crie uma tabela pandas com todos os dados que a gente guardou.
    df = pd.DataFrame(empresas)

    # Gera o nome do arquivo com a data atual
    data_hoje = datetime.today().strftime('%Y-%m-%d')

    # Cria a pasta data/bronze/extracao se ainda não existir
    pasta_destino = "dados/bronze/extracao"
    os.makedirs(pasta_destino, exist_ok=True)

    # Define o caminho do arquivo com nome baseado na data
    caminho_arquivo = os.path.join(pasta_destino, f"empresas_{data_hoje}.csv")

    # Salve essa tabela como um arquivo .csv
    df.to_csv(caminho_arquivo, index=False)

    # Mostre as 5 primeiras empresas da tabela e também diga quantas foram coletadas no total.
    print(df.head())
    print(f"\nTotal coletado: {len(df)} empresas.")
    print(f"Arquivo salvo em: {caminho_arquivo}")

# Executa a função se o arquivo for chamado diretamente
if __name__ == "__main__":
    scrape_glassdoor_empresas()
