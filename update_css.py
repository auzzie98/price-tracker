import os

css_path = r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\static\css\style.css'

# Read existing CSS
with open(css_path, 'r') as f:
    content = f.read()

# Replace the body section
content = content.replace(
    'body { background: #101713; color: #F4F8F5;',
    'body { background: #000000; color: #FFFFFF;'
)

# Replace header bar
content = content.replace(
    '.header-bar { background: #202E26; border: 1px solid #29372F;',
    '.header-bar { background: #121212; border: 1px solid #2D2D2D;'
)
content = content.replace(
    '.header-bar h1 { color: #F4F8F5;',
    '.header-bar h1 { color: #FFFFFF;'
)
content = content.replace(
    '.header-bar nav a { color: #9BAAA1;',
    '.header-bar nav a { color: #9CA3AF;'
)
content = content.replace(
    '.header-bar nav a.active { color: #36D6A0;',
    '.header-bar nav a.active { color: #00C805;'
)
content = content.replace(
    'margin: -1rem -1rem 2rem -1rem;',
    'margin: 0 0 2rem 0;'
)

# Replace page title
content = content.replace(
    '.page-title { color: #F4F8F5; font-size: 1.5rem;',
    '.page-title { color: #FFFFFF; font-size: 1.5rem;'
)
content = content.replace(
    '.page-subtitle { color: #9BAAA1; font-size: 0.9rem;',
    '.page-subtitle { color: #9CA3AF; font-size: 0.9rem;'
)

# Replace section headers
content = content.replace(
    '.section-header { color: #F4F8F5; font-size: 1.2rem;',
    '.section-header { color: #FFFFFF; font-size: 1.2rem;'
)

# Replace headline
content = content.replace(
    '.headline { padding: 1rem; border-bottom: 1px solid #29372F; margin: -1rem -1rem 2rem -1rem;',
    '.headline { padding: 1rem; border-bottom: 1px solid #2D2D2D; margin: 0 0 2rem 0;'
)

# Replace indices pills
content = content.replace(
    '.indices-pills { padding: 1rem; background: #18231D; border: 1px solid #29372F;',
    '.indices-pills { padding: 1rem; background: #1E1E1E; border: 1px solid #2D2D2D;'
)
content = content.replace(
    '.pill { background: #202E26; border: 1px solid #29372F; color: #9BAAA1;',
    '.pill { background: #1E1E1E; border: 1px solid #2D2D2D; color: #9CA3AF;'
)
content = content.replace(
    '.pill.active { background: #36D6A0; color: #101713;',
    '.pill.active { background: #00C805; color: #000000;'
)

# Replace main chart
content = content.replace(
    '#main-chart { background: #101713; border: 1px solid #29372F; border-radius: 4px; width: 100%; max-width: 100%; height: 400px; margin: 1rem 0;',
    '#main-chart { background: #000000; border: 1px solid #2D2D2D; border-radius: 4px; width: 100%; max-width: 100%; height: 350px; margin: 1rem 0;'
)

# Replace time toggles
content = content.replace(
    '.time-toggles { padding: 0.5rem 1rem; background: #18231D; border: 1px solid #29372F;',
    '.time-toggles { padding: 0.5rem 1rem; background: #121212; border: 1px solid #2D2D2D;'
)
content = content.replace(
    '.time-toggles .toggle { background: #202E26; border: 1px solid #29372F; color: #9BAAA1;',
    '.time-toggles .toggle { background: #121212; border: 1px solid #2D2D2D; color: #9CA3AF;'
)
content = content.replace(
    '.time-toggles .toggle.active { background: #36D6A0; color: #101713;',
    '.time-toggles .toggle.active { background: #00C805; color: #000000;'
)

# Replace individual models section
content = content.replace(
    '.individual-models { padding: 1rem; background: #18231D; border: 1px solid #29372F; border-radius: 4px; margin: 1rem -1rem 1rem -1rem;',
    '.individual-models { padding: 1rem; background: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 4px; margin: 1rem 0;'
)
content = content.replace(
    '.model-label { color: #9BAAA1; font-size: 0.75rem; margin: 0.5rem 0 0.5rem 0;',
    '.model-label { color: #9CA3AF; font-size: 0.75rem; margin: 0.5rem 0 0.5rem 0;'
)
content = content.replace(
    '.model-name { color: #F4F8F5; font-size: 0.85rem;',
    '.model-name { color: #FFFFFF; font-size: 0.85rem;'
)
content = content.replace(
    '.model-price { color: #9BAAA1; font-size: 0.85rem;',
    '.model-price { color: #9CA3AF; font-size: 0.85rem;'
)
content = content.replace(
    '.model-change { color: #36D6A0; font-size: 0.85rem; font-weight: bold;',
    '.model-change { color: #00C805; font-size: 0.85rem; font-weight: bold;'
)
content = content.replace(
    '.model-sparkline canvas { width: 120px; height: 30px; background: #202E26; border-radius: 3px; flex-shrink: 0;',
    '.model-sparkline canvas { width: 120px; height: 30px; background: #121212; border-radius: 3px; flex-shrink: 0;'
)

# Replace tiles section
content = content.replace(
    '.tiles { margin: 1rem -1rem 1rem -1rem;',
    '.tiles { margin: 1rem 0;'
)
content = content.replace(
    '.tile { background: #18231D; border: 1px solid #29372F; border-radius: 4px; padding: 1rem; margin-bottom: 1rem; width: 100%; color: #F4F8F5;',
    '.tile { background: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 4px; padding: 1rem; margin-bottom: 1rem; width: 100%; color: #FFFFFF;'
)
content = content.replace(
    '.tile-value { font-size: 1.2rem; font-weight: bold; color: #F4F8F5;',
    '.tile-value { font-size: 1.2rem; font-weight: bold; color: #FFFFFF;'
)
content = content.replace(
    '.tile-percent { font-size: 0.8rem; color: #9BAAA1;',
    '.tile-percent { font-size: 0.8rem; color: #9CA3AF;'
)

# Check for any remaining forbidden colors and replace them
forbidden = ['#101713', '#18231D', '#202E26', '#36D6A0', '#55BFA5']
for color in forbidden:
    if color in content:
        print(f'WARNING: Forbidden color {color} still in CSS!')
    else:
        print(f'OK: Forbidden color {color} removed')

# Write updated CSS
with open(css_path, 'w') as f:
    f.write(content)

print('CSS updated successfully to dark Robinhood theme')