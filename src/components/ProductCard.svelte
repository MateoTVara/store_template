<script lang="ts">
  import type { ProductDTO } from "@customtypes/Product";

  interface Props { product: ProductDTO }

  const { product }: Props = $props();
</script>

<div
  class="w-64 shrink-0"
>
  <a
    href={`/products/${product.id}`}
    class="flex flex-col gap-2 p-4 border rounded-lg hover:shadow-lg transition-shadow duration-300"
  >
    <img 
      src={product.imgs[0]} alt={product.name}
      class="w-full h-48 object-contain rounded-md"
    />
    <div
      class="flex flex-col gap-1 text-text"
    >
      <p class="font-semibold text-center truncate">{product.name}</p>
      <p class="font-bold text-center">S/. {product.price.toFixed(2)}</p>              
    </div>
  </a>

</div>