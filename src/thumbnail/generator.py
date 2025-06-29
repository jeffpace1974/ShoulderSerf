"""Thumbnail generation system matching existing design template."""

import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional, Tuple
import os
from ..config.settings import settings


logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """Generates thumbnails matching the C.S. Lewis series template."""
    
    def __init__(self):
        self.width = settings.thumbnail.width
        self.height = settings.thumbnail.height
        self.output_dir = settings.thumbnail.output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize fonts (will need system fonts or custom font files)
        self.title_font = self._load_font(settings.thumbnail.title_font_size)
        self.year_font = self._load_font(settings.thumbnail.year_font_size)
        self.header_font = self._load_font(48)  # For "C.S. Lewis" header
    
    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load font with fallback to default."""
        try:
            # Try to load a nice font (you may need to adjust paths)
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Arial.ttf",
                "arial.ttf"
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            
            # Fallback to default font
            return ImageFont.load_default()
            
        except Exception as e:
            logger.warning(f"Failed to load custom font: {e}")
            return ImageFont.load_default()
    
    def _draw_text_with_outline(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                               text: str, font: ImageFont.FreeTypeFont, 
                               fill_color: str, outline_color: str, outline_width: int = 3):
        """Draw text with outline for better visibility."""
        x, y = position
        
        # Draw outline
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text(position, text, font=font, fill=fill_color)
    
    def generate_thumbnail(self, title: str, year: str, 
                          background_image: Optional[str] = None,
                          output_filename: Optional[str] = None) -> str:
        """Generate thumbnail with specified title and year."""
        
        # Create base image
        if background_image and os.path.exists(background_image):
            # Use custom background
            img = Image.open(background_image)
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        else:
            # Use template background (nature scene from your thumbnail)
            template_path = "assets/thumbnail_template.png"
            if os.path.exists(template_path):
                img = Image.open(template_path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            else:
                # Fallback: create gradient background
                img = self._create_gradient_background()
        
        draw = ImageDraw.Draw(img)
        
        # Draw "C.S. Lewis" header (top, white cursive-style)
        header_text = "C.S. Lewis"
        header_bbox = draw.textbbox((0, 0), header_text, font=self.header_font)
        header_width = header_bbox[2] - header_bbox[0]
        header_x = (self.width - header_width) // 2
        header_y = 30
        
        self._draw_text_with_outline(
            draw, (header_x, header_y), header_text, 
            self.header_font, "#FFFFFF", "#000000", 2
        )
        
        # Draw main title (center, large green text)
        # Split long titles into multiple lines
        title_lines = self._wrap_text(title, self.title_font, self.width - 100)
        
        total_title_height = len(title_lines) * (settings.thumbnail.title_font_size + 10)
        start_y = (self.height - total_title_height) // 2
        
        for i, line in enumerate(title_lines):
            line_bbox = draw.textbbox((0, 0), line, font=self.title_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (self.width - line_width) // 2
            line_y = start_y + i * (settings.thumbnail.title_font_size + 10)
            
            self._draw_text_with_outline(
                draw, (line_x, line_y), line,
                self.title_font, settings.thumbnail.title_color, 
                settings.thumbnail.outline_color, 3
            )
        
        # Draw year (bottom right, white)
        year_bbox = draw.textbbox((0, 0), year, font=self.year_font)
        year_width = year_bbox[2] - year_bbox[0]
        year_x = self.width - year_width - 50
        year_y = self.height - settings.thumbnail.year_font_size - 30
        
        self._draw_text_with_outline(
            draw, (year_x, year_y), year,
            self.year_font, settings.thumbnail.year_color,
            settings.thumbnail.outline_color, 2
        )
        
        # Add avatar overlays if available
        self._add_avatars(img)
        
        # Save thumbnail
        if not output_filename:
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_filename = f"{safe_title}_{year}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path, "PNG", quality=95)
        
        logger.info(f"Generated thumbnail: {output_path}")
        return output_path
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Single word too long, add anyway
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _create_gradient_background(self) -> Image.Image:
        """Create a gradient background as fallback."""
        img = Image.new('RGB', (self.width, self.height), '#2E5C3E')
        
        # Add simple gradient effect
        for y in range(self.height):
            alpha = int(255 * (y / self.height) * 0.3)
            for x in range(self.width):
                pixel = img.getpixel((x, y))
                new_pixel = tuple(min(255, c + alpha // 3) for c in pixel)
                img.putpixel((x, y), new_pixel)
        
        return img
    
    def _add_avatars(self, img: Image.Image):
        """Add avatar overlays to match template design."""
        # This would add Robot Lady and host avatars in the corners
        # For now, just placeholder - you'll need to provide avatar images
        
        avatar_size = (150, 150)
        
        # Left avatar (Robot Lady) position
        left_x, left_y = 50, self.height - avatar_size[1] - 50
        
        # Right avatar (Host) position  
        right_x, right_y = self.width - avatar_size[0] - 50, self.height - avatar_size[1] - 50
        
        # Add colored circles as placeholders for avatars
        draw = ImageDraw.Draw(img)
        
        # Robot Lady placeholder (blue circle)
        draw.ellipse([left_x, left_y, left_x + avatar_size[0], left_y + avatar_size[1]], 
                    outline="#00BFFF", width=5)
        
        # Host placeholder (purple circle)
        draw.ellipse([right_x, right_y, right_x + avatar_size[0], right_y + avatar_size[1]], 
                    outline="#9932CC", width=5)
    
    def generate_from_content(self, lewis_text: str, context: str = "", year: str = None) -> str:
        """Generate thumbnail based on Lewis text content with AI-powered analysis."""
        from .content_analyzer import ContentAnalyzer
        
        # Initialize content analyzer
        analyzer = ContentAnalyzer()
        
        # Analyze content to extract title and year
        analysis = analyzer.analyze_content(lewis_text, year)
        
        logger.info(f"Content analysis: {analysis}")
        
        return self.generate_thumbnail(
            title=analysis["title"],
            year=analysis["year"]
        )
    
    def generate_from_image(self, image_path: str, year: str = None) -> str:
        """Generate thumbnail from book page image using OCR."""
        from .content_analyzer import ContentAnalyzer
        
        # Initialize content analyzer
        analyzer = ContentAnalyzer()
        
        # Extract text from image
        extracted_text = analyzer.extract_text_from_image(image_path)
        
        if not extracted_text:
            logger.error("No text extracted from image")
            return None
        
        # Analyze content to generate title
        analysis = analyzer.analyze_content(extracted_text, year)
        
        logger.info(f"Image analysis: {analysis}")
        
        return self.generate_thumbnail(
            title=analysis["title"],
            year=analysis["year"]
        )