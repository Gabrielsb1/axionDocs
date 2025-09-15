#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente RAG que integra busca semântica com geração de respostas
Usa o sistema RAG para encontrar contexto relevante e Ollama para gerar respostas
"""

import logging
from typing import Dict, Any, List, Optional
from rag_system import RAGSystem
from ollama_client import OllamaClient

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("RAGClient")

class RAGClient:
    """Cliente RAG que combina busca semântica com geração de respostas"""
    
    def __init__(self, rag_system: RAGSystem = None, ollama_client: OllamaClient = None):
        self.rag_system = rag_system or RAGSystem()
        self.ollama_client = ollama_client or OllamaClient()
        
        # Templates de prompt para diferentes tipos de perguntas
        self.prompt_templates = {
            "geral": """
Você é um assistente especializado em documentos de matrícula imobiliária. 
Use o contexto fornecido para responder à pergunta de forma precisa e útil.

CONTEXTO:
{context}

PERGUNTA: {question}

INSTRUÇÕES:
- Responda baseado APENAS no contexto fornecido
- Se a informação não estiver no contexto, diga "Não encontrei essa informação nos documentos"
- Seja específico e cite os documentos quando relevante
- Use linguagem clara e profissional
- Se houver números ou dados específicos, mencione-os exatamente como aparecem

RESPOSTA:""",

            "numeros": """
Você é um assistente especializado em extrair números e dados específicos de matrículas imobiliárias.

CONTEXTO:
{context}

PERGUNTA: {question}

INSTRUÇÕES:
- Extraia APENAS os números e dados que estão no contexto
- Se não encontrar o número solicitado, diga "Número não encontrado"
- Cite o documento de origem quando possível
- Seja preciso com os valores

RESPOSTA:""",

            "areas": """
Você é um especialista em áreas de imóveis. Analise o contexto para responder sobre áreas específicas.

CONTEXTO:
{context}

PERGUNTA: {question}

INSTRUÇÕES:
- Foque em informações sobre áreas (privativa, comum, total, etc.)
- Mencione unidades de medida (m², etc.)
- Se não encontrar informações sobre áreas, diga "Informações de área não encontradas"
- Cite o documento quando relevante

RESPOSTA:""",

            "proprietario": """
Você é um assistente para informações sobre proprietários de imóveis.

CONTEXTO:
{context}

PERGUNTA: {question}

INSTRUÇÕES:
- Extraia informações sobre proprietários, CPF, endereços
- Se não encontrar informações do proprietário, diga "Informações do proprietário não encontradas"
- Seja cuidadoso com dados pessoais
- Cite o documento de origem

RESPOSTA:"""
        }
    
    def add_document(self, filename: str, content: str, extracted_info: Dict[str, Any] = None) -> int:
        """Adiciona documento ao sistema RAG"""
        return self.rag_system.add_document(filename, content, extracted_info)
    
    def ask_question(self, question: str, question_type: str = "geral", max_context: int = 2000) -> Dict[str, Any]:
        """Faz uma pergunta ao sistema RAG"""
        try:
            # Buscar contexto relevante
            context = self.rag_system.get_context_for_query(question, max_context)
            
            if not context or context == "Nenhum documento relevante encontrado.":
                return {
                    "answer": "Não encontrei documentos relevantes para responder sua pergunta. Certifique-se de que há documentos processados no sistema.",
                    "context": "",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Escolher template de prompt
            template = self.prompt_templates.get(question_type, self.prompt_templates["geral"])
            prompt = template.format(context=context, question=question)
            
            # Gerar resposta com Ollama
            answer = self.ollama_client.generate_response(prompt)
            
            # Obter fontes dos resultados de busca
            search_results = self.rag_system.search(question, top_k=3)
            sources = [{"filename": r["filename"], "score": r["score"]} for r in search_results]
            
            # Calcular confiança baseada nos scores de similaridade
            confidence = min(1.0, max(0.0, sum(r["score"] for r in search_results) / len(search_results))) if search_results else 0.0
            
            return {
                "answer": answer.strip(),
                "context": context,
                "sources": sources,
                "confidence": confidence,
                "question_type": question_type
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            return {
                "answer": f"Erro ao processar sua pergunta: {str(e)}",
                "context": "",
                "sources": [],
                "confidence": 0.0
            }
    
    def get_suggested_questions(self) -> List[str]:
        """Retorna lista de perguntas sugeridas baseadas nos documentos"""
        questions = [
            "Qual é o número da matrícula?",
            "Quem é o proprietário do imóvel?",
            "Qual é a área privativa do imóvel?",
            "Qual é a área total do imóvel?",
            "Qual é o número da inscrição imobiliária?",
            "O imóvel tem vaga de garagem?",
            "Qual é a área de uso comum?",
            "Qual é o endereço do imóvel?",
            "Há alguma restrição no imóvel?",
            "Qual é o valor do imóvel?"
        ]
        return questions
    
    def get_document_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos documentos no sistema"""
        documents = self.rag_system.get_all_documents()
        total_docs = len(documents)
        
        # Extrair informações comuns dos documentos
        all_matriculas = []
        all_areas = []
        all_proprietarios = []
        
        for doc in documents:
            extracted_info = doc.get('extracted_info', {})
            
            if extracted_info.get('numero_matricula'):
                all_matriculas.append(extracted_info['numero_matricula'])
            
            if extracted_info.get('areas'):
                areas = extracted_info['areas']
                for area_type, area_value in areas.items():
                    if area_value and str(area_value).strip():
                        all_areas.append(f"{area_type}: {area_value}")
            
            # Aqui você poderia extrair proprietários se tivesse essa informação
        
        return {
            "total_documents": total_docs,
            "matriculas": list(set(all_matriculas)),
            "areas_encontradas": all_areas[:10],  # Limitar a 10
            "recent_documents": documents[:5]  # 5 mais recentes
        }
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos sem gerar resposta"""
        return self.rag_system.search(query, top_k)
    
    def get_document_count(self) -> int:
        """Retorna número de documentos"""
        return self.rag_system.get_document_count()
    
    def clear_all_documents(self):
        """Remove todos os documentos"""
        self.rag_system.clear_all()
        logger.info("Todos os documentos removidos do sistema RAG")
    
    def delete_document(self, document_id: int) -> bool:
        """Remove documento específico"""
        return self.rag_system.delete_document(document_id)
