### How to

1. Install requirements: `pip install -r requirements.txt`
2. Run Elasticsearch in Docker: `docker-compose -f opendistro-docker/docker-compose.yml up`
3. Run indexing: `python index_game_of_thrones_qa.py`
4. Update the question in the `game_of_thrones_qa.py` and run it `python game_of_thrones_qa.py`