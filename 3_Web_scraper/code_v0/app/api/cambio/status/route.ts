import { NextResponse } from "next/server"

export async function GET() {
  try {
    console.log("[v0] Verificando status da API de câmbio")

    // Tentar verificar se a API está acessível
    const response = await fetch("https://api.exchangerate.host/latest?base=GBP&symbols=BRL", {
      method: "GET",
    })

    const conexaoAtiva = response.ok

    console.log("[v0] Status da API de câmbio:", conexaoAtiva ? "online" : "offline")

    return NextResponse.json({
      conexao_ativa: conexaoAtiva,
      ultima_atualizacao: new Date().toISOString(),
      fonte: "exchangerate.host",
      cache_ativo: true,
      mensagem: conexaoAtiva
        ? "API de câmbio funcionando normalmente"
        : "API de câmbio indisponível, usando dados em cache",
    })
  } catch (error) {
    console.error("[v0] Erro ao verificar status do câmbio:", error)

    return NextResponse.json({
      conexao_ativa: false,
      ultima_atualizacao: new Date().toISOString(),
      fonte: "exchangerate.host",
      cache_ativo: true,
      mensagem: "Erro ao conectar com API de câmbio, usando dados em cache",
    })
  }
}
