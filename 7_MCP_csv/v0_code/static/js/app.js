let currentData = null
let selectedColumns = []
const columnFormats = {}

// Import Sortable library
import Sortable from "sortablejs"

// Configuração do upload de arquivo
document.addEventListener("DOMContentLoaded", () => {
  const uploadArea = document.getElementById("upload-area")
  const fileInput = document.getElementById("file-input")

  // Drag and drop
  uploadArea.addEventListener("dragover", (e) => {
    e.preventDefault()
    uploadArea.classList.add("drag-over")
  })

  uploadArea.addEventListener("dragleave", (e) => {
    e.preventDefault()
    uploadArea.classList.remove("drag-over")
  })

  uploadArea.addEventListener("drop", (e) => {
    e.preventDefault()
    uploadArea.classList.remove("drag-over")
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  })

  // Click para selecionar arquivo
  uploadArea.addEventListener("click", () => {
    fileInput.click()
  })

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0])
    }
  })
})

function handleFileUpload(file) {
  const formData = new FormData()
  formData.append("file", file)

  showLoading()

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      hideLoading()
      if (data.success) {
        currentData = data
        showConfigSection(data)
        updateStepIndicator(2)
      } else {
        showAlert("Erro: " + data.error, "danger")
      }
    })
    .catch((error) => {
      hideLoading()
      showAlert("Erro ao fazer upload: " + error.message, "danger")
    })
}

function showConfigSection(data) {
  document.getElementById("upload-section").style.display = "none"
  document.getElementById("config-section").style.display = "block"

  // Configurar delimitador detectado
  document.getElementById("delimiter-select").value = data.detected_delimiter

  // Mostrar informações do arquivo
  const fileInfo = document.getElementById("file-info")
  fileInfo.innerHTML = `
        <strong>Colunas:</strong> ${data.columns.length}<br>
        <strong>Linhas:</strong> ${data.total_rows}<br>
        <strong>Delimitador:</strong> ${getDelimiterName(data.detected_delimiter)}
    `

  // Mostrar preview
  showPreviewTable(data.sample_data, data.columns)
}

function showPreviewTable(sampleData, columns) {
  const table = document.getElementById("preview-table")
  let html = "<thead><tr>"

  columns.forEach((col) => {
    html += `<th>${col}</th>`
  })
  html += "</tr></thead><tbody>"

  sampleData.forEach((row) => {
    html += "<tr>"
    columns.forEach((col) => {
      html += `<td>${row[col] || ""}</td>`
    })
    html += "</tr>"
  })
  html += "</tbody>"

  table.innerHTML = html
}

function reconfigureDelimiter() {
  const delimiter = document.getElementById("delimiter-select").value

  showLoading()

  fetch("/configure", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ delimiter: delimiter }),
  })
    .then((response) => response.json())
    .then((data) => {
      hideLoading()
      if (data.success) {
        currentData = data
        showConfigSection(data)
        showAlert("Delimitador reconfigurado com sucesso!", "success")
      } else {
        showAlert("Erro: " + data.error, "danger")
      }
    })
    .catch((error) => {
      hideLoading()
      showAlert("Erro ao reconfigurar: " + error.message, "danger")
    })
}

