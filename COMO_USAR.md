# 🚀 Como Usar o Sistema de Extração de Matrícula

## 📋 Pré-requisitos

1. **Ollama instalado e rodando** com o modelo phi3:3.8b
2. **Python 3.8+** instalado
3. **Dependências instaladas**: `pip install -r requirements.txt`

## 🎯 Passo a Passo

### 1. Verificar se o Ollama está rodando
```bash
ollama list
```
Deve mostrar o modelo `phi3:3.8b` instalado.

### 2. Iniciar o Ollama (se não estiver rodando)
```bash
ollama serve
```

### 3. Executar a aplicação
```bash
streamlit run app.py
```
Ou simplesmente execute o arquivo `run.bat` no Windows.

### 4. Usar a interface web
1. Acesse http://localhost:8501 no navegador
2. Faça upload do PDF da matrícula
3. Clique em "Extrair Informações" para processar o PDF
4. Clique em "Analisar com Ollama" para extrair dados específicos
5. Visualize os resultados e exporte se necessário

## 🧪 Testar o Sistema

Para testar se tudo está funcionando:
```bash
python test_system.py
```

## 📊 Informações Extraídas

O sistema extrai automaticamente:

- ✅ **Número da Matrícula**
- ✅ **Tipo do Imóvel** (urbano/rural)
- ✅ **Descrição Completa**
- ✅ **Localização** (endereço, município, estado, bairro)
- ✅ **Dimensões** (frente, laterais, fundos)
- ✅ **Áreas** (privativa, acessória, uso comum, total, construção, fração ideal)
- ✅ **Dependências** (salão, lavabo, garagem, etc.)
- ✅ **Proprietários** (atual, vendedor, comprador)
- ✅ **Valor da Transação**
- ✅ **Inscrição Imobiliária**
- ✅ **Registro Anterior**
- ✅ **Data do Registro**
- ✅ **Custos** (ITBI, emolumentos)

## 🔧 Solução de Problemas

### Erro de Conexão com Ollama
- Verifique se o Ollama está rodando: `ollama list`
- Confirme se o modelo phi3:3.8b está instalado
- Verifique se a porta 11434 está disponível

### Erro ao Processar PDF
- Verifique se o arquivo é um PDF válido
- Confirme se o PDF não está protegido por senha
- Teste com um PDF menor primeiro

### Erro de Memória
- Para PDFs muito grandes, considere processar página por página
- Aumente o timeout no `ollama_client.py`

## 📁 Estrutura dos Arquivos

```
axionDocs/
├── app.py                 # Interface principal Streamlit
├── pdf_extractor.py       # Extração de texto de PDFs
├── ollama_client.py       # Comunicação com Ollama
├── test_system.py         # Script de teste
├── requirements.txt       # Dependências
├── run.bat               # Script para Windows
├── README.md             # Documentação completa
├── COMO_USAR.md          # Este arquivo
└── matricula3ri.pdf      # Exemplo de matrícula
```

## 🎉 Exemplo de Uso

1. **Upload**: Carregue o arquivo `matricula3ri.pdf` como exemplo
2. **Processamento**: O sistema extrairá automaticamente o texto
3. **Análise**: A IA analisará e extrairá informações estruturadas
4. **Resultado**: Visualize dados como:
   - Número da matrícula: 62743.2.0008332-23
   - Tipo: Imóvel Urbano
   - Localização: São Luís/MA
   - Área total: 80,96 m²
   - Valor: R$ 280.879,56

## 💡 Dicas

- Use PDFs de boa qualidade para melhor extração
- O sistema funciona melhor com matrículas em português
- Você pode exportar os resultados em JSON ou texto
- A interface mostra o status da conexão com Ollama

---

**Sistema desenvolvido para extração inteligente de informações de matrículas usando IA local!** 🤖📄
