ARG OPEN_DISTRO_VERSION

FROM amazon/opendistro-for-elasticsearch:$OPEN_DISTRO_VERSION
RUN bin/elasticsearch-plugin install --batch ingest-attachment
