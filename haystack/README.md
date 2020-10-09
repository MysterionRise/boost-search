## How to

### Docker compose example

1. Install requirements for scripts execution `pip install -r qa_api/requirements.txt`
2. Install models into `data` by running `python download_models.py`, copy data
3. Build all images: `docker-compose -f docker-compose-dev.yml build`
4. Run containers: `docker-compose -f docker-compose-dev.yml up`
5. Index SEC data by running `python index_sec_data.py` (or create API for indexing)
6. Ask questions: `http://localhost:8080/askquestion?question=who%20are%20you?`