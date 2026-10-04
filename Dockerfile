# PyTrainer in a container: no clone, no Python install.
#   docker run --rm -p 127.0.0.1:8765:8765 -v pytrainer-data:/data ghcr.io/zawuoff/pytrainer
# then open http://localhost:8765. Progress lives in the pytrainer-data volume.
FROM python:3.13-slim

# git and curl are used by the terminal labs; bubblewrap is the code sandbox when the container is
# allowed user namespaces (otherwise PyTrainer falls back, and the container itself is the boundary).
RUN apt-get update \
 && apt-get install -y --no-install-recommends bubblewrap git curl \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir "jedi>=0.19" \
 && useradd --create-home --uid 1000 pytrainer \
 && mkdir /data && chown pytrainer /data

WORKDIR /app
COPY --chown=pytrainer server.py ./
COPY --chown=pytrainer pytrainer ./pytrainer
COPY --chown=pytrainer static ./static

USER pytrainer
ENV PYTRAINER_DATA=/data PYTHONUNBUFFERED=1
VOLUME ["/data"]
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/state', timeout=4)"
# Listen on all interfaces inside the container; the server still only answers requests addressed
# to localhost, so publish the port on 127.0.0.1 as shown above.
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8765"]
