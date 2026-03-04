import type { ProductRaw, ProductDTO } from "@customtypes/Product"
import productsLocalJson from "./products.local.json"

const mapProduct = (product: ProductRaw): ProductDTO => ({
  id: product.id,
  name: product.nombre,
  category: product.categoria,
  price: product.precio,
  description: product.descripcion,
  imgs: [product.img1],
});

export const getProducts = () => productsLocalJson.map(mapProduct)

export const getProductById = (id: string) => {
  const product = getProducts().find((product) => product.id === id)
  if (!product) {
    throw new Error(`Product with id ${id} not found`)
  }
  return product
}

export const getProductsByCategory = (category: string) => {
  const products = getProducts().filter((product) => product.category === category)
  if (products.length === 0) {
    throw new Error(`No products found for category ${category}`)
  }
  return products
}

export const getAllCategories = () => {
  const categories = new Set<string>()
  getProducts().forEach((product) => categories.add(product.category))
  return Array.from(categories)
}