import streamlit as st
import re
from PyPDF2 import PdfReader
import io

def process_text(text_lines):
    processed_html = []
    in_code_block = False
    code_content = []

    for line in text_lines:
        cleaned = line.strip()
        
        # Handle Code Blocks (```java, ```xml, etc.)
        if cleaned.startswith("```"):
            if in_code_block:
                # Ending a code block
                code_str = "\n".join(code_content)
                processed_html.append(f'<pre class="code-block">{code_str}</pre>')
                code_content = []
                in_code_block = False
            else:
                # Starting a code block
                in_code_block = True
            continue
        
        if in_code_block:
            code_content.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        if not cleaned:
            continue
        
        # 1. Identify Questions (Starts with # Q. or # or ends with ?)
        if cleaned.startswith("# Q.") or cleaned.startswith("# ") or cleaned.endswith('?'):
            display_text = re.sub(r'^#+\s*', '', cleaned)
            processed_html.append(f'<span class="question">◤ Q: {display_text} ◢</span>')
            
        # 2. Identify Section Headers (Starts with ### or ALL CAPS)
        elif cleaned.startswith("###") or (cleaned.isupper() and len(cleaned) > 3):
            display_text = re.sub(r'^###\s*', '', cleaned)
            processed_html.append(f'<span class="heading">★ {display_text.upper()}</span>')
            
        # 3. Identify Inline Bold (**text**)
        elif "**" in cleaned:
            formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cleaned)
            processed_html.append(f'<span>{formatted}</span>')

        # 4. Identify Key Terms (contains colon, short prefix)
        elif ':' in cleaned and len(cleaned.split(':')[0]) < 30:
            parts = cleaned.split(':', 1)
            processed_html.append(f'<span class="key-term">❖ {parts[0].upper()}:</span> {parts[1]}')
            
        # 5. Standard text
        else:
            processed_html.append(f'<span>{cleaned}</span>')
            
    return " ".join(processed_html)

def generate_html(content, font_size, line_height, margin):
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Micro Notes</title>
    <style>
        @page {{
            size: A4;
            margin: {margin};
        }}
        body {{
            font-family: Arial, sans-serif;
            font-size: {font_size};
            line-height: {line_height};
            color: #000;
            background: #fff;
            margin: 0;
            padding: 0;
            text-align: justify;
            word-break: break-all;
        }}
        .heading {{
            font-weight: bold;
            text-decoration: underline;
            display: inline-block;
            margin-top: 4px;
        }}
        .question {{
            font-weight: bold;
            font-style: italic;
            display: inline-block;
            margin-top: 4px;
        }}
        .key-term {{
            font-weight: bold;
        }}
        .code-block {{
            font-family: 'Courier New', Courier, monospace;
            background-color: #f0f0f0;
            border: 0.5px solid #ccc;
            padding: 2px;
            font-size: 0.85em;
            line-height: 1.0;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 2px 0;
            display: block;
        }}
        span {{
            margin-right: 4px;
        }}
        b {{
            font-weight: bold;
        }}
        @media print {{
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""
    return html_template

st.set_page_config(page_title="Micro Notes Generator", page_icon="📝")
st.title("📝 Smart Micro Notes Generator")

# Sidebar settings
st.sidebar.header("Settings")
font_size = st.sidebar.text_input("Font Size", value="40px")
line_height = st.sidebar.text_input("Line Spacing", value="0.9")
margin = st.sidebar.text_input("Margin", value="5mm")

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])

if uploaded_file is not None:
    lines = []
    if uploaded_file.type == "text/plain":
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        lines = stringio.readlines()
    elif uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split('\n'))

    if lines:
        processed_content = process_text(lines)
        final_html = generate_html(processed_content, font_size, line_height, margin)
        
        st.success("Notes processed successfully!")
        st.download_button(
            label="Download Micro Notes HTML",
            data=final_html,
            file_name="micro_notes.html",
            mime="text/html"
        )
