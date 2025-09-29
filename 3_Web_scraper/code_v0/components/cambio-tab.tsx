"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { TrendingUp, RefreshCw, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface CambioInfo {
  cambio_ts: string
  gbp_brl: number
  gbp_usd: number
  fonte?: string
  base_currency?: string
}

interface CambioStatus {
  conexao_ativa: boolean
  ultima_atualizacao?: string
  fonte?: string
  cache_ativo: boolean
  erro?: string
}

export function CambioTab() {
  const [cambio, setCambio] = useState<CambioInfo | null>(null)
  const [status, setStatus] = useState<CambioStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [atualizando, setAtualizando] = useState(false)
  const [serverAvailable, setServerAvailable] = useState<boolean | null>(null)
  const { toast } = useToast()

  const buscarCambio = async () => {
    setLoading(true)
    try {
      console.log("[v0] Buscando dados de câmbio...")
      const response = await fetch("/api/cambio")
      if (response.ok) {
        const data = await response.json()
        setCambio(data)
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
        if (response.status === 404) {
          setServerAvailable(true)
          toast({
            title: "Dados Não Disponíveis",
            description: "Execute uma coleta primeiro para obter dados de câmbio.",
            variant: "destructive",
          })
        } else {
          throw new Error(`HTTP ${response.status}`)
        }
      }
    } catch (error) {
      console.error("[v0] Erro ao buscar câmbio:", error)
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

  const buscarStatus = async () => {
    try {
      console.log("[v0] Verificando status do câmbio...")
      const response = await fetch("/api/cambio/status")
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
        if (serverAvailable === null || serverAvailable === false) {
          setServerAvailable(true)
        }
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.error("[v0] Erro ao buscar status do câmbio:", error)
      if (serverAvailable !== false) {
        setServerAvailable(false)
      }
    }
  }

  const atualizarCambio = async () => {
    if (!serverAvailable) {
      toast({
        title: "Servidor Indisponível",
        description: "Inicie o servidor FastAPI primeiro: python main.py",
        variant: "destructive",
      })
      return
    }

    setAtualizando(true)
    try {
      const response = await fetch("/api/cambio/atualizar", {
        method: "POST",
      })

      if (response.ok) {
        const data = await response.json()
        setCambio(data.taxas)
        toast({
          title: "Câmbio Atualizado",
          description: "Taxas de câmbio atualizadas com sucesso",
        })
        await buscarStatus()
      } else {
        const error = await response.json()
        toast({
          title: "Erro",
          description: error.detail || "Erro ao atualizar câmbio",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("[v0] Erro ao atualizar câmbio:", error)
      toast({
        title: "Erro de Conexão",
        description: "Verifique se o servidor FastAPI está rodando na porta 8000",
        variant: "destructive",
      })
    } finally {
      setAtualizando(false)
    }
  }

  const formatarData = (isoString: string) => {
    return new Date(isoString).toLocaleString("pt-BR")
  }

  const calcularExemplo = (valor: number, taxa: number) => {
    return (valor * taxa).toFixed(2)
  }

  const getStatusIcon = () => {
    if (!status && serverAvailable === false) return <XCircle className="h-4 w-4 text-red-500" />
    if (!status) return <AlertCircle className="h-4 w-4 text-muted-foreground" />
    if (status.conexao_ativa) return <CheckCircle className="h-4 w-4 text-green-500" />
    return <XCircle className="h-4 w-4 text-red-500" />
  }

  const getStatusText = () => {
    if (serverAvailable === false) return "Servidor Offline"
    if (!status) return "Verificando..."
    if (status.conexao_ativa) return "Conectado"
    return "Desconectado"
  }

  const getStatusVariant = () => {
    if (serverAvailable === false) return "destructive"
    if (!status) return "outline"
    if (status.conexao_ativa) return "default"
    return "destructive"
  }

  useEffect(() => {
    buscarCambio()
    buscarStatus()

    const interval = setInterval(buscarStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      {serverAvailable === false && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Servidor FastAPI Offline</CardTitle>
            <CardDescription>
              O servidor Python não está rodando. As funcionalidades de câmbio não estão disponíveis.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="bg-muted p-4 rounded-lg">
              <p className="font-mono text-sm mb-2">Para usar as funcionalidades de câmbio:</p>
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
              <TrendingUp className="h-5 w-5" />
              Taxas de Câmbio Atuais
            </span>
            <div className="flex items-center gap-2">
              <Badge variant={getStatusVariant()} className="flex items-center gap-1">
                {getStatusIcon()}
                {getStatusText()}
              </Badge>
              <Button onClick={buscarCambio} variant="outline" size="sm" disabled={loading || !serverAvailable}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
                Recarregar
              </Button>
              <Button onClick={atualizarCambio} size="sm" disabled={atualizando || !serverAvailable}>
                <RefreshCw className={`h-4 w-4 mr-2 ${atualizando ? "animate-spin" : ""}`} />
                {atualizando ? "Atualizando..." : "Atualizar"}
              </Button>
            </div>
          </CardTitle>
          <CardDescription>
            Taxas utilizadas na conversão de preços (GBP para outras moedas) via MCP API Client
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p>Carregando dados de câmbio...</p>
            </div>
          ) : serverAvailable === false ? (
            <div className="text-center py-8">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-medium mb-2">Servidor FastAPI Offline</h3>
              <p className="text-muted-foreground mb-4">
                Inicie o servidor Python para acessar as funcionalidades de câmbio.
              </p>
              <Badge variant="destructive">Servidor não disponível</Badge>
            </div>
          ) : cambio ? (
            <div className="space-y-6">
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Última atualização: {formatarData(cambio.cambio_ts)}
                </div>
                {cambio.fonte && <Badge variant="outline">Fonte: {cambio.fonte}</Badge>}
                {status?.cache_ativo && <Badge variant="secondary">Cache Ativo</Badge>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center gap-2">🇬🇧 GBP → 🇧🇷 BRL</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-3xl font-bold text-green-600">R$ {cambio.gbp_brl.toFixed(4)}</div>
                      <div className="text-sm text-muted-foreground">
                        1 Libra Esterlina = {cambio.gbp_brl.toFixed(4)} Reais
                      </div>
                      <div className="pt-2 border-t">
                        <p className="text-sm font-medium mb-2">Exemplos de conversão:</p>
                        <div className="space-y-1 text-sm">
                          <div>£10.00 = R$ {calcularExemplo(10, cambio.gbp_brl)}</div>
                          <div>£25.50 = R$ {calcularExemplo(25.5, cambio.gbp_brl)}</div>
                          <div>£100.00 = R$ {calcularExemplo(100, cambio.gbp_brl)}</div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center gap-2">🇬🇧 GBP → 🇺🇸 USD</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-3xl font-bold text-blue-600">$ {cambio.gbp_usd.toFixed(4)}</div>
                      <div className="text-sm text-muted-foreground">
                        1 Libra Esterlina = {cambio.gbp_usd.toFixed(4)} Dólares
                      </div>
                      <div className="pt-2 border-t">
                        <p className="text-sm font-medium mb-2">Exemplos de conversão:</p>
                        <div className="space-y-1 text-sm">
                          <div>£10.00 = $ {calcularExemplo(10, cambio.gbp_usd)}</div>
                          <div>£25.50 = $ {calcularExemplo(25.5, cambio.gbp_usd)}</div>
                          <div>£100.00 = $ {calcularExemplo(100, cambio.gbp_usd)}</div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-muted/50">
                <CardHeader>
                  <CardTitle className="text-base">Informações do Sistema</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-2">
                  <p>• As taxas são obtidas via MCP API Client da API exchangerate.host</p>
                  <p>• Sistema de cache de 5 minutos para otimizar performance</p>
                  <p>• Validação automática de conexão com a API externa</p>
                  <p>• Os preços convertidos são calculados automaticamente para cada produto</p>
                  <p>• Para taxas mais recentes, use o botão "Atualizar" ou execute uma nova coleta</p>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="text-center py-8">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-medium mb-2">Dados de Câmbio Não Disponíveis</h3>
              <p className="text-muted-foreground mb-4">
                Execute uma coleta de dados ou clique em "Atualizar" para obter as taxas de câmbio atuais.
              </p>
              <div className="flex justify-center gap-2">
                <Badge variant="outline">Aguardando primeira coleta</Badge>
                {status?.erro && <Badge variant="destructive">Erro: {status.erro}</Badge>}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
