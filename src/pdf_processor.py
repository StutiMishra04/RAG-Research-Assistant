import io
from PIL import Image
import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_pdf_with_images(pdf_path):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=250,
        separators=["\n\n", "\n", ".", " "]
    )

    all_chunks = []

    doc = fitz.open(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            ### 1. Extract and chunk TEXT ###
            text = page.extract_text()
            if text:
                # Optional: try to preserve heading structure by buffering
                lines = text.split("\n")
                processed_text = ""
                for line in lines:
                    if line.strip().endswith(":") or line.strip().istitle():
                        processed_text += f"\n\n{line.strip()}"
                    else:
                        processed_text += f"\n{line.strip()}"
                
                chunks = splitter.split_text(processed_text)
                for chunk in chunks:
                    all_chunks.append({
                        'content': chunk,
                        'page': page_num + 1,
                        'type': 'text'
                    })

            ### 2. Extract and chunk TABLES ###
            tables = page.extract_tables()
            for table_num, table in enumerate(tables):
                table_text = "\n".join([
                    " | ".join([str(cell) if cell is not None else "" for cell in row])
                    for row in table if row
                ])

                if len(table_text) > 1000:
                    table_chunks = splitter.split_text(table_text)
                    for chunk_idx, chunk in enumerate(table_chunks):
                        all_chunks.append({
                            'content': chunk,
                            'page': page_num + 1,
                            'type': 'table',
                            'table_id': table_num
                        })
                else:
                    all_chunks.append({
                        'content': table_text,
                        'page': page_num + 1,
                        'type': 'table',
                        'table_id': table_num
                    })

            ### 3. Extract IMAGES + OCR ###
            fitz_page = doc.load_page(page_num)
            image_list = fitz_page.get_images()

            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)

                    if pix.n - pix.alpha < 4:
                        img_data = pix.tobytes("png")
                        image = Image.open(io.BytesIO(img_data))

                        ocr_text = pytesseract.image_to_string(image)
                        if ocr_text.strip():
                            all_chunks.append({
                                'content': f"[Image OCR Text]: {ocr_text.strip()}",
                                'page': page_num + 1,
                                'type': 'image_text',
                                'image_id': img_index
                            })

                        all_chunks.append({
                            'content': f"[Image on page {page_num + 1}]",
                            'page': page_num + 1,
                            'type': 'image',
                            'image_id': img_index,
                            'image_data': img_data
                        })

                    pix = None
                except Exception as e:
                    print(f"Error processing image {img_index} on page {page_num + 1}: {e}")

    doc.close()
    return all_chunks