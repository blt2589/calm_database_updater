FROM mambaorg/micromamba:1.5.10

# Install system-level SpatiaLite tooling (reliable, avoids conda package naming issues)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    spatialite-bin \
    libsqlite3-mod-spatialite \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
USER $MAMBA_USER

# Create conda env
COPY --chown=$MAMBA_USER:$MAMBA_USER docker/environment.yml /tmp/environment.yml
RUN micromamba create -y -n geo -f /tmp/environment.yml && \
    micromamba clean --all --yes

# Default to the geo environment
ENV MAMBA_DEFAULT_ENV=geo
ENV PATH=/opt/conda/envs/geo/bin:$PATH

WORKDIR /work
EXPOSE 8888