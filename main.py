from flask import *
import os, base64, sqlite3, random, string, requests, datetime
from telegraph import upload_file
#from flask_ngrok import run_with_ngrok

conn = sqlite3.connect('db.db', check_same_thread=False)
c = conn.cursor()

app=Flask(__name__)
app.secret_key="okVaiFuckYou"
#run_with_ngrok(app)

def createdb():
    c.execute('''CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, visits INTEGER DEFAULT 0, time TEXT)''')
createdb()



def saveIMG(name, url):
    time=str(datetime.datetime.now())
    c.execute('INSERT INTO images (name, url, time) VALUES (?, ?, ?)', (name, url, time))
    conn.commit()



def getIMG(name):
    c.execute('SELECT url FROM images WHERE name = ?', (name,))
    result = c.fetchone()
    
    if result:
        c.execute("UPDATE images SET visits=visits+1 WHERE name=?", (name,))
        conn.commit()
        print(result)
        return result[0]
        
    else:
        return None

def getInfoFromName(name):
    c.execute('SELECT visits, time FROM images WHERE name = ?', (name,))
    result = c.fetchone()
    
    if result:
        return result
    else:
        return None

def getRandomName(n=10):
    h=""
    for ok in range(n):
        h=h+random.choice(string.digits+string.ascii_uppercase)
    return h 



def getImgData(url):
    response = requests.get(url)
    if response.status_code == 200:
        content_type = response.headers['Content-Type']
        if 'image' in content_type:
            #image_data = base64.b64encode(response.content).decode('utf-8')
            image_data=response.content
            return image_data
    return None



@app.route("/")
def home():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Upload Image</title>
</head>
<body>
    <h1>Upload Image</h1>
    <form action="/api/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="image">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""


@app.route("/api/upload", methods=["POST"])
def upload_image():
    if request.files['image']:
        file = request.files['image']
        name=getRandomName(20)
        file.save(name+".jpg")
    
        
        #print(image_b64)
       # telegraph.Telegraph.create_account(short_name="wolfiexe9872")
        response = upload_file(name+".jpg")
        os.remove(name+".jpg")
        if response:
            url = 'https://telegra.ph' + response[0]
            
            saveIMG(name, url)
            return "ID: "+name+"\n\nhttp://127.0.0.1:5000/"+name
        else:
            return 'Error uploading image'
    else:
        return "Image Not Saved"


@app.route("/api/info/<name>")
def renderIMG(name):
    telegra=getInfoFromName(name)
    if telegra!=None:
        url=request.host_url+name
        visits=telegra[0]
        time=telegra[1]
        return jsonify(url=url, visits=visits, name=name, time=time)
    return "invalid alias"



@app.route("/<name>")
def infoapi(name):
    telegra=getIMG(name)
    if telegra!=None and "telegra.ph" in telegra:
        imgData=getImgData(telegra)
        if imgData!=None:
            try:
                return Response(imgData, mimetype='image/jpeg')
            except:
                return "Error"
        else:
            return "image deleted"
    return "invalid alias"

    
app.run(theaded=True)
