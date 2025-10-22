import fitz
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import io
import re

def spans_to_markdown_text(spans: List[Dict[str, Any]]) -> str:
    md_text = ""
    for span in spans:
        text = span.get('text', '')
        font = span.get('font', '').lower()
        is_bold = 'bold' in font
        is_italic = 'italic' in font
        
        if is_bold and is_italic: md_text += f"_**{text}**_"
        elif is_bold: md_text += f"**{text}**"
        elif is_italic: md_text += f"_{text}_"
        else: md_text += text
            
    return md_text.replace('\n', ' ').strip()

def spans_to_plain_text(spans: List[Dict[str, Any]]) -> str:
    return "".join([s.get('text', '') for s in spans]).replace('\n', ' ').strip()

def write_to_markdown(
    elements: List[Dict[str, Any]],
    pdf_path: Path,
    output_dir: Path
):
    
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    markdown_content = []
    image_counter = 1
    doc = fitz.open(pdf_path)


    doc_title = pdf_path.stem
    markdown_content.append(f"# {doc_title}\n")

    for element in elements:
        elem_type = element.get('type')
        spans = element.get('spans', [])
        
        if elem_type == "H1":
            plain_text = spans_to_plain_text(spans)
            clean_text = re.sub(r'^\d+\.?\s*', '', plain_text).strip()
            markdown_content.append(f"# {clean_text}\n")
        
        elif elem_type == "H2":
            plain_text = spans_to_plain_text(spans)
            clean_text = re.sub(r'^\d+\.\d+\.?\s*', '', plain_text).strip()
            markdown_content.append(f"## {clean_text}\n")

        elif elem_type == "H2_NO_NUM":
            plain_text = spans_to_plain_text(spans)
            markdown_content.append(f"## {plain_text}\n")
            
        elif elem_type in ["P", "LI"]:
            formatted_text = spans_to_markdown_text(spans)
            if elem_type == "P":
                markdown_content.append(f"{formatted_text}\n")
            else: 
                clean_text = re.sub(r'^[•\*\-\s]+|^\d+\.\s*', '', formatted_text)
                markdown_content.append(f"  * {clean_text}\n")

        elif elem_type == "CAPTION":
            formatted_text = spans_to_markdown_text(spans)
            match = re.match(r'(Hình \d+\.?)', formatted_text, re.IGNORECASE)
            if match:
                caption_part = match.group(1)
                rest_of_text = formatted_text[len(caption_part):].strip()
                markdown_content.append(f"_**{caption_part}** {rest_of_text}_\n")
            else:
                markdown_content.append(f"_{formatted_text}_\n")

        elif elem_type == "image":
            xref = element['xref']
            img_data = doc.extract_image(xref)['image']
            img = Image.open(io.BytesIO(img_data))
            if img.mode == 'RGBA': img = img.convert('RGB')
                
            image_filename = f"image{image_counter}.jpg"
            img.save(images_dir / image_filename, "JPEG")
            markdown_content.append(f"![](images/{image_filename})\n")
            image_counter += 1
    
    doc.close()

    final_markdown = "\n".join(markdown_content)
    output_md_path = output_dir / "main.md"
    output_md_path.write_text(final_markdown, encoding="utf-8")
    print(f"Đã ghi thành công file Markdown tại: {output_md_path}")
    print(f"Đã lưu tổng cộng {image_counter - 1} hình ảnh.")