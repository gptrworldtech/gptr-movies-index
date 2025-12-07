# 1. Python 3.9 Slim తీసుకుంటున్నాం
FROM python:3.9-slim

# 2. Chrome మాత్రమే ఇన్‌స్టాల్ చేస్తున్నాం (Xvfb అవసరం లేదు)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 3. వర్కింగ్ డైరెక్టరీ
WORKDIR /app

# 4. ఫైల్స్ కాపీ
COPY . .

# 5. సాఫ్ట్‌వేర్స్ ఇన్‌స్టాల్
RUN pip install --no-cache-dir -r requirements.txt

# 6. పోర్ట్
EXPOSE 10000

# 7. సింపుల్ స్టార్ట్ కమాండ్ (Xvfb తీసేసాం)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app:app"]
