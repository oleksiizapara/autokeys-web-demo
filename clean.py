import json
import re

with open('products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

for p in products:
    desc = p.get('description', '')
    
    # 1. Remove the title heading if it matches the front
    desc = re.sub(r'^\*\*(?:🔑*\s*)(?:[^*]+)\*\*\n+', '', desc)
    
    # 2. Fix the condition phrase
    desc = desc.replace('Second-hand, virginised to new state', 'Refurbished to virgin (new) state, ready to pair')
    desc = desc.replace('Used & Unlocked (ready for programming)', 'Refurbished to virgin (new) state, ready to pair')

    # Fix variations of "and ready for programming" if it's left over
    desc = desc.replace('Refurbished to virgin (new) state, ready to pair and ready for programming', 'Refurbished to virgin (new) state, ready to pair')
    
    # 3. Truncate everything from Important or Wholesale onwards
    parts = re.split(r'\n+(?:⚠️|💼|-{3,}|\*\*Important:|\*\*Important Key Advisory)', desc)
    desc = parts[0].strip()
    
    p['description'] = desc

with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)
    
print('Descriptions cleaned!')
