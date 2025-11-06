import json
from typing import Optional, Dict, List
from pathlib import Path


class GuidelineDatabase:
    """Medical guidelines database with file-based storage"""
    
    def __init__(self, base_path: str = "data/guidelines"):
        self.base_path = Path(base_path)
        self._guidelines_cache = {}
        self._load_all_guidelines()
    
    def _load_all_guidelines(self):
        """Load all guidelines into memory cache"""
        if not self.base_path.exists():
            print(f"WARNING: Guidelines directory not found: {self.base_path}")
            print("Run 'python scripts/setup_data.py' to create sample guidelines")
            return
        
        for category_dir in self.base_path.iterdir():
            if category_dir.is_dir():
                category = category_dir.name
                self._guidelines_cache[category] = {}
                
                for guideline_file in category_dir.glob("*.json"):
                    try:
                        with open(guideline_file, 'r') as f:
                            guideline_data = json.load(f)
                            guideline_id = guideline_data.get('id', guideline_file.stem)
                            self._guidelines_cache[category][guideline_id] = guideline_data
                    except Exception as e:
                        print(f"Error loading {guideline_file}: {e}")
        
        total_guidelines = sum(len(g) for g in self._guidelines_cache.values())
        print(f"Loaded {total_guidelines} guidelines across {len(self._guidelines_cache)} categories")
    
    def search(self, query: str, section: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
        """
        Search guidelines by query string
        
        Args:
            query: Search terms
            section: Specific section to search (diagnosis, treatment, monitoring, drug-dosing)
            category: Specific category (cardiology, diabetes, hypertension)
        
        Returns:
            List of matching guideline snippets
        """
        results = []
        query_lower = query.lower()
        
        # Determine which categories to search
        categories_to_search = [category] if category else self._guidelines_cache.keys()
        
        for cat in categories_to_search:
            if cat not in self._guidelines_cache:
                continue
            
            for guideline_id, guideline in self._guidelines_cache[cat].items():
                # Search in sections
                sections_to_search = guideline.get('sections', {})
                
                if section and section in sections_to_search:
                    # Search specific section only
                    sections_to_search = {section: sections_to_search[section]}
                
                for section_name, section_data in sections_to_search.items():
                    # Extract content
                    content = section_data.get('content', '')
                    key_points = section_data.get('key_points', [])
                    
                    # Simple keyword matching
                    content_lower = content.lower()
                    key_points_text = ' '.join(key_points).lower()
                    
                    # Check if query terms appear in content
                    query_terms = query_lower.split()
                    matches = sum(1 for term in query_terms if term in content_lower or term in key_points_text)
                    
                    if matches > 0:
                        # Calculate simple relevance score
                        relevance = matches / len(query_terms)
                        
                        results.append({
                            "guideline_id": guideline_id,
                            "title": guideline.get('title', ''),
                            "organization": guideline.get('organization', ''),
                            "year": guideline.get('year', ''),
                            "section": section_name,
                            "content": content,
                            "key_points": key_points,
                            "relevance": relevance,
                            "references": guideline.get('references', [])
                        })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results[:5]  # Return top 5 results


# Global instance
_guideline_db = None

def get_guideline_database() -> GuidelineDatabase:
    """Get or create guideline database singleton"""
    global _guideline_db
    if _guideline_db is None:
        _guideline_db = GuidelineDatabase()
    return _guideline_db


def search_guidelines(query: str, section: Optional[str] = None) -> Dict[str, List[Dict]]:
    """
    Search vetted clinical guidelines
    
    Args:
        query: Search query
        section: Specific section (diagnosis, treatment, monitoring, drug-dosing)
    
    Returns:
        Dictionary with hits containing guideline snippets
    """
    db = get_guideline_database()
    results = db.search(query, section=section)
    
    # Format results
    hits = []
    for result in results:
        hit = {
            "id": result['guideline_id'],
            "title": result['title'],
            "organization": result['organization'],
            "year": result['year'],
            "section": result['section'],
            "snippet": result['content'][:300] + "..." if len(result['content']) > 300 else result['content'],
            "key_points": result['key_points'][:3],  # Top 3 key points
            "relevance": f"{result['relevance']:.2f}"
        }
        hits.append(hit)
    
    return {"hits": hits, "total": len(hits)}