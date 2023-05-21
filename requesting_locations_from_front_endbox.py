To display all locations from the database in a CSS box with checkmark options and retrieve the selected locations as a JSON list, 
you can use Jinja templates in conjunction with Flask. 
Here's an updated version of the Flask app that incorporates these changes:

1. Update the `app.py` file with the following code:

```python
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import yaml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_username:your_password@localhost/your_database'
db = SQLAlchemy(app)

def get_table_columns():
    with open('schema.yaml', 'r') as file:
        schema = yaml.safe_load(file)
        return schema[0]['columns']

class RealEstate(db.Model):
    __tablename__ = 'real_estate'
    id = db.Column(db.Integer, primary_key=True)
    house_size = db.Column(db.Integer)
    house_location = db.Column(db.Text)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    price = db.Column(db.Numeric)
    date_added = db.Column(db.Date)

    def to_dict(self):
        return {
            'id': self.id,
            'house_size': self.house_size,
            'house_location': self.house_location,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'price': float(self.price),
            'date_added': str(self.date_added)
        }

db.create_all()

def get_database_connection():
    # Update the connection details with your PostgreSQL credentials
    connection = psycopg2.connect(
        host='localhost',
        database='your_database',
        user='your_username',
        password='your_password'
    )
    return connection

def apply_filters(query):
    filters = {}
    if 'min_area' in request.json:
        filters['house_size >='] = request.json['min_area']
    if 'max_area' in request.json:
        filters['house_size <='] = request.json['max_area']
    if 'locations' in request.json:
        filters['house_location'] = request.json['locations']
    if 'min_bedrooms' in request.json:
        filters['bedrooms >='] = request.json['min_bedrooms']
    if 'max_bedrooms' in request.json:
        filters['bedrooms <='] = request.json['max_bedrooms']
    return query.filter_by(**filters)

def get_all_locations():
    query = db.session.query(RealEstate.house_location.distinct()).all()
    locations = [location[0] for location in query]
    return locations

def get_selected_locations():
    selected_locations = []
    for location in get_all_locations():
        checkbox_value = request.form.get(location)
        if checkbox_value:
            selected_locations.append(location)
    return selected_locations

@app.route('/', methods=['GET', 'POST'])
def get_real_estate():
    if request.method == 'POST':
        selected_locations = get_selected_locations()
        return jsonify(selected_locations)

    locations = get_all_locations()
    return render_template('index.html', locations=locations)

if __name__ == '__main__':
    app.run()
```

2. Create a new directory named `templates` in the same directory as `app.py`.

3. Inside the `templates` directory, create a file named `index.html` with the following code:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Real Estate Locations</title>
    <style>
        .location-box {
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 10px;
        }
    </style>
</head

>
<body>
    <form action="/" method="post">
        {% for location in locations %}
            <div class="location-box">
                <label for="{{ location }}">{{ location }}</label>
                <input type="checkbox" id="{{ location }}" name="{{ location }}">
            </div>
        {% endfor %}
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

4. In the `get_real_estate()` route handler, if the request method is `POST`, the selected locations are 
retrieved using the `get_selected_locations()` function and returned as a JSON response.

5. If the request method is `GET`, the `locations` variable is populated with all locations using the `get_all_locations()` function, 
and the `index.html` template is rendered with the locations displayed inside CSS boxes with checkmark options.

6. Start the Flask app:
```
python app.py
```

Now, when you visit `http://localhost:5000/`, you will see a list of locations inside CSS boxes with checkmark options. 
    Upon submitting the form, the selected locations will be returned as a JSON response.
