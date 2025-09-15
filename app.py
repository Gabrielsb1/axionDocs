import streamlit as st
import json
from pdf_extractor_precise import PDFExtractor
from ollama_client import OllamaClient
from rag_client import RAGClient

# Configuração simples
st.set_page_config(
    page_title="Extrator de Matrícula",
    page_icon="🏠",
    layout="wide"
)

# CSS simples e funcional
st.markdown("""
<style>
    .main-title {
        color: #1f4e79;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
        font-weight: bold;
    }
    
    .error-box {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
        font-weight: bold;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border: 2px solid #17a2b8;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
    }
    
    .metric-box {
        background-color: #ffffff;
        border: 2px solid #007bff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        color: #004085;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #007bff;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<h1 class="main-title"> IA LOCAL</h1>', unsafe_allow_html=True)

# Navegação por abas
tab1, tab2, tab3 = st.tabs(["Processar PDF", "Perguntas RAG", "Documentos"])

# Inicialização
pdf_extractor = PDFExtractor()
ollama_client = OllamaClient()
rag_client = RAGClient()

# Verificação rápida de conexão
try:
    ollama_client.generate_response("teste")
    st.markdown('<div class="success-box"> Ollama conectado - Modelo: mistral:7b</div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="error-box"> Erro: Ollama não está rodando</div>', unsafe_allow_html=True)
    st.stop()

# ABA 1: PROCESSAR PDF
with tab1:
    st.markdown("##  Upload e Processamento de PDF")
    uploaded_file = st.file_uploader("Escolha um arquivo PDF", type=['pdf'])

    if uploaded_file is not None:
        # Processar PDF
        if st.button(" Processar PDF", type="primary"):
            with st.spinner("Processando..."):
                try:
                    pdf_text = pdf_extractor.extract_text_from_pdf(uploaded_file)
                    pdf_info = pdf_extractor.get_pdf_info(uploaded_file)
                    
                    st.session_state['pdf_text'] = pdf_text
                    st.session_state['pdf_info'] = pdf_info
                    
                    st.markdown('<div class="success-box"> PDF processado com sucesso!</div>', unsafe_allow_html=True)
                    st.rerun()
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box"> Erro: {str(e)}</div>', unsafe_allow_html=True)

    # Análise com IA
    if 'pdf_text' in st.session_state:
        st.markdown("##  Análise com IA")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(" Analisar com IA", type="primary"):
                with st.spinner("Analisando..."):
                    try:
                        extracted_info = ollama_client.extract_matricula_info(st.session_state['pdf_text'])
                        st.session_state['extracted_info'] = extracted_info
                        
                        st.markdown('<div class="success-box"> Análise concluída!</div>', unsafe_allow_html=True)
                        st.rerun()
                        
                    except Exception as e:
                        st.markdown(f'<div class="error-box"> Erro: {str(e)}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button(" Adicionar ao RAG", type="secondary"):
                with st.spinner("Adicionando ao sistema RAG..."):
                    try:
                        extracted_info = st.session_state.get('extracted_info', {})
                        filename = uploaded_file.name if uploaded_file else "documento_processado"
                        
                        doc_id = rag_client.add_document(
                            filename=filename,
                            content=st.session_state['pdf_text'],
                            extracted_info=extracted_info
                        )
                        
                        st.markdown(f'<div class="success-box"> Documento adicionado ao RAG (ID: {doc_id})!</div>', unsafe_allow_html=True)
                        st.rerun()
                        
                    except Exception as e:
                        st.markdown(f'<div class="error-box"> Erro ao adicionar ao RAG: {str(e)}</div>', unsafe_allow_html=True)

    # Resultados
    if 'extracted_info' in st.session_state:
        st.markdown("## Resultados")
        
        info = st.session_state['extracted_info']
        
        # Número da matrícula
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Número da Matrícula")
            numero = info.get('numero_matricula', '')
            if numero and str(numero).strip() and str(numero) != 'None':
                st.markdown(f'<div class="success-box"> <strong>Número:</strong> {numero}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box"> Não encontrado</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Inscrição Imobiliária")
            inscricao = info.get('inscricao_imobiliaria', '')
            if inscricao and str(inscricao).strip() and str(inscricao) != 'None':
                st.markdown(f'<div class="success-box"> <strong>Inscrição:</strong> {inscricao}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box"> Não encontrada</div>', unsafe_allow_html=True)
        
        # Áreas
        st.markdown("###  Áreas do Imóvel")
        areas = info.get('areas', {})
        
        if areas:
            cols = st.columns(3)
            area_labels = {
                'privativa_real': ' Privativa Real',
                'privativa_acessoria': ' Privativa Acessória',
                'uso_comum': ' Uso Comum',
                'total_real': ' Total Real',
                'equivalente_construcao': ' Equivalente',
                'vaga_garagem': ' Garagem'
            }
            
            for i, (key, label) in enumerate(area_labels.items()):
                with cols[i % 3]:
                    value = areas.get(key, '')
                    if value and str(value).strip() and str(value) != 'None':
                        st.markdown(f'''
                        <div class="metric-box">
                            <strong>{label}</strong><br>
                            <span class="metric-value">{value}</span>
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''
                        <div class="metric-box">
                            <strong>{label}</strong><br>
                            <span style="color: #6c757d;">Não informado</span>
                        </div>
                        ''', unsafe_allow_html=True)
        
        # Descrição
        st.markdown("###  Descrição Completa")
        descricao = info.get('descricao_imovel_completa', '')
        if descricao and str(descricao).strip() and str(descricao) != 'None':
            st.text_area("", value=descricao, height=200, disabled=True)
        else:
            st.markdown('<div class="error-box"> Descrição não encontrada</div>', unsafe_allow_html=True)
        
        # Exportar
        st.markdown("###  Exportar")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(" Baixar JSON"):
                json_str = json.dumps(info, indent=2, ensure_ascii=False)
                st.download_button(
                    " Baixar JSON",
                    data=json_str,
                    file_name=f"matricula_{info.get('numero_matricula', 'info')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button(" Nova Análise"):
                for key in ['pdf_text', 'pdf_info', 'extracted_info']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    # Informações do arquivo
    if 'pdf_info' in st.session_state:
        with st.expander(" Informações do Arquivo"):
            info = st.session_state['pdf_info']
            st.write(f"**Páginas:** {info.get('pages', 'N/A')}")
            st.write(f"**Tamanho:** {info.get('size', 'N/A')}")

    # Texto extraído
    if 'pdf_text' in st.session_state:
        with st.expander(" Ver Texto Extraído"):
            st.text_area("", value=st.session_state['pdf_text'], height=300, disabled=True)

# ABA 2: PERGUNTAS RAG
with tab2:
    st.markdown("##  Sistema de Perguntas e Respostas (RAG)")
    
    # Status do sistema RAG
    doc_count = rag_client.get_document_count()
    if doc_count > 0:
        st.markdown(f'<div class="success-box"> Sistema RAG ativo - {doc_count} documento(s) carregado(s)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box"> Nenhum documento no sistema RAG. Processe e adicione documentos na aba "Processar PDF"</div>', unsafe_allow_html=True)
    
    # Perguntas sugeridas
    if doc_count > 0:
        st.markdown("### Perguntas Sugeridas")
        suggested_questions = rag_client.get_suggested_questions()
        
        cols = st.columns(2)
        for i, question in enumerate(suggested_questions):
            with cols[i % 2]:
                if st.button(f" {question}", key=f"suggested_{i}"):
                    st.session_state['rag_question'] = question
                    st.rerun()
    
    # Input de pergunta
    st.markdown("### Faça sua Pergunta")
    question = st.text_input(
        "Digite sua pergunta sobre os documentos de matrícula:",
        value=st.session_state.get('rag_question', ''),
        placeholder="Ex: Qual é o número da matrícula do imóvel?"
    )
    
    # Tipo de pergunta
    question_type = st.selectbox(
        "Tipo de pergunta:",
        ["geral", "numeros", "areas", "proprietario"],
        format_func=lambda x: {
            "geral": " Pergunta Geral",
            "numeros": " Números e Dados",
            "areas": " Áreas do Imóvel", 
            "proprietario": " Informações do Proprietário"
        }[x]
    )
    
    # Botão de pergunta
    if st.button(" Buscar Resposta", type="primary") and question:
        with st.spinner("Processando pergunta..."):
            try:
                result = rag_client.ask_question(question, question_type)
                
                # Exibir resposta
                st.markdown("### Resposta")
                st.markdown(f'<div class="info-box">{result["answer"]}</div>', unsafe_allow_html=True)
                
                # Confiança
                confidence = result["confidence"]
                confidence_color = "success" if confidence > 0.7 else "warning" if confidence > 0.4 else "error"
                st.markdown(f"**Confiança:** {confidence:.1%}")
                
                # Fontes
                if result["sources"]:
                    st.markdown("### Fontes")
                    for source in result["sources"]:
                        st.write(f" {source['filename']} (similaridade: {source['score']:.2f})")
                
                # Contexto (expandível)
                if result["context"]:
                    with st.expander(" Ver Contexto Usado"):
                        st.text(result["context"])
                        
            except Exception as e:
                st.markdown(f'<div class="error-box"> Erro: {str(e)}</div>', unsafe_allow_html=True)

# ABA 3: DOCUMENTOS
with tab3:
    st.markdown("## Gerenciamento de Documentos")
    
    # Resumo do sistema
    summary = rag_client.get_document_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(" Total de Documentos", summary["total_documents"])
    with col2:
        st.metric(" Matrículas Únicas", len(summary["matriculas"]))
    with col3:
        st.metric(" Áreas Encontradas", len(summary["areas_encontradas"]))
    
    # Lista de documentos
    if summary["total_documents"] > 0:
        st.markdown("### Documentos no Sistema")
        
        documents = rag_client.rag_system.get_all_documents()
        
        for doc in documents:
            with st.expander(f" {doc['filename']} (ID: {doc['id']})"):
                st.write(f"**Adicionado em:** {doc['created_at']}")
                
                if doc['extracted_info']:
                    st.write("**Informações extraídas:**")
                    st.json(doc['extracted_info'])
                
                if st.button(f" Remover", key=f"remove_{doc['id']}"):
                    if rag_client.delete_document(doc['id']):
                        st.success("Documento removido!")
                        st.rerun()
                    else:
                        st.error("Erro ao remover documento")
        
        # Limpar todos
        st.markdown("### Ações Destrutivas")
        if st.button(" Remover Todos os Documentos", type="secondary"):
            rag_client.clear_all_documents()
            st.success("Todos os documentos foram removidos!")
            st.rerun()
    
    else:
        st.markdown('<div class="info-box"> Nenhum documento no sistema. Processe documentos na aba "Processar PDF"</div>', unsafe_allow_html=True)