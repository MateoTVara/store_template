<script lang="ts">
  import { fly } from "svelte/transition";
  import { getTheme, toggleTheme } from "@lib/state/themeState.svelte";

  const title = "Fake Store";
</script>

<header
  class="flex flex-row items-center justify-between p-4 transition-colors duration-300
  bg-gray-100 dark:bg-gray-800
  "
  >
  <h1 class="text-md lg:text-2xl font-bold dark:text-white">
    <a href="/">
      {title}
    </a>
  </h1>
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