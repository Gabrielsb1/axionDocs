#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema RAG (Retrieval-Augmented Generation) para documentos de matrícula
- Vetorização de documentos usando embeddings
- Busca semântica por similaridade
- Geração de respostas contextuais
"""

import os
import json
import sqlite3
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from sentence_transformers import SentenceTransformer
import faiss
import pickle

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("RAGSystem")

class RAGSystem:
    """Sistema RAG para documentos de matrícula imobiliária"""
    
    def __init__(self, db_path: str = "rag_database.db", model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.db_path = db_path
        self.model_name = model_name
        self.embedding_model = None
        self.index = None
        self.document_store = {}
        self.dimension = 384  # Dimensão do modelo multilingual
        
        # Inicializar componentes
        self._init_database()
        self._load_embedding_model()
        self._load_or_create_index()
    
    def _init_database(self):
        """Inicializa banco de dados SQLite para metadados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de documentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                extracted_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de chunks (fragmentos de texto)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_text TEXT NOT NULL,
                chunk_index INTEGER,
                embedding BLOB,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados inicializado")
    
    def _load_embedding_model(self):
        """Carrega modelo de embeddings"""
        try:
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info(f"Modelo de embeddings carregado: {self.model_name}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de embeddings: {e}")
            raise
    
    def _load_or_create_index(self):
        """Carrega ou cria índice FAISS"""
        index_path = "faiss_index.pkl"
        
        if os.path.exists(index_path):
            try:
                with open(index_path, 'rb') as f:
                    self.index = pickle.load(f)
                logger.info("Índice FAISS carregado")
            except Exception as e:
                logger.warning(f"Erro ao carregar índice: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Cria novo índice FAISS"""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product para similaridade coseno
        logger.info("Novo índice FAISS criado")
    
    def _save_index(self):
        """Salva índice FAISS"""
        try:
            with open("faiss_index.pkl", 'wb') as f:
                pickle.dump(self.index, f)
            logger.info("Índice FAISS salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar índice: {e}")
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Divide texto em chunks sobrepostos"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Tenta quebrar em ponto final ou quebra de linha
            if end < len(text):
                for i in range(end, max(start + chunk_size // 2, end - 50), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def add_document(self, filename: str, content: str, extracted_info: Dict[str, Any] = None) -> int:
        """Adiciona documento ao sistema RAG"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Inserir documento
        cursor.execute('''
            INSERT INTO documents (filename, content, extracted_info)
            VALUES (?, ?, ?)
        ''', (filename, content, json.dumps(extracted_info) if extracted_info else None))
        
        document_id = cursor.lastrowid
        
        # Processar chunks
        chunks = self._chunk_text(content)
        embeddings = self.embedding_model.encode(chunks)
        
        # Normalizar embeddings para similaridade coseno
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Adicionar chunks ao banco e índice
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            cursor.execute('''
                INSERT INTO chunks (document_id, chunk_text, chunk_index, embedding, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, chunk, i, embedding.tobytes(), json.dumps({"chunk_size": len(chunk)})))
            
            # Adicionar ao índice FAISS
            self.index.add(embedding.reshape(1, -1))
        
        conn.commit()
        conn.close()
        
        # Salvar índice
        self._save_index()
        
        logger.info(f"Documento adicionado: {filename} ({len(chunks)} chunks)")
        return document_id
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos relevantes para a query"""
        if self.index.ntotal == 0:
            return []
        
        # Gerar embedding da query
        query_embedding = self.embedding_model.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        
        # Buscar no índice FAISS
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Recuperar chunks do banco
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # Índice inválido
                continue
                
            cursor.execute('''
                SELECT c.chunk_text, c.metadata, d.filename, d.extracted_info
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                WHERE c.id = ?
            ''', (int(idx) + 1,))  # FAISS usa índices 0-based, SQLite usa 1-based
            
            row = cursor.fetchone()
            if row:
                chunk_text, metadata, filename, extracted_info = row
                results.append({
                    'chunk_text': chunk_text,
                    'score': float(score),
                    'filename': filename,
                    'metadata': json.loads(metadata) if metadata else {},
                    'extracted_info': json.loads(extracted_info) if extracted_info else {}
                })
        
        conn.close()
        return results
    
    def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """Obtém contexto relevante para uma query"""
        results = self.search(query, top_k=3)
        
        if not results:
            return "Nenhum documento relevante encontrado."
        
        context_parts = []
        current_length = 0
        
        for result in results:
            chunk = result['chunk_text']
            if current_length + len(chunk) <= max_context_length:
                context_parts.append(f"[{result['filename']}] {chunk}")
                current_length += len(chunk)
            else:
                # Adicionar parte do chunk se ainda couber
                remaining = max_context_length - current_length
                if remaining > 100:  # Só adiciona se sobrar espaço significativo
                    context_parts.append(f"[{result['filename']}] {chunk[:remaining]}...")
                break
        
        return "\n\n".join(context_parts)
    
    def get_document_count(self) -> int:
        """Retorna número de documentos no sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retorna lista de todos os documentos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, filename, created_at, extracted_info
            FROM documents
            ORDER BY created_at DESC
        ''')
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                'id': row[0],
                'filename': row[1],
                'created_at': row[2],
                'extracted_info': json.loads(row[3]) if row[3] else {}
            })
        
        conn.close()
        return documents
    
    def delete_document(self, document_id: int) -> bool:
        """Remove documento do sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obter chunks do documento
            cursor.execute("SELECT id FROM chunks WHERE document_id = ?", (document_id,))
            chunk_ids = [row[0] for row in cursor.fetchall()]
            
            # Remover do índice FAISS (reconstruir índice)
            if chunk_ids:
                self._rebuild_index_excluding_chunks(chunk_ids)
            
            # Remover do banco
            cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Documento {document_id} removido")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover documento: {e}")
            return False
    
    def _rebuild_index_excluding_chunks(self, exclude_chunk_ids: List[int]):
        """Reconstrói índice FAISS excluindo chunks específicos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obter todos os chunks exceto os excluídos
        placeholders = ','.join(['?' for _ in exclude_chunk_ids])
        cursor.execute(f'''
            SELECT embedding FROM chunks 
            WHERE id NOT IN ({placeholders})
            ORDER BY id
        ''', exclude_chunk_ids)
        
        embeddings = []
        for row in cursor.fetchall():
            embedding = np.frombuffer(row[0], dtype=np.float32)
            embeddings.append(embedding)
        
        conn.close()
        
        if embeddings:
            # Recriar índice
            self.index = faiss.IndexFlatIP(self.dimension)
            embeddings_array = np.vstack(embeddings)
            self.index.add(embeddings_array)
            self._save_index()
        else:
            # Índice vazio
            self.index = faiss.IndexFlatIP(self.dimension)
            self._save_index()
    
    def clear_all(self):
        """Remove todos os documentos do sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks")
        cursor.execute("DELETE FROM documents")
        conn.commit()
        conn.close()
        
        # Recriar índice vazio
        self.index = faiss.IndexFlatIP(self.dimension)
        self._save_index()
        
        logger.info("Todos os documentos removidos")
