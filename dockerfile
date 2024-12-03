FROM python:3.13.0

RUN python -m venv /opt/env
RUN /opt/env/bin/pip install --upgrade pip
ENV PATH="/opt/env/bin:$PATH"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
