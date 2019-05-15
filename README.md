# Sins on Twitter

# Team Information
group 68  
Darren Pinto, 1033936  
Matthew Yong, 765353  
Mengzhu Long, 943089  
Wenhao Zhang, 970012  
Yang Liu, 837689  

## Website Link
unimelb network needed
* http://172.26.38.38/app/
* http://172.26.37.231/app/
* http://172.26.38.62/app/

* Test server: http://172.26.38.51/app/

## project directory
```bash
├── deploy                // ansible and deployment configuration
└── src                   // source code root
    ├── tweet_collector   // tweet harverster
    │   └── resources     // resources file used by tweet harverster
    └── web               // flask web application
        ├── resources     // resources file used by tweet web app
        ├── static        // front-end static file
        ├── templates     // front-end pages
        └── utils         // utility module


```

## development setup
### install packages
install python packages including couchdb, flask, etc

```
pip install -r requirements.txt
```

### run docker for couchdb
run docker couchdb image to have couchdb container run 
```
docker run --name sin_database -v <custom_empty_folder>:/opt/couchdb/data -p 5984:5984 -d couchdb
```

### tweet harvester
start collecting new tweet
```
python src/tweet_collector/collect_sin_streaming.py
```

start collecting tweet in past 7 day
```
python src/tweet_collect/collect_sin_search.py
```

### aurin data
import collected aurin data into couchdb

```
python src/web/aurin_processor.py
```

### flask web application
run flask web app on `localhost:5000`

```
python src/web/app.py
```
