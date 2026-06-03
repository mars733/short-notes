import streamlit as st
import re
from PyPDF2 import PdfReader
import io

def process_text(text_lines):
    processed_html = []
    for line in text_lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        
        # 1. Identify Headings
        if cleaned.isupper() or cleaned.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', 'Chapter', 'Section')):
            processed_html.append(f'<span class="heading">★ {cleaned.upper()}</span>')
            
        # 2. Identify Questions
        elif cleaned.endswith('?'):
            processed_html.append(f'<span class="question">◤ Q: {cleaned} ◢</span>')
            
        # 3. Identify Key Terms
        elif ':' in cleaned and len(cleaned.split(':')[0]) < 30:
            parts = cleaned.split(':', 1)
            processed_html.append(f'<span class="key-term">❖ {parts[0].upper()}:</span> {parts[1]}')
            
        # 4. Standard text
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
            color: #000;
        }}
        .question {{
            font-weight: bold;
            font-style: italic;
        }}
        .key-term {{
            font-weight: bold;
        }}
        span {{
            margin-right: 4px;
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
st.markdown("""
Upload your notes (.txt or .pdf) and get a high-density HTML file optimized for micro-printing.
Once downloaded, open the file and print it using **'9 pages per sheet'** in your printer settings.
""")

# Sidebar settings
st.sidebar.header("Settings")
font_size = st.sidebar.text_input("Font Size", value="40px")
line_height = st.sidebar.text_input("Line Spacing", value="0.9")
margin = st.sidebar.text_input("Margin", value="5mm")

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])

if uploaded_file is not None:
    lines = []
    if uploaded_file.type == "text/plain":
        # Process TXT
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        lines = stringio.readlines()
    elif uploaded_file.type == "application/pdf":
        # Process PDF
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
        
        st.info("💡 Pro Tip: After downloading, open the file in Chrome/Edge and use the 'Print' dialog to set 'Pages per sheet' to 9.")
    else:
        st.error("Could not extract any text from the file.")
