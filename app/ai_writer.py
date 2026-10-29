import re

def slugify(text):
    text = text.strip()
    # Replace any punctuation and symbols, keeping alphanumeric (Latin + Arabic)
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text).strip('-')
    return text[:60] or "new-article"

def generate_seo_description(text, max_len=145):
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) <= max_len:
        return clean
    # Cut at last whole word
    cut = clean[:max_len]
    last_space = cut.rfind(' ')
    if last_space > 80:
        cut = cut[:last_space]
    return cut.strip() + "..."

def markdown_to_html(md_text):
    """
    Converts standard Markdown into clean Blogger-compatible HTML.
    Supports H2, H3, bold, lists, callouts, blockquotes, code blocks.
    """
    lines = md_text.splitlines()
    html_lines = []
    in_list = False
    in_code = False
    
    for line in lines:
        stripped = line.strip()
        
        # Code block
        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                html_lines.append("<pre><code>")
            else:
                in_code = False
                html_lines.append("</code></pre>")
            continue
            
        if in_code:
            html_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            continue
            
        # Empty line
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
            
        # Headings
        if stripped.startswith("### "):
            if in_list: html_lines.append("</ul>"); in_list = False
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
            continue
        elif stripped.startswith("## "):
            if in_list: html_lines.append("</ul>"); in_list = False
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
            continue
        elif stripped.startswith("# "):
            if in_list: html_lines.append("</ul>"); in_list = False
            html_lines.append(f"<h2>{stripped[2:]}</h2>")
            continue
            
        # Bullet list
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item_text = stripped[2:]
            # Bold & italic replacements
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item_text)
            item_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', item_text)
            html_lines.append(f"<li>{item_text}</li>")
            continue
            
        # Blockquote / Tip callout
        if stripped.startswith("> "):
            if in_list: html_lines.append("</ul>"); in_list = False
            content = stripped[2:]
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            html_lines.append(f"<blockquote class='tip-box'>{content}</blockquote>")
            continue
            
        # Regular paragraph
        if in_list: html_lines.append("</ul>"); in_list = False
        p_text = stripped
        p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p_text)
        p_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', p_text)
        p_text = re.sub(r'`(.*?)`', r'<code>\1</code>', p_text)
        html_lines.append(f"<p>{p_text}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_code:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)
