import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Hayan\Documents\blogger-studio-pro\static\js\dashboard.js', encoding='utf-8') as f:
    text = f.read()

idx = 187246
id_pos = text.rfind('"id":', 0, idx)
print('ID snippet:', text[id_pos:id_pos+100])

next_id = text.find('"id":', idx)
post_slice = text[id_pos:next_id] if next_id != -1 else text[id_pos:id_pos+15000]

print("\n--- ALL ANCHORS IN POST ---")
for m in re.finditer(r'<a\s+[^>]*>.*?</a>', post_slice, re.DOTALL | re.IGNORECASE):
    print("Found Anchor:", m.group(0)[:300])

print("\n--- SEARCH FOR DOWNLOAD OR BUTTON OR LINK PATTERNS ---")
for m in re.finditer(r'(?:تحميل|تنزيل|download|btn|button|drive\.google|mediafire|mega\.nz|apk)', post_slice, re.IGNORECASE):
    st = max(0, m.start() - 100)
    en = min(len(post_slice), m.end() + 200)
    print("Match keyword:", post_slice[st:en])
    print("-" * 50)
