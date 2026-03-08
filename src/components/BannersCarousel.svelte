<script lang="ts">
  import type { BannerDTO } from "@customtypes/Banner";
  import softFade from "@styles/transitions/softFade";
  import { getBanners } from "@data/banners/bannersRepository";
  import { onDestroy, onMount } from "svelte";
  import { CarouselState } from "@lib/state/carouselState.svelte";

  const banners: BannerDTO[] = getBanners();
  const carousel = new CarouselState(banners.length, 4000);

  const currentBanner = $derived<BannerDTO>(banners[carousel.current]);

  onMount(() => carousel.start());
  onDestroy(() => carousel.stop());
</script>

<div class="relative w-full overflow-hidden select-none">
  <!-- Slides -->
  {#key carousel.current}
    <div
      class="relative h-56 md:h-72 lg:h-96"
      class:bg-amber-800={currentBanner.id === "BANNER-0001"}
      class:bg-white={currentBanner.id === "BANNER-0002"}
      class:bg-blue-300={currentBanner.id === "BANNER-0003"}
      in:softFade={{ duration: 500 }}
    >
      <!-- cover version for full images -->
      <div
        class="absolute inset-0 bg-cover bg-center"
        style="background-image: url({currentBanner.image})"
      >
        <div class="w-full h-full flex items-start justify-center pt-5 bg-black/40">
          <h2 class="text-white text-xl font-bold drop-shadow">{currentBanner.text}</h2>
        </div>
      </div>

      <!-- positioned version for icon like images -->
      <!-- <div class="w-full h-full flex items-center justify-start pl-15 bg-black/40">
        <h2 class="text-white text-sm lg:text-xl font-bold drop-shadow">{currentBanner.text}</h2>
      </div>
      <img src={currentBanner.image} alt={currentBanner.text}
        class="absolute bottom-5 right-5 w-16 h-16 lg:w-40 lg:h-40 object-cover"
      > -->
    </div>
  {/key}

  <!-- Prev button -->
  <button
    onclick={carousel.prev}
    aria-label="Previous banner"
    class="absolute left-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full w-9 h-9 flex items-center justify-center transition-colors"
  >
    &#8249;
  </button>

  <!-- Next button -->
  <button
    onclick={carousel.next}
    aria-label="Next banner"
    class="absolute right-2 top-1/2 -translate-y-1/2 bg-black/40 hover:bg-black/60 text-white rounded-full w-9 h-9 flex items-center justify-center transition-colors"
  >
    &#8250;
  </button>

  <!-- Dot indicators -->
  <div class="absolute bottom-2 left-1/2 -translate-x-1/2 px-2 flex gap-2">
    {#each banners as _, i}
      <button
        onclick={() => carousel.goTo(i)}
        aria-label="Go to banner {i + 1}"
        class="w-2 h-2 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-white"
        class:bg-white={i === carousel.current}
        class:bg-gray-400={i !== carousel.current}
      ></button>
    {/each}
  </div>
</div>

