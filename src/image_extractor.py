import fitz
from pathlib import Path
from typing import List, Dict, Any

def extract_image_objects(pdf_path: Path) -> List[Dict[str, Any]]:
    image_objects = []
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            for img_info in page.get_image_info(xrefs=True):
                image_obj = {
                    'type': 'image',
                    'bbox': img_info.get('bbox'),
                    'page_num': page_num,
                    'xref': img_info.get('xref'),
                    'width': img_info.get('width', 0),
                    'height': img_info.get('height', 0),
                    'smask': img_info.get('smask', 0) 
                }
                image_objects.append(image_obj)

        doc.close()
        print(f"Đã trích xuất được {len(image_objects)} đối tượng hình ảnh.")

    except Exception as e:
        print(f"Lỗi khi trích xuất đối tượng hình ảnh: {e}")

    return image_objects