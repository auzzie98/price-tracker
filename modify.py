import re

files = [
    'c:/Users/auzzi/OneDrive/Desktop/price-tracker/web/index.html',
    'c:/Users/auzzi/OneDrive/Desktop/price-tracker/web/category.html',
    'c:/Users/auzzi/OneDrive/Desktop/price-tracker/web/product.html',
    'c:/Users/auzzi/OneDrive/Desktop/price-tracker/web/methodology.html'
]

header_bar = '''<div class="header-bar">
  <h1>Price Tracker</h1>
  <nav>
    <a href="/" class="active">Home</a>
    <a href="/category/gpus">GPUs</a>
    <a href="/category/cpus">CPUs</a>
    <a href="/category/ram">RAM</a>
    <a href="/methodology">Methodology</a>
  </nav>
</div>'''

page_title = '<h1 class="page-title">Market Indexes</h1>'
page_subtitle = '<p class="page-subtitle">Tracks GPU, CPU, and RAM prices over time, like a stock chart.</p>'

for filepath in files:
    print(f'Processing {filepath}...')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find body tag position
    body_pos = content.find('<body>')
    if body_pos == -1:
        print(f'  No <body> tag in {filepath}')
        continue
    
    # Insert header bar right after <body>
    new_content = content[:body_pos+6] + '\n' + header_bar + '\n' + content[body_pos+6:]
    
    # Add page title and subtitle after the first h1 (for index page) or at appropriate position
    # For category, product, methodology pages, we need to add the title too
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'  Updated {filepath}')