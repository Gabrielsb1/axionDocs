import requests
import json
import re
from typing import Dict, Any

class OllamaClient:
    """Classe para interagir com o modelo Ollama mistral:7b"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral:7b"
    
    def generate_response(self, prompt: str) -> str:
        """Gera resposta do modelo Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model, 
                "prompt": prompt, 
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Reduz criatividade para respostas mais consistentes
                    "top_p": 0.9,        # Foca nas respostas mais prováveis
                    "num_predict": 1000  # Limita tamanho da resposta para ser mais rápido
                }
            }
            response = requests.post(url, json=payload, timeout=120)  # Reduz timeout
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na comunicação com Ollama: {str(e)}")
    
    def extract_matricula_info(self, pdf_text: str) -> Dict[str, Any]:
        """Extrai informações específicas de matrícula usando IA"""
        
        prompt = f"""Extraia informações da matrícula em JSON:

TEXTO: {pdf_text[:2000]}...

Extraia:
1. numero_matricula: CNM, Matrícula N, Registro Geral (apenas dígitos finais)
2. descricao_imovel_completa: descrição completa do imóvel
3. areas: áreas mencionadas (privativa, comum, total, etc.)
4. inscricao_imobiliaria: número da inscrição

JSON:
{{"numero_matricula": "", "descricao_imovel_completa": "", "areas": {{}}, "inscricao_imobiliaria": ""}}"""
        
        try:
            response = self.generate_response(prompt)
            
            # Tenta extrair JSON da resposta
            try:
                clean_response = response.replace('```json', '').replace('```', '').strip()
                start_idx = clean_response.find('{')
                if start_idx != -1:
                    # Encontrar o final do JSON
                    brace_count = 0
                    end_idx = start_idx
                    for i, char in enumerate(clean_response[start_idx:], start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    if end_idx > start_idx:
                        json_str = clean_response[start_idx:end_idx]
                        parsed_json = json.loads(json_str)
                        return parsed_json
            except json.JSONDecodeError:
                pass
            
            # Fallback manual: regex para CNM, Matrícula, Registro Geral, Inscrição Imobiliária e áreas
            numero_matricula = self._extract_matricula(pdf_text)
            inscricao_imobiliaria = self._extract_inscricao(pdf_text)
            areas = self._extract_areas(pdf_text)
            descricao = pdf_text.strip().replace('\n', ' ')
            
            return {
                "numero_matricula": numero_matricula,
                "descricao_imovel_completa": descricao,
                "areas": areas,
                "inscricao_imobiliaria": inscricao_imobiliaria
            }
            
        except Exception as e:
            raise Exception(f"Erro ao extrair informações: {str(e)}")
    
    def _extract_matricula(self, text: str) -> str:
        # Padrões comuns de matrícula
        patterns = [
            r"CNM\d+.\d+.(\d+)-\d+",
            r"MATRICULA N\.?\s*(\d+)",
            r"REGISTRO GERAL\s*(\d+)"
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def _extract_inscricao(self, text: str) -> str:
        match = re.search(r"INSCRIÇÃO IMOBILIÁRIA[:\s]*([\d]+)", text, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _extract_areas(self, text: str) -> Dict[str, str]:
        areas = {}
        # Padrões básicos para áreas
        area_patterns = {
            "privativa_real": r"área privativa real de\s*([\d.,]+m\??)",
            "privativa_acessoria": r"área privativa acessória .*?de\s*([\d.,]+m\??)",
            "uso_comum": r"área de uso comum .*?de\s*([\d.,]+m\??)",
            "total_real": r"área total real .*?de\s*([\d.,]+m\??)",
            "equivalente_construcao": r"área equivalente .*?igual a\s*([\d.,]+m\??)",
            "vaga_garagem": r"vaga de garagem .*?de\s*([\d.,]+m\??)"
        }
        for key, pat in area_patterns.items():
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                areas[key] = match.group(1)
            else:
                areas[key] = ""
        return areas