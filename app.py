from flask import Flask, request, send_file
import requests
app = Flask(__name__)

@app.route('/')
def user_download():
    url = request.args['url']  # user provides url in query string
    r = requests.get(url)

    # write to a file in the app's instance folder
    # come up with a better file name
    with app.open_instance_resource('downloaded_file', 'wb') as f:
        f.write(r.content)
        
# @app.route('/<path:path>')
# def forecast(path):
# #     path = request.args.get('filePath')
#     return send_file(path[5:], as_attachment=True)
# #     return {'name': request.args.get('name'), 'time': request.args.get('time')}

if __name__ == "__main__":
    app.run()
