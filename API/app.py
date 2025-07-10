from flask import Flask, jsonify
import psycopg2
import hashlib

app = Flask(__name__)




@app.route('/search/<text>', methods=['GET'])
def search(text):
    text = text.replace(" ", "%")

    conn = psycopg2.connect(
    host='postgres',
    port="5432",
    password="postgres",
    dbname="bitmagnet",
    user="postgres"
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM torrents  WHERE name LIKE %s ORDER BY updated_at DESC LIMIT 100", ('%' + text + '%',))

    
    rows = cur.fetchall()
    results = []
    for row in rows:
        md5_hash =row[0].hex()
        magnet= 'magnet:?xt=urn:btih:'+md5_hash+'&tr=udp://opentor.net:6969&tr=http://retracker.local/announce'
        cur0 = conn.cursor()
        query = "SELECT * FROM torrents_torrent_sources  WHERE info_hash = %s"
        cur0.execute(query, (row[0],))
        rows0 = cur0.fetchone()
        results.append({'MagnetUri': magnet,'InfoHash':md5_hash,'Title': row[1], 'Size': row[2], 'Description': row[1], 'PublishDate': row[4], 'updated': row[5],'Seeders': rows0[3],'Peers': rows0[4]})
        cur0.close()

    cur.close()
    conn.close()
    return jsonify(results)



@app.route('/search2/<text>/<text2>', methods=['GET'])
def search2(text,text2):
    text2 = text2.replace(" ", "%")
    text = text.replace(" ", "%")
    conn = psycopg2.connect(
    host='postgres',
    port="5432",
    password="postgres",
    dbname="bitmagnet",
    user="postgres"
    )
    cur = conn.cursor()

    cur.execute("SELECT * FROM torrents  WHERE name LIKE %s or name LIKE %s ORDER BY updated_at DESC LIMIT 100", ('%' + text + '%','%' + text2 + '%',))
    
    rows = cur.fetchall()
    if len(rows) < 4:
        text=text[:-7];
        text2=text2[:-7];
        cur.execute("SELECT * FROM torrents  WHERE name LIKE %s or name LIKE %s ORDER BY updated_at DESC LIMIT 100", ('%' + text + '%','%' + text2 + '%',))
        rows = cur.fetchall()
    results = []
    for row in rows:
        md5_hash =row[0].hex()
        magnet= 'magnet:?xt=urn:btih:'+md5_hash+'&tr=udp://opentor.net:6969&tr=http://retracker.local/announce'
        cur0 = conn.cursor()
        query = "SELECT * FROM torrents_torrent_sources  WHERE info_hash = %s"
        cur0.execute(query, (row[0],))
        rows0 = cur0.fetchone()
        results.append({'MagnetUri': magnet,'InfoHash':md5_hash,'Title': row[1], 'Size': row[2], 'Description': row[1], 'PublishDate': row[4], 'updated': row[5],'Seeders': rows0[3],'Peers': rows0[4]})
        cur0.close()


    cur.close()
    conn.close()
    return jsonify(results)


@app.route('/jpan/', methods=['GET'])
def jpan():
    conn = psycopg2.connect(
    host='postgres',
    port="5432",
    password="postgres",
    dbname="bitmagnet",
    user="postgres"
    )
    cur = conn.cursor()
    query = "SELECT * FROM torrents  WHERE name ~* '([Έ-Ͽ]|[Ա-᱿][Ա-ῼ]|[Ⲁ-⿿]|[ぁ-ﻼ])' ORDER BY created_at DESC LIMIT 50000"
    cur.execute(query)

    
    rows = cur.fetchall()
    results = []
    for row in rows:
        cur0 = conn.cursor()
        cur0.execute("DELETE FROM torrent_files WHERE info_hash = %s", (row[0],))
        cur0.execute("DELETE FROM torrent_contents WHERE info_hash = %s", (row[0],))
        cur0.execute("UPDATE torrents SET name='***' WHERE info_hash= %s", (row[0],))
        conn.commit()
        cur0.close()
        results.append({'name': row[1], 'size': row[2], 'private': row[3], 'created': row[4], 'updated': row[5]})
    cur.execute("DELETE FROM torrent_files  WHERE path ~* '([Έ-Ͽ]|[Ա-᱿][Ա-ῼ]|[Ⲁ-⿿]|[ぁ-ﻼ])'")    
    conn.commit()
    cur.close()
    conn.close()
    return '[{ok}]'

@app.route('/dellex/', methods=['GET'])
def dell():
    conn = psycopg2.connect(
    host='postgres',
    port="5432",
    password="postgres",
    dbname="bitmagnet",
    user="postgres"
    )
   
    cur = conn.cursor()
    mass=['exe','mp4','avi','mkv','wmv','zip','rar','fb2','m4b']
    query = "DELETE FROM torrent_files WHERE extension NOT IN ({0})".format(",".join("'{0}'".format(x) for x in mass))
    cur.execute(query)
    cur.execute("DELETE FROM torrent_files WHERE extension is NULL")
    conn.commit()

    cur.close()
    conn.close()
    return '[{ok}]'


    
if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0', port=5000)