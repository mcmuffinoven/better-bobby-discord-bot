FROM python:3.11-slim

COPY . .

RUN apt-get update && apt-get install -y git wget

RUN apt install -y binfmt-support qemu-user-static qemu-system

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux-aarch64.tar.gz
RUN tar -xvzf geckodriver-v0.33.0-linux-aarch64.tar.gz && mv geckodriver /usr/bin/

RUN apt install -y firefox-esr 
RUN pip install -r requirements.txt

WORKDIR /src

CMD ["python", "main.py"]