import re
content = open(r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\index.html').read()

# Read the file and replace using regex with proper line handling
# Pattern: find ctx.strokeStyle = '#36D6A0' and replace with '#00C805'
# We'll do this by working with the file content as a whole

# Replace all occurrences of the gradient color stops first
# Gradient stop 0 in drawMainChart / drawMainChartUI
content = content.replace(
    "gradient.addColorStop(0, 'rgba(54, 214, 160, 0.3)')",
    "gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)')"
)
# Gradient stop 1 in drawMainChart / drawMainChartUI
content = content.replace(
    "gradient.addColorStop(1, 'rgba(54, 214, 160, 0)')",
    "gradient.addColorStop(1, 'rgba(0, 200, 5, 0)')"
)

# Now replace the strokeStyle - do it twice with context
# First replacement: include the ctx.createLinearGradient line for context
old_text1 = "var gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);\n      gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)');\n      gradient.addColorStop(1, 'rgba(0, 200, 5, 0)');\n      ctx.fillStyle = gradient;\n      ctx.strokeStyle = '#36D6A0';"
new_text1 = "var gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);\n      gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)');\n      gradient.addColorStop(1, 'rgba(0, 200, 5, 0)');\n      ctx.fillStyle = gradient;\n      ctx.strokeStyle = '#00C805';"
content = content.replace(old_text1, new_text1, 1)

# Second replacement for drawMainChartUI
old_text2 = "var gradient = ctx.createLinearGradient(0, 0, 0, mainChartCanvas.height);\n      gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)');\n      gradient.addColorStop(1, 'rgba(0, 200, 5, 0)');\n      ctx.fillStyle = gradient;\n      ctx.strokeStyle = '#36D6A0';"
new_text2 = "var gradient = ctx.createLinearGradient(0, 0, 0, mainChartCanvas.height);\n      gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)');\n      gradient.addColorStop(1, 'rgba(0, 200, 5, 0)');\n      ctx.fillStyle = gradient;\n      ctx.strokeStyle = '#00C805';"
content = content.replace(old_text2, new_text2)

open(r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\index.html', 'w').write(content)
print('Gradient and stroke done')