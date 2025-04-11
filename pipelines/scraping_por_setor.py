import os
import json
import time
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

# Caminho do arquivo JSON com os setores
CAMINHO_SETORES = "config/setores.json"

# Função para salvar logs
def salvar_log(nome_setor, mensagem):
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{datetime.today().strftime('%Y-%m-%d')}.log", "a", encoding="utf-8") as f:
        f.write(f"[{nome_setor}] {mensagem}\n")

# Função principal
def scraping_por_setores():
    with open(CAMINHO_SETORES, "r", encoding="utf-8") as f:
        setores = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for id_setor, info in setores.items():
            nome_setor = info["nome"]
            tipo = info["tipo"]
            print(f"\n🔍 Iniciando scraping para o setor: {nome_setor}")
            empresas = []

            # Define a URL correta
            if tipo == "sector":
                url = f"https://www.glassdoor.com.br/Avaliacoes/index.htm?filterType=RATING_OVERALL&sector={id_setor}&page=1"
            else:
                url = f"https://www.glassdoor.com.br/Avaliacoes/index.htm?filterType=RATING_OVERALL&industry={id_setor}&page=1"

            page = browser.new_page()
            try:
                page.goto(url)
            except Exception as e:
                salvar_log(nome_setor, f"Falha ao acessar a URL: {e}")
                page.close()
                continue

            while True:
                time.sleep(3)
                cards = page.query_selector_all('div[data-test="employer-card"]')
                print(f"🔍 Coletando {len(cards)} empresas do setor: {nome_setor}")

                for card in cards:
                    try:
                        nome_elem = card.query_selector('div[data-test="employer-short-name"]')
                        nota_elem = card.query_selector('div[class*="ratingWithText"]')

                        nome = nome_elem.inner_text() if nome_elem else None
                        nota = nota_elem.inner_text().split()[0] if nota_elem else None

                        if nome:
                            empresas.append({
                                "nome": nome,
                                "nota": nota,
                                "setor": nome_setor,
                                "data_ingestao": datetime.today().strftime('%Y-%m-%d')
                            })

                    except Exception as e:
                        salvar_log(nome_setor, f"⚠Erro ao processar card: {e}")
                        continue

                try:
                    next_button = page.query_selector('button[data-test="next-page"]')
                    if next_button and next_button.is_enabled():
                        next_button.click()
                    else:
                        break
                except:
                    break

            page.close()

            if not empresas:
                salvar_log(nome_setor, "⚠Nenhuma empresa encontrada.")
                continue

            df = pd.DataFrame(empresas)

            nome_pasta = nome_setor.lower().replace(" ", "_").replace("ç", "c").replace("ã", "a") \
                                           .replace("á", "a").replace("â", "a").replace("ê", "e") \
                                           .replace("é", "e").replace("í", "i").replace("ó", "o") \
                                           .replace("ô", "o").replace("ú", "u").replace("ü", "u") \
                                           .replace("&", "e")

            pasta_destino = f"data/bronze/setor/{nome_pasta}"
            os.makedirs(pasta_destino, exist_ok=True)

            df.to_csv(os.path.join(pasta_destino, f"empresas_{datetime.today().strftime('%Y-%m-%d')}.csv"), index=False)
            df.to_parquet(os.path.join(pasta_destino, f"empresas_{datetime.today().strftime('%Y-%m-%d')}.parquet"), index=False)
            df.to_json(os.path.join(pasta_destino, f"empresas_{datetime.today().strftime('%Y-%m-%d')}.json"), orient="records", force_ascii=False)

            salvar_log(nome_setor, f"{len(df)} empresas coletadas.")

        browser.close()

if __name__ == "__main__":
    scraping_por_setores()
