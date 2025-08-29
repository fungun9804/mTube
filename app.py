import os
import json
import flask
from databaser import Databaser
from datetime import datetime
from flask import Flask, request, jsonify, render_template


app = flask.Flask(__name__)
db = Databaser()


COMMENTS_DIR = os.path.join('static', 'comments')
if not os.path.exists(COMMENTS_DIR):
    os.makedirs(COMMENTS_DIR)

def get_comment_file_path(video_id):
    return os.path.join(COMMENTS_DIR, f"{video_id}.txt")

def add_comment(video_id, author, text):
    comment_file = get_comment_file_path(video_id)
    
    comment_data = {
        'id': datetime.now().timestamp(),
        'author': author,
        'text': text,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(comment_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(comment_data, ensure_ascii=False) + '\n')
    
    return comment_data
    
def get_comments(video_id):
    comment_file = get_comment_file_path(video_id)
    comments = []

    
    if not os.path.exists(comment_file):
        print(f"Comment file not found: {comment_file}")
        return comments
    
    try:
        with open(comment_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Read {len(lines)} lines from comment file")
            
            for line in lines:
                line = line.strip()
                if line:
                    try:
                        comment_data = json.loads(line)
                        comments.append(comment_data)
                        print(f"Successfully parsed comment: {comment_data}")
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        print(f"Problematic line: {line}")
                        continue
    except Exception as e:
        print(f"Error reading file {comment_file}: {e}")
    
    print(f"Returning {len(comments)} comments")
    return comments

@app.route('/')
def root():
    videos = db.get_videos()
    return flask.render_template('index.html', videos=videos)


@app.route('/<video_id>')
def video_page(video_id):
    video = db.get_video(video_id)

    if video is None:
        return 'Видео не найдено'

    return flask.render_template('video_page.html', video=video)


@app.route('/<video_id>/like', methods=['POST'])
def like_video(video_id):
    video_id = int(video_id)
    db.like_video(video_id)
    return 'ok'

@app.route('/<video_id>/dislike', methods=['POST'])
def dislike_video(video_id):
    video_id = int(video_id)
    db.dislike_video(video_id)
    return 'ok'

@app.route('/video/<int:video_id>/comments', methods=['GET'])
def get_comments_route(video_id):
    try:
        comments = get_comments(video_id)
        return jsonify({'success': True, 'comments': comments})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'comments': []})

@app.route('/video/<int:video_id>/comment', methods=['POST'])
def add_comment_route(video_id):
    try:
        data = request.get_json()
        author = data.get('author', 'Аноним')
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'error': 'Комментарий не может быть пустым'})
        
        comment = add_comment(video_id, author, text)
        return jsonify({'success': True, 'comment': comment})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    

    
