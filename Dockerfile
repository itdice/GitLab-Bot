# Basic Image
FROM python:3.11.9-alpine

# Set Working Path
WORKDIR /app

# Set Requirements
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy Code
COPY ./main.py /app/main.py
COPY ./message.py /app/message.py

# Set Time
RUN apk add --no-cache chrony
RUN echo "server time.google.com iburst" > /etc/chrony/chrony.conf
CMD ["chronyd", "-d", "-s", "-f", "/etc/chorny/chorny.conf"]

# Set Run
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]