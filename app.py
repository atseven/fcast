from flask import Flask
app = Flask(__name__)

@app.route('/')
def forecast(name: str, time: int):
    return {'message': name, 'time': time}

if __name__ == "__main__":
    app.run()
