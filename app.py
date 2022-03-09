from flask import Flask, request, send_file
import requests
from fbprophet import Prophet 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
from datetime import datetime

app = Flask(__name__)
run_with_ngrok(app)   

def preprocessing(df):
  try:
    filename = str(df['ean'].iloc[0])
  except:
    filename="EAN"
  df.columns = ['orderid', 'ean', 'qty', 'date']
  df = df[['qty', 'date']]
  df = df.groupby(['date'], as_index=False)['qty'].sum()
  try:
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
  except:
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
  if(df.isna().sum().sum() > 0):
    df.dropna(inplace=True)
  df = df.sort_values(by='date')
  df.columns = ['ds', 'y']
  print(df.shape)
  return df, filename

def plotData(df, dbx_ob, path):
  sns.set()
  plt.figure(figsize=(20,5))
  plt.title('Original Data')
  plt.ylabel('Quantity')
  plt.xlabel('Date')
  plt.xticks(rotation=45)
  plt.plot(df['ds'], df['y'] )


def buildModel(df):
  model = Prophet(interval_width=0.95, yearly_seasonality=True) 
  model.fit(df)
  return model

def predict(mod, days=120):
  future = mod.make_future_dataframe(periods=days, freq='D')
  predictions = mod.predict(future)
  return predictions

def trendPlot(mod, predictions, dbx_ob, path):
  plot1 = mod.plot(predictions)

def predictionPlot(x, y, filename="EAN", dbx_ob="", path="/forecast", fileName=""):
  sns.set()
  plt.figure(figsize=(20,5))
  plt.title(filename)
  plt.ylabel('Quantity')
  plt.xlabel('Date')
  plt.xticks(rotation=45)
  plt.plot(x, y)

def upload_predictions(dataframe, path, storage, auth):

  df_string = dataframe.to_csv(index=False)
  db_bytes = bytes(df_string, 'utf8')

  fileName = "Future Prices.csv"
  storage.child(path + fileName).put(db_bytes)

  # Create Authentication user account in firebase

  # Enter your user account details 
  email = "alwaysstockedj@gmail.com"
  password = "Rana2020win"

  user = auth.sign_in_with_email_and_password(email, password)

  csvUrl = storage.child(path + fileName).get_url(user['idToken'])
  return csvUrl

@app.route('/forecast')
def forecast():
    try:
      filepath = str(request.args.get('filepath'))
      days=int(request.args.get('days'))
      
      print(filepath, days)

      print("\n\nPlease wait, future sales are predicting...\n")

      data = pd.read_csv(filepath)
      data, filename = preprocessing(data)

      firebaseConfig = {
        "apiKey": "AIzaSyAil4rCL7FMyMSBShnSoYWtHrgLubx47T4",
        "authDomain": "forecast-v1.firebaseapp.com",
        "projectId": "forecast-v1",
        "storageBucket": "forecast-v1.appspot.com",
        "messagingSenderId": "421731791843",
        "appId": "1:421731791843:web:06f958dbf0ed4c8380a6d6",
        "databaseURL":"gs://forecast-v1.appspot.com"
      };

      firebase = pyrebase.initialize_app(firebaseConfig)
      storage = firebase.storage()
      auth = firebase.auth()

      now = datetime.now()
      dt_string = now.strftime("%d/%m/%Y%H:%M:%S")

      model = buildModel(data)
      predictions = predict(model, days)

      # trendPlot(model, predictions, dbx, path="/forecast/" + dt_string)

      # predictionPlot(predictions['ds'], predictions['yhat'], "Possible Future Sales", dbx, path="/forecast/" + dt_string, fileName="Prediction Plot 1")
      # predictionPlot(predictions['ds'], predictions['yhat_upper'], "Max Possible Future Sales", dbx, path="/forecast/" + dt_string, fileName="Max Prediction Plot")

      predictions = predictions[['ds', 'yhat', 'yhat_upper']].round(decimals = 2)
      predictions.columns = ['Date', 'Quantity', 'Max Quantity']

      pred_link = upload_predictions(predictions, path="predictions/" + dt_string + "/", storage=storage, auth=auth)

      return {'predictions': pred_link}

    except Exception as e:
      print("error : ", e)
      return {'error': "Something went wrong"}

if __name__ == "__main__":
    app.run()
