"""
PlacidWay Semantic Chunker
Breaks down crawled documents into semantically coherent chunks with rich metadata
(page title, source URL, page type, section heading) for precise retrieval and source attribution.
"""

import json
import re
import os

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80):
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    
    current_chunk = []
    current_len = 0
    
    for p in paragraphs:
        p_len = len(p.split())
        if current_len + p_len <= chunk_size:
            current_chunk.append(p)
            current_len += p_len
        else:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [p]
            current_len = p_len
            
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
        
    return chunks

def build_chunked_index(knowledge_base_path: str, output_chunks_path: str):
    if not os.path.exists(knowledge_base_path):
        raise FileNotFoundError(f"Knowledge base not found at {knowledge_base_path}")
        
    with open(knowledge_base_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    all_chunks = []
    chunk_id = 0
    
    for doc_key, doc in data.items():
        raw_text = doc.get('content', '')
        url = doc.get('url', '')
        title = doc.get('title', '')
        page_type = doc.get('type', '')
        name = doc.get('name', '')
        
        # Split into sections based on typical headers
        sections = re.split(r'\n(?=[A-Z0-9][A-Za-z0-9\s\:\-\?]{3,50}\n)', raw_text)
        
        for sec in sections:
            sec_lines = [l.strip() for l in sec.splitlines() if l.strip()]
            if not sec_lines:
                continue
            section_title = sec_lines[0] if len(sec_lines[0]) < 80 else "General Information"
            sec_body = '\n'.join(sec_lines)
            
            sub_chunks = chunk_text(sec_body, chunk_size=350, overlap=50)
            for sc in sub_chunks:
                chunk_id += 1
                all_chunks.append({
                    'chunk_id': chunk_id,
                    'doc_key': doc_key,
                    'doc_name': name,
                    'page_type': page_type,
                    'title': title,
                    'url': url,
                    'section': section_title,
                    'text': sc
                })
                
    os.makedirs(os.path.dirname(output_chunks_path), exist_ok=True)
    with open(output_chunks_path, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated {len(all_chunks)} semantic chunks from {len(data)} documents.")
    return all_chunks

if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)
    kb_path = os.path.join(base_dir, '..', 'data', 'knowledge_base.json')
    chunks_path = os.path.join(base_dir, '..', 'data', 'chunks.json')
    build_chunked_index(kb_path, chunks_path)
