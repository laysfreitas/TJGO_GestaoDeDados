import { NextResponse } from "next/server"
import { mockProdutos } from "@/lib/mock-data"

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const pagina = Number.parseInt(searchParams.get("pagina") || "1")
    const porPagina = Number.parseInt(searchParams.get("por_pagina") || "20")
    const categoria = searchParams.get("categoria") || ""
    const busca = searchParams.get("busca") || ""

    console.log("[v0] Buscando produtos:", { pagina, porPagina, categoria, busca })

    let produtos = mockProdutos.getAll()

    // Filtrar por categoria
    if (categoria) {
      produtos = produtos.filter((p) => p.categoria === categoria)
    }

    // Filtrar por busca
    if (busca) {
      const buscaLower = busca.toLowerCase()
      produtos = produtos.filter(
        (p) => p.titulo.toLowerCase().includes(buscaLower) || p.categoria.toLowerCase().includes(buscaLower),
      )
    }

    // Paginação
    const total = produtos.length
    const totalPaginas = Math.ceil(total / porPagina)
    const inicio = (pagina - 1) * porPagina
    const fim = inicio + porPagina
    const produtosPaginados = produtos.slice(inicio, fim)

    console.log(`[v0] Retornando ${produtosPaginados.length} de ${total} produtos`)

    return NextResponse.json({
      produtos: produtosPaginados,
      total,
      pagina,
      por_pagina: porPagina,
      total_paginas: totalPaginas,
    })
  } catch (error) {
    console.error("[v0] Erro ao buscar produtos:", error)

    return NextResponse.json({
      produtos: [],
      total: 0,
      pagina: 1,
      por_pagina: 20,
      total_paginas: 0,
      erro: "Erro ao buscar produtos",
    })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()

    console.log("[v0] Criando produto:", body)

    const novoProduto = mockProdutos.create({
      titulo: body.titulo,
      preco_gbp: body.preco_gbp,
      preco_brl: body.preco_brl,
      disponibilidade: body.disponibilidade || "In stock",
      categoria: body.categoria,
      avaliacao: body.avaliacao || 0,
      url: body.url || "",
      data_coleta: new Date().toISOString(),
    })

    console.log("[v0] Produto criado com sucesso:", novoProduto)

    return NextResponse.json(novoProduto)
  } catch (error) {
    console.error("[v0] Erro ao criar produto:", error)

    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Erro ao criar produto" },
      { status: 500 },
    )
  }
}

export async function PUT(request: Request) {
  try {
    const body = await request.json()
    const { id, ...dados } = body

    console.log("[v0] Atualizando produto:", id, dados)

    const produtoAtualizado = mockProdutos.update(id, dados)

    if (!produtoAtualizado) {
      return NextResponse.json({ detail: "Produto não encontrado" }, { status: 404 })
    }

    console.log("[v0] Produto atualizado com sucesso:", produtoAtualizado)

    return NextResponse.json(produtoAtualizado)
  } catch (error) {
    console.error("[v0] Erro ao atualizar produto:", error)

    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Erro ao atualizar produto" },
      { status: 500 },
    )
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const id = Number.parseInt(searchParams.get("id") || "0")

    console.log("[v0] Deletando produto:", id)

    const sucesso = mockProdutos.delete(id)

    if (!sucesso) {
      return NextResponse.json({ detail: "Produto não encontrado" }, { status: 404 })
    }

    console.log("[v0] Produto deletado com sucesso")

    return NextResponse.json({ mensagem: "Produto deletado com sucesso" })
  } catch (error) {
    console.error("[v0] Erro ao deletar produto:", error)

    return NextResponse.json(
      { detail: error instanceof Error ? error.message : "Erro ao deletar produto" },
      { status: 500 },
    )
  }
}
