## Docker for Database
*opne databse*
- docker exec -it my_postgres_db psql -U postgres -d tradebuddy

*run docker file*
- docker-compose up -d --build



## Createing selfsignd key
```cmd
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout selfsigned.key -out selfsigned.crt

add certificate in nginx conf
```

