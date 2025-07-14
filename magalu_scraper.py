import asyncio
import json
from datetime import datetime
from pprint import pprint
from playwright.async_api import async_playwright, TimeoutError

async def magalu_scrap(target_url: str, ean:str, marca:str):
    url_busca = target_url
    resultados = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Pode tentar headless=True e ajustar timeouts
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url_busca, timeout=30000)
            await page.wait_for_selector('li.sc-iVDsrp')  # Lista de produtos

            # Seleciona todos os produtos no formato <li class="sc-iVDsrp ...">
            produtos = await page.query_selector_all('li.sc-iVDsrp')

            for idx, produto in enumerate(produtos):
                try:
                    # Link do produto (tag <a data-testid="product-card-container"> dentro do <li>)
                    a_tag = await produto.query_selector('a[data-testid="product-card-container"]')
                    if not a_tag:
                        continue
                    href = await a_tag.get_attribute("href")
                    produto_url = f"https://www.magazineluiza.com.br{href}"

                    # Abre página de detalhe do produto
                    detail_page = await context.new_page()
                    await detail_page.goto(produto_url)
                    await detail_page.wait_for_load_state("domcontentloaded")
                    await detail_page.wait_for_timeout(1500)

                    # Descrição do produto
                    desc_el = await detail_page.query_selector('h1[data-testid="heading-product-title"]')
                    descricao = (await desc_el.inner_text()).strip() if desc_el else ""

                    # Seller / loja
                    loja_el = await detail_page.query_selector('label[data-testid="link"]')
                    loja = (await loja_el.inner_text()).strip() if loja_el else "Desconhecido"

                    # Marketplace fixo
                    marketplace = "Magazine Luiza"

                    # Dados JSON-LD para preço, sku, imagem, review
                    jsonld_el = await detail_page.query_selector('script[data-testid="jsonld-script"]')
                    jsonld = {}
                    if jsonld_el:
                        jsonld_raw = await jsonld_el.inner_text()
                        jsonld = json.loads(jsonld_raw)

                    preco_final = jsonld.get("offers", {}).get("price", "")
                    imagem = jsonld.get("image", "")
                    try:
                        review = float(jsonld.get("aggregateRating", {}).get("ratingValue", 0))
                    except:
                        review = 0.0
                    sku = jsonld.get("sku", "")

                    # Dados auxiliares
                    data_hora = datetime.utcnow().isoformat() + "Z"
                    status = "ativo"
                    key_loja = loja.lower().replace(" ", "")
                    key_sku = f"{key_loja}_{sku}" if sku else None

                    resultado = {
                        "ean": ean,
                        "url": produto_url,
                        "sku": sku if sku else "SKU não encontrado",
                        "descricao": descricao,
                        "loja": loja,
                        "preco_final": preco_final,
                        "imagem": imagem,
                        "review": review,
                        "data_hora": data_hora,
                        "status": status,
                        "marketplace": marketplace,
                        "key_loja": key_loja,
                        "key_sku": key_sku,
                        "marca":marca
                    }

                    pprint(resultado)
                    resultados.append(resultado)
                    await detail_page.close()

                except Exception as e:
                    print(f"Erro ao processar produto {idx}: {e}")

        except TimeoutError:
            print("Timeout ao carregar a página ou elementos.")
        finally:
            await context.close()
            await browser.close()

    return resultados

