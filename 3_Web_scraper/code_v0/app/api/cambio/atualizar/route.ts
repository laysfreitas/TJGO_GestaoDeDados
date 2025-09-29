import { NextResponse } from "next/server"

export async function POST() {
  try {
    console.log("[v0] Atualizando taxas de câmbio")

    const response = await fetch("https://api.exchangerate.host/latest?base=GBP&symbols=BRL,USD,EUR", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }

    const data = await response.json()
    console.log("[v0] Taxas de câmbio atualizadas com sucesso:", data)

    return NextResponse.json({
      mensagem: "Taxas de câmbio atualizadas com sucesso",
      base: data.base,
      data: data.date,
      taxas: data.rates,
      ultima_atualizacao: new Date().toISOString(),
    })
  } catch (error) {
    console.error("[v0] Erro ao atualizar câmbio:", error)

    return NextResponse.json(
      {
        detail: error instanceof Error ? error.message : "Erro ao atualizar taxas de câmbio",
        mensagem: "Não foi possível atualizar as taxas. Usando dados em cache.",
      },
      { status: 500 },
    )
  }
}
