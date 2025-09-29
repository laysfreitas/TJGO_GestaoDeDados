import asyncio
import re
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import aiofiles
from pathlib import Path

class BooksToScrapeCollector:
    """Coletor de dados do site Books to Scrape usando MCP Web Scraper"""
    
    def __init__(self):
        self.base_url = "https://books.toscrape.com/"
        self.user_agent = "ColetaPrecos-Bot/1.0 (Educational Purpose - Price Research)"
        self.min_delay = 1.0  # Intervalo mínimo entre requisições
        self.categories = ["Travel", "Science"]
        self.max_pages_per_category = 3
        
    async def check_robots_txt(self) -> bool:
        """Verifica e respeita o robots.txt"""
        try:
            # Em implementação real, usaria MCP Web Scraper para verificar robots.txt
            # Por ora, assumimos conformidade
            return True
        except Exception as e:
            print(f"Erro ao verificar robots.txt: {e}")
            return False
    
    def normalize_price(self, price_text: str) -> float:
        """Normaliza preço de texto para número"""
        try:
            # Remove símbolo £ e converte para float
            price_clean = re.sub(r'[£,]', '', price_text.strip())
            return float(price_clean)
        except (ValueError, AttributeError):
            return 0.0
    
    def extract_rating(self, rating_class: str) -> int:
        """Extrai avaliação da classe CSS"""
        rating_map = {
            "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
        }
        
        for word, rating in rating_map.items():
            if word.lower() in rating_class.lower():
                return rating
        return 0
    
    async def save_raw_html(self, html_content: str, filename: str):
        """Salva HTML bruto em caso de erro de parsing"""
        raw_dir = Path("data/raw_html")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = raw_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(html_content)
        
        print(f"HTML bruto salvo em: {filepath}")
    
    async def scrape_product_page(self, product_url: str) -> Optional[Dict]:
        """Faz scraping de uma página de produto específica"""
        try:
            # Em implementação real, usaria MCP Web Scraper aqui
            # Simulando dados de produto para demonstração
            
            # Extrair ID do produto da URL para simulação
            product_id = product_url.split('/')[-1].replace('.html', '')
            
            # Dados simulados baseados na estrutura real do Books to Scrape
            simulated_data = {
                "produto_nome": f"Livro Exemplo {product_id}",
                "preco_bruto": round(15.0 + (hash(product_id) % 50), 2),
                "disponibilidade": "In stock" if hash(product_id) % 3 != 0 else "Out of stock",
                "avaliacao": (hash(product_id) % 5) + 1,
                "produto_url": product_url,
                "coleta_ts": datetime.now(timezone.utc).isoformat()
            }
            
            await asyncio.sleep(self.min_delay)  # Respeitar intervalo
            return simulated_data
            
        except Exception as e:
            print(f"Erro ao fazer scraping do produto {product_url}: {e}")
            # Em caso real, salvaria o HTML bruto aqui
            return None
    
    async def scrape_category_page(self, category: str, page: int = 1) -> List[str]:
        """Faz scraping de uma página de categoria para obter URLs de produtos"""
        try:
            # Em implementação real, usaria MCP Web Scraper
            # Simulando URLs de produtos
            
            base_id = f"{category.lower()}_{page}"
            product_urls = []
            
            # Simular 20 produtos por página
            for i in range(20):
                product_url = f"{self.base_url}catalogue/produto-{base_id}-{i}.html"
                product_urls.append(product_url)
            
            await asyncio.sleep(self.min_delay)
            return product_urls
            
        except Exception as e:
            print(f"Erro ao fazer scraping da categoria {category}, página {page}: {e}")
            return []
    
    async def collect_category_data(self, category: str, progress_callback=None) -> List[Dict]:
        """Coleta dados de uma categoria específica"""
        print(f"Iniciando coleta da categoria: {category}")
        products = []
        
        for page in range(1, self.max_pages_per_category + 1):
            if progress_callback:
                progress_callback(f"Coletando {category} - Página {page}")
            
            # Obter URLs dos produtos da página
            product_urls = await self.scrape_category_page(category, page)
            
            if not product_urls:
                break
            
            # Fazer scraping de cada produto
            for url in product_urls:
                product_data = await self.scrape_product_page(url)
                if product_data:
                    product_data["categoria"] = category
                    products.append(product_data)
                
                if progress_callback:
                    progress_callback(f"Coletados {len(products)} produtos de {category}")
        
        print(f"Coleta da categoria {category} finalizada: {len(products)} produtos")
        return products
    
    async def collect_all_data(self, progress_callback=None) -> List[Dict]:
        """Coleta dados de todas as categorias"""
        if not await self.check_robots_txt():
            raise Exception("Não foi possível verificar conformidade com robots.txt")
        
        all_products = []
        
        for category in self.categories:
            try:
                category_products = await self.collect_category_data(
                    category, progress_callback
                )
                all_products.extend(category_products)
                
            except Exception as e:
                print(f"Erro na coleta da categoria {category}: {e}")
                continue
        
        return all_products

# Instância global do coletor
books_scraper = BooksToScrapeCollector()
