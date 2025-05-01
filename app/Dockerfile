# Usa uma imagem leve do Python 3.11 como base
FROM python:3.11-slim

# Instala o Netcat (pacote correto: netcat-openbsd) e limpa o cache
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para o container
COPY . .

# Dá permissão de execução ao script que aguarda o PostgreSQL
RUN chmod +x wait-for-postgres.sh

# Comando padrão: espera o banco e inicia o servidor Django
CMD ["./wait-for-postgres.sh", "python", "manage.py", "runserver", "0.0.0.0:8000"]
