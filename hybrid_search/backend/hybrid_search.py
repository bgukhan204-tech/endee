import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import pandas as pd
from typing import List, Dict

class HybridSearchEngine:
    def __init__(self, documents: List[Dict]):
        self.documents = documents
        self.texts = [doc['title'] + ". " + doc['text'] for doc in self.documents]
        
        # Initialize Dense Model
        self.dense_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = self.dense_model.encode(self.texts)
        
        # Initialize Sparse Model (BM25)
        tokenized_corpus = [doc.lower().split() for doc in self.texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def dense_search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.dense_model.encode(query)
        # Calculate cosine similarity using dot product since embeddings are normalized by default in many models, 
        # or use standard cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding))
        
        top_k_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_k_indices:
            result = self.documents[idx].copy()
            result['dense_score'] = float(similarities[idx])
            results.append(result)
        return results

    def sparse_search(self, query: str, top_k: int = 5) -> List[Dict]:
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        top_k_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_k_indices:
            result = self.documents[idx].copy()
            result['sparse_score'] = float(scores[idx])
            results.append(result)
        return results

    def reciprocal_rank_fusion(self, dense_results: List[Dict], sparse_results: List[Dict], k: int = 60) -> List[Dict]:
        """
        Combines ranks from dense and sparse search using Reciprocal Rank Fusion.
        Score = 1 / (k + rank)
        """
        rrf_scores = {doc['id']: 0.0 for doc in self.documents}
        
        # Process dense results
        for rank, doc in enumerate(dense_results):
            rrf_scores[doc['id']] += 1.0 / (k + rank + 1)
            
        # Process sparse results
        for rank, doc in enumerate(sparse_results):
            rrf_scores[doc['id']] += 1.0 / (k + rank + 1)
            
        # Sort by RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        # Build final results
        final_results = []
        for doc_id in sorted_ids:
            if rrf_scores[doc_id] > 0:
                doc = next(d for d in self.documents if d['id'] == doc_id).copy()
                doc['rrf_score'] = rrf_scores[doc_id]
                final_results.append(doc)
                
        return final_results

    def search(self, query: str, top_k: int = 5) -> Dict:
        """Runs both searches and combines them using RRF."""
        dense_res = self.dense_search(query, top_k=len(self.documents)) # Need to pass all for fair RRF
        sparse_res = self.sparse_search(query, top_k=len(self.documents))
        
        hybrid_res = self.reciprocal_rank_fusion(dense_res, sparse_res)[:top_k]
        
        return {
            "query": query,
            "dense": dense_res[:top_k],
            "sparse": sparse_res[:top_k],
            "hybrid": hybrid_res
        }
