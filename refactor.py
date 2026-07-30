import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Pattern 1: <hX style='margin-bottom:1rem;'>...</h2>
content = re.sub(r'st\.markdown\([f]?["\']<h[1-6] [^>]*>([^<]+)</h[1-6]>["\'], unsafe_allow_html=True\)', r'section_heading("\1")', content)

# Pattern 2: <div class='cp-card'>...</div>
content = re.sub(r'st\.markdown\([f]?["\']<div class=[\'"]cp-card[\'"][^>]*>["\'], unsafe_allow_html=True\)', r'card_open()', content)
content = re.sub(r'st\.markdown\([f]?["\']</div>["\'], unsafe_allow_html=True\)', r'card_close()', content)

# Pattern 3: <hr>
content = re.sub(r'st\.markdown\([f]?["\']<hr>["\'], unsafe_allow_html=True\)', r'divider()', content)

# Pattern 4: <span class='cp-badge cp-badge-good'>...</span>
# Replace inline badges joining logic if possible, or just keep them since they are often dynamic
# Let's clean up the "What would you like to do next?" h3 -> section_heading
content = re.sub(r'st\.markdown\([f]?["\']<h3 style=\'text-align:center;margin-bottom:1rem;\'>([^<]+)</h3>["\'], unsafe_allow_html=True\)', r'section_heading("\1")', content)

# Pattern 5: <div class='cp-compare-grid'>
content = re.sub(r'st\.markdown\([f]?["\']<div class=[\'"]cp-compare-grid[\'"]>["\'], unsafe_allow_html=True\)', r'card_open(extra_classes="cp-compare-grid")', content)

# Pattern 6: <div style='text-align:center;'>
content = re.sub(r'st\.markdown\([f]?["\']<div style=\'text-align:center;\'>["\'], unsafe_allow_html=True\)', r'card_open(extra_classes="text-center")', content)

# Pattern 7: <p style='color:#6B7280...
content = re.sub(r'st\.markdown\([f]?["\']<p style=[\'"]color:#6B7280[^>]*>([^<]+)</p>["\'], unsafe_allow_html=True\)', r'st.caption("\1")', content)
content = re.sub(r'st\.markdown\([f]?["\']<p style=[\'"]color:#9CA3AF[^>]*>([^<]+)</p>["\'], unsafe_allow_html=True\)', r'st.caption("\1")', content)

# Pattern 8: <h4>...</h4>
content = re.sub(r'st\.markdown\([f]?["\']<h4 [^>]*>([^<]+)</h4>["\'], unsafe_allow_html=True\)', r'section_title("\1")', content)
content = re.sub(r'st\.markdown\([f]?["\']<h3 [^>]*>([^<]+)</h3>["\'], unsafe_allow_html=True\)', r'section_title("\1")', content)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
