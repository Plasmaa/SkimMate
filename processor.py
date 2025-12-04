import fitz  # PyMuPDF
import io
import re
from collections import defaultdict

def extract_sentences_with_keywords(pdf_file, keyword_map):
    """
    Extracts sentences containing keywords from the PDF.
    Returns:
        - stats: dict {category: count}
        - context: list of dicts {page, sentence, keyword, category}
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    stats = defaultdict(int)
    keyword_counts = defaultdict(int)
    context_data = []
    
    # Reset file pointer for later use
    pdf_file.seek(0)
    
    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        # Simple sentence splitting (can be improved)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if not clean_sentence:
                continue
                
            lower_sentence = clean_sentence.lower()
            
            # Check for keywords
            found_keywords = []
            for kw, category in keyword_map.items():
                if kw in lower_sentence:
                    # Basic word boundary check could be added here
                    stats[category] += 1
                    keyword_counts[kw] += 1
                    found_keywords.append((kw, category))
            
            if found_keywords:
                # Store context (taking the first found keyword's category for simplicity in display, 
                # or we could list all)
                for kw, category in found_keywords:
                    context_data.append({
                        "page": page_num + 1,
                        "sentence": clean_sentence,
                        "keyword": kw,
                        "category": category
                    })
                    
    return stats, keyword_counts, context_data

def highlight_pdf(pdf_file, keyword_map, color_map):
    """
    Highlights keywords in the PDF.
    Returns:
        - bytes: Highlighted PDF content
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_file.seek(0) # Reset
    
    for page in doc:
        for kw, category in keyword_map.items():
            # Search for the keyword
            quads = page.search_for(kw)
            
            # Get color for the category
            color = color_map.get(category, (1, 1, 0)) # Default yellow
            
            # Add highlight
            for quad in quads:
                annot = page.add_highlight_annot(quad)
                annot.set_colors(stroke=color)
                annot.update()
                
    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    return output_buffer.getvalue()
