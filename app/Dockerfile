# Utiliza uma imagem leve do Python 3.11 como base
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container (é onde o código vai rodar)
WORKDIR /app

# Copia o arquivo de dependências do projeto para dentro do container
COPY requirements.txt .

# Instala as dependências do projeto, sem guardar cache (mais leve)
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo da pasta local para o container
COPY . .

# Comando padrão: iniciar o servidor Django acessível para fora do container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
