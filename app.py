from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder='./vue-frontend/dist', static_url_path='/')

@app.route('/api/hello')
def hello_world():
    return jsonify(message='Hello from Flask!')

@app.route('/')
def serve_vue_app():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)