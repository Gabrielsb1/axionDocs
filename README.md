# 📄 Extrator de Informações de Matrícula

Este projeto utiliza Streamlit e Ollama para extrair informações específicas de PDFs de matrícula de imóveis usando inteligência artificial local.

## 🚀 Funcionalidades

## python -m streamlit run app.py
## ollama serve

- **Upload de PDF**: Interface simples para carregar arquivos PDF de matrícula
- **Extração de Texto**: OCR com Tesseract para todos os tipos de PDF
- **Processamento Universal**: Funciona com PDFs digitais e escaneados
- **Análise com IA**: Usa o modelo Ollama deepseek-r1:1.5b para extrair informações específicas:
  - Número da matrícula
  - Descrição completa do imóvel
  - Áreas do imóvel (terreno, construção, etc.)
  - Localização/endereço
  - Proprietário
  - Outras informações relevantes
- **Exportação**: Permite exportar os resultados em JSON ou texto
- **Interface Intuitiva**: Interface web moderna e responsiva

## 📋 Pré-requisitos

1. **Python 3.8+** instalado
2. **Ollama** instalado e configurado
3. **Modelo deepseek-r1:1.5b** baixado no Ollama
4. **Tesseract OCR** (obrigatório)

### Instalação do Ollama

1. Baixe o Ollama em: https://ollama.ai/
2. Instale o modelo deepseek-r1:1.5b:
   ```bash
   ollama pull deepseek-r1:1.5b
   ```

### Instalação do Tesseract OCR (Obrigatório)

Para processamento de todos os tipos de PDF:

1. Baixe o Tesseract OCR: [Download](https://github.com/UB-Mannheim/tesseract/wiki)
2. Execute o instalador e instale em `C:\Program Files\Tesseract-OCR\`
3. O sistema detectará automaticamente a instalação

## 🛠️ Instalação

1. **Clone ou baixe o projeto**
2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Como Usar

1. **Inicie o Ollama** (se não estiver rodando):
   ```bash
   ollama serve
   ```

2. **Execute a aplicação Streamlit**:
   ```bash
   streamlit run app.py
   ```

3. **Acesse a interface** no navegador (geralmente http://localhost:8501)

4. **Faça upload de um PDF** de matrícula

5. **Clique em "Extrair Informações"** para processar o PDF

6. **Clique em "Analisar com Ollama"** para extrair as informações específicas

7. **Visualize e exporte** os resultados

## 📁 Estrutura do Projeto

```
axionDocs/
├── app.py                 # Aplicação principal Streamlit
├── pdf_extractor.py       # Classe para extrair texto de PDFs
├── ollama_client.py       # Cliente para comunicação com Ollama
├── requirements.txt       # Dependências do projeto
└── README.md             # Este arquivo
```

## 🔧 Configuração

### Ollama
- **URL padrão**: http://localhost:11434
- **Modelo**: deepseek-r1:1.5b
- **Timeout**: 300 segundos

### OCR (Tesseract)
- **Detecção automática**: O sistema detecta automaticamente a instalação
- **Suporte a idiomas**: Português (por padrão)
- **Qualidade**: DPI 300 para melhor reconhecimento

Para alterar essas configurações, edite o arquivo `ollama_client.py`.

## 📊 Exemplo de Saída

O sistema extrai informações estruturadas como:

```json
{
  "numero_matricula": "12345",
  "descricao_completa": "Imóvel residencial localizado...",
  "areas": {
    "terreno": "500 m²",
    "construcao": "200 m²",
    "outras_areas": ["garagem", "quintal"]
  },
  "localizacao": "Rua das Flores, 123, Centro",
  "proprietario": "João Silva",
  "outras_informacoes": "Imóvel livre de ônus..."
}
```

## 🐛 Solução de Problemas

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

## 📝 Dependências

- **streamlit**: Interface web
- **pytesseract**: Interface Python para Tesseract OCR
- **pillow**: Processamento de imagens
- **PyMuPDF**: Conversão de PDF para imagens
- **requests**: Comunicação com Ollama
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🤝 Contribuição

Sinta-se à vontade para contribuir com melhorias:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é de uso livre para fins educacionais e comerciais.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de solução de problemas
2. Consulte a documentação do Ollama
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando Streamlit e Ollama**
