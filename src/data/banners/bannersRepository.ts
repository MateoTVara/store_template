import type { BannerRaw, BannerDTO } from "@customtypes/Banner";
import bannersLocalJson from "./banners.local.json"

const mapBanner = (banner: BannerRaw): BannerDTO => ({
  id: banner.id,
  text: banner.texto,
  image: banner.imagen,
});

export const getBanners = () => bannersLocalJson.map(mapBanner)

export const getBannerById = (id: string) => {
  const banner = getBanners().find((banner) => banner.id === id)
  if (!banner) {
    throw new Error(`Banner with id ${id} not found`)
  }
  return banner
}