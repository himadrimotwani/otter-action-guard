import re
from typing import Dict, List, Tuple


class ContextualSpeechCorrector:
    """
    Context-aware ASR transcript post-corrector.
    Leverages domain glossaries and phonetic/n-gram heuristics to repair
    acoustic mis-transcriptions common in automated speech recognition (ASR)
    for enterprise, supply-chain, and engineering meetings.
    
    (Inspired by speech post-processing pipelines for domain-specific ASR).
    """

    DEFAULT_GLOSSARY: Dict[str, List[str]] = {
        "SKU": [r"\bskew\b", r"\bskew\s+(\d+)\b", r"\bsku's\b", r"\bskews\b"],
        "BOM": [r"\bbomb\b", r"\bbee oh em\b", r"\bbeaum\b"],
        "WMS": [r"\bwomen's\b(?=.*(?:inventory|warehouse|system|order))", r"\bdouble you em ess\b"],
        "FOB": [r"\beff oh bee\b", r"\bf\.o\.b\.\b"],
        "PO": [r"\bpee oh\b", r"\bp\.o\.\b", r"\bpost office\b(?=.*(?:number|order|invoice|issue))"],
        "Foxconn": [r"\bfox\s+con\b", r"\bfox\s+com\b"],
        "ERP": [r"\bee are pee\b", r"\be\.r\.p\.\b"],
        "MCP": [r"\bem see pee\b", r"\bm\.c\.p\.\b"],
        "SLO": [r"\bslow\b(?=.*(?:metric|breach|latency|uptime))", r"\bes ell oh\b"],
        "CI/CD": [r"\bsee eye see dee\b", r"\bsea eye sea dee\b"],
    }

    def __init__(self, custom_glossary: Dict[str, List[str]] = None):
        self.glossary = {**self.DEFAULT_GLOSSARY, **(custom_glossary or {})}

    def correct_text(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Applies phonetic & acoustic corrections to the transcript line.
        Returns:
            corrected_text: The repaired transcript text.
            corrections: List of modifications made with domain justification.
        """
        corrected = text
        changes: List[Dict[str, str]] = []

        for canonical_term, patterns in self.glossary.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, corrected, re.IGNORECASE))
                if matches:
                    for match in reversed(matches):
                        original_str = match.group(0)
                        # Retain captured group digits if pattern contains them
                        if len(match.groups()) > 0 and match.group(1):
                            replacement = f"{canonical_term} {match.group(1)}"
                        else:
                            replacement = canonical_term

                        start, end = match.span()
                        corrected = corrected[:start] + replacement + corrected[end:]
                        changes.append({
                            "original": original_str,
                            "corrected": replacement,
                            "domain_term": canonical_term
                        })

        return corrected, changes
