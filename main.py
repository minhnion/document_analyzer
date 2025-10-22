from pathlib import Path
import fitz
from src.pdf_extractor import extract_text_blocks
from src.image_extractor import extract_image_objects
from src.block_processor import process_elements
from src.markdown_writer import write_to_markdown

def run_extraction_pipeline(input_pdf_path: Path, base_output_dir: Path):
    print("="*50)
    print(f"Đang xử lý file: {input_pdf_path.name}")
    
    pdf_name_without_ext = input_pdf_path.stem
    pdf_output_dir = base_output_dir / "extracted" / pdf_name_without_ext
    
    # Bước 2: Trích xuất (đã sửa lỗi)
    raw_text_blocks = extract_text_blocks(pdf_path=input_pdf_path)
    raw_image_objects = extract_image_objects(pdf_path=input_pdf_path)

    # Bước 3: Xử lý
    print("\n--- Bắt đầu Bước 3: Xử lý các phần tử (Text & Image) ---")
    try:
        doc = fitz.open(input_pdf_path)
        page_height = doc.load_page(0).rect.height
        doc.close()
    except Exception as e:
        print(f"Không thể đọc kích thước trang, sử dụng giá trị mặc định. Lỗi: {e}")
        page_height = 841.89

    structured_elements = []
    if raw_text_blocks or raw_image_objects:
        structured_elements = process_elements(
            raw_text_blocks=raw_text_blocks,
            raw_image_objects=raw_image_objects,
            page_height=page_height,
            pdf_path=input_pdf_path
        )
        print(f"Bước 3 hoàn thành: Đã xử lý xong {len(structured_elements)} phần tử nội dung.")
    else:
        print("Không có phần tử nào được trích xuất.")
        return

    # Bước 4: Ghi file
    if structured_elements:
        write_to_markdown(
            elements=structured_elements,
            pdf_path=input_pdf_path,
            output_dir=pdf_output_dir
        )
    
    print("\nPIPELINE TRÍCH XUẤT HOÀN TẤT!")
    print("="*50)

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    
    SAMPLE_PDF_PATH = DATA_DIR / "samples" / "sample.pdf"
    
    if not SAMPLE_PDF_PATH.exists():
        print(f"Lỗi: Không tìm thấy file sample tại '{SAMPLE_PDF_PATH}'")
    else:
        run_extraction_pipeline(
            input_pdf_path=SAMPLE_PDF_PATH, 
            base_output_dir=OUTPUT_DIR
        )