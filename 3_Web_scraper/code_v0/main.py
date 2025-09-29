from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import csv
import os
from datetime import datetime, timezone
import pandas as pd
from pathlib import Path
import logging

from scraper.books_scraper import books_scraper
from scraper.exchange_client import exchange_client
from utils.export_manager import export_manager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Coleta de Preços API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretórios necessários
os.makedirs("data", exist_ok=True)
os.makedirs("data/raw_html", exist_ok=True)
os.makedirs("data/exports", exist_ok=True)

# Modelos Pydantic
class ProdutoBase(BaseModel):
    produto_nome: str
    preco_bruto: float
    disponibilidade: str
    categoria: str
    avaliacao: int
    produto_url: str

class Produto(ProdutoBase):
    id: int
    coleta_ts: str
    preco_brl: Optional[float] = None
    preco_usd: Optional[float] = None

class ColetaStatus(BaseModel):
    status: str
    progresso: int
    total: int
    categoria_atual: str
    mensagem: str

class CambioInfo(BaseModel):
    cambio_ts: str
    gbp_brl: float
    gbp_usd: float
    fonte: Optional[str] = None
    base_currency: Optional[str] = None

class ExportRequest(BaseModel):
    formato: str = "csv"  # csv, json, excel
    incluir_metadados: bool = True
    filtros: Optional[dict] = None

# Estado global da aplicação
coleta_status = {
    "ativa": False,
    "progresso": 0,
    "total": 0,
    "categoria_atual": "",
    "mensagem": "Pronto para iniciar coleta"
}

produtos_db = []
ultimo_cambio = None

@app.get("/")
async def root():
    return {"message": "API de Coleta de Preços - v1.0.0"}

@app.get("/api/status")
async def get_status():
    return ColetaStatus(**coleta_status)

@app.post("/api/coleta/iniciar")
async def iniciar_coleta(background_tasks: BackgroundTasks):
    if coleta_status["ativa"]:
        raise HTTPException(status_code=400, detail="Coleta já está em andamento")
    
    background_tasks.add_task(executar_coleta)
    return {"message": "Coleta iniciada com sucesso"}

@app.get("/api/produtos")
async def listar_produtos(
    categoria: Optional[str] = None,
    busca: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    ordenar_por: str = "coleta_ts",
    ordem: str = "desc",
    pagina: int = 1,
    por_pagina: int = 20
):
    produtos_filtrados = produtos_db.copy()
    
    # Aplicar filtros
    if categoria and categoria != "all":
        produtos_filtrados = [p for p in produtos_filtrados if p.get("categoria", "").lower() == categoria.lower()]
    
    if busca:
        produtos_filtrados = [p for p in produtos_filtrados if busca.lower() in p.get("produto_nome", "").lower()]
    
    if data_inicio:
        produtos_filtrados = [p for p in produtos_filtrados if p.get("coleta_ts", "") >= data_inicio]
    
    if data_fim:
        produtos_filtrados = [p for p in produtos_filtrados if p.get("coleta_ts", "") <= data_fim]
    
    # Ordenação
    reverse = ordem == "desc"
    produtos_filtrados.sort(key=lambda x: x.get(ordenar_por, ""), reverse=reverse)
    
    # Paginação
    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    produtos_pagina = produtos_filtrados[inicio:fim]
    
    return {
        "produtos": produtos_pagina,
        "total": len(produtos_filtrados),
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total_paginas": (len(produtos_filtrados) + por_pagina - 1) // por_pagina
    }

@app.get("/api/cambio")
async def get_cambio():
    if not ultimo_cambio:
        raise HTTPException(status_code=404, detail="Dados de câmbio não disponíveis")
    return ultimo_cambio

@app.post("/api/cambio/atualizar")
async def atualizar_cambio():
    """Atualiza as taxas de câmbio manualmente"""
    try:
        logger.info("Atualizando taxas de câmbio manualmente")
        
        # Forçar refresh das taxas
        novas_taxas = await exchange_client.get_latest_rates(force_refresh=True)
        
        if novas_taxas:
            global ultimo_cambio
            ultimo_cambio = novas_taxas
            
            # Salvar dados atualizados
            hoje = datetime.now().strftime("%Y-%m-%d")
            await exchange_client.save_exchange_data(novas_taxas, hoje)
            
            return {
                "message": "Taxas de câmbio atualizadas com sucesso",
                "taxas": novas_taxas
            }
        else:
            raise HTTPException(status_code=500, detail="Falha ao obter novas taxas de câmbio")
            
    except Exception as e:
        logger.error(f"Erro ao atualizar câmbio: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/cambio/status")
