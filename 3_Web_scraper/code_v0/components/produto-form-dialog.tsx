"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useToast } from "@/hooks/use-toast"

interface Produto {
  id?: number
  produto_nome: string
  preco_bruto: number
  disponibilidade: string
  categoria: string
  avaliacao: number
  produto_url: string
}

interface ProdutoFormDialogProps {
  aberto: boolean
  onClose: () => void
  produto?: Produto | null
  onSalvar: () => void
}

export function ProdutoFormDialog({ aberto, onClose, produto, onSalvar }: ProdutoFormDialogProps) {
  const [formData, setFormData] = useState<Produto>({
    produto_nome: "",
    preco_bruto: 0,
    disponibilidade: "In stock",
    categoria: "Travel",
    avaliacao: 5,
    produto_url: "",
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const { toast } = useToast()

  const isEdicao = !!produto?.id

  useEffect(() => {
    if (produto) {
      setFormData(produto)
    } else {
      setFormData({
        produto_nome: "",
        preco_bruto: 0,
        disponibilidade: "In stock",
        categoria: "Travel",
        avaliacao: 5,
        produto_url: "",
      })
    }
    setErrors({})
  }, [produto, aberto])

  const validarFormulario = () => {
    const novosErros: Record<string, string> = {}

    if (!formData.produto_nome.trim()) {
      novosErros.produto_nome = "Nome do produto é obrigatório"
    }

    if (formData.preco_bruto <= 0) {
      novosErros.preco_bruto = "Preço deve ser maior que zero"
    }

    if (!formData.produto_url.trim()) {
      novosErros.produto_url = "URL do produto é obrigatória"
    } else if (!formData.produto_url.startsWith("http")) {
      novosErros.produto_url = "URL deve começar com http:// ou https://"
    }

    setErrors(novosErros)
    return Object.keys(novosErros).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validarFormulario()) {
      return
    }

    setLoading(true)
    try {
      const url = isEdicao ? `/api/produtos/${produto!.id}` : "/api/produtos"
      const method = isEdicao ? "PUT" : "POST"

      console.log(`[v0] ${method} produto:`, formData)

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        toast({
          title: isEdicao ? "Produto Atualizado" : "Produto Criado",
          description: `Produto ${isEdicao ? "atualizado" : "criado"} com sucesso`,
        })
        onSalvar()
        onClose()
      } else {
        const error = await response.json()
        toast({
          title: "Erro",
          description: error.detail || "Erro ao salvar produto",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("[v0] Erro ao salvar produto:", error)
      toast({
        title: "Erro de Conexão",
        description: "Servidor FastAPI não disponível. Inicie o servidor Python com: python main.py",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: keyof Produto, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))

    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }))
    }
  }

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key === "s" && aberto) {
        e.preventDefault()
        handleSubmit(e as any)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [aberto, formData])

  return (
    <Dialog open={aberto} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{isEdicao ? "Editar Produto" : "Novo Produto"}</DialogTitle>
          <DialogDescription>
            {isEdicao ? "Atualize as informações do produto abaixo." : "Preencha as informações do novo produto."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="produto_nome">Nome do Produto *</Label>
            <Input
              id="produto_nome"
              value={formData.produto_nome}
              onChange={(e) => handleInputChange("produto_nome", e.target.value)}
              placeholder="Digite o nome do produto"
              className={errors.produto_nome ? "border-red-500" : ""}
            />
            {errors.produto_nome && <p className="text-sm text-red-500">{errors.produto_nome}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="preco_bruto">Preço (GBP) *</Label>
              <Input
                id="preco_bruto"
                type="number"
                step="0.01"
                min="0"
                value={formData.preco_bruto}
                onChange={(e) => handleInputChange("preco_bruto", Number.parseFloat(e.target.value) || 0)}
                placeholder="0.00"
                className={errors.preco_bruto ? "border-red-500" : ""}
              />
              {errors.preco_bruto && <p className="text-sm text-red-500">{errors.preco_bruto}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="avaliacao">Avaliação</Label>
              <Select
                value={formData.avaliacao.toString()}
                onValueChange={(value) => handleInputChange("avaliacao", Number.parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 Estrela</SelectItem>
                  <SelectItem value="2">2 Estrelas</SelectItem>
                  <SelectItem value="3">3 Estrelas</SelectItem>
                  <SelectItem value="4">4 Estrelas</SelectItem>
                  <SelectItem value="5">5 Estrelas</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="categoria">Categoria</Label>
              <Select value={formData.categoria} onValueChange={(value) => handleInputChange("categoria", value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Travel">Travel</SelectItem>
                  <SelectItem value="Science">Science</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="disponibilidade">Disponibilidade</Label>
              <Select
                value={formData.disponibilidade}
                onValueChange={(value) => handleInputChange("disponibilidade", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="In stock">In stock</SelectItem>
                  <SelectItem value="Out of stock">Out of stock</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="produto_url">URL do Produto *</Label>
            <Input
              id="produto_url"
              type="url"
              value={formData.produto_url}
              onChange={(e) => handleInputChange("produto_url", e.target.value)}
              placeholder="https://books.toscrape.com/catalogue/produto.html"
              className={errors.produto_url ? "border-red-500" : ""}
            />
            {errors.produto_url && <p className="text-sm text-red-500">{errors.produto_url}</p>}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Salvando..." : isEdicao ? "Atualizar" : "Criar"}
              <kbd className="ml-2 text-xs bg-muted px-1 rounded">Alt+S</kbd>
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
