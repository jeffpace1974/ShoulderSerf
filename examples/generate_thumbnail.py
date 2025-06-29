"""Example script for generating thumbnails using the Sserf system."""

import sys
import os
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.thumbnail.generator import ThumbnailGenerator


def main():
    """Generate example thumbnails."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize thumbnail generator
    generator = ThumbnailGenerator()
    
    # Example 1: Basic thumbnail
    logger.info("Generating basic thumbnail...")
    
    output1 = generator.generate_thumbnail(
        title="Lewis Discusses University Life",
        year="1924",
        output_filename="example_1924.png"
    )
    
    if output1:
        logger.info(f"Generated: {output1}")
    
    # Example 2: Longer title that will wrap
    logger.info("Generating thumbnail with long title...")
    
    output2 = generator.generate_thumbnail(
        title="The Profound Impact of Medieval Literature on Modern Thought",
        year="1935",
        output_filename="example_1935.png"
    )
    
    if output2:
        logger.info(f"Generated: {output2}")
    
    # Example 3: Content-based generation
    logger.info("Generating content-based thumbnail...")
    
    sample_lewis_text = """
    The real problem is not why some pious, humble, believing people suffer, 
    but why some do not. Our Lord Himself, it will be remembered, explained 
    the salvation of those who are fortunate in this world only by referring 
    to the special difficulty of their task.
    """
    
    output3 = generator.generate_from_content(sample_lewis_text)
    
    if output3:
        logger.info(f"Generated: {output3}")
    
    # Example 4: Different years
    examples = [
        ("Early Oxford Years", "1920"),
        ("The Great War Reflections", "1918"),
        ("Inklings Meetings Begin", "1933"),
        ("The Lion, The Witch and The Wardrobe", "1950"),
        ("Mere Christianity Published", "1952"),
        ("Cambridge Professorship", "1954")
    ]
    
    logger.info("Generating series of example thumbnails...")
    
    for title, year in examples:
        output = generator.generate_thumbnail(
            title=title,
            year=year,
            output_filename=f"lewis_{year}_{title.replace(' ', '_').lower()}.png"
        )
        
        if output:
            logger.info(f"Generated: {os.path.basename(output)}")
    
    logger.info("Thumbnail generation complete!")
    logger.info(f"Check the '{generator.output_dir}' directory for generated thumbnails.")


if __name__ == "__main__":
    main()