## How to

1. Run Elasticsearch cluster - `docker-compose -f elk-docker/docker-compose.yml up`
2. Run Nboost proxy:

```
boost                                  \
    --uhost localhost                   \
    --uport 9200                        \
    --search_route "/<index>/_search"   \
    --query_path url.query.q            \
    --topk_path url.query.size          \
    --default_topk 10                   \
    --choices_path body.hits.hits       \
    --cvalues_path _source.passage
```

3. 