import re
from bs4 import BeautifulSoup

# Sample from EnhanceFox post
raw_sample = """
<div class="separator" dir="ltr" style="text-align: left;">
<blockquote>&nbsp;<h1 style="display: contents; font-size: 20px;">Download free 100% Enhance Fox</h1>&nbsp;</blockquote>
<br />
<ul id="btnd">
<li><a href="https://install.appcenter.ms/users/hyayn5/apps/hayan/distribution_groups/apk/releases/146" target="_blank">Free Download</a></li>
</ul>
</div>
"""

soup = BeautifulSoup(raw_sample, 'html.parser')
a = soup.find('a')
print("Initial Anchor:", a)

# Let's see the parent tree
curr = a.parent
steps = 0
targetWrapper = a
extractedTitle = ''
while curr and steps < 5:
    tag = curr.name.upper()
    currText = curr.get_text().strip()
    currId = curr.get('id', '').lower()
    currClass = ' '.join(curr.get('class', [])).lower()
    currStyle = curr.get('style', '').lower()

    if tag == 'LI':
        targetWrapper = curr.parent if curr.parent and curr.parent.name in ['ul', 'ol'] else curr
    elif tag in ['UL', 'OL']:
        if 'btn' in currId or 'btn' in currClass or len(curr.find_all('a')) <= 2:
            targetWrapper = curr
    elif tag in ['DIV', 'BLOCKQUOTE', 'SECTION', 'P']:
        anchors = curr.find_all('a')
        if len(anchors) <= 2 and len(currText) < 350:
            h = curr.find(['h1', 'h2', 'h3', 'h4', 'blockquote', 'strong', 'b'])
            if h and not extractedTitle:
                extractedTitle = h.get_text().strip()
            targetWrapper = curr
    curr = curr.parent
    steps += 1

print("\nTarget Wrapper identified to replace:", targetWrapper.name, targetWrapper.attrs)
print("Extracted Title:", extractedTitle)

card_html = f'<div class="pro-download-card"><h3>{extractedTitle}</h3><a href="{a["href"]}">{a.get_text().strip()}</a></div>'
new_node = BeautifulSoup(card_html, 'html.parser')
targetWrapper.replace_with(new_node)

print("\n--- FINAL RESULT ---")
print(str(soup).strip())
