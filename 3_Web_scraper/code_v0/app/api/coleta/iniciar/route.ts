import { NextResponse } from "next/server"
import { mockBooksData, mockProdutos } from "@/lib/mock-data"

export async function POST() {
  try {
    console.log("[v0] Iniciando coleta simulada de dados")

    // Simular delay de processamento
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Limpar produtos existentes
    mockProdutos.clear()

    // Simular taxa de câmbio GBP para BRL
    const taxaCambio = 6.15

    // Adicionar produtos simulados
    let produtosAdicionados = 0
    for (const book of mockBooksData) {
      const produto = {
        titulo: book.titulo,
        preco_gbp: book.preco_gbp,
        preco_brl: Number((book.preco_gbp * taxaCambio).toFixed(2)),
        disponibilidade: book.disponibilidade,
        categoria: book.categoria,
        avaliacao: book.avaliacao,
        url: book.url,
        data_coleta: new Date().toISOString(),
      }
      mockProdutos.create(produto)
      produtosAdicionados++
    }

    console.log(`[v0] Coleta concluída: ${produtosAdicionados} produtos adicionados`)

    return NextResponse.json({
      mensagem: "Coleta iniciada com sucesso",
      status: "concluido",
      produtos_coletados: produtosAdicionados,
    })
  } catch (error) {
    console.error("[v0] Erro ao iniciar coleta:", error)

    return NextResponse.json(
      {
        detail: error instanceof Error ? error.message : "Erro ao processar coleta",
      },
      { status: 500 },
    )
  }
}
