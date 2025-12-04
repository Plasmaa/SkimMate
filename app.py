import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
import processor
from utils import DEFAULT_KEYWORDS, CATEGORY_COLORS, get_flattened_keywords
import re

st.set_page_config(page_title="SkimMate", layout="wide", initial_sidebar_state="collapsed")

# Handle Navigation via Query Params
if "nav" in st.query_params:
    st.session_state['page'] = 'landing'
    st.query_params.clear()

# Initialize Session State
if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'
if 'processed' not in st.session_state:
    st.session_state['processed'] = False

def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        :root {
            --bg-color: #0E1117;
            --card-bg: #161B22;
            --text-color: #E6E6E6;
            --text-muted: #8B949E;
            --border-color: #30363D;
            --accent-color: #58A6FF;
            --header-bg: rgba(14, 17, 23, 0.95);
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            background-color: var(--bg-color);
        }
        
        /* Hide default header and footer */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Compact Layout & Reduce default Streamlit padding */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1100px !important; /* Constrain width */
            margin: 0 auto;
        }
        
        /* Custom Header */
        .custom-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.8rem 0;
            background-color: var(--header-bg);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
            position: sticky;
            top: 0;
            z-index: 999;
        }
        .logo-area {
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
        }
        .logo-icon {
            background-color: #238636; /* Darker green/blue */
            color: white;
            padding: 6px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 1.1rem;
        }
        .app-name {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-color);
        }
        .nav-links {
            display: flex;
            gap: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .nav-link {
            text-decoration: none !important;
            color: var(--text-muted);
            transition: color 0.2s;
        }
        .nav-link:hover {
            color: var(--accent-color);
            cursor: pointer;
        }
        
        /* Info Sections */
        .info-section {
            padding: 4rem 0;
            border-bottom: 1px solid var(--border-color);
        }
        .info-title {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
            color: var(--text-color);
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            max-width: 900px;
            margin: 0 auto;
        }
        .feature-item {
            text-align: center;
            padding: 1.5rem;
            background: var(--card-bg);
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }
        .feature-item h3 {
            color: var(--text-color);
        }
        .feature-item p {
            color: var(--text-muted);
        }
        
        /* Landing Page */
        .hero-section {
            text-align: center;
            padding: 3rem 0 5rem 0;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-color);
            margin-bottom: 0.8rem;
        }
        .hero-subtitle {
            font-size: 1rem;
            color: var(--text-muted);
            max-width: 550px;
            margin: 0 auto 2.5rem auto;
            line-height: 1.5;
        }
        .upload-card {
            background: var(--card-bg);
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            border: 1px solid var(--border-color);
            max-width: 600px;
            margin: 0 auto;
            text-align: center;
        }
        
        /* Dashboard */
        .dashboard-container {
            padding: 0;
        }
        .card {
            background: var(--card-bg);
            border-radius: 10px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            border: 1px solid var(--border-color);
            margin-bottom: 1.2rem;
        }
        .stat-card {
            border-left: 4px solid var(--border-color);
        }
        .stat-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .stat-title {
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--text-color);
        }
        .stat-count {
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--text-color);
        }
        .keyword-list {
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 8px;
            padding-left: 8px;
        }
        .keyword-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 3px;
        }
        
        /* Buttons */
        .stButton button {
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.9rem;
            padding: 0.4rem 1rem;
        }
        
        /* Custom Colors for Stat Cards */
        .border-red { border-left-color: #FF6B6B !important; }
        .border-green { border-left-color: #4ECDC4 !important; }
        .border-blue { border-left-color: #45B7D1 !important; }
        .border-purple { border-left-color: #A06BFF !important; }
        
        .icon-red { color: #FF6B6B; }
        .icon-green { color: #4ECDC4; }
        .icon-blue { color: #45B7D1; }
        .icon-purple { color: #A06BFF; }

    </style>
    """, unsafe_allow_html=True)

local_css()

# --- Custom Header ---
nav_links_html = ""
if st.session_state['page'] == 'landing':
    nav_links_html = """<div class="nav-links">
        <a href="#features" target="_self" class="nav-link">Features</a>
        <a href="#how-it-works" target="_self" class="nav-link">How It Works</a>
        <a href="#about" target="_self" class="nav-link">About</a>
    </div>"""

st.markdown(f"""
<div class="custom-header">
    <a href="/?nav=landing" target="_self" style="text-decoration: none;">
        <div class="logo-area">
            <div class="logo-icon">📄</div>
            <div>
                <div class="app-name">SkimMate</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">Research Paper Highlighter</div>
            </div>
        </div>
    </a>
    {nav_links_html}
</div>
""", unsafe_allow_html=True)

# --- Landing Page ---
if st.session_state['page'] == 'landing':
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">Intelligent Research Paper Analysis</div>
        <div class="hero-subtitle">
            Upload your research paper and let SkimMate automatically identify and highlight key concepts, methodologies, findings, and limitations with color-coded precision.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; margin-bottom: 1rem;'><strong>Upload Research Paper</strong><br><span style='color: var(--text-muted); font-size: 0.9rem;'>Supports PDF files up to 50MB</span></div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
            
            st.markdown("### Custom Keywords")
            custom_input = st.text_input("Add custom keywords (comma separated)", placeholder="e.g. specific chemical, algorithm name")
            
            if uploaded_file:
                if st.button("Analyze Paper", type="primary", use_container_width=True):
                    st.session_state['uploaded_file'] = uploaded_file
                    st.session_state['custom_input'] = custom_input
                    st.session_state['page'] = 'dashboard'
                    st.rerun()

    # --- Info Sections ---
    st.markdown("""
    <div id="features" class="info-section">
        <div class="info-title">Features</div>
        <div class="feature-grid">
            <div class="feature-item">
                <h3>🔍 Smart Analysis</h3>
                <p>Automatically detects errors, novel contributions, and methodologies.</p>
            </div>
            <div class="feature-item">
                <h3>🎨 Color-Coded</h3>
                <p>Visual highlighting makes skimming papers faster and more effective.</p>
            </div>
            <div class="feature-item">
                <h3>📊 Instant Stats</h3>
                <p>Get immediate frequency counts of key terms and concepts.</p>
            </div>
        </div>
    </div>
    
    <div id="how-it-works" class="info-section">
        <div class="info-title">How It Works</div>
        <div style="max-width: 700px; margin: 0 auto; text-align: center; line-height: 1.6; color: var(--text-muted);">
            <p>1. <strong>Upload</strong> your research paper (PDF).</p>
            <p>2. <strong>SkimMate</strong> scans the text against a curated database of research keywords.</p>
            <p>3. <strong>Review</strong> the dashboard for insights and download the highlighted version.</p>
        </div>
    </div>
    
    <div id="about" class="info-section">
        <div class="info-title">About</div>
        <div style="max-width: 700px; margin: 0 auto; text-align: center; color: var(--text-muted);">
            <p>SkimMate is designed to help researchers, students, and academics rapidly assess the value and content of scientific papers without reading every word.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- Dashboard Page ---
elif st.session_state['page'] == 'dashboard':
    uploaded_file = st.session_state['uploaded_file']
    custom_input = st.session_state['custom_input']
    
    # Process if not already processed
    if not st.session_state['processed']:
        with st.spinner("Analyzing and Highlighting..."):
            # Prepare keywords
            custom_keywords = [k.strip() for k in custom_input.split(",") if k.strip()]
            # Select all categories by default for now
            selected_categories = list(DEFAULT_KEYWORDS.keys())
            keyword_map = get_flattened_keywords(selected_categories, custom_keywords)
            
            # Analysis
            stats, keyword_counts, context_data = processor.extract_sentences_with_keywords(uploaded_file, keyword_map)
            
            # Phase 2: AI Triage & Citations
            # We need raw text for these. Since we already read the stream in processor, we might need to re-read or adjust.
            # However, processor.extract_sentences_with_keywords reads it. 
            # Let's just re-read here for simplicity or better yet, let's extract text once.
            # For now, we'll just re-open in processor functions as they handle seek(0).
            
            # Get full text for triage/citations (simplified extraction)
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            uploaded_file.seek(0) # Reset
            
            triage_data = processor.generate_paper_triage(full_text)
            citations = processor.extract_citations(full_text)

            # Highlighting
            highlighted_pdf_bytes = processor.highlight_pdf(uploaded_file, keyword_map, CATEGORY_COLORS)
            
            st.session_state['stats'] = stats
            st.session_state['keyword_counts'] = keyword_counts
            st.session_state['context_data'] = context_data
            st.session_state['triage_data'] = triage_data
            st.session_state['citations'] = citations
            st.session_state['highlighted_pdf'] = highlighted_pdf_bytes
            st.session_state['processed'] = True
            st.rerun()
            
    # Layout
    left_col, right_col = st.columns([1, 3])
    
    with left_col:
        if st.button("↺ Upload New Paper", use_container_width=True):
            st.session_state['page'] = 'landing'
            st.session_state['processed'] = False
            st.session_state.pop('uploaded_file', None)
            st.rerun()

        st.markdown("### Keyword Analysis")
        st.markdown("<div style='color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;'>Toggle categories to filter results</div>", unsafe_allow_html=True)
        
        stats = st.session_state['stats']
        keyword_counts = st.session_state['keyword_counts']
        
        # Helper to render stat card
        def render_stat_card(category, color_class, icon_class, icon_char):
            count = stats.get(category, 0)
            st.markdown(f"""
            <div class="card stat-card {color_class}">
                <div class="stat-card-header">
                    <div class="stat-title"><span class="{icon_class}">■</span> {category}</div>
                    <div class="stat-count">{count}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Expandable keywords
            with st.expander("Show Keywords", expanded=True):
                # Filter keywords for this category
                if category != "Custom":
                    cat_map = get_flattened_keywords([category], [])
                    cat_keywords = {k: v for k, v in keyword_counts.items() if k in cat_map}
                else:
                    cat_keywords = {k: v for k, v in keyword_counts.items() if k in custom_input.lower()}
                
                # Sort by count desc
                sorted_kws = sorted(cat_keywords.items(), key=lambda item: item[1], reverse=True)
                
                for kw, cnt in sorted_kws:
                    st.markdown(f"""
                    <div class="keyword-item">
                        <span>{kw}</span>
                        <span style="color: #888;">{cnt}</span>
                    </div>
                    """, unsafe_allow_html=True)

        render_stat_card("Errors/Mistakes", "border-red", "icon-red", "■")
        render_stat_card("Novelty/Contribution", "border-green", "icon-green", "■")
        render_stat_card("Methodology", "border-blue", "icon-blue", "■")
        render_stat_card("Analysis/Results", "border-purple", "icon-purple", "■")
        

            
        # --- Phase 2: Citations Sidebar ---
        if 'citations' in st.session_state:
            st.sidebar.markdown("---")
            with st.sidebar.expander("Detected Citations", expanded=False):
                citations = st.session_state['citations']
                if citations:
                    for c in citations:
                        st.markdown(f"- {c}")
                else:
                    st.info("No citations detected.")

    with right_col:
        # --- Phase 2: Triage Deck ---
        if 'triage_data' in st.session_state:
            triage = st.session_state['triage_data']
            st.markdown("### AI Triage Deck")
            t1, t2, t3 = st.columns(3)
            
            def render_triage_card(title, content, emoji):
                st.markdown(f"""
                <div class="card" style="height: 200px; overflow-y: auto;">
                    <div style="font-weight: bold; margin-bottom: 8px; color: var(--accent-color);">{emoji} {title}</div>
                    <div style="font-size: 0.9rem; color: var(--text-color);">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with t1:
                render_triage_card("The Gap", triage['research_gap'], "🎯")
            with t2:
                render_triage_card("Data Source", triage['dataset_used'], "📊")
            with t3:
                render_triage_card("The Verdict", triage['main_conclusion'], "💡")
            
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

        # Process & Highlight Section
        st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin: 0; color: var(--text-color);">Process & Highlight</h3>
                    <p style="color: var(--text-muted); margin: 5px 0 0 0;">Generate a highlighted version of your PDF with color-coded keywords</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Download Button (Streamlit button needs to be outside HTML block for functionality)
        st.download_button(
            label="⬇ Download Highlighted PDF",
            data=st.session_state['highlighted_pdf'],
            file_name="highlighted_paper.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
        # --- Extracted Sentences Preview ---
        st.markdown("""
        <div class="card" style="margin-top: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: var(--text-color);">Extracted Sentences Preview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container(height=500):
            # Group sentences by keyword
            context_data = st.session_state.get('context_data', [])
            grouped_sentences = {}
            for item in context_data:
                kw = item['keyword']
                if kw not in grouped_sentences:
                    grouped_sentences[kw] = []
                grouped_sentences[kw].append(item['sentence'])
            
            # Display
            if not grouped_sentences:
                st.info("No sentences found with the selected keywords.")
            else:
                for kw in sorted(grouped_sentences.keys()):
                    st.markdown(f"<div style='color: var(--accent-color); font-weight: bold; margin-top: 10px; margin-bottom: 5px;'>--- {kw.upper()} ---</div>", unsafe_allow_html=True)
                    for i, sentence in enumerate(grouped_sentences[kw], 1):
                        # Find keyword and truncate
                        # Case-insensitive search
                        match = re.search(f"({re.escape(kw)})", sentence, re.IGNORECASE)
                        if match:
                            start, end = match.span()
                            # Context window
                            context_chars = 100
                            s_start = max(0, start - context_chars)
                            s_end = min(len(sentence), end + context_chars)
                            
                            prefix = "..." if s_start > 0 else ""
                            suffix = "..." if s_end < len(sentence) else ""
                            
                            snippet = sentence[s_start:s_end]
                            
                            # Highlight keyword in snippet
                            # We use a simple replace here on the snippet, but need to be careful with case
                            # A safer way is to re-find in snippet or just highlight the match we found if it's in range
                            # Let's just use regex sub on the snippet for simplicity, ensuring we only highlight the keyword
                            snippet_html = re.sub(f"({re.escape(kw)})", r"<span style='background-color: rgba(255, 255, 0, 0.2); color: #FFD700; font-weight: bold; padding: 0 4px; border-radius: 4px;'>\1</span>", snippet, flags=re.IGNORECASE)
                            
                            display_text = f"{prefix}{snippet_html}{suffix}"
                        else:
                            display_text = sentence # Fallback
                            
                        st.markdown(f"<div style='font-size: 0.9rem; margin-bottom: 8px; color: var(--text-color);'>{i}. {display_text}</div>", unsafe_allow_html=True)

        # PDF Preview Section
        st.markdown("""
        <div class="card" style="margin-top: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: var(--text-color);">Highlighted PDF Preview</h3>
            <p style="color: var(--text-muted); margin-bottom: 1rem;">View your processed document with color-coded highlights</p>
        </div>
        """, unsafe_allow_html=True)
        
        pdf_viewer(input=st.session_state['highlighted_pdf'], width=700, height=800)
