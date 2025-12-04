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

def generate_paper_triage(text_content):
    """
    Generates a heuristic-based triage of the paper using keyword matching.
    """
    triage = {
        "research_gap": "Not detected.",
        "dataset_used": "Not detected.",
        "main_conclusion": "Not detected."
    }
    
    # Heuristics
    gap_keywords = ["limitation", "gap", "however", "although", "future work", "remains to be", "insufficient", "lack of"]
    data_keywords = ["dataset", "survey", "participants", "sample size", "n =", "collected from", "database", "corpus"]
    conclusion_keywords = ["conclude", "conclusion", "results show", "findings indicate", "summary", "demonstrate", "suggests"]
    
    # Split into sentences (simple split)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text_content)
    
    # Helper to find best sentence
    def find_best_sentence(keywords):
        best_sent = None
        max_score = 0
        
        for sent in sentences:
            clean_sent = sent.strip()
            if len(clean_sent) < 20 or len(clean_sent) > 500: # Filter too short/long
                continue
                
            score = 0
            lower_sent = clean_sent.lower()
            for kw in keywords:
                if kw in lower_sent:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_sent = clean_sent
                
        return best_sent

    # Find best matches
    gap = find_best_sentence(gap_keywords)
    if gap: triage["research_gap"] = gap
    
    data = find_best_sentence(data_keywords)
    if data: triage["dataset_used"] = data
    
    conclusion = find_best_sentence(conclusion_keywords)
    if conclusion: triage["main_conclusion"] = conclusion
    
    return triage

def extract_citations(text):
    """
    Extracts citations from the text using regex.
    Supports formats like [1], [12], (Author, 2023).
    """
    citations = set()
    
    # Pattern for [1], [12], [1-3]
    bracket_pattern = r'\[\d+(?:-\d+)?(?:,\s*\d+)*\]'
    matches = re.findall(bracket_pattern, text)
    citations.update(matches)
    
    # Pattern for (Author, Year) - simplified
    # Looks for (Word, 19xx or 20xx)
    author_year_pattern = r'\([A-Z][a-z]+(?: et al\.)?, \d{4}\)'
    matches = re.findall(author_year_pattern, text)
    citations.update(matches)
    
    return sorted(list(citations))
