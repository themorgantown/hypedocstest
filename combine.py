#!/usr/bin/env python3
"""
Combine all markdown files in the /md/ directory into a single markdown file.
Files are processed in alphabetical order.
"""

import os
import glob
import re
from pathlib import Path

def process_youtube_videos(content):
    """Convert embedded YouTube videos to markdown links."""
    # Pattern to match the YouTube div structure
    youtube_pattern = r'<div class="js-lazyYT" data-youtube-id="([^"]+)"[^>]*>Loading\.\.\.</div>'
    
    def replace_youtube(match):
        video_id = match.group(1)
        return f"[View Tutorial Video](https://www.youtube.com/watch?v={video_id})"
    
    return re.sub(youtube_pattern, replace_youtube, content)

def process_images(content):
    """Modify images to use data-src-retina as the primary src."""
    # Pattern to match img tags with data-src-retina
    img_pattern = r'<img\s+([^>]*?)data-src-retina="([^"]+)"([^>]*?)>'
    
    def replace_img(match):
        before_attrs = match.group(1)
        retina_src = match.group(2)
        after_attrs = match.group(3)
        
        # Combine all attributes to search through
        all_attrs = before_attrs + after_attrs
        
        # Extract class, width, height, and alt attributes if they exist
        class_match = re.search(r'class="([^"]*)"', all_attrs)
        width_match = re.search(r'width="(\d+)"', all_attrs)
        height_match = re.search(r'height="(\d+)"', all_attrs)
        alt_match = re.search(r'alt="([^"]*)"', all_attrs)
        
        # Build the new img tag
        new_attrs = []
        
        # Add class if it exists
        if class_match:
            new_attrs.append(f'class="{class_match.group(1)}"')
        
        # Add the retina src as the primary src
        new_attrs.append(f'src="{retina_src}"')
        
        # Add width and height if they exist
        if width_match:
            new_attrs.append(f'width="{width_match.group(1)}"')
        if height_match:
            new_attrs.append(f'height="{height_match.group(1)}"')
        
        # Add alt attribute
        if alt_match:
            new_attrs.append(f'alt="{alt_match.group(1)}"')
        else:
            new_attrs.append('alt=""')
        
        return f'<img {" ".join(new_attrs)}/>'
    
    return re.sub(img_pattern, replace_img, content)

def process_data_src_images(content):
    """Convert images with data-src (but not data-src-retina) to use data-src as primary src."""
    # Pattern to match img tags with data-src but NOT data-src-retina
    # This uses negative lookahead to exclude images that have data-src-retina
    img_pattern = r'<img\s+([^>]*?)data-src="([^"]+)"(?![^>]*data-src-retina)([^>]*?)>'
    
    def replace_img(match):
        before_attrs = match.group(1)
        data_src = match.group(2)
        after_attrs = match.group(3)
        
        # Combine all attributes to search through
        all_attrs = before_attrs + after_attrs
        
        # Extract class, width, height, and alt attributes if they exist
        class_match = re.search(r'class="([^"]*)"', all_attrs)
        width_match = re.search(r'width="(\d+)"', all_attrs)
        height_match = re.search(r'height="(\d+)"', all_attrs)
        alt_match = re.search(r'alt="([^"]*)"', all_attrs)
        
        # Build the new img tag
        new_attrs = []
        
        # Add class if it exists
        if class_match:
            new_attrs.append(f'class="{class_match.group(1)}"')
        
        # Add the data-src as the primary src
        new_attrs.append(f'src="{data_src}"')
        
        # Add width and height if they exist
        if width_match:
            new_attrs.append(f'width="{width_match.group(1)}"')
        if height_match:
            new_attrs.append(f'height="{height_match.group(1)}"')
        
        # Add alt attribute
        if alt_match:
            new_attrs.append(f'alt="{alt_match.group(1)}"')
        else:
            new_attrs.append('alt=""')
        
        return f'<img {" ".join(new_attrs)}/>'
    
    return re.sub(img_pattern, replace_img, content)

def process_document_links(content):
    """Convert document/ links to full URLs."""
    # Pattern to match href or src attributes that start with "documents/" (not in the middle of a path)
    # ✅ Match: href="documents/something.html"
    #✅ Match: src="documents/image.png"
    #❌ NOT match: href="https://example.com/documents/something.html"
    #❌ NOT match: src="images/documents/file.png"
    doc_pattern = r'((?:href|src)=")documents/'
    
    def replace_doc_link(match):
        attr_start = match.group(1)  # Either 'href="' or 'src="'
        return f'{attr_start}https://tumult.com/hype/documentation/v4/documents/'
    
    return re.sub(doc_pattern, replace_doc_link, content)

def process_image_paths(content):
    """Convert local image/video paths to GitHub raw URLs."""
    # Pattern to match src/href/data-src-2x attributes that start with "images/"
    img_path_pattern = r'((?:src|href|data-src-2x)=")images/'
    
    def replace_img_path(match):
        attr_start = match.group(1)  # 'src="', 'href="', or 'data-src-2x="'
        return f'{attr_start}https://raw.githubusercontent.com/tumult/hype-documentation/refs/heads/main/images/'
    
    return re.sub(img_path_pattern, replace_img_path, content)

def combine_markdown_files():
    """Combine all .md files in the current directory into a single markdown file."""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    md_dir = script_dir / "md"
    
    # Find all .md files in the md directory (excluding the output file)
    md_files = []
    for file in md_dir.glob("*.md"):
        if file.name != "README.md":  # Don't include the output file
            md_files.append(file)
    
    # Sort files alphabetically
    md_files.sort(key=lambda x: x.name)
    
    if not md_files:
        print("No markdown files found in the directory.")
        return
    
    # Output file path
    output_file = script_dir / "README.md"
    
    print(f"Combining {len(md_files)} markdown files...")
    print("Files to be combined (in order):")
    for file in md_files:
        print(f"  - {file.name}")
    
    # Combine files
    with open(output_file, 'w', encoding='utf-8') as outfile:
        
        for i, md_file in enumerate(md_files):
            print(f"Processing: {md_file.name}")
            
            # Add file separator
            # outfile.write(f"<!-- File: {md_file.name} -->\n\n")
            
            try:
                with open(md_file, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    
                    # Process YouTube videos, images, and document links
                    content = process_youtube_videos(content)
                    content = process_images(content)
                    content = process_data_src_images(content)
                    content = process_document_links(content)
                    content = process_image_paths(content)
                    
                    # Write the content
                    outfile.write(content)
                    
                    # Add spacing between files (but not after the last file)
                    if i < len(md_files) - 1:
                        outfile.write("\n\n---\n\n")
                        
            except Exception as e:
                print(f"Error reading {md_file.name}: {e}")
                outfile.write(f"*Error reading file {md_file.name}: {e}*\n\n")
    
    print(f"\nSuccessfully combined files into: {output_file}")
    print(f"Total files processed: {len(md_files)}")

if __name__ == "__main__":
    combine_markdown_files()