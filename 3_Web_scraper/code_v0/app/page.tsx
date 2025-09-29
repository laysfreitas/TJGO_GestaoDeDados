"use client"

import { Suspense } from "react"
import { PageContent } from "@/components/page-content"

export default function Home() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Carregando aplicação...</p>
          </div>
        </div>
      }
    >
      <PageContent />
    </Suspense>
  )
}
