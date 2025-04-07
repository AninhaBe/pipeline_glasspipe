from playwright.sync_api import sync_playwright
import pandas as pd
import time
from datetime import datetime
import os

# Define uma função que vai raspar os dados de empresas, filtrando por um setor específico
def scrape_empresas_por_setor(setor_nome):
    base_url = "https://www.glassdoor.com.br/Avaliações/index.htm"
    empresas = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(base_url)

        # Aguarda o campo de setor aparecer
        page.wait_for_selector('input[data-test="industries-autocomplete-input"]')

        # Digita o setor e espera as sugestões carregarem
        input_setor = page.query_selector('input[data-test="industries-autocomplete-input"]')
        input_setor.fill(setor_nome)
        time.sleep(2)

        # Pressiona seta pra baixo + Enter pra selecionar o primeiro da lista
        input_setor.press("ArrowDown")
        input_setor.press("Enter")

        # Espera a página carregar com os resultados filtrados
        page.wait_for_timeout(4000)

        while True:
            cards = page.query_selector_all('div[data-test="employer-card"]')
            print(f"🔍 Coletando {len(cards)} empresas do setor: {setor_nome}")

            for card in cards:
                try:
                    nome_elem = card.query_selector('div[data-test="employer-short-name"]')
                    nome = nome_elem.inner_text() if nome_elem else None

                    nota_elem = card.query_selector('div[class*="ratingWithText"]')
                    nota = nota_elem.inner_text().split()[0] if nota_elem else None

                    empresas.append({
                        "nome": nome,
                        "nota": nota,
                        "setor": setor_nome
                    })

                except Exception as e:
                    print(f"Erro ao processar card: {e}")
                    continue

            # Tenta avançar pra próxima página
            try:
                next_button = page.query_selector('button[data-test="next-page"]')
                if next_button and next_button.is_enabled():
                    next_button.click()
                    page.wait_for_timeout(3000)
                else:
                    print("✅ Fim da paginação.")
                    break
            except:
                print("⛔ Botão 'next-page' não encontrado.")
                break

        browser.close()

    # Cria pasta de destino (bronze + nome do setor)
    data_hoje = datetime.today().strftime('%Y-%m-%d')
    pasta_destino = f"data/bronze/setor/{setor_nome.lower().replace(' ', '_')}"
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_destino, f"empresas_{data_hoje}.csv")

    # Salva os dados
    df = pd.DataFrame(empresas)
    df.to_csv(caminho_arquivo, index=False)

    print(df.head())
    print(f"\n💾 Dados salvos em: {caminho_arquivo}")
    print(f"📊 Total de empresas coletadas: {len(df)}")


# Rodar diretamente
if __name__ == "__main__":
    # Teste com 1 setor (você pode mudar esse nome depois)
    scrape_empresas_por_setor("Tecnologia da informação")
