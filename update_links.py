import os

def update_links():
    root_dir = '.'
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in dirpath:
            continue
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace links
                # We renamed 'assets' folder to 'Assets_Collection'
                # So any path containing 'assets/' or './assets/' or '../../assets/' needs update
                # but we must be careful not to double replace if I run it twice, though Assets_Collection != assets so it's fine.
                
                # Simple string replacement should work for relative paths
                new_content = content.replace('assets/media', 'Assets_Collection/media')
                new_content = content.replace('./assets/', './Assets_Collection/')
                new_content = content.replace('../../assets/', '../../Assets_Collection/')
                # Catch cases like "assets/Animated..."
                new_content = new_content.replace('assets/Animated-GIFs-Collection.md', 'Assets_Collection/Animated-GIFs-Collection.md')
                
                # Just generic replace 'assets/' -> 'Assets_Collection/' might be safer but could hit text.
                # Given the grep results, usage is mostly in src="" or href=""
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filepath}")

if __name__ == "__main__":
    update_links()
