# Usar uma imagem base oficial do Python
FROM python:3.9

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos os arquivos do projeto para o diretório de trabalho no contêiner
COPY . .

# Definir o comando padrão para rodar a aplicação
CMD ["python", "OVH_CLI.py"]
