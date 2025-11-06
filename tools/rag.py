import json
from typing import Dict, List
from pathlib import Path
import numpy as np


class MedicalCorpus:
    """Medical literature corpus with simple TF-IDF search"""
    
    def __init__(self, corpus_path: str = "data/rag_corpus/medical_literature.jsonl"):
        self.corpus_path = Path(corpus_path)
        self.documents = []
        self._load_corpus()
    
    def _load_corpus(self):
        """Load medical literature corpus"""
        if not self.corpus_path.exists():
            print(f"WARNING: Corpus file not found: {self.corpus_path}")
            print("Run 'python scripts/setup_data.py' to create sample corpus")
            return
        
        with open(self.corpus_path, 'r') as f:
            for line in f:
                if line.strip():
                    doc = json.loads(line)
                    self.documents.append(doc)
        
        print(f"Loaded {len(self.documents)} documents from medical corpus")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search corpus using simple keyword matching
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of relevant documents with scores
        """
        if not self.documents:
            return []
        
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        # Score each document
        scored_docs = []
        for doc in self.documents:
            # Create searchable text from document
            searchable_text = ' '.join([
                doc.get('title', ''),
                doc.get('abstract', ''),
                ' '.join(doc.get('keywords', [])),
                ' '.join(doc.get('key_findings', []))
            ]).lower()
            
            # Simple keyword scoring
            matches = sum(1 for term in query_terms if term in searchable_text)
            
            # Boost score if terms appear in title or key findings
            title_matches = sum(1 for term in query_terms if term in doc.get('title', '').lower())
            
            score = matches + (title_matches * 2)  # Weight title matches higher
            
            if score > 0:
                scored_docs.append({
                    'document': doc,
                    'score': score
                })
        
        # Sort by score
        scored_docs.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top k
        results = []
        for item in scored_docs[:k]:
            doc = item['document']
            results.append({
                "id": doc.get('id', ''),
                "title": doc.get('title', ''),
                "abstract": doc.get('abstract', ''),
                "journal": doc.get('journal', ''),
                "year": doc.get('year', ''),
                "key_findings": doc.get('key_findings', []),
                "relevance": min(item['score'] / len(query_terms), 1.0)  # Normalize score
            })
        
        return results


# Global instance
_medical_corpus = None

def get_medical_corpus() -> MedicalCorpus:
    """Get or create medical corpus singleton"""
    global _medical_corpus
    if _medical_corpus is None:
        _medical_corpus = MedicalCorpus()
    return _medical_corpus


def retrieve_rag(query: str, k: int = 5) -> Dict[str, List[Dict]]:
    """
    Retrieve top-k passages from medical corpus using RAG
    
    Args:
        query: Search query
        k: Number of passages to retrieve
    
    Returns:
        Dictionary with relevant passages
    """
    corpus = get_medical_corpus()
    results = corpus.search(query, k=k)
    
    # Format passages
    passages = []
    for result in results:
        passage = {
            "id": result['id'],
            "title": result['title'],
            "text": result['abstract'],
            "source": f"{result['journal']} {result['year']}",
            "key_findings": result['key_findings'][:3],  # Top 3 findings
            "relevance": f"{result['relevance']:.2f}"
        }
        passages.append(passage)
    
    return {"passages": passages, "total": len(passages)}