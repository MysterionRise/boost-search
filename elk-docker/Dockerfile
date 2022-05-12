ARG ELK_VERSION

FROM docker.elastic.co/elasticsearch/elasticsearch-oss:$ELK_VERSION
RUN bin/elasticsearch-plugin install --batch ingest-attachment

