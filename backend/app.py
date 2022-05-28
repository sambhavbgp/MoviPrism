from flask import *
from recommender import *
from flask_cors import CORS
import numpy as np
import json
import os
import pandas as pd
import requests

app = Flask(__name__)
CORS(app)

df = pd.read_csv("title_to_tmdb_id.csv")

# @app.route("/")
# def index():
#     return render_template("index.html")


@app.route("/search")
def search():
    n = request.args.get("name")
    filtered_data = df[df["name"].str.contains(n, case=False)].head(5)
    jsonData = filtered_data.to_dict(orient="records")
    for i in jsonData:
        ID = i["id"]
        r = requests.get(
            f"https://api.themoviedb.org/3/movie/{ID}?api_key=4e5a5661e752328d0a6b2463aec07f5e&language=en-US"
        )
        tmdbResponse = r.json()
        i["adult"] = tmdbResponse["adult"]
        i["poster"] = tmdbResponse["poster_path"]
        i["genres"] = []
        for j in tmdbResponse["genres"] :
            i["genres"].append(j["name"])
        
    return Response(json.dumps(jsonData), headers={"Content-Type": "application/json"})


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

#get movie id from url and return the recommended movie id
@app.route('/')
def index():
    movie_id = request.args.get('movie_id')
    if movie_id:
        movie_id = int(movie_id)
        recommend_movie_ids = recommend_same_genre_movie(movie_id)
        
        # print(recommend_movie_ids)
        # print(jsonify(results = recommend_movie_ids))
        # results = json.dumps(recommend_movie_ids)
        # print(results)
        return jsonify(results = recommend_movie_ids)
        return render_template('index.html', movie_id=movie_id, recommend_movie_ids=recommend_movie_ids,len = len(recommend_movie_ids))
    else:
        return 'Recommender API'

if __name__ == '__main__':
    app.run()