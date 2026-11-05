# bob-bench — IBM Bob 2.3.0 sous Xvfb, sans display hôte
# Build : docker build -t bob-bench:2.3.0 harness/container
# Run   : docker run --rm bob-bench:2.3.0
#
# Pins gravés dans l'image (source : private/baseline-2.3.0/) :
#   App version   : 2.3.0  (product.json bobideVersion)
#   bob-code      : 2.3.0  (extensions/bob-code/package.json)
#   extension.js  : 57b8ecdb5c7fe7967695aaea023243f6d5ea3a30 (SHA-1)
#   Paquet Linux  : IBM-Bob-linux-amd64-1.126.0+bob2.3.0.deb

FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# ── Dépendances système ───────────────────────────────────────────────────────
# Electron / VS Code fork requiert : libglib2, libnss, libatk, libdrm, libgbm, libxkbcommon,
# libgtk-3, libxcomposite, libxdamage, libxrandr, libpango, libcairo, libxss,
# libasound, libxtst, libexpat, libfontconfig, fonts-liberation.
# Xvfb + xdpyinfo pour le display virtuel.
# python3 pour l'assertion des pins (présent dans ubuntu:22.04).
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    xvfb \
    x11-utils \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgbm1 \
    libxkbcommon0 \
    libgtk-3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libxss1 \
    libasound2 \
    libxtst6 \
    libexpat1 \
    libfontconfig1 \
    fonts-liberation \
    xdg-utils \
    python3 \
  && rm -rf /var/lib/apt/lists/*

# ── Téléchargement et installation de bobide 2.3.0 ───────────────────────────
# L'URL de téléchargement est une pré-URL signée (TTL 60 s) ; elle est obtenue
# via le endpoint public /api/download/bobide du site bob.ibm.com.
# Cette étape est la seule source de non-déterminisme : IBM peut retirer le paquet.
# Lier le build à ce hash SHA-256 sur le .deb n'est pas possible car IBM ne publie
# pas de somme de contrôle officielle pour le paquet Linux — on s'appuie donc sur
# l'assertion post-installation des trois pins ci-dessous, qui sont dérivés du
# contenu du paquet et vérifiés à chaque démarrage du conteneur.
RUN DEB_URL=$(curl -s -o /dev/null -D - -X POST \
      "https://bob.ibm.com/api/download/bobide" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      --data-urlencode "platform=linux" \
      --data-urlencode "version=1.126.0+bob2.3.0" \
      --data-urlencode "architecture=amd64" \
      --data-urlencode "packageType=deb" \
      | grep -i "^location:" | tr -d '\r' | awk '{print $2}') \
  && curl -fL -o /tmp/ibm-bob.deb "${DEB_URL}" \
  && dpkg -i /tmp/ibm-bob.deb \
  && rm /tmp/ibm-bob.deb

# ── Désactivation de l'auto-update ───────────────────────────────────────────
# product.json « updateUrl » est lié en dur dans le binaire via l'app bundle ;
# on le neutralise dans le fichier de ressources installé sur disque (Linux :
# /usr/share/ibm-bob/resources/app/product.json).
# Le binaire lit ce fichier au démarrage pour construire les URLs d'update.
# Mettre updateUrl à "" désactive les vérifications de mise à jour.
RUN python3 -c "import json, pathlib; p = pathlib.Path('/usr/share/bobide/resources/app/product.json'); d = json.loads(p.read_text()); d['updateUrl'] = ''; p.write_text(json.dumps(d, separators=(',', ':')))"

# ── Vérification des pins post-installation ──────────────────────────────────
# Les pins sont définis dans assert-pins.sh et correspondent à baseline-2.3.0/.
# Si le paquet téléchargé n'est pas exactement le bon build, ce RUN échoue.
COPY assert-pins.sh /usr/local/bin/assert-pins.sh
RUN chmod +x /usr/local/bin/assert-pins.sh && /usr/local/bin/assert-pins.sh

# ── Entrypoint ───────────────────────────────────────────────────────────────
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Workspace vide par défaut (peut être monté via -v à l'exécution)
RUN mkdir -p /workspace
WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
