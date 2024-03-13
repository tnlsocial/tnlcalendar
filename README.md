# tnlcalender
A Flask site where you can share a calendar with others

## Development

Uncomment the sqlite database file
```python
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/tnlcalendar/db/calendar.db'
# Local development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
```

Create a new virtualenv

```shell
python -m venv venv
```

Load the virtualenv and pull in the requirements

```shell
# Linux
source venv/bin/activate
# Windows
.\venv\Scripts\activate

pip install -r requirements.txt
```

Set the ```FLASK_ENV``` and ```FLASK_DEBUG``` environment variables and run flask

```shell
# Linux
export FLASK_ENV=development
export FLASK_DEBUG=true

# Windows
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "true"

flask run
```
