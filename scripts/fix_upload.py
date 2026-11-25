#!/usr/bin/env python
content = open('web/upload_receipt.html').read()

# Remove the second button (the reject one)
old_btn = '<button class="primary-button" id="primary-button" disabled="">Reject photo</button>'
new_btn = ''

content = content.replace(old_btn, new_btn)

# Fix the first button id from primary-button to submit-button
content = content.replace('<button class="primary-button" id="primary-button" disabled="">Submit for review</button>', 
                          '<button class="primary-button" id="submit-button" disabled="">Submit for review</button>')

open('web/upload_receipt.html', 'w').write(content)
print('Done')