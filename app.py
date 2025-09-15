import streamlit as st
import json
from pdf_extractor_precise import PDFExtractor
from ollama_client import OllamaClient

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
st.markdown('<h1 class="main-title">🏠 Extrator de Matrícula Imobiliária</h1>', unsafe_allow_html=True)

# Inicialização
pdf_extractor = PDFExtractor()
ollama_client = OllamaClient()

# Verificação rápida de conexão
try:
    ollama_client.generate_response("teste")
    st.markdown('<div class="success-box">✅ Ollama conectado - Modelo: mistral:7b</div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="error-box">❌ Erro: Ollama não está rodando</div>', unsafe_allow_html=True)
    st.stop()

# Upload do PDF
st.markdown("## 📁 Upload do PDF")
uploaded_file = st.file_uploader("Escolha um arquivo PDF", type=['pdf'])

if uploaded_file is not None:
    # Processar PDF
    if st.button("🔄 Processar PDF", type="primary"):
        with st.spinner("Processando..."):
            try:
                pdf_text = pdf_extractor.extract_text_from_pdf(uploaded_file)
                pdf_info = pdf_extractor.get_pdf_info(uploaded_file)
                
                st.session_state['pdf_text'] = pdf_text
                st.session_state['pdf_info'] = pdf_info
                
                st.markdown('<div class="success-box">✅ PDF processado com sucesso!</div>', unsafe_allow_html=True)
                st.rerun()
                
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Erro: {str(e)}</div>', unsafe_allow_html=True)

# Análise com IA
if 'pdf_text' in st.session_state:
    st.markdown("## 🧠 Análise com IA")
    
    if st.button("🧠 Analisar com IA", type="primary"):
        with st.spinner("Analisando..."):
            try:
                extracted_info = ollama_client.extract_matricula_info(st.session_state['pdf_text'])
                st.session_state['extracted_info'] = extracted_info
                
                st.markdown('<div class="success-box">✅ Análise concluída!</div>', unsafe_allow_html=True)
                st.rerun()
                
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Erro: {str(e)}</div>', unsafe_allow_html=True)

# Resultados
if 'extracted_info' in st.session_state:
    st.markdown("## 📋 Resultados")
    
    info = st.session_state['extracted_info']
    
    # Número da matrícula
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Número da Matrícula")
        numero = info.get('numero_matricula', '')
        if numero and str(numero).strip() and str(numero) != 'None':
            st.markdown(f'<div class="success-box">✅ <strong>Número:</strong> {numero}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">❌ Não encontrado</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🏠 Inscrição Imobiliária")
        inscricao = info.get('inscricao_imobiliaria', '')
        if inscricao and str(inscricao).strip() and str(inscricao) != 'None':
            st.markdown(f'<div class="success-box">✅ <strong>Inscrição:</strong> {inscricao}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">❌ Não encontrada</div>', unsafe_allow_html=True)
    
    # Áreas
    st.markdown("### 📐 Áreas do Imóvel")
    areas = info.get('areas', {})
    
    if areas:
        cols = st.columns(3)
        area_labels = {
            'privativa_real': '🏠 Privativa Real',
            'privativa_acessoria': '🏡 Privativa Acessória',
            'uso_comum': '🏢 Uso Comum',
            'total_real': '📏 Total Real',
            'equivalente_construcao': '🏗️ Equivalente',
            'vaga_garagem': '🚗 Garagem'
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
    st.markdown("### 📝 Descrição Completa")
    descricao = info.get('descricao_imovel_completa', '')
    if descricao and str(descricao).strip() and str(descricao) != 'None':
        st.text_area("", value=descricao, height=200, disabled=True)
    else:
        st.markdown('<div class="error-box">❌ Descrição não encontrada</div>', unsafe_allow_html=True)
    
    # Exportar
    st.markdown("### 💾 Exportar")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Baixar JSON"):
            json_str = json.dumps(info, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Baixar JSON",
                data=json_str,
                file_name=f"matricula_{info.get('numero_matricula', 'info')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🔄 Nova Análise"):
            for key in ['pdf_text', 'pdf_info', 'extracted_info']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Informações do arquivo
if 'pdf_info' in st.session_state:
    with st.expander("📄 Informações do Arquivo"):
        info = st.session_state['pdf_info']
        st.write(f"**Páginas:** {info.get('pages', 'N/A')}")
        st.write(f"**Tamanho:** {info.get('size', 'N/A')}")

# Texto extraído
if 'pdf_text' in st.session_state:
    with st.expander("📄 Ver Texto Extraído"):
        st.text_area("", value=st.session_state['pdf_text'], height=300, disabled=True)