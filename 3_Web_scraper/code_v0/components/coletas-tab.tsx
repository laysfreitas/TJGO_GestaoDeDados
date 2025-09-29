"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { PlayCircle, RefreshCw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface ColetaStatus {
  status: string
  progresso: number
  total: number
  categoria_atual: string
  mensagem: string
}

export function ColetasTab() {
  const [status, setStatus] = useState<ColetaStatus>({
    status: "idle",
    progresso: 0,
    total: 100,
    categoria_atual: "",
    mensagem: "Pronto para iniciar coleta",
  })
  const [isLoading, setIsLoading] = useState(false)
  const [serverAvailable, setServerAvailable] = useState<boolean | null>(null)
  const { toast } = useToast()

  const fetchStatus = async () => {
    try {
      console.log("[v0] Tentando buscar status do servidor...")
      const response = await fetch("/api/status")
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
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
      console.error("[v0] Erro ao buscar status:", error)
      if (serverAvailable !== false) {
        setServerAvailable(false)
        setStatus({
          status: "offline",
          progresso: 0,
          total: 100,
          categoria_atual: "",
          mensagem: "Servidor FastAPI não disponível",
        })
      }
    }
  }

  const iniciarColeta = async () => {
    if (!serverAvailable) {
      toast({
        title: "Servidor Indisponível",
        description: "Inicie o servidor FastAPI primeiro: python main.py",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch("/api/coleta/iniciar", {
        method: "POST",
      })

      if (response.ok) {
        toast({
          title: "Coleta Iniciada",
          description: "A coleta de dados foi iniciada com sucesso.",
        })
        const interval = setInterval(fetchStatus, 2000)

        const checkComplete = setInterval(() => {
          if (!status.status.includes("ativa")) {
            clearInterval(interval)
            clearInterval(checkComplete)
          }
        }, 1000)
      } else {
        const error = await response.json()
        toast({
          title: "Erro",
          description: error.detail || "Erro ao iniciar coleta",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Erro de Conexão",
        description: "Verifique se o servidor FastAPI está rodando na porta 8000",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const isActive = status.mensagem.includes("ativa") || isLoading
  const isComplete = status.progresso === 100 && !isActive

  return (
    <div className="space-y-6">
      {serverAvailable === false && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Servidor FastAPI Offline</CardTitle>
            <CardDescription>O servidor Python não está rodando. Siga os passos abaixo para iniciar:</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="bg-muted p-4 rounded-lg">
              <p className="font-mono text-sm mb-2">1. Abra um terminal na pasta do projeto</p>
              <p className="font-mono text-sm mb-2">2. Instale as dependências:</p>
              <code className="bg-background px-2 py-1 rounded text-sm">pip install -r requirements.txt</code>
              <p className="font-mono text-sm mt-2 mb-2">3. Inicie o servidor:</p>
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
          <CardTitle className="flex items-center gap-2">
            <PlayCircle className="h-5 w-5" />
            Controle de Coleta
            {serverAvailable === true && (
              <Badge variant="secondary" className="ml-auto">
                Servidor Online
              </Badge>
            )}
            {serverAvailable === false && (
              <Badge variant="destructive" className="ml-auto">
                Servidor Offline
              </Badge>
            )}
          </CardTitle>
          <CardDescription>Inicie e monitore o processo de coleta de preços do Books to Scrape</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Button
              onClick={iniciarColeta}
              disabled={isActive || !serverAvailable}
              size="lg"
              className="flex items-center gap-2"
            >
              {isActive ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Coletando...
                </>
              ) : (
                <>
                  <PlayCircle className="h-4 w-4" />
                  Iniciar Coleta
                </>
              )}
            </Button>

            <Badge variant={isActive ? "default" : isComplete ? "secondary" : "outline"}>
              {isActive ? "Em Andamento" : isComplete ? "Concluído" : "Aguardando"}
            </Badge>
          </div>

          {status.categoria_atual && status.status !== "offline" && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>
                  Categoria Atual: <strong>{status.categoria_atual}</strong>
                </span>
                <span>{status.progresso}%</span>
              </div>
              <Progress value={status.progresso} className="w-full" />
              <p className="text-sm text-muted-foreground">{status.mensagem}</p>
            </div>
          )}

          {status.status === "offline" && (
            <div className="text-center py-4">
              <p className="text-muted-foreground">{status.mensagem}</p>
              <p className="text-sm text-muted-foreground mt-2">
                Inicie o servidor FastAPI para usar a funcionalidade de coleta
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Configurações de Coleta</CardTitle>
          <CardDescription>Parâmetros utilizados na coleta automatizada</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Site Alvo:</strong>
              <p className="text-muted-foreground">Books to Scrape</p>
            </div>
            <div>
              <strong>Categorias:</strong>
              <p className="text-muted-foreground">Travel, Science</p>
            </div>
            <div>
              <strong>Intervalo entre Requisições:</strong>
              <p className="text-muted-foreground">1 segundo mínimo</p>
            </div>
            <div>
              <strong>Conformidade:</strong>
              <p className="text-muted-foreground">Respeita robots.txt</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
