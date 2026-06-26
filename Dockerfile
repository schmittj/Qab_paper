FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    g++ \
    git \
    latexmk \
    libflint-dev \
    libgmp-dev \
    make \
    python3 \
    python3-dev \
    python3-pip \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-latex-recommended \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY requirements-optional.txt /work/
RUN python3 -m pip install --break-system-packages -r requirements-optional.txt

COPY . /work

CMD ["make", "verify-full"]
