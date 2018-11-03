from common.database import Database
from models.user import User
from models.post import Post
from models.topic import Topic
from models.Place import Place
from geopy.geocoders import Nominatim
from models.cities import Cities
from models.bucket import List
from models.contact import Con
from models.rating_op import Rating
import folium
from models.promo import Promotion
from models.rating import Rating
from models.recommend import Food
import numpy as np
import secrets
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer

__author__ = 'Jetfire'


from flask import Flask, render_template, request, session, make_response, flash, jsonify
from flask_avatars import Avatars
import hashlib
import datetime
import json
import base64

app = Flask(__name__)  # '__main__'
app.secret_key = "Bose"
avatars = Avatars(app)
BASECOORD = [22.3511148, 78.6677428]

@app.route('/')
def index_template():
    session.clear()
    return render_template('index.html')


@app.route('/contact')
def contact_template():
    return render_template('contact.html')


@app.route('/place_rate/<string:place>')
def rating_template1(place):
    places = Rating.from_place_id(place)
    return render_template('rating1.html', places=places,username=session['username'], picture=session['picture'])


@app.route('/Rest')
def rating_template2():
    return render_template('rating2.html')


@app.route('/hotel')
def rating_template3():
    return render_template('rating3.html')


@app.route('/about')
def about_template():
    return render_template('about.html')


@app.route('/home')
def home_template():
    return render_template('home.html', username=session['username'], picture=session['picture'])


@app.route('/profile/<string:username>')
def profile_template(username):
    users = session['username']
    if username is not None:
        user = User.get_by_username(users)
    users1 = user.show_all_list(username)
    posts = Post.from_user_topic(session['username'])
    lists = List.from_user_list(session['username'])
    return render_template('profile.html', users=users1, username=session['username'],
                           picture=session['picture'], posts=posts, lists=lists)


@app.route('/edit_profile', methods=['POST'])
def edit_man():
        picture1 = session['picture']
        print(picture1)
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        phone = request.form['mobile']
        username = session['username']
        col1 = Database.DATABASE['users']
        col1.update_one({"username": username},
                        {"$set": {"first_name": first_name, "last_name": last_name, "gender": gender, "phone": phone}},
                        upsert=False)
        flash("Edited Successfully", category='success')
        return render_template('home.html', username=session['username'], picture =session['picture'])


@app.route('/edit_profile2')
def edit_template():
    return render_template('edit_profile.html', username=session['username'],
                           picture=session['picture'])




@app.route('/login')
def login_template():
    session.clear()
    return render_template('login.html')


