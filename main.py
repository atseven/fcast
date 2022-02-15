from flask import Flask
app = Flask(__name__)

@app.get('/')
def forecast():
    return {'message': "rana"}

if __name__ == "__main__":
    app.run()
