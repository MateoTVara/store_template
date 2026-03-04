<script lang="ts">
  import { getAllCategories, getProductsByCategory } from "@data/products/productsRepository";
  import ProductCard from "./ProductCard.svelte";

  const categories = getAllCategories();
</script>

<div class="p-4">
  <h1 class="text-2xl font-bold text-text mb-4">Catálogo de Productos</h1>
  <div>
    {#each categories as category}
      <h2 class="text-xl font-semibold text-text mb-2">{category}</h2>
      <div class="flex flex-row py-4 overflow-x-auto gap-4 mb-6">
        {#each getProductsByCategory(category) as product}
          <ProductCard {product} />
        {/each}
      </div>
    {/each}
  </div>
</div>