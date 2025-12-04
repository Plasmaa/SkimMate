import streamlit as st

# Default Keyword Categories and Colors
DEFAULT_KEYWORDS = {
    "Errors/Mistakes": [
        "problem", "problems", "error", "errors", "mistakes", "contradict", "contradicts", "contradicted", "contradictory",
        "challenge", "challenges", "challenging", "erroneous", "deficit", "deficits", "limitation", "limitations", 
        "gap", "gaps", "discrepancy", "discrepancies", "anomaly", "anomalies", "complexity", "complexities", 
        "contrast", "sharp contrast"
    ],
    "Novelty/Contribution": [
        "discover", "discovers", "discovered", "discovery", "discoveries", "finding", "findings", "novel", "novelty",
        "contribute", "contributes", "contributed", "contribution", "contributions", "propose", "proposes", "proposed",
        "insight", "insights", "outperform", "outperforms", "outperformed", "highlight", "highlights", "highlighted"
    ],
    "Methodology": [
        "methodology", "methodologies", "algorithm", "algorithms", "framework", "frameworks", "model", "models",
        "implement", "implements", "implemented", "implementation", "application", "applications", "experiment", "experiments",
        "simulation", "simulation experiment", "survey", "surveys", "interview", "interviews", "data collection", 
        "primary data", "qualitative", "quantitative", "KPI", "performance evaluation", "observation", "observations",
        "pragmatic", "heuristic"
    ],
    "Analysis/Results": [
        "verify", "verifies", "verified", "verification", "justify", "justifies", "justified", "justification",
        "evident", "evidence", "results", "validate", "validates", "validated", "validation", "performance", 
        "performs", "performed", "evaluation", "argument", "arguments", "argues", "argued", "suggest", "suggests", 
        "suggested", "implication", "implications", "hypothesis", "hypotheses", "confirmation", "clarifies", 
        "clarification", "argumentative", "report", "reports", "reported", "aim", "aims", "goals", "outcome", "outcomes"
    ]
}

# Colors for highlighting (RGB tuples 0-1)
CATEGORY_COLORS = {
    "Errors/Mistakes": (1, 0.6, 0.6),       # Light Red
    "Novelty/Contribution": (0.6, 1, 0.6),  # Light Green
    "Methodology": (0.6, 0.6, 1),           # Light Blue
    "Analysis/Results": (0.8, 0.6, 1),      # Light Purple
    "Custom": (1, 1, 0.6)                   # Light Yellow
}

def get_flattened_keywords(selected_categories, custom_keywords):
    """
    Returns a dictionary mapping keyword -> category.
    """
    keyword_map = {}
    
    # Add selected category keywords
    for category in selected_categories:
        if category in DEFAULT_KEYWORDS:
            for kw in DEFAULT_KEYWORDS[category]:
                keyword_map[kw.lower()] = category
                
    # Add custom keywords
    for kw in custom_keywords:
        if kw.strip():
            keyword_map[kw.lower().strip()] = "Custom"
            
    return keyword_map
