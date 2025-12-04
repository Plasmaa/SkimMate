# SkimMate - Project Documentation

## 1. Project Overview
SkimMate is an intelligent research paper analysis tool built with Python and Streamlit. It is designed to help researchers, students, and academics rapidly assess the value and content of scientific papers (PDFs) without reading every word.

The application automatically scans uploaded PDF documents against a curated database of research keywords, categorizing them into:
-   **Errors/Mistakes**
-   **Novelty/Contribution**
-   **Methodology**
-   **Analysis/Results**
-   **Custom Keywords** (User defined)

It provides a visual dashboard with statistical insights, a highlighted PDF view, and an extracted sentences preview for quick context.

## 2. Key Features
-   **Smart Keyword Analysis**: Automatically detects and categorizes key terms related to research quality and content.
-   **Interactive Dashboard**:
    -   **Keyword Statistics**: Visual cards showing the frequency of terms in each category.
    -   **Extracted Sentences Preview**: A scrollable list of sentences containing keywords, grouped by term, with keyword highlighting and context truncation.
-   **PDF Highlighting**: Generates a downloadable PDF with color-coded highlights corresponding to the keyword categories.
-   **Integrated PDF Viewer**: View the highlighted PDF directly within the application.
-   **Custom Keywords**: Users can input specific terms (e.g., chemical names, algorithms) to track.
-   **Responsive Navigation**: Smooth scrolling navigation for the landing page sections.

## 3. Technical Stack
-   **Frontend/UI**: [Streamlit](https://streamlit.io/)
-   **PDF Processing**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
-   **Data Handling**: Python standard libraries (`re`, `collections`)
-   **Environment**: Python Virtual Environment (`.venv`)

## 4. Installation & Setup

### Prerequisites
-   Python 3.8 or higher

### Steps
1.  **Clone/Download** the project repository.
2.  **Create a Virtual Environment** (Recommended to keep dependencies isolated):
    ```bash
    python -m venv .venv
    ```
3.  **Activate the Virtual Environment**:
    -   Windows: `.venv\Scripts\activate`
    -   Mac/Linux: `source .venv/bin/activate`
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 5. Usage
1.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```
2.  **Access the App**: Open your browser to `http://localhost:8501`.
3.  **Workflow**:
    -   **Landing Page**: Read about features or click "Browse files" to upload a PDF.
    -   **Upload**: Select a research paper (PDF format). Optionally add custom keywords.
    -   **Analyze**: Click "Analyze Paper".
    -   **Dashboard**:
        -   Review the "Keyword Analysis" on the left to see what the paper focuses on.
        -   Use the "Extracted Sentences Preview" on the right to read specific findings in context.
        -   View the "Highlighted PDF Preview" or download the file.

## 6. Project Structure & Code Explanation

### `app.py`
The main entry point of the application.
-   **Configuration**: Sets page config, custom CSS for the dark theme and UI components.
-   **Navigation**: Handles routing between 'landing' and 'dashboard' states using `st.session_state`.
-   **UI Rendering**:
    -   **Landing Page**: Renders the hero section, features, and upload widget.
    -   **Dashboard**: Renders the split-column layout.
        -   *Left Column*: Displays keyword statistics cards.
        -   *Right Column*: Displays the "Extracted Sentences Preview" (with regex highlighting) and the PDF Viewer.

### `processor.py`
Handles the core logic for text analysis and PDF manipulation.
-   `extract_sentences_with_keywords(pdf_file, keyword_map)`:
    -   Reads the PDF text.
    -   Splits text into sentences.
    -   Searches for keywords and aggregates statistics.
    -   Returns stats, keyword counts, and a list of context sentences.
-   `highlight_pdf(pdf_file, keyword_map, color_map)`:
    -   Opens the PDF.
    -   Searches for keyword coordinates (quads).
    -   Adds highlight annotations with specific colors based on the category.
    -   Returns the binary content of the highlighted PDF.

### `utils.py`
Contains configuration data and helper functions.
-   `DEFAULT_KEYWORDS`: A dictionary mapping categories (e.g., "Methodology") to lists of related keywords.
-   `CATEGORY_COLORS`: Defines the RGB colors used for highlighting each category.
-   `get_flattened_keywords`: A helper to merge default and custom keywords into a single mapping for efficient lookup.

### `requirements.txt`
Lists all necessary Python packages:
-   `streamlit`
-   `pymupdf`
-   `streamlit-pdf-viewer`
-   `pandas` (if used for data handling)

## 7. Future Improvements
-   **Advanced NLP**: Implement sentence boundary detection using libraries like `spacy` for better accuracy than regex.
-   **Semantic Search**: Use embeddings to find conceptually similar sentences, not just exact keyword matches.
-   **Multi-file Upload**: Allow batch processing of multiple papers.
