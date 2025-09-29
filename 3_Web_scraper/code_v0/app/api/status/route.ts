import { NextResponse } from "next/server"

export async function GET() {
  return NextResponse.json({
    status: "idle",
    progresso: 0,
    total: 100,
    categoria_atual: "",
    mensagem: "Sistema pronto para coleta",
  })
}
