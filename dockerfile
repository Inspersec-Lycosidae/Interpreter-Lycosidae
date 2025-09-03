FROM python:3.13-slim
WORKDIR /interpreter
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x ./uvicorn.sh
ENV PYTHONPATH=/interpreter/app
CMD ["/bin/bash", "./uvicorn.sh"]
