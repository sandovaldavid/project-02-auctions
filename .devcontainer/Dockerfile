FROM python:3.11-slim

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar el sistema e instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    zsh \
    git \
    curl \
    build-essential \
    wget \
    software-properties-common \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
    tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh

# Verificar instalación de GitHub CLI
RUN gh --version

# Instalar Oh My Zsh
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" || true

# Configurar Zsh como shell predeterminado
SHELL ["/bin/zsh", "-c"]

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install django djangorestframework

# Configurar Git para evitar el error de "dubious ownership" (como el usuario creado)
RUN git config --global --add safe.directory '*'

# Configurar el directorio de trabajo
WORKDIR /workspace

# Copiar archivos del proyecto al contenedor
COPY . .

# Exponer el puerto predeterminado de Django
EXPOSE 8000

# Comando por defecto
CMD ["zsh"]