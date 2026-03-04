export interface ProductRaw {
  id: string
  nombre: string
  categoria: string
  precio: number
  descripcion: string
  img1: string
}

export interface ProductDTO {
  id: string
  name: string
  category: string
  price: number
  description: string
  imgs: string[]
}