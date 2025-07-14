import asyncio
import httpx
import pandas as pd
from pprint import pprint
from amazon_scraper import amazon_scrap
from beleza_scraper import beleza_na_web_scrape
from magalu_scraper import magalu_scrap

API_ENDPOINT = "http://127.0.0.1:8000/api/urls/"

async def get_from_api():
    async with httpx.AsyncClient() as client:
        try:
            print(f"🔎 Enviando GET para {API_ENDPOINT}")
            response = await client.get(API_ENDPOINT, timeout=10)
            print(f"[API] Resposta recebida. Status: {response.status_code}")
            if response.status_code != 200:
                print(f"[API] Erro na API: {response.text}")
                return None
            response_data = response.json()
            print(f"[API] Dados recebidos:")
            pprint(response_data)
            if isinstance(response_data, list):
                return pd.DataFrame(response_data)
            else:
                print(f"[API] Resposta não é uma lista: {response_data}")
                return None
        except httpx.RequestError as e:
            print(f"❌ Erro ao conectar com a API: {e}")
            return None
        except ValueError as e:
            print(f"❌ Erro ao processar JSON: {e}")
            return None

async def main():
    print(f"\n📋 Executando requisição GET para {API_ENDPOINT}")
    df = await get_from_api()
    print("\n🧾 RESULTADO FINAL (DataFrame):")
    if df is not None and not df.empty:
        print("Colunas do DataFrame:", df.columns.tolist())
        print(df)
    else:
        print("⚠️ Nenhum dado válido retornado ou DataFrame vazio.")
        return None

    # Process rows and call appropriate scraper based on URL
    for index, row in df.iterrows():
        
        if "amazon" in row['url']:
            print(f"Executando amazon_scrap para EAN: {row['ean']}")
            result = await amazon_scrap(row['url'],row['ean'],row['brand']), 
            print(f"Resultado amazon_scrap: {result}")
        elif "belezanaweb" in row['url']:
            print(f"\n🔎 Executando beleza_na_web_scrape para EAN: {row['ean']}")
            result = await beleza_na_web_scrape(row['url'],row['ean'],row['brand'])
            print(f"Resultado beleza_na_web_scrape: {result}")
        elif "magazineluiza" in row['url']:
            print(f"\n🔎 Executando magalu_scrap para EAN: {row['ean']}")
            result = await magalu_scrap(row['url'],row['ean'],row['brand'])
            print(f"Resultado magalu_scrap: {result}")

    return df

if __name__ == "__main__":
    df = asyncio.run(main())