content = open(r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\index.html').read()
# Replace chart stroke colors - up and down
content = content.replace("ctx.strokeStyle = up ? '#36D6A0' : '#F07878'", "ctx.strokeStyle = up ? '#00C805' : '#FF5000'")
# Replace gradient fill in drawChart
content = content.replace("gradient.addColorStop(0, 'rgba(54, 214, 160, 0.3)'", "gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)'")
content = content.replace("gradient.addColorStop(1, 'rgba(54, 214, 160, 0)'", "gradient.addColorStop(1, 'rgba(0, 200, 5, 0)'")
# Replace gradient fill in drawMainChartUI
content = content.replace("gradient.addColorStop(0, 'rgba(54, 214, 160, 0.3)'", "gradient.addColorStop(0, 'rgba(0, 200, 5, 0.1)'")
content = content.replace("gradient.addColorStop(1, 'rgba(54, 214, 160, 0)'", "gradient.addColorStop(1, 'rgba(0, 200, 5, 0)'")
# Replace standalone ctx.strokeStyle '#36D6A0' with '#00C805' (only the one in drawChart, not the one in drawMainChartUI context)
# Actually, let me be more careful - the ctx.strokeStyle appears in both drawChart and drawMainChartUI functions
# Let me replace all instances of '#36D6A0' with '#00C805' in the JS context
content = content.replace("'#36D6A0'", "'#00C805'")
content = content.replace('"#36D6A0"', '"#00C805"')
open(r'c:\Users\auzzi\OneDrive\Desktop\price-tracker\web\index.html', 'w').write(content)
print('JS updated')