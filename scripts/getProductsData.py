import requests, json, os, mimetypes, copy
import pyktok as pyk # type: ignore
import pandas as pd # type: ignore
from urllib.parse import ParseResult, urlparse
from dotenv import load_dotenv # type: ignore
from pathlib import Path
from io import StringIO
from typing import TypedDict, Sequence, Mapping, cast

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class Product(TypedDict): # Extend this with more fields as needed, but 'id' is required for diffing
    id: str
    nombre: str
    categoria: str
    precio: float
    descripcion: str
    img1: str

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------

PROJECT_ROOT: Path = Path(__file__).parent.parent                   # scripts/getData.py -> scripts/.. -> ROOT_DIR
OUTPUT_PATH: Path = PROJECT_ROOT / "src" / "data" / "products" / "rawData.json"          # source of truth (URLs as-is)
LOCALIZED_OUTPUT_PATH: Path = PROJECT_ROOT / "src" / "data" / "products" / "products.local.json"  # frontend-ready (local paths)
PUBLIC_MEDIA_DIR: Path = PROJECT_ROOT / "public" / "media" / "products"          # ROOT_DIR/public/media/products/{id}/{images,videos}/
ENV_PATH: Path = PROJECT_ROOT / ".env"                              # ROOT_DIR/.env
load_dotenv(ENV_PATH)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_IMAGE_EXTS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}

HTTP_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Referer": "https://www.yanbal.com/",
}

MEDIA_FIELDS: set[str] = {"img1"}

# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def get_required_env(name: str) -> str:
    """Return the value of a required environment variable, raising RuntimeError if absent."""
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(
            f"Environment variable '{name}' not found. "
            f"Make sure it is defined in {ENV_PATH} or in your runtime environment."
        )
    return value

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_sheet_data(spreadsheet_id: str, sheet_id: str) -> list[Product]:
    """Download a Google Sheet by spreadsheet ID and sheet GID and return it as a list of Products."""
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"
    res = requests.get(url)
    res.raise_for_status()
    csv_content = res.content.decode("utf-8")
    df = pd.read_csv(StringIO(csv_content))
    return cast(list[Product], json.loads(df.to_json(orient="records", force_ascii=False)))

