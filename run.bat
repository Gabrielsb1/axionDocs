@echo off
echo Iniciando Extrator de Informacoes de Matricula...
echo.
echo Verificando se o Ollama esta rodando...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Ollama nao esta rodando ou nao esta instalado!
    echo Por favor, inicie o Ollama primeiro:
    echo   ollama serve
    pause
    exit /b 1
)

echo Ollama detectado! Iniciando aplicacao Streamlit...
echo.
streamlit run app.py
pause
