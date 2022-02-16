from flask import Flask, request, send_file
app = Flask(__name__)

@app.route('/<path:path>')
def forecast(path):
#     path = request.args.get('filePath')
    return send_file(path, as_attachment=True)
#     return {'name': request.args.get('name'), 'time': request.args.get('time')}

if __name__ == "__main__":
    app.run()
