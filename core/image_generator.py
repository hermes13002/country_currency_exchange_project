import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils import timezone
from .models import Country, RefreshLog

IMG_WIDTH = 800
IMG_HEIGHT = 400
BG_COLOR = (28, 32, 39) # dark background
TITLE_COLOR = (255, 255, 255) # white
TEXT_COLOR = (200, 200, 200) # light grey
HIGHLIGHT_COLOR = (110, 180, 255) # light blue
PAD = 30 # padding from edges

def get_font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except IOError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            print(f"Warning: Could not find Arial or DejaVuSans. Using default font.")
            return ImageFont.load_default()


def generate_summary_image():
    """
    Generates a summary image with refresh stats and saves it to disk.
    
    The image will contain:
    1. Title
    2. Last Refresh Timestamp
    3. Total Countries
    4. Top 5 Countries by Estimated GDP
    """
    
    try:
        log = RefreshLog.objects.first()
        if not log:
            print("Image Generator: No RefreshLog found. Skipping image generation.")
            return

        top_countries = Country.objects.filter(
            estimated_gdp__isnull=False
        ).order_by('-estimated_gdp')[:5]

        total_countries_str = f"Total Countries Cached: {log.total_countries}"
        
        local_time = timezone.localtime(log.last_refreshed_at)
        timestamp_str = f"Last Refresh: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"

    except Exception as e:
        print(f"Error fetching data for image generation: {e}")
        return

    
    img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), color=BG_COLOR)
    d = ImageDraw.Draw(img)
    
    
    try:
        font_title = get_font(32)
        font_header = get_font(24)
        font_main = get_font(18)
    except Exception as e:
        print(f"Critical error loading fonts: {e}")
        return

    
    current_y = PAD

    
    d.text((PAD, current_y), "Country Data Refresh Summary", fill=TITLE_COLOR, font=font_title)
    current_y += 60 

    
    d.text((PAD, current_y), timestamp_str, fill=TEXT_COLOR, font=font_main)
    current_y += 35

    
    d.text((PAD, current_y), total_countries_str, fill=TEXT_COLOR, font=font_main)
    current_y += 50

    
    d.text((PAD, current_y), "Top 5 Countries by Estimated GDP:", fill=HIGHLIGHT_COLOR, font=font_header)
    current_y += 40

    
    if not top_countries:
        d.text((PAD + 10, current_y), "No countries with calculated GDP found.", fill=TEXT_COLOR, font=font_main)
    else:
        for i, country in enumerate(top_countries):
            
            gdp_billions = (country.estimated_gdp or 0) / Decimal('1000000000')
            gdp_str = f"${gdp_billions:,.2f} B"
            
            text = f"{i+1}. {country.name} ({gdp_str})"
            d.text((PAD + 10, current_y), text, fill=TEXT_COLOR, font=font_main)
            current_y += 30 

    
    save_path = settings.SUMMARY_IMAGE_PATH
    try:
        img.save(save_path)
        print(f"Summary image successfully saved to: {save_path}")
    except Exception as e:
        print(f"Error saving summary image: {e}")

# required for Decimal calculations
from decimal import Decimal