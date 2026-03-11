import os
import time
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
from urllib.parse import urljoin

base_url = 'https://autokeys.kiwi'
shop_url = f'{base_url}/shop/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

img_dir = os.path.join(os.getcwd(), 'images', 'shop')
os.makedirs(img_dir, exist_ok=True)

all_products = []

def download_image(img_url, img_name):
    file_path = os.path.join(img_dir, img_name)
    if os.path.exists(file_path):
        return True
    try:
        r = requests.get(img_url, headers=headers, stream=True, timeout=10)
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")
    return False

def scrape_product_page(product_url):
    print(f"  Scraping product: {product_url}")
    try:
        r = requests.get(product_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Title
        title_elem = soup.find('h1', class_='product_title')
        title = title_elem.text.strip() if title_elem else ''
        
        # Price
        summary = soup.find('div', class_='summary')
        price = ''
        if summary:
            # First try ins if it's on sale
            ins = summary.find('ins')
            if ins:
                p_elem = ins.find(class_='woocommerce-Price-amount')
                if p_elem: price = p_elem.text.strip()
            else:
                p_elem = summary.find(class_='woocommerce-Price-amount')
                if p_elem: price = p_elem.text.strip()
                
        # Description
        desc = ""
        desc_div = soup.find('div', id='tab-description') or soup.find('div', class_='woocommerce-product-details__short-description')
        if desc_div:
            # Get internal HTML but clean up any weird whitespace
            html = desc_div.decode_contents()
            desc = ' '.join(html.split())
            
        # Category
        cat_elem = soup.find('span', class_='posted_in')
        category = ''
        if cat_elem and cat_elem.find('a'):
            category = cat_elem.find('a').text.strip()
            
        # Image
        img = soup.find('div', class_='woocommerce-product-gallery__image')
        img_url = ''
        if img and img.find('a'):
            img_url = img.find('a').get('href')
        elif img and img.find('img'):
            img_url = img.find('img').get('data-src') or img.find('img').get('src')
            
        local_img_path = ''
        if img_url:
            filename = os.path.basename(urllib.parse.urlparse(img_url).path)
            if not filename:
                filename = title.replace(' ', '_').lower()[:20] + '.jpg'
            success = download_image(img_url, filename)
            if success:
                local_img_path = f"images/shop/{filename}"
                
        return {
            'title': title,
            'price': price,
            'description': desc,
            'category': category,
            'image': local_img_path
        }
    except Exception as e:
        print(f"  Error scraping {product_url}: {e}")
        return None

def main():
    page = 1
    while True:
        url = shop_url if page == 1 else f"{shop_url}page/{page}/"
        print(f"Scraping shop page {page}...")
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"Stopping at page {page}, status {r.status_code}")
                break
                
            soup = BeautifulSoup(r.text, 'html.parser')
            products_ul = soup.find('ul', class_='products')
            if not products_ul:
                print("No products list found. Ending pagination.")
                break
                
            products_li = products_ul.find_all('li', class_='product')
            if not products_li:
                print("No product items found. Ending pagination.")
                break
                
            for li in products_li:
                a = li.find('a', class_='woocommerce-LoopProduct-link')
                if a and a.get('href'):
                    prod_data = scrape_product_page(a.get('href'))
                    if prod_data and prod_data['title']:
                        all_products.append(prod_data)
                    time.sleep(1) # Be nice to the server
                    
            # Check for next page
            next_page = soup.find('a', class_='next page-numbers')
            if not next_page:
                print("No next page found. Ending pagination.")
                break
            page += 1
        except Exception as e:
            print(f"Error scraping shop page {page}: {e}")
            break

    print(f"Total products scraped: {len(all_products)}")
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
