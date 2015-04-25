curl -X POST 0.0.0.0:5000/checkin/twitter -H 'content-type:application/json' -d
'{
  "data": "Dogfish Head Beer Thousand",
  "source_id":"dryrun",
  "source":"saraveza",
  "date":"Mon Apr 20 22:57:24 +0000 2015",
  "needs_review":false
}'
