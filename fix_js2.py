import re
content = open(r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\index.html').read()

# Replace gradient color stops in drawMainChart function (before ctx.strokeStyle '#36D6A0')
# This is in the old drawChart function (not drawMainChartUI)
content = content.replace(
    "gradient.addColorStop(0, 'rgba(54, 214, 160, 0.3)');\n      ctx.strokeStyle = '#36D6A0';",
    "gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)');\n      ctx.strokeStyle = '#00C805';"
)

# Replace gradient color stops in drawMainChartUI function
content = content.replace(
    "gradient.addColorStop(1, 'rgba(54, 214, 160, 0)');\n      ctx.strokeStyle = '#36D6A0';",
    "gradient.addColorStop(1, 'rgba(0, 200, 5, 0)');\n      ctx.strokeStyle = '#00C805';"
)

# Replace the drawChart up/down strokeStyle
content = content.replace(
    "ctx.strokeStyle = up ? '#36D6A0' : '#F07878';",
    "ctx.strokeStyle = up ? '#00C805' : '#FF5000';"
)

open(r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\index.html', 'w').write(content)
print('JS fixes done')