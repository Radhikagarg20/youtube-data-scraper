from flask import Flask, render_template, request, jsonify
import googleapiclient.discovery

app = Flask(__name__)

YOUTUBE_API_KEY = "AIzaSyBuxWONaSwq6rFR398Nw1P3ZU0Cw0KRp7E"

def scrape_yt_data(url, data_type):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    if "watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
        channel_id = None
    elif "/channel/" in url:
        channel_id = url.split("/channel/")[-1].split("/")[0]
        video_id = None
    else:
        return {"error": "Invalid URL"}

    if video_id:
        if data_type == 'comments':
            request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=100)
            response = request.execute()
            return [{
                "author": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
            } for item in response.get("items", [])]
        elif data_type == 'likes':
            request = youtube.videos().list(part="statistics", id=video_id)
            response = request.execute()
            return {"likes": response.get("items", [])[0]["statistics"]["likeCount"]}
        elif data_type == 'views': 
            request = youtube.videos().list(part="statistics", id=video_id)
            response = request.execute()
            return {"views": response.get("items", [])[0]["statistics"]["viewCount"]}
        else:
            return {"error": "Invalid YouTube video request."}
    
    elif channel_id:
        if data_type == 'subscribers':
            request = youtube.channels().list(part="statistics", id=channel_id)
            response = request.execute()
            return {"subscribers": response.get("items", [])[0]["statistics"]["subscriberCount"]}
        else:
            return {"error": "Invalid YouTube channel request."}
    
    return {"error": "Invalid URL or data type"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    data_type = request.form['data_type']
    result = scrape_yt_data(url, data_type)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
