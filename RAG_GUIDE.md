# 🤖 Guia do Sistema RAG (Retrieval-Augmented Generation)

## O que é RAG?

RAG (Retrieval-Augmented Generation) é uma técnica que combina:
- **Retrieval (Busca)**: Encontra informações relevantes em documentos
- **Augmented Generation (Geração Aumentada)**: Usa essas informações para gerar respostas mais precisas

## Como Funciona no axionDocs

### 1. **Processamento de Documentos**
- Upload de PDFs de matrícula
- Extração de texto com OCR
- Análise com IA para extrair informações estruturadas
- **Adição ao sistema RAG** para busca semântica

### 2. **Sistema de Busca Semântica**
- Cada documento é dividido em "chunks" (fragmentos)
- Cada chunk é convertido em vetores (embeddings)
- Busca por similaridade semântica usando FAISS
- Banco de dados SQLite para metadados

### 3. **Geração de Respostas**
- Pergunta do usuário é convertida em vetor
- Sistema encontra chunks mais relevantes
- Contexto é enviado para o Ollama (Mistral 7B)
- Resposta é gerada baseada no contexto encontrado

## Funcionalidades

### 📄 **Aba "Processar PDF"**
- Upload e processamento de PDFs
- Extração de informações com IA
- **Novo**: Botão "Adicionar ao RAG" para incluir no sistema de busca

### 🤖 **Aba "Perguntas RAG"**
- Sistema de perguntas e respostas inteligente
- Perguntas sugeridas baseadas no tipo de documento
- Diferentes tipos de pergunta:
  - **Geral**: Perguntas amplas sobre o documento
  - **Números**: Foco em dados numéricos e matrículas
  - **Áreas**: Informações sobre áreas do imóvel
  - **Proprietário**: Dados do proprietário

### 📊 **Aba "Documentos"**
- Visualização de todos os documentos no sistema
- Estatísticas do sistema RAG
- Gerenciamento (remover documentos individuais ou todos)

## Exemplos de Perguntas

### Perguntas sobre Números:
- "Qual é o número da matrícula?"
- "Qual é a inscrição imobiliária?"
- "Qual é o valor do imóvel?"

### Perguntas sobre Áreas:
- "Qual é a área privativa do imóvel?"
- "O imóvel tem vaga de garagem?"
- "Qual é a área total construída?"

### Perguntas Gerais:
- "Quem é o proprietário do imóvel?"
- "Qual é o endereço completo?"
- "Há alguma restrição no imóvel?"

## Instalação das Dependências

```bash
pip install -r requirements.txt
```

### Dependências RAG:
- `sentence-transformers`: Para gerar embeddings de texto
- `faiss-cpu`: Para busca vetorial eficiente
- `numpy`: Para operações matemáticas

## Arquivos do Sistema RAG

### `rag_system.py`
- Classe principal do sistema RAG
- Gerenciamento de embeddings e busca vetorial
- Banco de dados SQLite para metadados
- Índice FAISS para busca rápida

### `rag_client.py`
- Interface entre o sistema RAG e o Ollama
- Templates de prompt para diferentes tipos de pergunta
- Geração de respostas contextuais

### `app.py` (atualizado)
- Interface Streamlit com 3 abas
- Integração completa do sistema RAG
- Gerenciamento de documentos

## Banco de Dados

O sistema cria automaticamente:
- `rag_database.db`: Banco SQLite com metadados
- `faiss_index.pkl`: Índice vetorial para busca rápida

## Vantagens do RAG

1. **Precisão**: Respostas baseadas em documentos reais
2. **Contexto**: Sistema entende o significado, não apenas palavras-chave
3. **Escalabilidade**: Funciona com muitos documentos
4. **Transparência**: Mostra fontes e contexto usado
5. **Flexibilidade**: Diferentes tipos de pergunta

## Limitações

1. **Dependência de Documentos**: Precisa de documentos processados
2. **Qualidade do OCR**: Depende da qualidade da extração de texto
3. **Modelo de Embeddings**: Usa modelo multilíngue (português/inglês)
4. **Contexto Limitado**: Respostas baseadas em chunks encontrados

## Dicas de Uso

1. **Processe vários documentos** para ter mais contexto
2. **Use perguntas específicas** para melhores resultados
3. **Verifique a confiança** das respostas
4. **Consulte as fontes** para validar informações
5. **Use o contexto expandível** para entender como a resposta foi gerada

## Troubleshooting

### Erro: "Modelo de embeddings não encontrado"
- Instale: `pip install sentence-transformers`

### Erro: "FAISS não disponível"
- Instale: `pip install faiss-cpu`

### Respostas imprecisas
- Verifique se os documentos foram processados corretamente
- Tente perguntas mais específicas
- Verifique a qualidade do OCR

### Sistema lento
- O primeiro uso é mais lento (download do modelo)
- Documentos grandes podem demorar para processar
- Busca é otimizada com FAISS

## Próximos Passos

1. **Melhorar templates de prompt** para diferentes tipos de documento
2. **Adicionar mais tipos de pergunta** (valores, restrições, etc.)
3. **Implementar cache** para respostas frequentes
4. **Adicionar métricas** de qualidade das respostas
5. **Suporte a mais idiomas** se necessário
