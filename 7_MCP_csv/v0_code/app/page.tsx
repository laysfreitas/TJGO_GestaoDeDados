"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Upload, Download, Settings, Eye, FileText } from "lucide-react"

interface CSVData {
  headers: string[]
  rows: string[][]
}

interface ColumnConfig {
  name: string
  format: "text" | "number" | "currency" | "date"
  visible: boolean
  order: number
}

export default function CSVProcessor() {
  const [csvData, setCsvData] = useState<CSVData | null>(null)
  const [delimiter, setDelimiter] = useState<string>(",")
  const [columns, setColumns] = useState<ColumnConfig[]>([])
  const [currentStep, setCurrentStep] = useState<number>(1)
  const [fileName, setFileName] = useState<string>("")

  const handleFileUpload = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0]
      if (!file) return

      setFileName(file.name)
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        parseCSV(text)
      }
      reader.readAsText(file)
    },
    [delimiter],
  )

  const parseCSV = (text: string) => {
    const delim = delimiter === "tab" ? "\t" : delimiter === "pipe" ? "|" : delimiter
    const lines = text.split("\n").filter((line) => line.trim())
    const headers = lines[0].split(delim).map((h) => h.trim().replace(/"/g, ""))
    const rows = lines.slice(1).map((line) => line.split(delim).map((cell) => cell.trim().replace(/"/g, "")))

    setCsvData({ headers, rows })
    setColumns(
      headers.map((header, index) => ({
        name: header,
        format: "text" as const,
        visible: true,
        order: index,
      })),
    )
    setCurrentStep(2)
  }

  const formatValue = (value: string, format: string): string => {
    switch (format) {
      case "number":
        const num = Number.parseFloat(value)
        return isNaN(num) ? value : num.toLocaleString()
      case "currency":
        const curr = Number.parseFloat(value)
        return isNaN(curr)
          ? value
          : new Intl.NumberFormat("pt-BR", {
              style: "currency",
              currency: "BRL",
            }).format(curr)
      case "date":
        const date = new Date(value)
        return isNaN(date.getTime()) ? value : date.toLocaleDateString("pt-BR")
      default:
        return value
    }
  }

  const exportData = () => {
    if (!csvData) return

    const visibleColumns = columns.filter((col) => col.visible).sort((a, b) => a.order - b.order)

    const headers = visibleColumns.map((col) => col.name)
    const exportRows = csvData.rows.map((row) =>
      visibleColumns.map((col) => {
        const colIndex = csvData.headers.indexOf(col.name)
        return formatValue(row[colIndex] || "", col.format)
      }),
    )

    const csvContent = [headers, ...exportRows].map((row) => row.map((cell) => `"${cell}"`).join(",")).join("\n")

    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `processed_${fileName}`
    a.click()
    URL.revokeObjectURL(url)
  }

  const moveColumn = (index: number, direction: "up" | "down") => {
    const newColumns = [...columns]
    const targetIndex = direction === "up" ? index - 1 : index + 1
    if (targetIndex < 0 || targetIndex >= newColumns.length) return
    ;[newColumns[index], newColumns[targetIndex]] = [newColumns[targetIndex], newColumns[index]]
    newColumns[index].order = index
    newColumns[targetIndex].order = targetIndex
    setColumns(newColumns)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Processador de CSV</h1>
          <p className="text-lg text-gray-600">Faça upload, configure e processe seus dados CSV com facilidade</p>
        </div>

        <div className="mb-6">
          <div className="flex justify-center space-x-4">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
                  currentStep >= step ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-600"
                }`}
              >
                <span className="font-semibold">{step}</span>
                <span className="text-sm">
                  {step === 1 && "Upload"}
                  {step === 2 && "Configurar"}
                  {step === 3 && "Visualizar"}
                  {step === 4 && "Exportar"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <Tabs value={currentStep.toString()} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="1" disabled={currentStep < 1}>
              <Upload className="w-4 h-4 mr-2" />
              Upload
            </TabsTrigger>
            <TabsTrigger value="2" disabled={currentStep < 2}>
              <Settings className="w-4 h-4 mr-2" />
              Configurar
            </TabsTrigger>
            <TabsTrigger value="3" disabled={currentStep < 3}>
              <Eye className="w-4 h-4 mr-2" />
              Visualizar
            </TabsTrigger>
            <TabsTrigger value="4" disabled={currentStep < 4}>
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </TabsTrigger>
          </TabsList>

          <TabsContent value="1" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Upload do Arquivo CSV
                </CardTitle>
                <CardDescription>Selecione seu arquivo CSV e configure o delimitador</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="delimiter">Delimitador</Label>
                  <Select value={delimiter} onValueChange={setDelimiter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value=",">Vírgula (,)</SelectItem>
                      <SelectItem value=";">Ponto e vírgula (;)</SelectItem>
                      <SelectItem value="tab">Tabulação</SelectItem>
                      <SelectItem value="pipe">Pipe (|)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="file">Arquivo CSV</Label>
                  <Input id="file" type="file" accept=".csv" onChange={handleFileUpload} className="cursor-pointer" />
                </div>
                {fileName && (
                  <Badge variant="secondary" className="mt-2">
                    Arquivo: {fileName}
                  </Badge>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="2" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Configuração das Colunas</CardTitle>
                <CardDescription>Configure a visibilidade, ordem e formato das colunas</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {columns.map((column, index) => (
                    <div key={column.name} className="flex items-center space-x-4 p-4 border rounded-lg">
                      <div className="flex-1">
                        <Label className="font-medium">{column.name}</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Label htmlFor={`visible-${index}`} className="text-sm">
                          Visível
                        </Label>
                        <input
                          id={`visible-${index}`}
                          type="checkbox"
                          checked={column.visible}
                          onChange={(e) => {
                            const newColumns = [...columns]
                            newColumns[index].visible = e.target.checked
                            setColumns(newColumns)
                          }}
                        />
                      </div>
                      <Select
                        value={column.format}
                        onValueChange={(value: any) => {
                          const newColumns = [...columns]
                          newColumns[index].format = value
                          setColumns(newColumns)
                        }}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="text">Texto</SelectItem>
                          <SelectItem value="number">Número</SelectItem>
                          <SelectItem value="currency">Moeda</SelectItem>
                          <SelectItem value="date">Data</SelectItem>
                        </SelectContent>
                      </Select>
                      <div className="flex space-x-1">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => moveColumn(index, "up")}
                          disabled={index === 0}
                        >
                          ↑
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => moveColumn(index, "down")}
                          disabled={index === columns.length - 1}
                        >
                          ↓
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6">
                  <Button onClick={() => setCurrentStep(3)} className="w-full">
                    Visualizar Dados
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="3" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Visualização dos Dados</CardTitle>
                <CardDescription>Prévia dos dados processados com as configurações aplicadas</CardDescription>
              </CardHeader>
              <CardContent>
                {csvData && (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {columns
                            .filter((col) => col.visible)
                            .sort((a, b) => a.order - b.order)
                            .map((column) => (
                              <TableHead key={column.name}>{column.name}</TableHead>
                            ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {csvData.rows.slice(0, 10).map((row, rowIndex) => (
                          <TableRow key={rowIndex}>
                            {columns
                              .filter((col) => col.visible)
                              .sort((a, b) => a.order - b.order)
                              .map((column) => {
                                const colIndex = csvData.headers.indexOf(column.name)
                                return (
                                  <TableCell key={column.name}>
                                    {formatValue(row[colIndex] || "", column.format)}
                                  </TableCell>
                                )
                              })}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    {csvData.rows.length > 10 && (
                      <p className="text-sm text-gray-500 mt-2">Mostrando 10 de {csvData.rows.length} linhas</p>
                    )}
                  </div>
                )}
                <div className="mt-6">
                  <Button onClick={() => setCurrentStep(4)} className="w-full">
                    Prosseguir para Exportação
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="4" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Exportar Dados</CardTitle>
                <CardDescription>Baixe seus dados processados no formato desejado</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center space-y-4">
                  <p className="text-lg">Seus dados estão prontos para exportação!</p>
                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <strong>Colunas visíveis:</strong> {columns.filter((c) => c.visible).length}
                    </div>
                    <div>
                      <strong>Total de linhas:</strong> {csvData?.rows.length || 0}
                    </div>
                  </div>
                  <Button onClick={exportData} size="lg" className="w-full">
                    <Download className="w-4 h-4 mr-2" />
                    Baixar CSV Processado
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
