curl -X DELETE "localhost:9200/pdfs"

curl -X PUT "localhost:9200/pdfs?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "sentence_emb": {
        "type": "dense_vector",
        "dims": 768

      },
      "sentence_text" : {
        "type" : "text",
        "fields" : {
          "keyword" : {
            "type" : "keyword",
            "ignore_above" : 256
          }
        }
      },
      "chapter_name" : {
        "type" : "text",
        "fields" : {
          "keyword" : {
            "type" : "keyword",
            "ignore_above" : 256
          }
        }
      }
    }
  }
}
'
