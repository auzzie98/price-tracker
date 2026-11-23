css_path = r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\static\css\style.css'

with open(css_path, 'r') as f:
    content = f.read()

# Make sure we have the exact Robinhood dark theme colors
# Replace #6B7280 with #9CA3AF where needed (secondary text)
# Replace #E5E7EB with #2D2D2D where needed (borders)

# Replace secondary text color #6B7280 with #9CA3AF
content = content.replace('#6B7280', '#9CA3AF')

# Replace border #E5E7EB with #2D2D2D where it's for dark theme borders
# But we need to be careful - #E5E7EB might be used differently
# Let's check what we have

# The key colors we need:
# Background: #000000 (already there)
# Card background: #1E1E1E (need to ensure this is set)
# Primary text: #FFFFFF (already there)
# Secondary text: #9CA3AF (just replaced #6B7280 -> #9CA3AF)
# Border: #2D2D2D (need to ensure this is set)
# Primary green up: #00C805 (already there)
# Red down: #FF5000 (need to check)

print('Colors after replacement check:')
import re
colors = re.findall(r'#[0-9A-Fa-f]{6}', content)
unique = list(set(colors))
for c in unique:
    print(f'  {c}')

with open(css_path, 'w') as f:
    f.write(content)

print('CSS updated with #9CA3AF replacing #6B7280')