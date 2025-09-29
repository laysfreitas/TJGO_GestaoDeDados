import { NextResponse } from "next/server"

export async function GET() {
  try {
    console.log("[v0] Buscando taxas de câmbio da API exchangerate.host")

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
    console.log("[v0] Dados de câmbio recebidos:", data)

    return NextResponse.json({
      base: data.base,
      data: data.date,
      taxas: data.rates,
      ultima_atualizacao: new Date().toISOString(),
    })
  } catch (error) {
    console.error("[v0] Erro ao buscar câmbio:", error)

    // Retornar dados simulados em caso de erro
    return NextResponse.json({
      base: "GBP",
      data: new Date().toISOString().split("T")[0],
      taxas: {
        BRL: 6.15,
        USD: 1.27,
        EUR: 1.17,
      },
      ultima_atualizacao: new Date().toISOString(),
      simulado: true,
    })
  }
}
