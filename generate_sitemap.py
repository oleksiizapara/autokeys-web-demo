import json
import re
from datetime import datetime

# Domain of the website
DOMAIN = "https://autokeys.kiwi"

def generate_slug(title):
    # Same logic as in javascript:
    # lowercased, replace non-alphanumeric with hyphens, and strip trailing/leading hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return slug

def main():
    sitemap_content = []
    
    # Standard XML Sitemap Header
    sitemap_content.append('<?xml version="1.0" encoding="UTF-8"?>')
    sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Add static pages
    static_pages = [
        {"url": f"{DOMAIN}/", "priority": "1.0", "changefreq": "weekly"},
        {"url": f"{DOMAIN}/index.html", "priority": "0.9", "changefreq": "weekly"},
        {"url": f"{DOMAIN}/shop.html", "priority": "0.9", "changefreq": "daily"}
    ]
    
    for page in static_pages:
        sitemap_content.append('  <url>')
        sitemap_content.append(f'    <loc>{page["url"]}</loc>')
        sitemap_content.append(f'    <lastmod>{current_date}</lastmod>')
        sitemap_content.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        sitemap_content.append(f'    <priority>{page["priority"]}</priority>')
        sitemap_content.append('  </url>')
    
    # Load products configuration
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
            
        # Add dynamic product pages
        for product in products:
            if 'title' in product:
                slug = generate_slug(product['title'])
                product_url = f"{DOMAIN}/shop.html?product={slug}"
                
                sitemap_content.append('  <url>')
                sitemap_content.append(f'    <loc>{product_url}</loc>')
                sitemap_content.append(f'    <lastmod>{current_date}</lastmod>')
                sitemap_content.append('    <changefreq>weekly</changefreq>')
                sitemap_content.append('    <priority>0.8</priority>')
                sitemap_content.append('  </url>')
                
    except FileNotFoundError:
        print("products.json not found! Generating sitemap only for static pages.")
    except json.JSONDecodeError:
        print("Error decoding products.json formatting.")

    # Footer
    sitemap_content.append('</urlset>')
    
    # Write to sitemap.xml
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sitemap_content))
        
    print(f"Successfully generated sitemap.xml with {len(static_pages) + (len(products) if 'products' in locals() else 0)} URLs.")

if __name__ == "__main__":
    main()
