# Fleet
1.Create virtual environment and activate it
virtualenv venv
source venv/bin/activate

2.Pip install requirements
pip install -r requirements.txt

3.create db
CMD :
python
>from app import db
>db.create_all()
>exit()

4.Run App
flask run

CRDU operation for movies

Add movie
curl http://localhost:5000/movies -X POST -H "Content-Type: application/json" -d '{"title":"Antim", "year":2021,"votes":"0","genre":"action","release_date":"26-11-2021","reviews":"Very Bad"}'

Get list of movie
curl http://localhost:5000/movies

Update movie
curl http://localhost:5000/movies/1 -X PUT -H "Content-Type: application/json" -d '{"title":"Antim", "year":2021,"votes":"0","genre":"action","release_date":"26-11-2021","reviews":"Good"}'

Delete movie
curl -X DELETE "http://localhost:5000/movies/1"


