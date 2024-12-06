FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    zsh \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar Oh My Zsh globalmente
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Usar Zsh como shell predeterminado
SHELL ["/bin/zsh", "-c"]

# Establecer el directorio de trabajo para tu proyecto y copiar los archivos
WORKDIR /workspace/project2_commerce
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto para Django
EXPOSE 8000

# Comando de entrada
CMD ["zsh"]
