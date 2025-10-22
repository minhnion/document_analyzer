import re
import math
from typing import Dict, Any
def is_watermark(block: Dict[str, Any]) -> bool:
    if 'lines' in block and block['lines'] and 'spans' in block['lines'][0] and block['lines'][0]['spans']:
        text = block['lines'][0]['spans'][0]['text']
        watermark_pattern = re.compile(r'\d{4}-\d{2}-\d{2}|_Al Race|TD003|Lần ban hành', re.IGNORECASE)
        if watermark_pattern.search(text):
            return True
    
    if 'transform' in block:
        transform = block['transform']
        angle_rad = math.atan2(transform[1], transform[0])
        if not math.isclose(angle_rad, 0.0, abs_tol=1e-6):
            return True
            
    return False