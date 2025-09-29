import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Optional
import aiofiles
from pathlib import Path
import logging

from .mcp_client import mcp_client

logger = logging.getLogger(__name__)

class ExchangeRateClient:
    """Cliente para API de câmbio usando MCP API Client"""
    
    def __init__(self):
        self.base_currency = "GBP"
        self.target_currencies = ["BRL", "USD"]
        self.cache_duration = 300  # 5 minutos de cache
        self._last_rates = None
        self._last_update = None
    
    async def get_latest_rates(self, force_refresh: bool = False) -> Optional[Dict]:
        """Obtém as taxas de câmbio mais recentes com cache"""
        try:
            # Verificar cache se não forçar refresh
            if not force_refresh and self._last_rates and self._last_update:
                time_diff = (datetime.now(timezone.utc) - self._last_update).total_seconds()
                if time_diff < self.cache_duration:
                    logger.info("Usando taxas de câmbio do cache")
                    return self._last_rates
            
            logger.info("Obtendo novas taxas de câmbio via MCP API Client")
            
            # Obter taxas via MCP
            symbols = ",".join(self.target_currencies)
            rates_data = await mcp_client.get_exchange_rates(
                base=self.base_currency,
                symbols=symbols
            )
            
            if rates_data:
                # Atualizar cache
                self._last_rates = rates_data
                self._last_update = datetime.now(timezone.utc)
                
                logger.info(f"Taxas obtidas: GBP/BRL={rates_data['gbp_brl']:.4f}, GBP/USD={rates_data['gbp_usd']:.4f}")
                return rates_data
            else:
                logger.error("Falha ao obter taxas de câmbio")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao obter taxas de câmbio: {e}")
            return None
    
    async def save_exchange_data(self, exchange_data: Dict, date_str: str):
        """Salva dados de câmbio em arquivo JSON com metadados"""
        try:
            # Adicionar metadados
            enhanced_data = {
                **exchange_data,
                "metadata": {
                    "coleta_realizada_em": datetime.now(timezone.utc).isoformat(),
                    "fonte_api": exchange_data.get("fonte", "exchangerate.host"),
                    "base_currency": exchange_data.get("base_currency", self.base_currency),
                    "target_currencies": self.target_currencies,
                    "cache_duration_seconds": self.cache_duration
                }
            }
            
            # Criar diretório se não existir
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            filename = data_dir / f"cambio_{date_str}.json"
            
            async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(enhanced_data, indent=2, ensure_ascii=False))
            
            logger.info(f"Dados de câmbio salvos em: {filename}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de câmbio: {e}")
    
    def convert_prices(self, products: list, exchange_rates: Dict) -> list:
        """Converte preços dos produtos usando as taxas de câmbio"""
        if not exchange_rates:
            logger.warning("Taxas de câmbio não disponíveis para conversão")
            return products
        
        gbp_brl = exchange_rates.get("gbp_brl", 1.0)
        gbp_usd = exchange_rates.get("gbp_usd", 1.0)
        
        converted_count = 0
        
        for product in products:
            if "preco_bruto" in product and isinstance(product["preco_bruto"], (int, float)):
                try:
                    product["preco_brl"] = round(product["preco_bruto"] * gbp_brl, 2)
                    product["preco_usd"] = round(product["preco_bruto"] * gbp_usd, 2)
                    product["taxa_cambio_brl"] = gbp_brl
                    product["taxa_cambio_usd"] = gbp_usd
                    product["cambio_timestamp"] = exchange_rates.get("cambio_ts")
                    converted_count += 1
                except (TypeError, ValueError) as e:
                    logger.warning(f"Erro ao converter preço do produto {product.get('id', 'N/A')}: {e}")
        
        logger.info(f"Preços convertidos para {converted_count} produtos")
        return products
    
    async def get_historical_rates(self, date: str) -> Optional[Dict]:
        """Obtém taxas históricas para uma data específica"""
        try:
            # Em implementação real, usaria endpoint histórico da API
            # Por ora, retorna as taxas atuais
            logger.info(f"Obtendo taxas históricas para {date}")
            return await self.get_latest_rates()
        except Exception as e:
            logger.error(f"Erro ao obter taxas históricas: {e}")
            return None
    
    async def validate_connection(self) -> bool:
        """Valida conexão com a API de câmbio"""
        try:
            return await mcp_client.validate_api_connection()
        except Exception:
            return False

# Instância global do cliente de câmbio
exchange_client = ExchangeRateClient()
