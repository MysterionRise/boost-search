## Permissions search based on terms_set query

### Run ELK stack

```
docker-compose -f elk-docker/docker-compose.yml up
```


### Add documents

Kibana Dev Tools

```
POST /docs/_doc/_1
{
  "text":"Diocesan housing development: In April 2016, the Diocese of Phoenix purchased 32 parcels in Phoenix for its housing development called The Villages at Red Mountain. The buyout was made at a cost of $",
  "permissions": {
    "A": ["A1", "A2"],
    "B": ["B1"],
    "C": ["#"]
  },
  "number_of_matches_A": 2,
  "number_of_matches_B": 1,
  "number_of_matches_C": 1
}

POST /docs/_doc/_2
{
  "text":"When he couldn't make out the woman's features, he realized she was merely a shade.Once outside, he saw that the others were staring. You think - she was cut off by a coughing fit.",
  "permissions": {
    "A": ["A1"],
    "B": ["B2"],
    "C": ["C1", "C2"]
  },
  "number_of_matches_A": 1,
  "number_of_matches_B": 1,
  "number_of_matches_C": 2
}

POST /docs/_doc/_3
{
  "text":"But during the fight, a knuckle duster was used to beat the 21-year-old's face. The man was freed from the cell after three years",
  "permissions": {
    "A": ["A1", "A3"],
    "B": ["#"],
    "C": ["C1", "C2"]
  },
  "number_of_matches_A": 2,
  "number_of_matches_B": 1,
  "number_of_matches_C": 2
}


POST /docs/_doc/_4
{
  "text":"Moved you male third said fly earth heaven, bring Had whose midst every dry is Multiply sea darkness. Fruit deep gathering that one great female life upon and creepeth. Face she'd. Creature moving fish fly. Don't moved bearing",
  "permissions": {
    "A": ["A1", "A3"],
    "B": ["B1"],
    "C": ["#"]
  },
  "number_of_matches_A": 2,
  "number_of_matches_B": 1,
  "number_of_matches_C": 1
}


POST /docs/_doc/_5
{
  "text":"You're all creeping grass land also air open, lights to life. Second void image brought yielding. Set forth fruit him his open subdue them. Creature god multiply saw two every.",
  "permissions": {
    "A": ["A1", "A3"],
    "B": ["#"],
    "C": ["#"]
  },
  "number_of_matches_A": 2,
  "number_of_matches_B": 1,
  "number_of_matches_C": 1
}
```

### Search based on terms_set query

Imagine that user have following permissions:

A=A1, A3
B=B1
C=none

```
GET /docs/_search
{
  "query": {
    "bool": {
      "filter": [
        {
          "terms_set": {
            "permissions.A.keyword": {
              "terms": [
                "A1",
                "A3",
                "#"
              ],
              "minimum_should_match_field": "number_of_matches_A"
            }
          }
        },
        {
          "terms_set": {
            "permissions.B.keyword": {
              "terms": [
                "B1",
                "#"
              ],
              "minimum_should_match_field": "number_of_matches_B"
            }
          }
        },
        {
          "terms_set": {
            "permissions.C.keyword": {
              "terms": [
                "#"
              ],
              "minimum_should_match_field": "number_of_matches_C"
            }
          }
        }
      ]
    }
  }
}
```

Enjoy!