async def status_cambio():
    """Verifica o status da conexão com a API de câmbio"""
    try:
        conexao_ok = await exchange_client.validate_connection()
        
        return {
            "conexao_ativa": conexao_ok,
            "ultima_atualizacao": ultimo_cambio.get("cambio_ts") if ultimo_cambio else None,
            "fonte": ultimo_cambio.get("fonte") if ultimo_cambio else None,
            "cache_ativo": exchange_client._last_rates is not None
        }
    except Exception as e:
        return {
            "conexao_ativa": False,
            "erro": str(e)
        }

@app.post("/api/exportar")
async def exportar_dados(request: ExportRequest):
    """Exporta dados em formato especificado com filtros opcionais"""
    try:
        if not produtos_db:
            raise HTTPException(status_code=404, detail="Nenhum dado para exportar")
        
        # Aplicar filtros se fornecidos
        dados_para_exportar = produtos_db
        if request.filtros:
            # Usar o sistema de filtros do export_manager
            resultado = await export_manager.export_filtered_data(
                dados_para_exportar, 
                request.filtros, 
                request.formato
            )
        else:
            # Exportar todos os dados
            if request.formato.lower() == "csv":
                resultado = await export_manager.export_to_csv(
                    dados_para_exportar, 
                    include_metadata=request.incluir_metadados
                )
            elif request.formato.lower() == "json":
                resultado = await export_manager.export_to_json(
                    dados_para_exportar, 
                    include_metadata=request.incluir_metadados
                )
            elif request.formato.lower() == "excel":
                resultado = await export_manager.export_to_excel(
                    dados_para_exportar, 
                    include_summary=request.incluir_metadados
                )
            else:
                raise HTTPException(status_code=400, detail=f"Formato não suportado: {request.formato}")
        
        if resultado["success"]:
            return {
                "message": f"Dados exportados com sucesso em formato {request.formato.upper()}",
                **resultado
            }
        else:
            raise HTTPException(status_code=500, detail=resultado["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na exportação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/exportar/csv")
async def exportar_csv():
    """Endpoint legado para compatibilidade"""
    if not produtos_db:
        raise HTTPException(status_code=404, detail="Nenhum dado para exportar")
    
    resultado = await export_manager.export_to_csv(produtos_db)
    
    if resultado["success"]:
        return {
            "message": f"Arquivo CSV exportado: {resultado['filename']}",
            "arquivo": resultado["filename"]
        }
    else:
        raise HTTPException(status_code=500, detail=resultado["error"])

@app.get("/api/exportar/arquivos")
async def listar_arquivos_exportacao():
    """Lista arquivos de exportação disponíveis"""
    try:
        arquivos = export_manager.list_export_files()
        return {
            "arquivos": arquivos,
            "total": len(arquivos)
        }
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/exportar/download/{filename}")
async def download_arquivo_exportacao(filename: str):
    """Download de arquivo de exportação"""
    try:
        filepath = Path("data/exports") / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/exportar/copiar")
async def copiar_listagem(
    formato: str = Query("texto", description="Formato: texto, markdown, html"),
    categoria: Optional[str] = Query(None),
    busca: Optional[str] = Query(None)
):
    """Gera texto formatado para copiar para área de transferência"""
    try:
        if not produtos_db:
            raise HTTPException(status_code=404, detail="Nenhum dado disponível")
        
        # Aplicar filtros básicos
        produtos_filtrados = produtos_db.copy()
        
        if categoria and categoria != "all":
            produtos_filtrados = [p for p in produtos_filtrados 
                                if p.get("categoria", "").lower() == categoria.lower()]
        
        if busca:
            produtos_filtrados = [p for p in produtos_filtrados 
                                if busca.lower() in p.get("produto_nome", "").lower()]
        
        # Gerar texto no formato solicitado
        if formato.lower() == "texto":
            texto = "\n".join([
                f"{p['produto_nome']} - £{p['preco_bruto']:.2f} ({p['categoria']}) - {p['disponibilidade']}"
                for p in produtos_filtrados
            ])
        elif formato.lower() == "markdown":
            texto = "| Produto | Preço GBP | Categoria | Disponibilidade |\n"
            texto += "|---------|-----------|-----------|----------------|\n"
            for p in produtos_filtrados:
                texto += f"| {p['produto_nome']} | £{p['preco_bruto']:.2f} | {p['categoria']} | {p['disponibilidade']} |\n"
        elif formato.lower() == "html":
            texto = "<table>\n<tr><th>Produto</th><th>Preço GBP</th><th>Categoria</th><th>Disponibilidade</th></tr>\n"
            for p in produtos_filtrados:
                texto += f"<tr><td>{p['produto_nome']}</td><td>£{p['preco_bruto']:.2f}</td><td>{p['categoria']}</td><td>{p['disponibilidade']}</td></tr>\n"
            texto += "</table>"
        else:
            raise HTTPException(status_code=400, detail=f"Formato não suportado: {formato}")
        
        return {
            "texto": texto,
            "formato": formato,
            "total_produtos": len(produtos_filtrados)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar listagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

async def executar_coleta():
    """Executa a coleta de dados em background usando MCP"""
    global coleta_status, produtos_db, ultimo_cambio
    
    try:
        coleta_status.update({
            "ativa": True,
            "progresso": 0,
            "total": 100,
            "categoria_atual": "Iniciando...",
            "mensagem": "Preparando coleta de dados"
        })
        
        logger.info("Iniciando processo de coleta")
        
        def update_progress(message: str):
            coleta_status["mensagem"] = message
            logger.info(f"Progresso: {message}")
        
        # Validar conexão com API de câmbio primeiro
        coleta_status.update({
            "categoria_atual": "Validação",
            "mensagem": "Validando conexão com API de câmbio"
        })
        
        conexao_cambio = await exchange_client.validate_connection()
        if not conexao_cambio:
            logger.warning("Conexão com API de câmbio falhou, continuando sem conversão")
        
        coleta_status["progresso"] = 5
        
        # Obter dados de câmbio
        coleta_status.update({
            "categoria_atual": "Câmbio",
            "mensagem": "Obtendo taxas de câmbio atuais via MCP API Client"
        })
        
        ultimo_cambio = await exchange_client.get_latest_rates(force_refresh=True)
        if not ultimo_cambio:
            logger.warning("Falha ao obter dados de câmbio, continuando sem conversão")
        
        coleta_status["progresso"] = 15
        
        # Executar coleta de produtos
        coleta_status.update({
            "categoria_atual": "Produtos",
            "mensagem": "Iniciando coleta de produtos via MCP Web Scraper"
        })
        
        produtos_coletados = await books_scraper.collect_all_data(update_progress)
        
        if not produtos_coletados:
            raise Exception("Nenhum produto foi coletado")
        
        coleta_status["progresso"] = 80
        
        # Converter preços usando taxas de câmbio
        if ultimo_cambio:
            coleta_status.update({
                "mensagem": "Convertendo preços para BRL e USD"
            })
            
            produtos_com_conversao = exchange_client.convert_prices(
                produtos_coletados, ultimo_cambio
            )
        else:
            produtos_com_conversao = produtos_coletados
            logger.warning("Conversão de preços pulada devido à falha no câmbio")
        
        # Adicionar IDs únicos
        for i, produto in enumerate(produtos_com_conversao):
            produto["id"] = len(produtos_db) + i + 1
        
        produtos_db.extend(produtos_com_conversao)
        
        coleta_status["progresso"] = 90
        
        # Salvar arquivos
        hoje = datetime.now().strftime("%Y-%m-%d")
        
        coleta_status.update({
            "mensagem": "Salvando dados coletados"
        })
        
        # CSV de preços usando o novo sistema de exportação
        resultado_csv = await export_manager.export_to_csv(
            produtos_com_conversao, 
            f"precos_brutos_{hoje}.csv"
        )
        
        # JSON de câmbio (se disponível)
        if ultimo_cambio:
            await exchange_client.save_exchange_data(ultimo_cambio, hoje)
        
        coleta_status.update({
            "ativa": False,
            "progresso": 100,
            "categoria_atual": "Concluído",
            "mensagem": f"Coleta finalizada! {len(produtos_com_conversao)} produtos coletados e salvos"
        })
        
        logger.info(f"Coleta concluída com sucesso: {len(produtos_com_conversao)} produtos")
        
    except Exception as e:
        error_msg = f"Erro durante a coleta: {str(e)}"
        coleta_status.update({
            "ativa": False,
            "categoria_atual": "Erro",
            "mensagem": error_msg
        })
        logger.error(error_msg)

@app.post("/api/produtos")
async def criar_produto(produto: ProdutoBase):
    novo_produto = produto.dict()
    novo_produto["id"] = len(produtos_db) + 1
    novo_produto["coleta_ts"] = datetime.now(timezone.utc).isoformat()
    produtos_db.append(novo_produto)
    return {"message": "Produto criado com sucesso", "produto": novo_produto}

@app.get("/api/produtos/{produto_id}")
async def obter_produto(produto_id: int):
    produto = next((p for p in produtos_db if p.get("id") == produto_id), None)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.put("/api/produtos/{produto_id}")
async def atualizar_produto(produto_id: int, produto_atualizado: ProdutoBase):
    for i, produto in enumerate(produtos_db):
        if produto.get("id") == produto_id:
            produtos_db[i].update(produto_atualizado.dict())
            return {"message": "Produto atualizado com sucesso", "produto": produtos_db[i]}
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.delete("/api/produtos/{produto_id}")
async def excluir_produto(produto_id: int):
    for i, produto in enumerate(produtos_db):
        if produto.get("id") == produto_id:
            produto_removido = produtos_db.pop(i)
            return {"message": "Produto excluído com sucesso", "produto": produto_removido}
    raise HTTPException(status_code=404, detail="Produto não encontrado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
