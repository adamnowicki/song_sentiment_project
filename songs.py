from flask import Flask
import pymysql
from flask import request 
import math
from flask_basicauth import BasicAuth
import json
from flask import abort
import os
from flask_swagger_ui import get_swaggerui_blueprint

swaggerui_blueprint = get_swaggerui_blueprint(
    base_url='/docs',
    api_url='/static/openapi.yaml',)

app = Flask(__name__)
mysql_password = "19Klipsch46"
app.register_blueprint(swaggerui_blueprint)
auth = BasicAuth(app)
app.config.from_file("flask_config.json", load=json.load)
MAX_PAGE_SIZE = 50


@app.route("/artists/<artist>")
@auth.required
def artist(artist):

    db_conn= pymysql.connect(host="localhost", user="root", password=mysql_password, database="song_sentiment_db", cursorclass=pymysql.cursors.DictCursor)
    artist = artist.replace("_", " ")

    
    with db_conn.cursor() as cursor:
        cursor.execute("""
            SELECT s.artist FROM songs AS s
            WHERE s.artist = %s
        """, (artist,))
        artist_info = cursor.fetchone()

        if artist_info:
            cursor.execute("""
                SELECT s.title, sent.positive_score, sent.negative_score, sent.neutral_score 
                FROM songs_sentiment AS sent
                LEFT JOIN songs AS s ON sent.song_id = s.song_id
                WHERE s.artist = %s
            """, (artist,))
            songs = cursor.fetchall()

            artist_info['songs'] = [{'title': s['title'], 'positive_score': s['positive_score'], 'negative_score': s['negative_score'], 'neutral_score': s['neutral_score']} for s in songs]
            return artist_info
        else:
            return f"Artist '{artist}' not found", 404

@app.route("/genres/<genre>")
@auth.required
def genre(genre):
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)
    db_conn= pymysql.connect(host="localhost", user="root", password=mysql_password, database="song_sentiment_db", cursorclass=pymysql.cursors.DictCursor)
    offset = (page - 1) * page_size
    
    with db_conn.cursor() as cursor:
        cursor.execute("""
            SELECT s.tag FROM songs AS s
            WHERE s.tag = %s
        """, (genre,))
        genre_info = cursor.fetchone()

        if genre_info:
            cursor.execute("""
                  SELECT s.title, s.artist, s.tag, sent.positive_score, sent.negative_score, sent.neutral_score 
    FROM songs_sentiment AS sent
    LEFT JOIN songs AS s ON sent.song_id = s.song_id
    WHERE s.tag = %s
    LIMIT %s OFFSET %s
""", (genre, page_size, offset))
            songs = cursor.fetchall()

            genre_info['songs'] = [{'title': s['title'], 'artist': s['artist'],'positive_score': s['positive_score'], 'negative_score': s['negative_score'], 'neutral_score': s['neutral_score']} for s in songs]
        
        with db_conn.cursor() as cursor:
            cursor.execute("Select count(*) as total from songs")
            total = cursor.fetchone()
            last_page=math.ceil(total['total']/ page_size)

         
        db_conn.close()
            
        return {
        'genre': genre_info,
        'next_page': f'/genres?page={page+1}&page_size={page_size}',
        'last_page': f'/genres?page={last_page}&page_size={page_size}',
    }     
    #else:
            #return f"Artist '{artist}' not found", 404
    
    

if __name__ == "__main__":
    app.run(debug=True)


