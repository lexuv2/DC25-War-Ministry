#  Backend documentation
## Swagger

Swagger is available to show all endpoints at :
```
http://localhost:8080/swagger-ui/index.html#/
```

Endpoints /mails are mostly useless for now, no need to worry about them

## Typical use case
- Call parser function with a CV in pdf format as a parameter
```
POST /parser/pdf
```
- The function calls the parser and returns a JSON file while also saving a CV / candidate in database
- Call to view all CVs / candidates saved in a database
```
GET /cv
```
