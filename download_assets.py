import re
import os
import requests
import urllib.parse

# Configuration
SOURCE_FILE = 'assets/Animated-GIFs-Collection.md'
MEDIA_DIR = 'assets/media'
BASE_URL_PREFIX = 'https://github.com/Abhishek-Maheshwari-778/all_in_1_github_profile_creator_elements/blob/main/'

def download_file(url, folder):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Extract filename from URL
        parsed_url = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename:
             return None

        # Clean filename - remove query parameters and weird chars
        filename = urllib.parse.unquote(filename)
        filename = re.sub(r'[^\w\-\.]', '_', filename)

        filepath = os.path.join(folder, filename)
        
        # Check if file already exists to avoid re-downloading (or handle duplicates)
        if os.path.exists(filepath):
             base, ext = os.path.splitext(filename)
             i = 1
             while os.path.exists(os.path.join(folder, f"{base}_{i}{ext}")):
                 i += 1
             filename = f"{base}_{i}{ext}"
             filepath = os.path.join(folder, filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filename
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def main():
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find images: ![][url] or <img src="url">
    # We will handle <img src="..."> primarily as the file uses HTML mainly
    
    # Strategy: Replace line by line to keep context or just regex replace?
    # Since we want to categorize, we might need to parse headers.
    
    lines = content.split('\n')
    new_lines = []
    
    current_category = "General"
    
    # Regex for markdown image ![alt](url)
    md_img_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
    # Regex for HTML image <img src="url" ...>
    html_img_pattern = re.compile(r'<img\s+[^>]*src=["\'](.*?)["\'][^>]*>')
    
    processed_urls = {}

    for line in lines:
        # Check for category header
        header_match = re.match(r'^##\s+(.*?)(\s+\[.*\]\(.*\))?$', line)
        if header_match:
            # Clean category name
            raw_cat = header_match.group(1).strip()
            # Remove emojis and brackets
            current_category = re.sub(r'[^\w\s-]', '', raw_cat).strip().replace(' ', '_')
            if not current_category:
                current_category = "General"
            
            # Create category directory
            cat_dir = os.path.join(MEDIA_DIR, current_category)
            if not os.path.exists(cat_dir):
                os.makedirs(cat_dir)
        
        # Prepare category folder
        cat_dir = os.path.join(MEDIA_DIR, current_category)

        # Process HTML images
        def replace_html_src(match):
            url = match.group(1)
            if url.startswith('http'):
                if url in processed_urls:
                    local_path = processed_urls[url]
                else:
                    filename = download_file(url, cat_dir)
                    if filename:
                        # Construct relative path for README
                        # assets/Animated-GIFs-Collection.md is in assets/
                        # media is in assets/media
                        # so relative path is ./media/{category}/{filename}
                        local_path = f"./media/{current_category}/{filename}"
                        processed_urls[url] = local_path
                        print(f"Downloaded: {url} -> {local_path}")
                    else:
                        local_path = url # Keep original if failed
                        
                return match.group(0).replace(url, local_path)
            return match.group(0)

        line = html_img_pattern.sub(replace_html_src, line)

        # Process Markdown images
        def replace_md_src(match):
            alt = match.group(1)
            url = match.group(2)
            if url.startswith('http'):
                if url in processed_urls:
                    local_path = processed_urls[url]
                else:
                    filename = download_file(url, cat_dir)
                    if filename:
                        local_path = f"./media/{current_category}/{filename}"
                        processed_urls[url] = local_path
                        print(f"Downloaded: {url} -> {local_path}")
                    else:
                        local_path = url
                return f"![{alt}]({local_path})"
            return match.group(0)

        line = md_img_pattern.sub(replace_md_src, line)
        
        new_lines.append(line)

    # Clean up branding (simple removal of top div if it matches known branding)
    # Be careful not to delete useful content. 
    # The file starts with a div containing branding.
    
    cleaned_lines = []
    skip_div = False
    
    # branding_removed = False
    # for line in new_lines:
    #     if not branding_removed and '<div align="center">' in line and 'Made with' in new_lines[new_lines.index(line)+2]:
    #         # Identify start of branding block
    #         skip_div = True
    #     
    #     if skip_div:
    #         if '</div>' in line:
    #             skip_div = False
    #             branding_removed = True
    #         continue
    #         
    #     cleaned_lines.append(line)
    
    # Manual cleanup based on file knowledge
    # The file starts with branding lines 1-10 regarding "Made with ... by Anmol"
    # We will verify this range.
    
    with open(SOURCE_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("Done! Assets downloaded and links updated.")

if __name__ == "__main__":
    main()
