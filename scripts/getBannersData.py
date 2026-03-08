import requests
import json
import os
import mimetypes
from pathlib import Path
from io import StringIO
from urllib.parse import urlparse
from typing import TypedDict, Sequence, cast

import pandas as pd  # type: ignore
from dotenv import load_dotenv  # type: ignore


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class Banner(TypedDict):
    id: str
    texto: str
    imagen: str


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent

RAW_OUTPUT = PROJECT_ROOT / "src/data/banners/rawData.json"
LOCAL_OUTPUT = PROJECT_ROOT / "src/data/banners/banners.local.json"

PUBLIC_MEDIA_DIR = PROJECT_ROOT / "public/media/banners"

ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


# ---------------------------------------------------------------------------
# Fetch sheet
# ---------------------------------------------------------------------------

def fetch_sheet_data(spreadsheet_id: str, sheet_id: str) -> list[Banner]:

    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"

    res = requests.get(url)
    res.raise_for_status()

    csv_content = res.content.decode("utf-8")
    df = pd.read_csv(StringIO(csv_content))

    return cast(list[Banner], json.loads(df.to_json(orient="records", force_ascii=False)))


# ---------------------------------------------------------------------------
# Local file helpers
# ---------------------------------------------------------------------------

def save_json(data: list[Banner], path: Path) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: Path) -> list[Banner]:

    if not path.exists():
        save_json([], path)

    with open(path, encoding="utf-8") as f:
        return cast(list[Banner], json.load(f))


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------

def get_new(new: Sequence[Banner], old: Sequence[Banner]) -> list[Banner]:
    old_ids = {x["id"] for x in old}
    return [x for x in new if x["id"] not in old_ids]


def get_deleted(new: Sequence[Banner], old: Sequence[Banner]) -> list[Banner]:
    new_ids = {x["id"] for x in new}
    return [x for x in old if x["id"] not in new_ids]


def get_modified(new: Sequence[Banner], old: Sequence[Banner]) -> list[Banner]:

    old_map = {x["id"]: x for x in old}
    modified = []

    for item in new:
        if item["id"] in old_map and item != old_map[item["id"]]:
            modified.append(item)

    return modified


# ---------------------------------------------------------------------------
# Media
# ---------------------------------------------------------------------------

def banner_dir(banner: Banner) -> Path:
    path = PUBLIC_MEDIA_DIR / banner["id"]
    path.mkdir(parents=True, exist_ok=True)
    return path


def delete_banner_media(banner: Banner):

    path = PUBLIC_MEDIA_DIR / banner["id"]

    if path.exists():
        for f in path.rglob("*"):
            if f.is_file():
                f.unlink()

        for d in reversed(list(path.rglob("*"))):
            if d.is_dir():
                d.rmdir()

        path.rmdir()

    print(f"Deleted media: {banner['id']}")


def download_banner_image(banner: Banner):

    url = banner["imagen"]
    dest_dir = banner_dir(banner)

    for f in dest_dir.glob("*"):
        f.unlink()

    try:

        res = requests.get(url, timeout=15)
        res.raise_for_status()

        _, ext = os.path.splitext(urlparse(url).path)

        if ext.lower() not in VALID_IMAGE_EXTS:
            mime = res.headers.get("Content-Type", "").split(";")[0]
            ext = mimetypes.guess_extension(mime) or ".bin"

        file = dest_dir / f"image{ext}"

        file.write_bytes(res.content)

        print(f"Downloaded {banner['id']} -> {file.name}")

    except Exception as e:
        print(f"Error downloading {banner['id']}: {e}")


# ---------------------------------------------------------------------------
# Localization
# ---------------------------------------------------------------------------

def localize_images(banner: Banner):

    media_dir = PUBLIC_MEDIA_DIR / banner["id"]

    for ext in VALID_IMAGE_EXTS:
        file = media_dir / f"image{ext}"

        if file.exists():
            banner["imagen"] = f"/media/banners/{banner['id']}/image{ext}"
            return


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def build_banners():

    spreadsheet_id = get_required_env("SPREADSHEET_ID")
    sheet_id = "565783107" # full image
    # sheet_id = "55303911" # icon like image

    new_data = fetch_sheet_data(spreadsheet_id, sheet_id)
    old_data = load_json(RAW_OUTPUT)

    new_items = get_new(new_data, old_data)
    deleted_items = get_deleted(new_data, old_data)
    modified_items = get_modified(new_data, old_data)

    print("New:", len(new_items))
    print("Deleted:", len(deleted_items))
    print("Modified:", len(modified_items))

    for banner in new_items:
        download_banner_image(banner)

    for banner in deleted_items:
        delete_banner_media(banner)

    for banner in modified_items:
        delete_banner_media(banner)
        download_banner_image(banner)

    save_json(new_data, RAW_OUTPUT)

    localized = json.loads(json.dumps(new_data))

    for banner in localized:
        localize_images(banner)

    save_json(localized, LOCAL_OUTPUT)


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build_banners()