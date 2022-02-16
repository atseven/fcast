from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def forecast():
    return {'name': request.args.get('name'), 'time': request.args.get('time')}

if __name__ == "__main__":
    app.run()
