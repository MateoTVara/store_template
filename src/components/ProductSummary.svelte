<script lang="ts">
  import type { ProductDTO } from "@customtypes/Product";

  interface Props { product: ProductDTO }
  const { product }: Props = $props();

  let buttonText = $state("Compartir");

  const appendToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      buttonText = "¡Copiado!";
      setTimeout(() => {
        buttonText = "Compartir";
      }, 2000);
    } catch (err) {
      console.error("Error al copiar al portapapeles: ", err);
    }
  };
</script>

<div class="flex-1">
  <h1 class="text-2xl font-bold mb-2">
    {product.name}
  </h1>

  <div
    class="w-full mt-4 flex justify-between items-center gap-4"
  >
    <p class="text-xl font-semibold">
      ${product.price.toFixed(2)}
    </p>
    <button
      onclick={appendToClipboard}
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors duration-300"
    >
      {buttonText}
    </button>
  </div>

  <p class="text-gray-700 mt-4">
    {product.description}
  </p>
</div>