def save_data(data: list[Product], file_path: Path) -> None:
    """Serialize the product list to a JSON file, creating parent directories as needed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated: {file_path.name}")

def load_local_data(file_path: Path) -> list[Product]:
    """Load the local JSON data file; create an empty one if it does not exist."""
    if not file_path.exists():
        print(f"File {file_path} not found. Creating a new empty one.")
        save_data([], file_path)
    with open(file_path, encoding="utf-8") as f:
        return cast(list[Product], json.load(f))

# ---------------------------------------------------------------------------
# Product diff helpers
# ---------------------------------------------------------------------------

def get_new_products(new_json: Sequence[Product], old_json: Sequence[Product]) -> list[Product]:
    """Return products present in new_json but absent in old_json (i.e. newly added)."""
    old_ids = {item["id"] for item in old_json}
    return [item for item in new_json if item["id"] not in old_ids]

def get_deleted_products(new_json: Sequence[Product], old_json: Sequence[Product]) -> list[Product]:
    """Return products present in old_json but absent in new_json (i.e. removed)."""
    new_ids = {item["id"] for item in new_json}
    return [item for item in old_json if item["id"] not in new_ids]

def get_modified_products(new_json: Sequence[Product], old_json: Sequence[Product]) -> list[Product]:
    """Return products whose field values differ between old_json and new_json (returns new versions)."""
    old_dict = {item["id"]: item for item in old_json}
    modified = []

    for item in new_json:
        product_id = item["id"]
        if product_id in old_dict:
            if item != old_dict[product_id]:
                print("DIFFERENCE IN:", product_id)
                for k in item:
                    if item.get(k) != old_dict[product_id].get(k):
                        print("  ", k, "->", item.get(k), "|", old_dict[product_id].get(k))
                modified.append(item)

    return modified

# ---------------------------------------------------------------------------
# File-system helpers
# ---------------------------------------------------------------------------

def make_product_media_dir(item: Product) -> tuple[Path, Path]:
    """Create and return the images and videos directories for the given product."""
    img_dir: Path = PUBLIC_MEDIA_DIR / item['id'] / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    video_dir: Path = PUBLIC_MEDIA_DIR / item['id'] / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    return (img_dir, video_dir)

def removeDownloadedMedia(item: Product) -> None:
    """Delete the entire media directory tree for the given product."""
    media_path: Path = PUBLIC_MEDIA_DIR / item['id']
    if media_path.exists() and media_path.is_dir():
        for child in media_path.rglob('*'):
            if child.is_file():
                child.unlink()
        for child in reversed(list(media_path.rglob('*'))):
            if child.is_dir():
                child.rmdir()
        media_path.rmdir()
    print(f"Deleted: {item['id']}")

# ---------------------------------------------------------------------------
# Media download helpers
# ---------------------------------------------------------------------------

def downloadImagesForProduct(item: Product, dest_dir: Path) -> None:
    """Download all product images into dest_dir, replacing any previously downloaded files."""
    # --- clear existing files in the directory ---
    for existing in dest_dir.iterdir():
        if existing.is_file():
            try:
                existing.unlink()
            except Exception as e:
                print(f"Could not delete {existing.name}: {e}")

    image_url_list = [
        url for url in [
            item.get("img1"),
        ] if url
    ]

    print(f"Downloading images for {item['id']}")

    session = requests.Session()
    session.headers.update(HTTP_HEADERS)

    # --- download ---
    for i, url in enumerate(image_url_list, start=1):
        try:
            parsed: ParseResult = urlparse(url)
            per_request_headers = {
                **session.headers,
                "Referer": f"{parsed.scheme}://{parsed.netloc}/",
            }

            response = session.get(url, headers=per_request_headers, timeout=15)
            response.raise_for_status()

            _, ext = os.path.splitext(os.path.basename(urlparse(url).path))
            ext = ext.lower()

            if ext not in VALID_IMAGE_EXTS:
                mime_type = response.headers.get("Content-Type", "").split(";")[0]
                ext = mimetypes.guess_extension(mime_type) or ".bin"

            dest_file = dest_dir / f"{i}{ext}"
            dest_file.write_bytes(response.content)

            print(f"\t✔ Image {i} downloaded -> {dest_file.name}")

        except Exception as e:
            print(f"\t✘ Error downloading image {i}: {e}")

    print(f"\tDone for {item['id']}\n")

def download_videos_for_product(item: Product, dest_dir: Path) -> None:
    """
    Download all TikTok videos for the product into dest_dir.

    pyktok always saves files to the current working directory, so the
    working directory is temporarily changed to dest_dir for the duration
    of the download and restored afterwards.
    """
    tiktok_urls = [
        url for url in [
            item.get("video1"),
        ]
        if url
    ]

    if not tiktok_urls:
        return

    for existing in dest_dir.glob("*.mp4"):
        existing.unlink()

    print(f"Downloading videos for {item['id']}")
    original_cwd = os.getcwd()
    os.chdir(dest_dir)
    try:
        pyk.save_tiktok_multi_urls(tiktok_urls, save_video=True, metadata_fn="data.csv", sleep=2)
    finally:
        os.chdir(original_cwd)
    print(f"Videos downloaded for {item['id']}")
# ---------------------------------------------------------------------------
# Image path helpers
# ---------------------------------------------------------------------------

def localize_image_fields(product: Product) -> None:
    """
    Replace remote image URLs in a product with local /media/{id}/images/{n}.{ext}
    paths, but only when the corresponding file has already been downloaded.
    Falls back to the original URL if the file is not found locally.
    """
    img_dir: Path = PUBLIC_MEDIA_DIR / product["id"] / "images"
    image_fields: list[str] = ["img1"]  # extend here if more image fields are added
    for i, field in enumerate(image_fields, start=1):
        if not product.get(field):  # type: ignore[arg-type]
            continue
        for ext in VALID_IMAGE_EXTS:
            local_file = img_dir / f"{i}{ext}"
            if local_file.exists():
                product[field] = f"/media/{product['id']}/images/{i}{ext}"  # type: ignore[literal-required]
                break

# ---------------------------------------------------------------------------
# Per-product processing
# ---------------------------------------------------------------------------

def process_new_product(product: Product) -> None:
    """Create media directories and download all images and videos for a new product."""
    dirs = make_product_media_dir(product)
    downloadImagesForProduct(product, dirs[0])
    # download_videos_for_product(product, dirs[1])

def process_deleted_product(product: Product) -> None:
    """Remove all downloaded media assets for a product that no longer exists."""
    removeDownloadedMedia(product)

def process_modified_product(product: Product, old_data_map: Mapping[str, Product]) -> None:
    old_product = old_data_map[product["id"]]

    modified_fields = {
        k for k in product
        if product.get(k) != old_product.get(k)
    }

    # Only re-download if media fields changed
    if not (modified_fields & MEDIA_FIELDS):
        print(f"Product {product['id']} modified but no media changes, skipping download.")
        return

    print(f"Media-related changes detected for {product['id']}, re-downloading.")

    removeDownloadedMedia(product)
    dirs = make_product_media_dir(product)
    downloadImagesForProduct(product, dirs[0])
    # download_videos_for_product(product, dirs[1])

# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def build_all_products(sheet_ids: dict[str, str]) -> None:
    """
    Orchestrate the full data sync pipeline for all product categories.

    Steps:
        1. Load the current local rawData.json as the previous state baseline.
        2. Fetch the latest data from each Google Sheet and assign the category.
        3. Diff each category against the local baseline to find new, deleted,
           and modified products.
        4. Download / remove media assets accordingly.
        5. Persist the merged product list (URLs unchanged) to rawData.json.
        6. Write a separate products.local.json with remote URLs replaced by
           local /media/… paths for frontend consumption.
    """

    try:
        spreadsheet_id = get_required_env("SPREADSHEET_ID")
        old_data = load_local_data(OUTPUT_PATH)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    all_products: list[Product] = []

    for category, sheet_id in sheet_ids.items():
        print(f"Fetching sheet: {category}")

        fetched_products = fetch_sheet_data(spreadsheet_id, sheet_id)

        for product in fetched_products:
            product["categoria"] = category

        old_category_data = [p for p in old_data if p.get("categoria") == category]

        print("Sources match:", old_category_data == fetched_products)

        new_products = get_new_products(fetched_products, old_category_data)
        deleted_products = get_deleted_products(fetched_products, old_category_data)
        modified_products = get_modified_products(fetched_products, old_category_data)

        print(f"\nNew products:      {len(new_products)}")
        print(f"Deleted products:  {len(deleted_products)}")
        print(f"Modified products: {len(modified_products)}\n")

        for new_product in new_products:
            try:
                process_new_product(new_product)
            except Exception as e:
                print(f"Error processing product {new_product.get('id', 'unknown ID')}: {e}")

        for deleted_product in deleted_products:
            try:
                process_deleted_product(deleted_product)
            except Exception as e:
                print(f"Error removing media for product {deleted_product.get('id', 'unknown ID')}: {e}")

        old_data_map = {p["id"]: p for p in old_category_data}
        for modified_product in modified_products:
            try:
                process_modified_product(modified_product, old_data_map)
            except Exception as e:
                print(f"Error processing product {modified_product.get('id', 'unknown ID')}: {e}")

        all_products.extend(fetched_products)

    # --- persist raw data exactly as fetched (source of truth for diffs) ---
    save_data(all_products, OUTPUT_PATH)

    # --- build frontend-ready copy with local /media/… paths ---
    localized_products = copy.deepcopy(all_products)
    for product in localized_products:
        localize_image_fields(product)
    save_data(localized_products, LOCALIZED_OUTPUT_PATH)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
    
if __name__ == "__main__":
    # Replace with the official business sheet IDs
    SHEETS_IDS = {
        "Men's Clothing": "39317466",
        "Jewelry": "154127679",
        "Electronics": "92713497",
        "Woman's Clothing": "1909018467"
    }

    build_all_products(SHEETS_IDS)
