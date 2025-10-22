import fitz 
from pathlib import Path
from PIL import Image
from typing import List, Dict, Any

def convert_pdf_to_images(pdf_path: Path, output_dir:Path, dpi: int = 400) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = []

    try:
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=dpi)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            image_path = output_dir / f"page_{page_num + 1}.png"
            img.save(image_path, "PNG")
            image_paths.append(image_path) 
    
    except Exception as e:
        return []
    
    return image_paths

def extract_text_blocks(pdf_path: Path) -> List[Dict[str, Any]]:
    all_blocks = []
    
    try:
        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            page_blocks = page.get_text("dict")["blocks"]

            for block in page_blocks:
                if block['type'] == 0:
                    block['page_num'] = page_num
                    all_blocks.append(block)
        doc.close()
    
    except Exception as e:
        print("Error extract text block: {e}")
    
    return all_blocks