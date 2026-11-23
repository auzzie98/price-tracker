content = open('c:\\Users\\auzzi\\OneDrive\\Desktop\\price-tracker\\web\\index.html').read()
# Remove the second header bar (lines 20-29)
old = '<div class="header-bar">\n  <h1>Price Tracker</h1>\n  <nav>\n    <a href="/" class="active">Home</a>\n    <a href="/category/gpus">GPUs</a>\n    <a href="/category/cpus">CPUs</a>\n    <a href="/category/ram">RAM</a>\n    <a href="/methodology">Methodology</a>\n  </nav>\n</div>'
content = content.replace(old, '')
open('c:\\Users\\auzzi\\OneDrive\\Desktop\\price-tracker\\web\\index.html', 'w').write(content)
print('Done')