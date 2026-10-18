import ast
import os

import chromadb
import requests

from config import WORKSPACE, CHROMA_DIR, EMBED_MODEL, EMBED_URL, get_headers
from tools.fs import SKIP_DIRS

def iter_py_files():
        found = []
        for dirpath,dirnames,filenames in os.walk(WORKSPACE):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for name in filenames:
                        if name.endswith('.py'):
                                full =os.path.join(dirpath,name)
                                found.append(os.path.relpath(full,WORKSPACE).replace('\\','/'))
        return sorted(found)
def split_functions(source,rel):
        tree = ast.parse(source,rel)
        chunks = []
        for node in tree.body:
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                        seg = ast.get_source_segment(source,node)
                        if not seg:
                                continue
                        chunks.append({
                                'text': f'# {rel} · 函数 {node.name}\n{seg}',
                                'rel':rel,
                                'name': node.name,
                                'line': node.lineno,
                        }
                        )
        if not chunks and source.strip():
                chunks.append({'text': source, 'rel': rel, 'name': '(整个文件)', 'line': 1})
        return chunks
def collect_chunks():
        all_chunks = []
        for rel in iter_py_files():
                full = os.path.join(WORKSPACE,rel)
                with open(full,encoding='utf-8') as f:
                        source = f.read()
                try:
                        all_chunks.extend(split_functions(source,rel))
                except SyntaxError as e:
                        print(f'跳过{rel}:语法错误{e.msg}')
        return all_chunks
def embed(texts):
        data = {'model':EMBED_MODEL,'input':texts}
        resp = requests.post(EMBED_URL,json=data,headers=get_headers(),timeout=120)
        if resp.status_code != 200:
                raise RuntimeError(f'嵌入失败{resp.status_code}{resp.text[:200]}')
        items = sorted(resp.json()['data'], key=lambda d:d['index'])
        return [d['embedding'] for d in items]
def build_embed():
        chunks = collect_chunks()
        if not chunks:
                return 0
        texts = [c['text'] for c in chunks]
        vectors = embed(texts)
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        try:
                client.delete_collection('code_chunks')
        except Exception:
                pass
        col = client.get_or_create_collection(
                'code_chunks',
                embedding_function=None,
                metadata={'hnsw:space':'cosine'}
        )
        col.add(
                ids = [f"{c['rel']}:{c['line']}:{c['name']}" for c in chunks],
                documents=texts,
                embeddings=vectors,
                metadatas=[{'rel':c['rel'],'name':c['name'],'line':c['line']} for c in chunks],
        )
        return len(chunks)
def search_codebase(query,k=3):
        vector = embed([query])[0]
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        col = client.get_collection('code_chunks',embedding_function=None)
        res = col.query(query_embeddings=[vector],n_results=k)

        lines = []
        for i ,meta in enumerate(res['metadatas'][0]):
                sim = 1 -res['distances'][0][i]
                code = res['documents'][0][i]
                lines.append(f"[{i+1}]{meta['rel']}:{meta['name']}:{meta['line']} 相似度{sim:.4f}\n"
                             f"{code[:600]}")
        return '\n'.join(lines)
if __name__ == '__main__':
    n = build_embed()
    print(f'索引完成，一共 {n} 块\n')

    for q in ['怎么把一堆数加起来然后除以它们的个数',
              '两个数字相除',
              '验证平均数算得对不对']:
        print('问：', q)
        print(search_codebase(q))
        print('-' * 45)


































































