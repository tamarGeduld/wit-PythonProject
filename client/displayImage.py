from PIL import Image
import requests
from io import BytesIO

def display_image_from_url(url, title=None):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        if title:
            print(f"\n{title}")
        img.show()
    except Exception as e:
        print(f"Failed to display image from {url}: {e}")