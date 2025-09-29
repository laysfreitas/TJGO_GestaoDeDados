"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Download, FileText, FileSpreadsheet, FileJson, Folder } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface ExportDialogProps {
  aberto: boolean
  onClose: () => void
  filtrosAtuais: any
}

interface ArquivoExportacao {
  filename: string
  filepath: string
  size: number
  created: string
  modified: string
  format: string
}

export function ExportDialog({ aberto, onClose, filtrosAtuais }: ExportDialogProps) {
  const [formato, setFormato] = useState("csv")
  const [incluirMetadados, setIncluirMetadados] = useState(true)
  const [aplicarFiltros, setAplicarFiltros] = useState(false)
  const [loading, setLoading] = useState(false)
  const [arquivos, setArquivos] = useState<ArquivoExportacao[]>([])
  const [mostrarArquivos, setMostrarArquivos] = useState(false)
  const { toast } = useToast()

  const exportarDados = async () => {
    setLoading(true)
    try {
      const requestBody = {
        formato,
        incluir_metadados: incluirMetadados,
        filtros: aplicarFiltros ? filtrosAtuais : null,
      }

      console.log("[v0] Exportando dados:", requestBody)

      const response = await fetch("/api/exportar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Exportação Concluída",
          description: `${data.message} (${data.records_count} registros, ${(data.file_size / 1024).toFixed(1)} KB)`,
        })

        await listarArquivos()
        onClose()
      } else {
        const error = await response.json()
        toast({
          title: "Erro",
          description: error.detail || "Erro na exportação",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("[v0] Erro na exportação:", error)
      toast({
        title: "Erro de Conexão",
        description: "Servidor FastAPI não disponível. Inicie o servidor Python com: python main.py",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const listarArquivos = async () => {
    try {
      console.log("[v0] Listando arquivos de exportação...")
      const response = await fetch("/api/exportar/arquivos")
      if (response.ok) {
        const data = await response.json()
        setArquivos(data.arquivos)
      }
    } catch (error) {
      console.error("[v0] Erro ao listar arquivos:", error)
    }
  }

  const downloadArquivo = async (filename: string) => {
    try {
      console.log("[v0] Baixando arquivo:", filename)
      const response = await fetch(`/api/exportar/download/${filename}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)

        toast({
          title: "Download Iniciado",
          description: `Arquivo ${filename} está sendo baixado`,
        })
      }
    } catch (error) {
      console.error("[v0] Erro no download:", error)
      toast({
        title: "Erro de Conexão",
        description: "Não foi possível baixar o arquivo. Verifique se o servidor FastAPI está rodando.",
        variant: "destructive",
      })
    }
  }

  const formatarTamanho = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatarData = (isoString: string) => {
    return new Date(isoString).toLocaleString("pt-BR")
  }

  const getFormatoIcon = (format: string) => {
    switch (format.toLowerCase()) {
      case "csv":
        return <FileText className="h-4 w-4" />
      case "xlsx":
        return <FileSpreadsheet className="h-4 w-4" />
      case "json":
        return <FileJson className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const handleOpenDialog = () => {
    if (aberto && !mostrarArquivos) {
      listarArquivos()
    }
  }

  return (
    <Dialog open={aberto} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]" onOpenAutoFocus={handleOpenDialog}>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Exportar Dados
          </DialogTitle>
          <DialogDescription>
            Configure as opções de exportação e baixe seus dados em diferentes formatos.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Configurações</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="formato">Formato de Exportação</Label>
                <Select value={formato} onValueChange={setFormato}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="csv">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        CSV - Valores Separados por Vírgula
                      </div>
                    </SelectItem>
                    <SelectItem value="excel">
                      <div className="flex items-center gap-2">
                        <FileSpreadsheet className="h-4 w-4" />
                        Excel - Planilha com Resumos
                      </div>
                    </SelectItem>
                    <SelectItem value="json">
                      <div className="flex items-center gap-2">
                        <FileJson className="h-4 w-4" />
                        JSON - Dados Estruturados
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox id="metadados" checked={incluirMetadados} onCheckedChange={setIncluirMetadados} />
                <Label htmlFor="metadados" className="text-sm">
                  Incluir metadados (informações de exportação, resumos)
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox id="filtros" checked={aplicarFiltros} onCheckedChange={setAplicarFiltros} />
                <Label htmlFor="filtros" className="text-sm">
                  Aplicar filtros atuais da tela de dados
                </Label>
              </div>

              {aplicarFiltros && (
                <div className="p-3 bg-muted rounded-md">
                  <p className="text-sm font-medium mb-2">Filtros que serão aplicados:</p>
                  <div className="flex flex-wrap gap-2">
                    {filtrosAtuais.categoria !== "all" && (
                      <Badge variant="outline">Categoria: {filtrosAtuais.categoria}</Badge>
                    )}
                    {filtrosAtuais.busca && <Badge variant="outline">Busca: "{filtrosAtuais.busca}"</Badge>}
                    {filtrosAtuais.data_inicio && <Badge variant="outline">De: {filtrosAtuais.data_inicio}</Badge>}
                    {filtrosAtuais.data_fim && <Badge variant="outline">Até: {filtrosAtuais.data_fim}</Badge>}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Folder className="h-4 w-4" />
                Arquivos de Exportação
                <Button variant="ghost" size="sm" onClick={() => setMostrarArquivos(!mostrarArquivos)}>
                  {mostrarArquivos ? "Ocultar" : "Mostrar"}
                </Button>
              </CardTitle>
              <CardDescription>Arquivos exportados anteriormente disponíveis para download</CardDescription>
            </CardHeader>
            {mostrarArquivos && (
              <CardContent>
                {arquivos.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Nenhum arquivo de exportação encontrado
                  </p>
                ) : (
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {arquivos.slice(0, 5).map((arquivo) => (
                      <div key={arquivo.filename} className="flex items-center justify-between p-2 border rounded-md">
                        <div className="flex items-center gap-2">
                          {getFormatoIcon(arquivo.format)}
                          <div>
                            <p className="text-sm font-medium">{arquivo.filename}</p>
                            <p className="text-xs text-muted-foreground">
                              {formatarTamanho(arquivo.size)} • {formatarData(arquivo.modified)}
                            </p>
                          </div>
                        </div>
                        <Button size="sm" variant="outline" onClick={() => downloadArquivo(arquivo.filename)}>
                          <Download className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            )}
          </Card>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button onClick={exportarDados} disabled={loading}>
            {loading ? "Exportando..." : "Exportar Dados"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
