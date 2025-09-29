"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ColetasTab } from "@/components/coletas-tab"
import { DadosTab } from "@/components/dados-tab"
import { CambioTab } from "@/components/cambio-tab"

export function PageContent() {
  const [activeTab, setActiveTab] = useState("coletas")

  // Atalhos de teclado globais
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey) {
        switch (e.key) {
          case "n":
            e.preventDefault()
            setActiveTab("coletas")
            break
          case "f":
            e.preventDefault()
            setActiveTab("dados")
            break
          case "c":
            e.preventDefault()
            setActiveTab("cambio")
            break
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-foreground">Coleta de Preços de Produtos</h1>
          <p className="text-muted-foreground mt-2">Sistema automatizado de coleta e análise de preços</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="coletas" className="flex items-center gap-2">
              <span>📊</span>
              Coletas
              <kbd className="ml-2 text-xs bg-muted px-1 rounded">Alt+N</kbd>
            </TabsTrigger>
            <TabsTrigger value="dados" className="flex items-center gap-2">
              <span>📋</span>
              Dados
              <kbd className="ml-2 text-xs bg-muted px-1 rounded">Alt+F</kbd>
            </TabsTrigger>
            <TabsTrigger value="cambio" className="flex items-center gap-2">
              <span>💱</span>
              Câmbio
              <kbd className="ml-2 text-xs bg-muted px-1 rounded">Alt+C</kbd>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="coletas" className="mt-6">
            <ColetasTab />
          </TabsContent>

          <TabsContent value="dados" className="mt-6">
            <DadosTab />
          </TabsContent>

          <TabsContent value="cambio" className="mt-6">
            <CambioTab />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
