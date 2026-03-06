<script lang="ts">
  import type { ProductDTO } from "@customtypes/Product";
  import softFade from "@styles/transitions/softFade";
  import { onDestroy, onMount } from "svelte";
  import { CarouselState } from "@lib/state/carouselState.svelte";

  interface Props { product: ProductDTO }

  const { product }: Props = $props();

  // svelte-ignore state_referenced_locally
  const carousel = new CarouselState(product.imgs.length, 3000);
  const currentImage = $derived(product.imgs[carousel.current]);

  onMount(() => carousel.start());
  onDestroy(() => carousel.stop());
</script>

<div class="flex flex-col-reverse lg:flex-row flex-1 gap-4">
  <!-- Thumbnail Navigation -->
  <div class="flex flex-row shrink-0 justify-center gap-2 mt-4 lg:mt-0 lg:flex-col">
    {#each product.imgs as img, index}
      <button
        type="button"
        class={`w-16 h-16 rounded border-2 overflow-hidden ${
          carousel.current === index ? "border-blue-500" : "border-transparent"
        }`}
        onclick={() => carousel.goTo(index)}
      >
        <img src={img} alt="" class="w-full h-full object-contain" />
      </button>
    {/each}
  </div>

  <!-- Main Image Display -->
  <div class="relative w-full grow lg:w-1/2 h-64 md:h-80 lg:h-96 overflow-hidden rounded-lg">
    {#key carousel.current}
      <img
        src={currentImage}
        alt={product.name}
        class="w-full h-full object-contain"
        in:softFade={{ duration: 500 }}
      />
    {/key}
    <button
      class="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 text-white text-center w-8 h-8 flex items-center justify-center rounded-full hover:bg-black/70 transition-opacity"
      onclick={carousel.prev}
    >
      &#9664;
    </button>

    <button
      class="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 text-white text-center w-8 h-8 flex items-center justify-center rounded-full hover:bg-black/70 transition-opacity"
      onclick={carousel.next}
    >
      &#9654;
    </button>
  </div>
</div>