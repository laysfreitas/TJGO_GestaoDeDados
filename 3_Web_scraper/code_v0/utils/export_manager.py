"""
Gerenciador de exportação de dados
Suporte para múltiplos formatos: CSV, JSON, Excel
"""

import json
import csv
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ExportManager:
    """Gerenciador de exportação de dados em múltiplos formatos"""
    
    def __init__(self):
        self.export_dir = Path("data/exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, base_name: str, format_type: str, timestamp: bool = True) -> str:
        """Gera nome de arquivo com timestamp opcional"""
        if timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{base_name}_{ts}.{format_type}"
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
            return f"{base_name}_{date_str}.{format_type}"
    
    async def export_to_csv(
        self, 
        data: List[Dict], 
        filename: Optional[str] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Exporta dados para CSV com metadados opcionais"""
        try:
            if not data:
                raise ValueError("Nenhum dado para exportar")
            
            if not filename:
                filename = self._generate_filename("produtos_exportados", "csv")
            
            filepath = self.export_dir / filename
            
            # Preparar dados
            df = pd.DataFrame(data)
            
            # Reordenar colunas para melhor legibilidade
            preferred_order = [
                'id', 'produto_nome', 'categoria', 'preco_bruto', 
                'preco_brl', 'preco_usd', 'avaliacao', 'disponibilidade',
                'produto_url', 'coleta_ts'
            ]
            
            # Reorganizar colunas mantendo as que existem
            existing_cols = [col for col in preferred_order if col in df.columns]
            other_cols = [col for col in df.columns if col not in preferred_order]
            df = df[existing_cols + other_cols]
            
            # Adicionar metadados como comentários no CSV se solicitado
            if include_metadata:
                metadata_lines = [
                    f"# Exportação gerada em: {datetime.now(timezone.utc).isoformat()}",
                    f"# Total de registros: {len(data)}",
                    f"# Colunas: {', '.join(df.columns.tolist())}",
                    ""  # Linha vazia antes dos dados
                ]
                
                # Escrever metadados manualmente
                with open(filepath, 'w', encoding='utf-8', newline='') as f:
                    for line in metadata_lines:
                        f.write(line + '\n')
                    
                    # Escrever dados CSV
                    df.to_csv(f, index=False, encoding='utf-8')
            else:
                df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"Dados exportados para CSV: {filepath}")
            
            return {
                "success": True,
                "filename": filename,
                "filepath": str(filepath),
                "records_count": len(data),
                "file_size": os.path.getsize(filepath),
                "format": "CSV"
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {e}")
            return {
                "success": False,
                "error": str(e),
                "format": "CSV"
            }
    
    async def export_to_json(
        self, 
        data: List[Dict], 
        filename: Optional[str] = None,
        include_metadata: bool = True,
        pretty_print: bool = True
    ) -> Dict[str, Any]:
        """Exporta dados para JSON com metadados opcionais"""
        try:
            if not data:
                raise ValueError("Nenhum dado para exportar")
            
            if not filename:
                filename = self._generate_filename("produtos_exportados", "json")
            
            filepath = self.export_dir / filename
            
            # Preparar estrutura de dados
            export_data = {
                "dados": data
            }
            
            if include_metadata:
                export_data["metadata"] = {
                    "exportado_em": datetime.now(timezone.utc).isoformat(),
                    "total_registros": len(data),
                    "formato": "JSON",
                    "versao_exportador": "1.0.0",
                    "campos_disponiveis": list(data[0].keys()) if data else []
                }
            
            # Escrever arquivo JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty_print:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                else:
                    json.dump(export_data, f, ensure_ascii=False, default=str)
            
            logger.info(f"Dados exportados para JSON: {filepath}")
            
            return {
                "success": True,
                "filename": filename,
                "filepath": str(filepath),
                "records_count": len(data),
                "file_size": os.path.getsize(filepath),
                "format": "JSON"
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar JSON: {e}")
            return {
                "success": False,
                "error": str(e),
                "format": "JSON"
            }
    
    async def export_to_excel(
        self, 
        data: List[Dict], 
        filename: Optional[str] = None,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """Exporta dados para Excel com planilhas múltiplas"""
        try:
            if not data:
                raise ValueError("Nenhum dado para exportar")
            
            if not filename:
                filename = self._generate_filename("produtos_exportados", "xlsx")
            
            filepath = self.export_dir / filename
            
            # Criar DataFrame principal
            df = pd.DataFrame(data)
            
            # Criar arquivo Excel com múltiplas planilhas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Planilha principal com todos os dados
                df.to_excel(writer, sheet_name='Produtos', index=False)
                
                if include_summary:
                    # Planilha de resumo por categoria
                    if 'categoria' in df.columns and 'preco_bruto' in df.columns:
                        summary_categoria = df.groupby('categoria').agg({
                            'preco_bruto': ['count', 'mean', 'min', 'max', 'sum'],
                            'avaliacao': 'mean' if 'avaliacao' in df.columns else 'count'
                        }).round(2)
                        
                        summary_categoria.columns = [
                            'Total_Produtos', 'Preco_Medio', 'Preco_Min', 
                            'Preco_Max', 'Valor_Total', 'Avaliacao_Media'
                        ]
                        summary_categoria.to_excel(writer, sheet_name='Resumo_Categoria')
                    
                    # Planilha de resumo por disponibilidade
                    if 'disponibilidade' in df.columns:
                        summary_disponibilidade = df.groupby('disponibilidade').size().to_frame('Quantidade')
                        summary_disponibilidade.to_excel(writer, sheet_name='Resumo_Disponibilidade')
                    
                    # Planilha de metadados
                    metadata_df = pd.DataFrame([
                        ['Data de Exportação', datetime.now(timezone.utc).isoformat()],
                        ['Total de Registros', len(data)],
                        ['Formato', 'Excel (XLSX)'],
                        ['Colunas Disponíveis', ', '.join(df.columns.tolist())],
                        ['Categorias Únicas', df['categoria'].nunique() if 'categoria' in df.columns else 'N/A'],
                        ['Faixa de Preços (GBP)', f"£{df['preco_bruto'].min():.2f} - £{df['preco_bruto'].max():.2f}" if 'preco_bruto' in df.columns else 'N/A']
                    ], columns=['Campo', 'Valor'])
                    
                    metadata_df.to_excel(writer, sheet_name='Metadados', index=False)
            
            logger.info(f"Dados exportados para Excel: {filepath}")
            
            return {
                "success": True,
                "filename": filename,
                "filepath": str(filepath),
                "records_count": len(data),
                "file_size": os.path.getsize(filepath),
                "format": "Excel",
                "sheets": ["Produtos", "Resumo_Categoria", "Resumo_Disponibilidade", "Metadados"] if include_summary else ["Produtos"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar Excel: {e}")
            return {
                "success": False,
                "error": str(e),
                "format": "Excel"
            }
    
    async def export_filtered_data(
        self, 
        data: List[Dict], 
        filters: Dict[str, Any],
        format_type: str = "csv"
    ) -> Dict[str, Any]:
        """Exporta dados filtrados em formato especificado"""
        try:
            # Aplicar filtros
            filtered_data = self._apply_filters(data, filters)
            
            # Gerar nome de arquivo com informações do filtro
            filter_info = "_".join([f"{k}-{v}" for k, v in filters.items() if v])
            base_name = f"produtos_filtrados_{filter_info}"
            
            # Exportar no formato solicitado
            if format_type.lower() == "csv":
                return await self.export_to_csv(filtered_data, 
                    self._generate_filename(base_name, "csv"))
            elif format_type.lower() == "json":
                return await self.export_to_json(filtered_data, 
                    self._generate_filename(base_name, "json"))
            elif format_type.lower() == "excel":
                return await self.export_to_excel(filtered_data, 
                    self._generate_filename(base_name, "xlsx"))
            else:
                raise ValueError(f"Formato não suportado: {format_type}")
                
        except Exception as e:
            logger.error(f"Erro ao exportar dados filtrados: {e}")
            return {
                "success": False,
                "error": str(e),
                "format": format_type
            }
    
    def _apply_filters(self, data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Aplica filtros aos dados"""
        filtered_data = data.copy()
        
        for key, value in filters.items():
            if not value:
                continue
                
            if key == "categoria" and value != "all":
                filtered_data = [item for item in filtered_data 
                               if item.get("categoria", "").lower() == value.lower()]
            elif key == "busca":
                filtered_data = [item for item in filtered_data 
                               if value.lower() in item.get("produto_nome", "").lower()]
            elif key == "data_inicio":
                filtered_data = [item for item in filtered_data 
                               if item.get("coleta_ts", "") >= value]
            elif key == "data_fim":
                filtered_data = [item for item in filtered_data 
                               if item.get("coleta_ts", "") <= value]
        
        return filtered_data
    
    def list_export_files(self) -> List[Dict[str, Any]]:
        """Lista arquivos de exportação disponíveis"""
        try:
            files = []
            for file_path in self.export_dir.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "format": file_path.suffix.upper().replace(".", "")
                    })
            
            # Ordenar por data de modificação (mais recente primeiro)
            files.sort(key=lambda x: x["modified"], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"Erro ao listar arquivos de exportação: {e}")
            return []

# Instância global do gerenciador de exportação
export_manager = ExportManager()
