FROM python:3.12-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r requirements.txt 

COPY *.py ./

VOLUME ["/volume/output"]

CMD ["python", "scheduler.py"]
