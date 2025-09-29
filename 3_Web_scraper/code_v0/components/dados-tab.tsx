"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import {
  Search,
  Download,
  Copy,
  Edit,
  Trash2,
  Plus,
  ChevronLeft,
  ChevronRight,
  FileText,
  FileSpreadsheet,
  FileJson,
  List,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { ProdutoFormDialog } from "./produto-form-dialog"
import { ExportDialog } from "./export-dialog"

interface Produto {
  id: number
  produto_nome: string
  preco_bruto: number
  disponibilidade: string
  categoria: string
  avaliacao: number
  produto_url: string
  coleta_ts: string
  preco_brl?: number
  preco_usd?: number
}

interface ProdutosResponse {
  produtos: Produto[]
  total: number
  pagina: number
  por_pagina: number
  total_paginas: number
}

export function DadosTab() {
  const [produtos, setProdutos] = useState<Produto[]>([])
  const [loading, setLoading] = useState(false)
  const [serverAvailable, setServerAvailable] = useState<boolean | null>(null)
  const [filtros, setFiltros] = useState({
    busca: "",
    categoria: "all",
    data_inicio: "",
    data_fim: "",
    ordenar_por: "coleta_ts",
    ordem: "desc",
  })
  const [paginacao, setPaginacao] = useState({
    pagina: 1,
    por_pagina: 20,
    total: 0,
    total_paginas: 0,
  })
  const [dialogAberto, setDialogAberto] = useState(false)
  const [exportDialogAberto, setExportDialogAberto] = useState(false)
  const [produtoEditando, setProdutoEditando] = useState<Produto | null>(null)
  const { toast } = useToast()

  const buscarProdutos = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        pagina: paginacao.pagina.toString(),
        por_pagina: paginacao.por_pagina.toString(),
        ...filtros,
      })

      console.log("[v0] Buscando produtos via API...")
      const response = await fetch(`/api/produtos?${params}`)
      if (response.ok) {
        const data: ProdutosResponse = await response.json()
        setProdutos(data.produtos)
        setPaginacao((prev) => ({
          ...prev,
          total: data.total,
          total_paginas: data.total_paginas,
        }))
        if (serverAvailable === false) {
          setServerAvailable(true)
          toast({
            title: "Servidor Conectado",
            description: "Conexão com o servidor FastAPI estabelecida!",
          })
        } else if (serverAvailable === null) {
          setServerAvailable(true)
        }
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.error("[v0] Erro ao buscar produtos:", error)
      if (serverAvailable !== false) {
        setServerAvailable(false)
      }
      toast({
        title: "Erro de Conexão",
        description: "Servidor FastAPI não disponível. Inicie o servidor Python com: python main.py",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const exportarRapido = async (formato: string) => {
    if (!serverAvailable) {
      toast({
        title: "Servidor Indisponível",
        description: "Inicie o servidor FastAPI primeiro: python main.py",
        variant: "destructive",
      })
      return
    }

    try {
      const response = await fetch("/api/exportar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          formato,
          incluir_metadados: true,
          filtros: filtros.categoria !== "all" || filtros.busca ? filtros : null,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Exportação Concluída",
          description: `${data.message} (${data.records_count} registros)`,
        })
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
        description: "Verifique se o servidor FastAPI está rodando na porta 8000",
        variant: "destructive",
      })
    }
  }

  const copiarListagem = async (formato = "texto") => {
    if (!serverAvailable) {
      toast({
        title: "Servidor Indisponível",
        description: "Inicie o servidor FastAPI primeiro: python main.py",
        variant: "destructive",
      })
      return
    }

    try {
      const params = new URLSearchParams({
        formato,
        ...(filtros.categoria !== "all" && { categoria: filtros.categoria }),
        ...(filtros.busca && { busca: filtros.busca }),
      })

      const response = await fetch(`/api/exportar/copiar?${params}`)
      if (response.ok) {
        const data = await response.json()

        await navigator.clipboard.writeText(data.texto)
        toast({
          title: "Copiado",
          description: `Listagem copiada (${data.total_produtos} produtos, formato ${formato})`,
        })
      }
    } catch (error) {
      console.error("[v0] Erro ao copiar:", error)
      toast({
        title: "Erro de Conexão",
        description: "Verifique se o servidor FastAPI está rodando",
        variant: "destructive",
      })
    }
  }

  const excluirProduto = async (id: number) => {
    if (!serverAvailable) {
      toast({
        title: "Servidor Indisponível",
        description: "Inicie o servidor FastAPI primeiro: python main.py",
        variant: "destructive",
      })
      return
    }

    try {
      const response = await fetch(`/api/produtos/${id}`, {
        method: "DELETE",
      })

      if (response.ok) {
        toast({
          title: "Produto Excluído",
          description: "Produto removido com sucesso",
        })
        buscarProdutos()
      }
    } catch (error) {
      console.error("[v0] Erro ao excluir:", error)
      toast({
        title: "Erro de Conexão",
        description: "Verifique se o servidor FastAPI está rodando",
        variant: "destructive",
      })
    }
  }

  const formatarData = (isoString: string) => {
    return new Date(isoString).toLocaleString("pt-BR")
  }

  const renderEstrelas = (avaliacao: number) => {
    return "★".repeat(avaliacao) + "☆".repeat(5 - avaliacao)
  }

  useEffect(() => {
    buscarProdutos()
  }, [filtros, paginacao.pagina])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key === "f") {
        e.preventDefault()
        document.getElementById("busca-input")?.focus()
      }
      if (e.altKey && e.key === "s") {
        e.preventDefault()
        setExportDialogAberto(true)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return (
    <div className="space-y-6">
      {serverAvailable === false && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Servidor FastAPI Offline</CardTitle>
            <CardDescription>
              O servidor Python não está rodando. Os dados não podem ser carregados ou modificados.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="bg-muted p-4 rounded-lg">
              <p className="font-mono text-sm mb-2">Para usar as funcionalidades de dados:</p>
              <p className="font-mono text-sm mb-2">1. Abra um terminal na pasta do projeto</p>
              <p className="font-mono text-sm mb-2">2. Execute:</p>
              <code className="bg-background px-2 py-1 rounded text-sm">python main.py</code>
            </div>
            <p className="text-sm text-muted-foreground">
              O servidor deve iniciar em <strong>http://localhost:8000</strong>
            </p>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Filtros e Busca
              {serverAvailable === true && (
                <Badge variant="secondary" className="ml-2">
                  Servidor Online
                </Badge>
              )}
              {serverAvailable === false && (
                <Badge variant="destructive" className="ml-2">
                  Servidor Offline
                </Badge>
              )}
            </span>
            <div className="flex gap-2">
              <Button
                onClick={() => {
                  setProdutoEditando(null)
                  setDialogAberto(true)
                }}
                size="sm"
                className="flex items-center gap-2"
                disabled={!serverAvailable}
              >
                <Plus className="h-4 w-4" />
                Novo
              </Button>
              <Button onClick={() => exportarRapido("csv")} variant="outline" size="sm" disabled={!serverAvailable}>
                <FileText className="h-4 w-4 mr-2" />
                CSV
              </Button>
              <Button onClick={() => exportarRapido("excel")} variant="outline" size="sm" disabled={!serverAvailable}>
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Excel
              </Button>
              <Button onClick={() => exportarRapido("json")} variant="outline" size="sm" disabled={!serverAvailable}>
                <FileJson className="h-4 w-4 mr-2" />
                JSON
              </Button>
              <Button
                onClick={() => setExportDialogAberto(true)}
                variant="default"
                size="sm"
                className="flex items-center gap-2"
                disabled={!serverAvailable}
              >
                <Download className="h-4 w-4" />
                Exportar
                <kbd className="ml-1 text-xs bg-muted px-1 rounded">Alt+S</kbd>
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              id="busca-input"
              placeholder="Buscar produtos..."
              value={filtros.busca}
              onChange={(e) => setFiltros((prev) => ({ ...prev, busca: e.target.value }))}
              disabled={!serverAvailable}
            />
            <Select
              value={filtros.categoria}
              onValueChange={(value) => setFiltros((prev) => ({ ...prev, categoria: value }))}
              disabled={!serverAvailable}
            >
              <SelectTrigger>
                <SelectValue placeholder="Categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="Travel">Travel</SelectItem>
                <SelectItem value="Science">Science</SelectItem>
              </SelectContent>
            </Select>
            <Input
              type="date"
              value={filtros.data_inicio}
              onChange={(e) => setFiltros((prev) => ({ ...prev, data_inicio: e.target.value }))}
              disabled={!serverAvailable}
            />
            <Input
              type="date"
              value={filtros.data_fim}
              onChange={(e) => setFiltros((prev) => ({ ...prev, data_fim: e.target.value }))}
              disabled={!serverAvailable}
            />
          </div>
          <div className="flex gap-2 mt-4">
            <Button onClick={() => copiarListagem("texto")} variant="ghost" size="sm" disabled={!serverAvailable}>
              <Copy className="h-4 w-4 mr-2" />
              Copiar Texto
            </Button>
            <Button onClick={() => copiarListagem("markdown")} variant="ghost" size="sm" disabled={!serverAvailable}>
              <List className="h-4 w-4 mr-2" />
              Copiar Markdown
            </Button>
            <Button onClick={() => copiarListagem("html")} variant="ghost" size="sm" disabled={!serverAvailable}>
              <FileText className="h-4 w-4 mr-2" />
              Copiar HTML
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Produtos Coletados</CardTitle>
          <CardDescription>
            {serverAvailable === false
              ? "Servidor offline - dados não disponíveis"
              : `${paginacao.total} produtos encontrados`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Produto</TableHead>
                  <TableHead>Preço GBP</TableHead>
                  <TableHead>Preço BRL</TableHead>
                  <TableHead>Preço USD</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Avaliação</TableHead>
                  <TableHead>Disponibilidade</TableHead>
                  <TableHead>Data Coleta</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8">
                      Carregando...
                    </TableCell>
                  </TableRow>
                ) : serverAvailable === false ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8">
                      <div className="space-y-2">
                        <p className="text-muted-foreground">Servidor FastAPI não disponível</p>
                        <p className="text-sm text-muted-foreground">
                          Inicie o servidor Python para visualizar os dados
                        </p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : produtos.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8">
                      Nenhum produto encontrado
                    </TableCell>
                  </TableRow>
                ) : (
                  produtos.map((produto) => (
                    <TableRow key={produto.id}>
                      <TableCell className="font-medium max-w-xs truncate">{produto.produto_nome}</TableCell>
                      <TableCell>£{produto.preco_bruto.toFixed(2)}</TableCell>
                      <TableCell>{produto.preco_brl ? `R$ ${produto.preco_brl.toFixed(2)}` : "-"}</TableCell>
                      <TableCell>{produto.preco_usd ? `$ ${produto.preco_usd.toFixed(2)}` : "-"}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{produto.categoria}</Badge>
                      </TableCell>
                      <TableCell>
                        <span title={`${produto.avaliacao}/5 estrelas`}>{renderEstrelas(produto.avaliacao)}</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={produto.disponibilidade === "In stock" ? "default" : "secondary"}>
                          {produto.disponibilidade}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">{formatarData(produto.coleta_ts)}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setProdutoEditando(produto)
                              setDialogAberto(true)
                            }}
                            disabled={!serverAvailable}
                          >
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => excluirProduto(produto.id)}
                            disabled={!serverAvailable}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
          {paginacao.total_paginas > 1 && serverAvailable && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-muted-foreground">
                Página {paginacao.pagina} de {paginacao.total_paginas}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginacao((prev) => ({ ...prev, pagina: prev.pagina - 1 }))}
                  disabled={paginacao.pagina === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Anterior
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginacao((prev) => ({ ...prev, pagina: prev.pagina + 1 }))}
                  disabled={paginacao.pagina === paginacao.total_paginas}
                >
                  Próxima
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <ProdutoFormDialog
        aberto={dialogAberto}
        onClose={() => setDialogAberto(false)}
        produto={produtoEditando}
        onSalvar={buscarProdutos}
      />

      <ExportDialog aberto={exportDialogAberto} onClose={() => setExportDialogAberto(false)} filtrosAtuais={filtros} />
    </div>
  )
}
