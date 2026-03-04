<script lang="ts">
  import { fly } from "svelte/transition";
  import { onMount } from "svelte";
  import { getTheme, toggleTheme } from "@lib/state/themeState.svelte";
  import { getProductsLike } from "@data/products/productsRepository";

  const title = "Fake Store";



  let searchQuery = $state("");
  let searchResults = $derived(getProductsLike(searchQuery));



  let hidden = $state(false);
  let lastY = 0;

  onMount(() => {
    const onScroll = () => {
      const currentY = window.scrollY;
      hidden = currentY > lastY && currentY > 60;
      lastY = currentY;
      searchQuery = "";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  });
</script>

<header
  class="fixed top-0 left-0 right-0 z-50 flex flex-row items-center justify-between gap-1 p-4 transition-all duration-300
  bg-gray-100 dark:bg-gray-800
  {hidden ? '-translate-y-full shadow-none' : 'translate-y-0 shadow-md'}"
>
  <!-- Title -->
  <h1 class="text-sm lg:text-2xl font-bold dark:text-white">
    <a href="/">
      {title}
    </a>
  </h1>

  <!-- Search -->
  <div class="relative lg:w-full max-w-md">
    <input
      type="text"
      placeholder="Buscar productos..."
      bind:value={searchQuery}
      class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-full"
    >
    {#if searchQuery}
      <div class="absolute mt-1 w-full bg-white dark:bg-gray-700 rounded-md shadow-lg max-h-60 overflow-y-auto">
        {#if searchResults.length > 0}
          {#each searchResults as product}
            <a href={`/products/${product.id}`} class="flex flex-row items-center gap-4 px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-600">
              <img src={product.imgs[0]} alt={product.name} class="w-8 h-8 lg:w-16 lg:h-16 shrink-0 object-contain object-center">
              <span class="text-sm truncate text-gray-700 dark:text-gray-300">{product.name}</span>
            </a>
          {/each}
        {:else}
          <div class="px-4 py-2 text-gray-500">No se encontraron productos</div>
        {/if}
      </div>
    {/if}
  </div> 

  <!-- Theme toggle -->
  <button
    class="
    relative w-16 h-9 rounded-full 
    transition-all duration-300 ease-in-out
    flex items-center px-1
  bg-gray-300 dark:bg-gray-700"
    onclick={toggleTheme}
  >
    {#if getTheme() === "light"}
      <span
        in:fly={{ x: 10, duration: 300 }}
        class="flex items-center justify-center w-7 h-7
        absolute left-2 text-sm text-center rounded-full transition-opacity duration-300 z-20
        bg-gray-200"
      >
        ☀️
      </span>
    {:else}
      <span
        in:fly={{ x: -10, duration: 300 }}
        class="flex items-center justify-center w-7 h-7
        absolute right-2 text-sm text-center rounded-full transition-opacity duration-300 z-20
        bg-blue-950"
      >
        🌙
      </span>
    {/if}
  </button>
</header>