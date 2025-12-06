# Python 3.9 Slim వాడుతున్నాం
FROM python:3.9-slim

# Chrome, Driver మరియు Virtual Screen (XVFB) ఇన్‌స్టాల్ చేస్తున్నాం
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# వర్కింగ్ డైరెక్టరీ
WORKDIR /app

# ఫైల్స్ కాపీ చేస్తున్నాం
COPY . .

# Python ప్యాకేజీలు
RUN pip install --no-cache-dir -r requirements.txt

# పోర్ట్
EXPOSE 10000

# స్టార్ట్ కమాండ్ (ఇక్కడే మ్యాజిక్ ఉంది)
# xvfb-run అంటే "వర్చువల్ స్క్రీన్ ఆన్ చేసి, అందులో మన యాప్ రన్ చెయ్యి" అని అర్థం
CMD ["xvfb-run", "-a", "--server-args='-screen 0 1280x800x24'", "gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app:app"]
