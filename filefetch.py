import os
import sys
import itertools
import mimetypes
from urllib.parse import urlparse, unquote
import requests


FETCH_DIR = "Fetched_Images"
CHUNK_SIZE = 8192
TIMEOUT = 15  # seconds


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def extract_name_from_url(url: str) -> str:
    """
    Extract a filename candidate from the URL path (without query/fragment).
    Returns an empty string if nothing meaningful is available.
    """
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    name = unquote(name)
    # Remove any trailing slashes that produce empty names
    if not name or name in ("/", ".", ".."):
        return ""
    return name


def ensure_extension(filename: str, content_type: str) -> str:
   
    base, ext = os.path.splitext(filename)
    if ext:
        return filename
    if content_type:
        # Normalize and guess extension
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip(), strict=False)
        if guessed:
            return base + guessed
    # Default fallback
    return filename if filename else "image"


def unique_path(directory: str, filename: str) -> str:
   
    base, ext = os.path.splitext(filename or "image")
    candidate = os.path.join(directory, (base or "image") + (ext or ""))
    if not os.path.exists(candidate):
        return candidate
    for i in itertools.count(1):
        cand = os.path.join(directory, f"{base}-{i}{ext}")
        if not os.path.exists(cand):
            return cand


def is_image_response(resp: requests.Response) -> bool:
    ctype = resp.headers.get("Content-Type", "")
    return ctype.lower().startswith("image/")


def download_image(url: str) -> str:
   
    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
            # Raises on 4xx/5xx
            resp.raise_for_status()

            if not is_image_response(resp):
                raise ValueError("The provided URL did not return an image (Content-Type is not image/*).")

            # Determine filename
            filename = extract_name_from_url(url)
            filename = ensure_extension(filename, resp.headers.get("Content-Type", ""))

            ensure_dir(FETCH_DIR)
            save_path = unique_path(FETCH_DIR, filename)

            # Stream to disk
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)

            return save_path

    except requests.exceptions.MissingSchema:
        raise ValueError("Invalid URL. Please include the scheme (e.g., https://example.com/image.jpg).")
    except requests.exceptions.InvalidURL:
        raise ValueError("That doesn’t look like a valid URL. Please check and try again.")
    except requests.exceptions.Timeout:
        raise ValueError("The request timed out. Your connection may be slow or the server is busy.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Could not connect to the server. Please check your internet connection or the URL.")
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        raise ValueError(f"HTTP error {status}. The resource may be unavailable or restricted.")
    except OSError:
        raise ValueError("Could not write the file to disk. Check permissions or available space.")
    except requests.exceptions.RequestException:
        raise ValueError("An unexpected network error occurred while fetching the image.")


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print('Enter an image URL (e.g., "https://example.com/picture.jpg"):')
        url = input("> ").strip()

    if not url:
        print("No URL provided. Exiting.")
        sys.exit(1)

    try:
        saved = download_image(url)
        print(f"Success! Image saved to: {saved}")
    except ValueError as e:
        print(f"Respectful notice: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
