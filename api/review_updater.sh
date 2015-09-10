#docker start c4aa480149fd
curl -X POST 0.0.0.0:5000/checkin/raw -H 'content-type:application/json' -d \
'{
  "data": "Double Mountain Gypsy Stumper",
  "source_id":"592466161389801472",
  "date":"Sun Apr 26 23:11:55 +0000 2015",
  "needs_review":false,
  "venue":"49be98edf964a520c0541fe3"
}'
