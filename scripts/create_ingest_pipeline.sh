curl -X PUT "localhost:9200/_ingest/pipeline/pdf-indexing?pretty" -H 'Content-Type: application/json' -d'
{
  "description" : "Extract attachment information",
  "processors" : [
    {
      "attachment" : {
        "field" : "data"
      }
    }
  ]
}
'
