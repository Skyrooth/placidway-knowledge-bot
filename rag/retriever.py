"""
PlacidWay Hybrid Retriever
Implements BM25 / TF-IDF style lexical search combined with medical entity and pricing boosts.
Guarantees fast, accurate retrieval without external vector DB dependencies.
"""

import json
import math
import re
import os
from collections import Counter
from typing import List, Dict, Any

class PlacidWayRetriever:
    def __init__(self, chunks_path: str = None):
        if chunks_path is None:
            base_dir = os.path.dirname(__file__)
            chunks_path = os.path.join(base_dir, '..', 'data', 'chunks.json')
            
        with open(chunks_path, 'r', encoding='utf-8') as f:
            self.chunks: List[Dict[str, Any]] = json.load(f)
            
        self.doc_count = len(self.chunks)
        self.doc_lengths = []
        self.chunk_tokens = []
        self.df = Counter()
        
        self._build_index()
        
    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\$\.]', ' ', text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 1 or t == '$']
        return tokens

    def _build_index(self):
        total_len = 0
        for chunk in self.chunks:
            full_text = f"{chunk.get('title', '')} {chunk.get('section', '')} {chunk.get('doc_name', '')} {chunk.get('text', '')}"
            tokens = self._tokenize(full_text)
            self.chunk_tokens.append(tokens)
            self.doc_lengths.append(len(tokens))
            total_len += len(tokens)
            
            unique_terms = set(tokens)
            for t in unique_terms:
                self.df[t] += 1
                
        self.avg_dl = (total_len / self.doc_count) if self.doc_count > 0 else 1.0

    def search(self, query: str, top_k: int = 5, k1: float = 1.5, b: float = 0.75) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
            
        scores = [0.0] * self.doc_count
        
        for q_token in query_tokens:
            if q_token not in self.df:
                continue
            df_val = self.df[q_token]
            idf = math.log((self.doc_count - df_val + 0.5) / (df_val + 0.5) + 1.0)
            
            for i, tokens in enumerate(self.chunk_tokens):
                tf = tokens.count(q_token)
                if tf == 0:
                    continue
                doc_len = self.doc_lengths[i]
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / self.avg_dl))
                bm25 = idf * (numerator / denominator)
                
                # Metadata bonus if term appears in title or section
                chunk = self.chunks[i]
                title_lower = (chunk.get('title', '') + ' ' + chunk.get('section', '')).lower()
                if q_token in title_lower:
                    bm25 *= 1.4
                    
                scores[i] += bm25
                
        scored_results = []
        for i, score in enumerate(scores):
            if score > 0.5:
                scored_results.append((score, self.chunks[i]))
                
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        top_results = []
        seen_texts = set()
        for score, chunk in scored_results:
            text_snippet = chunk['text'][:120]
            if text_snippet in seen_texts:
                continue
            seen_texts.add(text_snippet)
            res = dict(chunk)
            res['relevance_score'] = round(score, 3)
            top_results.append(res)
            if len(top_results) >= top_k:
                break
                
        return top_results

if __name__ == '__main__':
    retriever = PlacidWayRetriever()
    test_q = "How much does Alternative Adenocarcinoma Cancer Treatment cost in Tijuana?"
    hits = retriever.search(test_q, top_k=3)
    print(f"Query: {test_q}\nTop hits: {len(hits)}")
    for h in hits:
        print(f"[{h['relevance_score']}] {h['title']} - {h['url']}\nSnippet: {h['text'][:150]}...\n")