@app.route('/bucket_new', methods=['POST', 'GET'])
def create_new_list():
    if request.method == 'GET':
        return render_template('bucket.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_username(session['username'])

        List.lists(user.username, title, description)
        flash("Posted Successfully", category='success')
        return make_response(show_lists(user.username))


@app.route('/lists_show/<string:username>')
@app.route('/lists_show')
def show_lists(username):
    users = session['username']
    if username is not None:
        user = User.get_by_username(users)
    lists = List.from_user_list(session['username'])
    return render_template('bucket.html', lists=lists, username=session['username'], picture=session['picture'])


@app.route('/bucket')
def bucket_template():
    return render_template('bucket.html', username=session['username'], picture=session['picture'])


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.route('/city_map')
def city_map_template():
    cities = Cities.from_all_cities()
    return render_template('city.html', cities=cities, username=session['username'], picture=session['picture'])


@app.route('/place_map/<string:city>')
@app.route('/place_map')
def place_map_template(city):
    df, df1 = [], []
    col1 = Database.DATABASE['place_rec']
    col1.drop()
    for food in Database.find(collection='place', query={}):
        food1 = Database.find(collection='place', query={})
        df = pd.DataFrame(list(food1))

    for cols in Database.find('rating_place', {}).limit(1):
        food2 = Database.find('rating_place', {})
        df1 = pd.DataFrame(list(food2))

    rating_count = pd.DataFrame(df1, columns=['place_id', 'no_of_rating'])
    rating_count = rating_count.sort_values('no_of_rating', ascending=False)
    rating_count1 = rating_count['place_id'][:10]
    rating_count1 = rating_count1.values.tolist()
    rating = pd.DataFrame(df1.groupby('place_id')['no_of_rating'].mean())
    rating.sort_values('no_of_rating', ascending=False)
    rating_pivot = pd.pivot_table(data=df1, values='user_rating', index='user_id', columns='place_id')
    oneman = rating_pivot[rating_count1[1]]
    similar_to = rating_pivot.corrwith(oneman)
    corr_oneman = pd.DataFrame(similar_to, columns=['PearsonR'])
    oneman_sum = corr_oneman.join(rating)
    oneman_sum1 = oneman_sum.sort_values('PearsonR', ascending=False)
    oneman_sum2 = oneman_sum1.index.values.tolist()
    place_coor = pd.DataFrame(oneman_sum2, index=np.arange(160), columns=['place_id'])
    sumarry = pd.merge(place_coor, df, on='place_id')
    places = sumarry[:10]
    record = places.to_dict('records')
    Database.insert('place_rec', record)
    foods = [p for p in Database.find(collection='place_rec', query={})]
    #sumarry = json.loads(sumarry[:10].to_json()).values()
    #places=[i for i in sum1]
    #places = Place.from_city_place(city)
    place = Database.find("place",{'city':city})
    df2 = pd.DataFrame(list(place))
    m = folium.Map(location=[15.6, 74.6], tiles="OpenStreetMap", zoom_start=10)
    for i in range(len(df2)):
        icon_url = 'https://cdn1.iconfinder.com/data/icons/maps-locations-2/96/Geo2-Number-512.png'
        icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
        popup=folium.Popup(df2.iloc[i]['Location'], parse_html=True)
        folium.Marker([df2.iloc[i]['lat'], df2.iloc[i]['lon']], popup=popup, icon=icon).add_to(m)
    m.save('templates/map.html')
    return render_template('place_map.html', foods=foods, username=session['username'], picture=session['picture'])


@app.route('/place_rating/<string:place_id>', methods=['POST'])
def place_ratings(place_id):
    rate = request.form['name']
    username = session['username']
    user = User.get_by_username(username)
    user1 = user._id
    rating = float(place_id)
    np.set_printoptions(precision=1)
    q = np.random.uniform(low=1.0, high=5.0, size=1)
    q = '%.1f'%q
    c = np.random.randint(low=100, high=10000, size=1)
    data = {"place_id":rating,
            "avg_rating": q,
            "no_of_rating": c,
            "user_id": user1,
            "user_rating": rate}
    place_rating = pd.DataFrame(data, columns=["place_id", "avg_rating", "no_of_rating", "user_id", "user_rating"])
    places = place_rating.to_dict(orient='records')
    Database.insert('rating_place', places)
    print(places)
    flash("Rated Successfully", category='success')
    return render_template('home.html', username=session['username'], picture=session['picture'])

@app.route('/hotel_map/<string:city>')
@app.route('/hotel_map')
def hotel_map_template(city):
    df1, df = [], []
    col1 = Database.DATABASE['hotel_rec']
    col1.drop()
    for food in Database.find(collection='Hotel', query={}):
        food1 = Database.find(collection='Hotel', query={})
        df = pd.DataFrame(list(food1))

    for cols in Database.find('Hotel_rating', {}).limit(1):
        food2 = Database.find('Hotel_rating', {})
        df1 = pd.DataFrame(list(food2))

    rating_count = pd.DataFrame(df1, columns=['hotel_id', 'no_of_rating'])
    rating_count = rating_count.sort_values('no_of_rating', ascending=False)
    rating_count1 = rating_count['hotel_id'][:10]
    rating_count1 = rating_count1.values.tolist()
    rating = pd.DataFrame(df1.groupby('hotel_id')['no_of_rating'].mean())
    rating.sort_values('no_of_rating', ascending=False)
    rating_pivot = pd.pivot_table(data=df1, values='user_rating', index='user_id', columns='hotel_id')
    oneman = rating_pivot[rating_count1[1]]
    similar_to = rating_pivot.corrwith(oneman)
    corr_oneman = pd.DataFrame(similar_to, columns=['PearsonR'])
    oneman_sum = corr_oneman.join(rating)
    oneman_sum1 = oneman_sum.sort_values('PearsonR', ascending=False)
    oneman_sum2 = oneman_sum1.index.values.tolist()
    place_coor = pd.DataFrame(oneman_sum2, index=np.arange(161), columns=['hotel_id'])
    sumarry = pd.merge(place_coor, df, on='hotel_id')
    places = sumarry[:10]
    record = places.to_dict('records')
    Database.insert('hotel_rec', record)
    foods = [p for p in Database.find(collection='hotel_rec', query={})]
    #sumarry = json.loads(sumarry[:10].to_json()).values()
    #places=[i for i in sum1]
    #places = Place.from_city_place(city)
    place = Database.find("Hotel",{'City':city})
    df2 = pd.DataFrame(list(place))
    m = folium.Map(location=[15.6, 74.6], tiles="OpenStreetMap", zoom_start=10)
    for i in range(len(df2)):
        icon_url = 'https://cdn1.iconfinder.com/data/icons/maps-locations-2/96/Geo2-Number-512.png'
        icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
        popup=folium.Popup(df2.iloc[i]['Location'], parse_html=True)
        folium.Marker([df2.iloc[i]['lat'], df2.iloc[i]['lon']], popup=popup, icon=icon).add_to(m)
    m.save('templates/map.html')
    return render_template('hotel_map.html',  foods=foods,username=session['username'], picture=session['picture'])


@app.route('/city_map1')
def city_hotel_template():
    cities = Cities.from_all_cities()
    return render_template('city1.html', cities=cities, username=session['username'], picture=session['picture'])


@app.route('/city_map2')
def city_rest_template():
    cities = Cities.from_all_cities()
    return render_template('city2.html', cities=cities, username=session['username'], picture=session['picture'])



@app.route('/rest_map/<string:city>')
@app.route('/rest_map')
def rest_map_template(city):
    df, df1 = [], []
    col1 = Database.DATABASE['rest_rec']
    col1.drop()
    for food in Database.find(collection='Resturants', query={}):
        food1 = Database.find(collection='Resturants', query={})
        df = pd.DataFrame(list(food1))

    for cols in Database.find('Rest_rating', {}).limit(1):
        food2 = Database.find('Rest_rating', {})
        df1 = pd.DataFrame(list(food2))

    rating_count = pd.DataFrame(df1, columns=['rest_id', 'no_of_rating', 'avg_rating'])
    rating_count = rating_count.sort_values('no_of_rating', ascending=False)
    rating_count1 = rating_count['rest_id'][:10]
    rating_count1 = rating_count1.values.tolist()
    rating = pd.DataFrame(df1.groupby('rest_id')['no_of_rating', 'avg_rating'].mean())
    print(rating)
    rating.sort_values('no_of_rating', ascending=False)
    rating_pivot = pd.pivot_table(data=df1, values='user_rating', index='user_id', columns='rest_id')
    oneman = rating_pivot[rating_count1[1]]
    similar_to = rating_pivot.corrwith(oneman)
    corr_oneman = pd.DataFrame(similar_to, columns=['PearsonR'])
    oneman_sum = corr_oneman.join(rating)
    oneman_sum1 = oneman_sum.sort_values('PearsonR', ascending=False)
    oneman_sum2 = oneman_sum1.index.values.tolist()
    place_coor = pd.DataFrame(oneman_sum2, index=np.arange(393), columns=['rest_id'])
    sumarry = pd.merge(place_coor, df, on='rest_id')
    places = sumarry[:10]
    record = places.to_dict('records')
    Database.insert('rest_rec', record)
    foods = [p for p in Database.find(collection='rest_rec', query={})]
    #sumarry = json.loads(sumarry[:10].to_json()).values()
    #places=[i for i in sum1]
    #places = Place.from_city_place(city)
    place = Database.find("Resturants",{'City':city})
    df2 = pd.DataFrame(list(place))
    m = folium.Map(location=[15.6, 74.6], tiles="OpenStreetMap", zoom_start=10)
    for i in range(len(df2)):
        icon_url = 'https://cdn1.iconfinder.com/data/icons/maps-locations-2/96/Geo2-Number-512.png'
        icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
        popup=folium.Popup(df2.iloc[i]['Location'], parse_html=True)
        folium.Marker([df2.iloc[i]['lat'], df2.iloc[i]['lon']], popup=popup, icon=icon).add_to(m)
    m.save('templates/map.html')
    return render_template('rest_map.html', foods=foods,username=session['username'], picture=session['picture'])


@app.route('/city', methods = ['POST', 'GET'])
def city_maps():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        city = request.form['city']
        geolocator = Nominatim(user_agent="Test")
        location = geolocator.geocode(city)
        lat = location.latitude
        lon = location.longitude
        check = Cities.find_by_city(city)
        if Cities.from_mongo(city):
            return make_response(city_places(city))
        else:
            new_city = Cities(city, lat, lon)
            new_city.save_to_mongo()
            flash("Posted Successfully", category='success')
        return make_response(city_places(city))


@app.route('/place/<string:city>')
@app.route('/place')
def city_places(city):
    cities = Cities.find_by_city(city)
    return render_template("city_map.html", cities=cities, username=session['username'], picture=session['picture'])


@app.route('/travel')
def travel_template():
    return render_template('travel.html',username=session['username'], picture=session['picture'])


@app.route('/travel_choice')
def travel_choice_template():
    return render_template('travel_choice.html',username=session['username'], picture=session['picture'])


@app.route('/promo_new', methods=['POST', 'GET'])
def create_new_promo():
    if request.method == 'GET':
        return render_template('travel.html')
    else:
        agencyname = request.form['agencyname']
        mobile = request.form['mobile']
        message = request.form['message']
        username = session['username']
        Promotion.promos(agencyname, mobile, message)
        flash("Posted Successfully", category='success')
        return make_response(promolist())


@app.route('/promos_list/<string:user_id>')
@app.route('/promos')
def promolist():
    df =[]
    a = np.random.randint(low=1, high=10, size=10)
    a = a.tolist()
    b = secrets.choice(a)
    col1 = Database.DATABASE['promo_rec']
    col1.drop()
    # foods = Food.recommend(b)
    # foods = Food.food_show()
    food_vec = TfidfVectorizer(stop_words='english')
    for food in Database.find(collection='promo', query={}).limit(1):
        food1 = Database.find(collection='promo', query={})
        df = pd.DataFrame(list(food1))

    print(df)
    df['descirption'] = df['description'].fillna('')
    food_td_mat = food_vec.fit_transform(df['description'])
    cos_sim = linear_kernel(food_td_mat, food_td_mat)
    indiecs = pd.Series(df['agencyname'].index)
    id = indiecs[b]
    sim_score = list(enumerate(cos_sim[id]))
    sim_score = sorted(sim_score, key=lambda x: x[1], reverse=True)
    sim_score = sim_score[1:5]
    food_index = [i[0] for i in sim_score]
    food = df.iloc[food_index]
    #food = json.loads(df.iloc[food_index].T.to_json()).values()
    record = food.to_dict('records')
    Database.insert('promo_rec', record)
    #topics = [p for p in Database.find(collection='promo_rec', query={})]
    #topics = foods['description','agencyname', 'mobile']
    foods = [p for p in Database.find(collection='promo_rec', query={})]
    return render_template("travel.html", foods=foods, username=session['username'], picture=session['picture'])


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/contact_new', methods=['POST'])
def create_new_con():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        username = request.form['username']
        email = request.form['email']
        message = request.form['message']

        Con.cons(username, email, message)
        flash("Posted Successfully", category='success')
        return render_template("contact.html")


@app.route('/auth_login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    if User.login_valid(username, password):
        User.login(username)
    else:
        session['username'] = None
        return render_template("index.html")

    currentTime = datetime.datetime.now()
    if currentTime.hour < 12:
        Time = "Morning"
    elif 12 <= currentTime.hour < 18:
        Time = "Afternoon"
    else:
        Time = "Evening"

    return render_template("home.html", username=session['username'], picture=session['picture'], Time=Time)


@app.route('/logout')
def logout_user():
    User.logout()
    return render_template('index.html')


@app.route('/public_travel')
def public_template():
    return render_template('public_travel.html',username=session['username'], picture=session['picture'])


@app.route('/auth_register', methods=['POST'])
def register_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    gender = request.form['gender']
    phone = request.form['mobile']
    picture = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    email1 = Database.find_one("users", {'email':email})
    user1 = Database.find_one("users",{'username':username})
    if email1 is not None or user1 is not None:
        flash("Username or email Taken", category='danger')
        return render_template("register.html")
    elif email1 is None and user1 is None:
        User.register(email, username, password, first_name, last_name, gender, phone, picture)
        flash("Registered Successfully", category='success')
        return render_template("register.html")


@app.route('/chrip/<string:user_id>')
@app.route('/chrips')
def user_chrips(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_username(session['username'])

    topics = user.get_chrips()

    return render_template("user_chrips.html", topics=topics, username=user.username, picture=session['picture'])


@app.route('/chrip_new', methods=['POST', 'GET'])
def create_new_chrip():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_username(session['username'])

        new_blog = Topic(user.username, title, description, user._id)
        new_blog.save_to_mongo()
        flash("Posted Successfully", category='success')
        return make_response(user_chrips(user._id))


@app.route('/view_user_all/<string:topic_id>')
def user_post(topic_id):
    topic = Topic.from_mongo(topic_id)
    posts = topic.get_posts()
    return render_template('posts.html', posts=posts, topic_title=topic.title, topic_id=topic._id,
                           username=session['username'], picture=session['picture'])


@app.route('/new_post/<string:topic_id>', methods=['POST', 'GET'])
def new_post(topic_id):
    if request.method == 'GET':
        return render_template('new_post.html', topic_id=topic_id)
    else:
        message = request.form['content']
        user = User.get_by_username(session['username'])
        topic = Topic.from_mongo(topic_id)

        new_post = Post( message, topic_id,user.username,user.picture,topic.description,topic.title)
        new_post.save_to_mongo()

        return make_response(user_post(topic_id))


@app.route('/all_post')
def all_post():
    posts = Post.from_all_topic()
    return render_template('all_post.html', posts=posts, username=session['username'], picture=session['picture'])


@app.route('/food_rec')
def food_red():
    a = np.random.randint(low=1, high=100, size=150)
    a = a.tolist()
    b = secrets.choice(a)
    col1 = Database.DATABASE['food_rec']
    col1.drop()
    #foods = Food.recommend(b)
    #foods = Food.food_show()
    food_vec = TfidfVectorizer(stop_words='english')
    for food in Database.find(collection='food', query={}):
        food1 = Database.find(collection='food', query={})
        df = pd.DataFrame(list(food1))
        #print(df)

    df['Descrptions'] = df['Descrptions'].fillna('')
    food_td_mat = food_vec.fit_transform(df['Descrptions'])
    cos_sim = linear_kernel(food_td_mat, food_td_mat)
    indiecs = pd.Series(df['Dishes'].index)
    id = indiecs[b]
    sim_score = list(enumerate(cos_sim[id]))
    sim_score = sorted(sim_score, key=lambda x: x[1], reverse=True)
    sim_score = sim_score[1:11]
    food_index = [i[0] for i in sim_score]
    #foods = df.iloc[food_index]
    food = json.loads(df.iloc[food_index].T.to_json()).values()
    Database.insert('food_rec', food)
    foods = [p for p in Database.find(collection='food_rec', query={})]
    return render_template('food.html',foods=foods ,username=session['username'], picture=session['picture'])


if __name__ == '__main__':
    app.run(port=5000, debug=True)
