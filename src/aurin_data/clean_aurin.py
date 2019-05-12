import couchdb

couch = couchdb.Server('http://localhost:5984/')
couch.resource.credentials = ("admin", "admin")

DATABASE_ADULT_HEALTH = "adult_health"
DATABASE_PERSONAL_INCOME = "personal_income"

couch.delete(DATABASE_ADULT_HEALTH)
couch.delete(DATABASE_PERSONAL_INCOME)