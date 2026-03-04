<script lang="ts">
  import type { BannerDTO } from "@customtypes/Banner";
  import softFade from "@styles/transitions/softFade";
  import { getBanners } from "@data/banners/bannersRepository";
  import { onDestroy, onMount } from "svelte";

  const banners: BannerDTO[] = getBanners();

  let current = $state(0);
  const currentBanner = $derived<BannerDTO>(banners[current]);

  let interval: ReturnType<typeof setInterval>;

  const INTERVAL_MS = 4000;

  function prev() {
    current = (current - 1 + banners.length) % banners.length;
    resetInterval();
  }

  function next() {
    current = (current + 1) % banners.length;
    resetInterval();
  }

  function goTo(index: number) {
    current = index;
    resetInterval();
  }

  function resetInterval() {
    clearInterval(interval);
    interval = setInterval(next, INTERVAL_MS);
  }

  onMount(() => {
    interval = setInterval(next, INTERVAL_MS);
  });

  onDestroy(() => {
    clearInterval(interval);
  });
</script>

<div class="relative w-full overflow-hidden select-none">
  <!-- Slides -->
  {#key current}
    <div class="relative h-56 md:h-72 lg:h-96">
      <div
        class="absolute inset-0 bg-cover bg-center"
        in:softFade={{ duration: 500 }}
        style="background-image: url({currentBanner.image})"
      >
        <div class="w-full h-full flex items-start justify-center pt-5 bg-black/40">
          <h2 class="text-white text-xl font-bold drop-shadow">{currentBanner.text}</h2>
        </div>
      </div>
    </div>
  {/key}

  <!-- Prev button -->
  <button
    onclick={prev}
    aria-label="Previous banner"
    class="absolute left-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full w-9 h-9 flex items-center justify-center transition-colors"
  >
    &#8249;
  </button>

  <!-- Next button -->
  <button
    onclick={next}
    aria-label="Next banner"
    class="absolute right-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full w-9 h-9 flex items-center justify-center transition-colors"
  >
    &#8250;
  </button>

  <!-- Dot indicators -->
  <div class="absolute bottom-2 left-1/2 -translate-x-1/2 px-2 flex gap-2">
    {#each banners as _, i}
      <button
        onclick={() => goTo(i)}
        aria-label="Go to banner {i + 1}"
        class="w-2 h-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-white"
        class:bg-white={i === current}
        class:bg-gray-400={i !== current}
      ></button>
    {/each}
  </div>
</div>

