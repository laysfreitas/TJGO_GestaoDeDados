// Dados simulados para demonstração
export interface Produto {
  id: number
  titulo: string
  preco_gbp: number
  preco_brl: number
  disponibilidade: string
  categoria: string
  avaliacao: number
  url: string
  data_coleta: string
}

let produtos: Produto[] = []
let nextId = 1

export const mockProdutos = {
  getAll: () => produtos,

  getById: (id: number) => produtos.find((p) => p.id === id),

  create: (produto: Omit<Produto, "id">) => {
    const novoProduto = { ...produto, id: nextId++ }
    produtos.push(novoProduto)
    return novoProduto
  },

  update: (id: number, produto: Partial<Produto>) => {
    const index = produtos.findIndex((p) => p.id === id)
    if (index !== -1) {
      produtos[index] = { ...produtos[index], ...produto }
      return produtos[index]
    }
    return null
  },

  delete: (id: number) => {
    const index = produtos.findIndex((p) => p.id === id)
    if (index !== -1) {
      produtos.splice(index, 1)
      return true
    }
    return false
  },

  clear: () => {
    produtos = []
    nextId = 1
  },
}

// Dados simulados de livros do Books to Scrape
export const mockBooksData = [
  {
    titulo: "A Light in the Attic",
    preco_gbp: 51.77,
    categoria: "Poetry",
    avaliacao: 3,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  },
  {
    titulo: "Tipping the Velvet",
    preco_gbp: 53.74,
    categoria: "Historical Fiction",
    avaliacao: 1,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
  },
  {
    titulo: "Soumission",
    preco_gbp: 50.1,
    categoria: "Fiction",
    avaliacao: 1,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/soumission_998/index.html",
  },
  {
    titulo: "Sharp Objects",
    preco_gbp: 47.82,
    categoria: "Mystery",
    avaliacao: 4,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/sharp-objects_997/index.html",
  },
  {
    titulo: "Sapiens: A Brief History of Humankind",
    preco_gbp: 54.23,
    categoria: "History",
    avaliacao: 5,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html",
  },
  {
    titulo: "The Requiem Red",
    preco_gbp: 22.65,
    categoria: "Young Adult",
    avaliacao: 1,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/the-requiem-red_995/index.html",
  },
  {
    titulo: "The Dirty Little Secrets of Getting Your Dream Job",
    preco_gbp: 33.34,
    categoria: "Business",
    avaliacao: 4,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html",
  },
  {
    titulo: "The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull",
    preco_gbp: 17.93,
    categoria: "Default",
    avaliacao: 3,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html",
  },
  {
    titulo: "The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics",
    preco_gbp: 22.6,
    categoria: "Default",
    avaliacao: 4,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html",
  },
  {
    titulo: "The Black Maria",
    preco_gbp: 52.15,
    categoria: "Poetry",
    avaliacao: 1,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/the-black-maria_991/index.html",
  },
  {
    titulo: "Starving Hearts (Triangular Trade Trilogy, #1)",
    preco_gbp: 13.99,
    categoria: "Romance",
    avaliacao: 2,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html",
  },
  {
    titulo: "Shakespeare's Sonnets",
    preco_gbp: 20.66,
    categoria: "Poetry",
    avaliacao: 4,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/shakespeares-sonnets_989/index.html",
  },
  {
    titulo: "Set Me Free",
    preco_gbp: 17.46,
    categoria: "Young Adult",
    avaliacao: 5,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/set-me-free_988/index.html",
  },
  {
    titulo: "Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)",
    preco_gbp: 52.29,
    categoria: "Sequential Art",
    avaliacao: 5,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html",
  },
  {
    titulo: "Rip it Up and Start Again",
    preco_gbp: 35.02,
    categoria: "Music",
    avaliacao: 5,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/rip-it-up-and-start-again_986/index.html",
  },
  {
    titulo: "Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991",
    preco_gbp: 57.25,
    categoria: "Music",
    avaliacao: 3,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html",
  },
  {
    titulo: "Olio",
    preco_gbp: 23.88,
    categoria: "Poetry",
    avaliacao: 1,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/olio_984/index.html",
  },
  {
    titulo: "Mesaerion: The Best Science Fiction Stories 1800-1849",
    preco_gbp: 37.59,
    categoria: "Classics",
    avaliacao: 1,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html",
  },
  {
    titulo: "Libertarianism for Beginners",
    preco_gbp: 51.33,
    categoria: "Politics",
    avaliacao: 2,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/libertarianism-for-beginners_982/index.html",
  },
  {
    titulo: "It's Only the Himalayas",
    preco_gbp: 45.17,
    categoria: "Travel",
    avaliacao: 2,
    disponibilidade: "In stock",
    url: "https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html",
  },
]
