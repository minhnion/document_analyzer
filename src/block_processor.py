import fitz 
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import io
import re
from src.watermark_remove import is_watermark

def get_main_font_properties(block: Dict[str, Any]) -> Dict[str, Any]:
    if 'lines' in block and block['lines'] and 'spans' in block['lines'][0] and block['lines'][0]['spans']:
        span = block['lines'][0]['spans'][0]
        full_text = " ".join([s['text'] for line in block['lines'] for s in line['spans']])
        return {
            'size': round(span.get('size', 0)),
            'font': span.get('font', '').lower(),
            'flags': span.get('flags', 0),
            'text': full_text
        }
    return {'size': 0, 'font': '', 'flags': 0, 'text': ''}

def get_spans_from_block(block: Dict[str, Any]) -> List[Dict[str, Any]]:
    spans = []
    if 'lines' in block:
        for line in block['lines']:
            if 'spans' in line:
                spans.extend(line['spans'])
    return spans

def classify_block(block: Dict[str, Any]) -> str:
    spans = get_spans_from_block(block)
    if not spans:
        return "P"

    first_span_text = spans[0].get('text', '').strip()
    font_size = round(spans[0].get('size', 0))
    font_name = spans[0].get('font', '').lower()

    if re.match(r'hình \d+\.', first_span_text, re.IGNORECASE):
        return "CAPTION"

    if 'bold' in font_name:
        if font_size >= 14 or re.match(r'^\d+\.\s', first_span_text):
            return "H1"
        if font_size >= 12 or re.match(r'^\d+\.\d+\s', first_span_text):
            return "H2"
        if font_size >= 11:
            return "H3"

    if first_span_text.startswith(('•', '*', '-', 'a)', 'b)')) or re.match(r'^\d+\.', first_span_text):
        return "LI"
        
    return "P"

def process_elements(
    raw_text_blocks: List[Dict[str, Any]],
    raw_image_objects: List[Dict[str, Any]],
    page_height: float,
    pdf_path: Path
) -> List[Dict[str, Any]]:
    
    all_elements = raw_text_blocks + raw_image_objects
    cleaned_elements = []
    header_margin, footer_margin = page_height * 0.12, page_height * 0.90
    
    doc = fitz.open(pdf_path)
    for element in all_elements:
        bbox = element.get('bbox')
        if not bbox or bbox[1] < header_margin or bbox[3] > footer_margin: continue
        
        if element.get('type') == 'image':
            if not (element.get('width', 0) > 15 and element.get('height', 0) > 15): continue
            try:
                img_data = doc.extract_image(element['xref'])['image']
                img = Image.open(io.BytesIO(img_data))
                colors = img.getcolors(maxcolors=256)
                if colors is not None and len(colors) <= 4: continue
                cleaned_elements.append(element)
            except Exception: continue
        else:
            if not is_watermark(element): cleaned_elements.append(element)
    doc.close()
    
    structured_elements = []
    for element in cleaned_elements:
        if element.get('type') == 'image':
            structured_elements.append(element)
        else:
            block_type = classify_block(element)
            spans = get_spans_from_block(element)
            if spans:
                structured_elements.append({
                    'type': block_type, 'spans': spans,
                    'bbox': element['bbox'], 'page_num': element['page_num']
                })
                
    structured_elements.sort(key=lambda x: (x['page_num'], x.get('bbox', (0,0))[1], x.get('bbox', (0,0))[0]))
    
    if not structured_elements: return []
        
    merged_elements = []
    i = 0
    while i < len(structured_elements):
        current_element = structured_elements[i]
        
        if current_element.get('type') == 'P':
            combined_spans = list(current_element.get('spans', []))
            j = i + 1
            while j < len(structured_elements) and structured_elements[j].get('type') == 'P':
                combined_spans.append({'text': ' '}) 
                combined_spans.extend(structured_elements[j].get('spans', []))
                j += 1
            
            merged_elements.append({'type': 'P', 'spans': combined_spans})
            i = j 
        else:
            merged_elements.append(current_element)
            i += 1

    return merged_elements