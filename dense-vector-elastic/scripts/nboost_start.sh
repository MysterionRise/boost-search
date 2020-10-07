docker run koursaros/nboost:latest-pt --uhost localhost --uport 9200 --search_route "/pdfs/_search" --model_dir bert-base-uncased

# map to manually downloaded model
docker run -v /home/mysterion/projects/boost-search/models/:/opt/conda/lib/python3.6/site-packages/nboost/.cache/nboost/pt-tinybert-msmarco/ -p 8000:8000 --network="host" koursaros/nboost:0.3.3-pt --uhost localhost --uport 9200 --search_route "/pdfs/_search" --model "PtBertRerankModelPlugin" --model_dir "nboost/pt-tinybert-msmarco" --cvalues_path _source.attachment.content