function goToColumnSelection() {
  document.getElementById("config-section").style.display = "none"
  document.getElementById("column-section").style.display = "block"
  updateStepIndicator(3)

  // Preencher colunas disponíveis
  const availableColumns = document.getElementById("available-columns")
  availableColumns.innerHTML = ""

  currentData.columns.forEach((column) => {
    const columnDiv = document.createElement("div")
    columnDiv.className = "column-item"
    columnDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>${column}</span>
                <small class="text-muted">${currentData.data_types[column]}</small>
            </div>
        `
    columnDiv.onclick = () => selectColumn(column, columnDiv)
    availableColumns.appendChild(columnDiv)
  })

  // Configurar sortable para colunas selecionadas
  const selectedColumnsElement = document.getElementById("selected-columns")
  new Sortable(selectedColumnsElement, {
    animation: 150,
    ghostClass: "sortable-ghost",
  })
}

function selectColumn(column, element) {
  if (selectedColumns.includes(column)) {
    // Remover coluna
    selectedColumns = selectedColumns.filter((col) => col !== column)
    element.classList.remove("selected-column")
    removeFromSelectedColumns(column)
  } else {
    // Adicionar coluna
    selectedColumns.push(column)
    element.classList.add("selected-column")
    addToSelectedColumns(column)
  }
}

function addToSelectedColumns(column) {
  const selectedDiv = document.getElementById("selected-columns")

  // Remover mensagem de placeholder se existir
  const placeholder = selectedDiv.querySelector("p")
  if (placeholder) {
    placeholder.remove()
  }

  const columnDiv = document.createElement("div")
  columnDiv.className = "column-item selected-column"
  columnDiv.dataset.column = column
  columnDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <span><i class="fas fa-grip-vertical me-2"></i>${column}</span>
            <button class="btn btn-sm btn-outline-danger" onclick="removeColumn('${column}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `
  selectedDiv.appendChild(columnDiv)
}

function removeFromSelectedColumns(column) {
  const element = document.querySelector(`[data-column="${column}"]`)
  if (element) {
    element.remove()
  }

  // Adicionar placeholder se não há colunas selecionadas
  const selectedDiv = document.getElementById("selected-columns")
  if (selectedDiv.children.length === 0) {
    selectedDiv.innerHTML = '<p class="text-muted text-center">Clique nas colunas à esquerda para selecioná-las</p>'
  }
}

function removeColumn(column) {
  selectedColumns = selectedColumns.filter((col) => col !== column)
  removeFromSelectedColumns(column)

  // Remover seleção visual da coluna disponível
  const availableColumns = document.getElementById("available-columns")
  const columnElements = availableColumns.querySelectorAll(".column-item")
  columnElements.forEach((el) => {
    if (el.textContent.includes(column)) {
      el.classList.remove("selected-column")
    }
  })
}

function goToFormatting() {
  if (selectedColumns.length === 0) {
    showAlert("Selecione pelo menos uma coluna para continuar.", "warning")
    return
  }

  document.getElementById("column-section").style.display = "none"
  document.getElementById("format-section").style.display = "block"
  updateStepIndicator(4)

  // Atualizar ordem das colunas baseada na ordem visual
  const selectedElements = document.getElementById("selected-columns").children
  selectedColumns = Array.from(selectedElements).map((el) => el.dataset.column)

  // Criar controles de formatação
  createFormatControls()
}

function createFormatControls() {
  const formatControls = document.getElementById("format-controls")
  formatControls.innerHTML = ""

  selectedColumns.forEach((column) => {
    const controlDiv = document.createElement("div")
    controlDiv.className = "mb-4 p-3 border rounded"
    controlDiv.innerHTML = `
            <h6>${column}</h6>
            <div class="row">
                <div class="col-md-4">
                    <label class="form-label">Tipo de Formatação:</label>
                    <select class="form-select format-type" data-column="${column}" onchange="toggleFormatOptions('${column}')">
                        <option value="string">Texto (sem formatação)</option>
                        <option value="number">Número</option>
                        <option value="currency">Moeda</option>
                        <option value="date">Data</option>
                    </select>
                </div>
                <div class="col-md-8">
                    <div id="format-options-${column}" class="format-options">
                        <!-- Opções específicas aparecerão aqui -->
                    </div>
                </div>
            </div>
        `
    formatControls.appendChild(controlDiv)
  })
}

function toggleFormatOptions(column) {
  const select = document.querySelector(`[data-column="${column}"]`)
  const optionsDiv = document.getElementById(`format-options-${column}`)
  const formatType = select.value

  let optionsHtml = ""

  switch (formatType) {
    case "number":
      optionsHtml = `
                <label class="form-label">Casas Decimais:</label>
                <input type="number" class="form-control" min="0" max="10" value="2" 
                       onchange="updateColumnFormat('${column}', 'decimal_places', this.value)">
            `
      break
    case "currency":
      optionsHtml = `
                <div class="row">
                    <div class="col-6">
                        <label class="form-label">Símbolo:</label>
                        <input type="text" class="form-control" value="R$" 
                               onchange="updateColumnFormat('${column}', 'symbol', this.value)">
                    </div>
                    <div class="col-6">
                        <label class="form-label">Casas Decimais:</label>
                        <input type="number" class="form-control" min="0" max="10" value="2" 
                               onchange="updateColumnFormat('${column}', 'decimal_places', this.value)">
                    </div>
                </div>
            `
      break
    case "date":
      optionsHtml = `
                <label class="form-label">Formato de Data:</label>
                <select class="form-select" onchange="updateColumnFormat('${column}', 'format', this.value)">
                    <option value="%Y-%m-%d">YYYY-MM-DD</option>
                    <option value="%d/%m/%Y">DD/MM/YYYY</option>
                    <option value="%m/%d/%Y">MM/DD/YYYY</option>
                    <option value="%d-%m-%Y">DD-MM-YYYY</option>
                    <option value="%Y/%m/%d">YYYY/MM/DD</option>
                </select>
            `
      break
  }

  optionsDiv.innerHTML = optionsHtml

  // Inicializar formato da coluna
  if (!columnFormats[column]) {
    columnFormats[column] = {}
  }
  columnFormats[column].type = formatType

  // Definir valores padrão
  if (formatType === "number") {
    columnFormats[column].decimal_places = 2
  } else if (formatType === "currency") {
    columnFormats[column].symbol = "R$"
    columnFormats[column].decimal_places = 2
  } else if (formatType === "date") {
    columnFormats[column].format = "%Y-%m-%d"
  }
}

function updateColumnFormat(column, property, value) {
  if (!columnFormats[column]) {
    columnFormats[column] = {}
  }
  columnFormats[column][property] = value
}

function processData() {
  showLoading()

  const requestData = {
    selected_columns: selectedColumns,
    column_order: selectedColumns,
    column_formats: columnFormats,
  }

  fetch("/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestData),
  })
    .then((response) => response.json())
    .then((data) => {
      hideLoading()
      if (data.success) {
        showResultSection(data)
        updateStepIndicator(5)
      } else {
        showAlert("Erro: " + data.error, "danger")
      }
    })
    .catch((error) => {
      hideLoading()
      showAlert("Erro ao processar dados: " + error.message, "danger")
    })
}

function showResultSection(data) {
  document.getElementById("format-section").style.display = "none"
  document.getElementById("result-section").style.display = "block"

  // Criar tabela de resultado
  const table = document.getElementById("result-table")
  let html = '<thead class="table-dark"><tr>'

  data.columns.forEach((col) => {
    html += `<th>${col}</th>`
  })
  html += "</tr></thead><tbody>"

  data.data.forEach((row) => {
    html += "<tr>"
    data.columns.forEach((col) => {
      html += `<td>${row[col] || ""}</td>`
    })
    html += "</tr>"
  })
  html += "</tbody>"

  table.innerHTML = html

  showAlert(`Dados processados com sucesso! ${data.total_rows} linhas processadas.`, "success")
}

function exportData() {
  window.location.href = "/export"
}

// Funções auxiliares
function updateStepIndicator(currentStep) {
  for (let i = 1; i <= 5; i++) {
    const step = document.getElementById(`step-${i}`)
    step.classList.remove("active", "completed")

    if (i < currentStep) {
      step.classList.add("completed")
    } else if (i === currentStep) {
      step.classList.add("active")
    }
  }
}

function showLoading() {
  document.getElementById("loading").style.display = "block"
}

function hideLoading() {
  document.getElementById("loading").style.display = "none"
}

function showAlert(message, type) {
  const alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  document.querySelector(".container").insertBefore(alertDiv, document.querySelector(".container").firstChild)

  // Auto-remover após 5 segundos
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove()
    }
  }, 5000)
}

function getDelimiterName(delimiter) {
  const names = {
    ",": "Vírgula (,)",
    ";": "Ponto e vírgula (;)",
    "\t": "Tabulação",
    "|": "Pipe (|)",
  }
  return names[delimiter] || delimiter
}

// Funções de navegação
function goToConfig() {
  document.getElementById("column-section").style.display = "none"
  document.getElementById("config-section").style.display = "block"
  updateStepIndicator(2)
}
