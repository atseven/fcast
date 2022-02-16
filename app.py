from flask import Flask, request, send_file
import requests
from fbprophet import Prophet # Prophet modelling library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
from datetime import datetime
import dropbox
import io
from PIL import Image

app = Flask(__name__)

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

  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  im = Image.open(buf)
  buf = io.BytesIO()
  im.save(buf, format='png')
  byte_im = buf.getvalue()

  dbx_ob.files_upload(
      f=byte_im,
      path=path + "/Original Data.png",
      mode=dropbox.files.WriteMode.overwrite
  )
  buf.close()


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

  buf = io.BytesIO()
  plot1.savefig(buf, format='png')
  buf.seek(0)
  im = Image.open(buf)
  buf = io.BytesIO()
  im.save(buf, format='png')
  byte_im = buf.getvalue()

  dbx_ob.files_upload(
      f=byte_im,
      path= path + "/Prediction Plot 2.png",
      mode=dropbox.files.WriteMode.overwrite
  )
  # im.show()
  buf.close()

  plot2 = mod.plot_components(predictions)
  buf = io.BytesIO()
  plot2.savefig(buf, format='png')
  buf.seek(0)
  im = Image.open(buf)
  buf = io.BytesIO()
  im.save(buf, format='png')
  byte_im = buf.getvalue()

  dbx_ob.files_upload(
      f=byte_im,
      path=path + "/Trend Plot.png",
      mode=dropbox.files.WriteMode.overwrite
  )
  # im.show()
  buf.close()

def predictionPlot(x, y, filename="EAN", dbx_ob="", path="/forecast", fileName=""):
  sns.set()
  plt.figure(figsize=(20,5))
  plt.title(filename)
  plt.ylabel('Quantity')
  plt.xlabel('Date')
  plt.xticks(rotation=45)
  plt.plot(x, y)

  buf = io.BytesIO()
  plt.savefig(buf, format='png')
  buf.seek(0)
  im = Image.open(buf)
  buf = io.BytesIO()
  im.save(buf, format='png')
  byte_im = buf.getvalue()

  dbx_ob.files_upload(
      f=byte_im,
      path=path + "/" + fileName + ".png",
      mode=dropbox.files.WriteMode.overwrite
  )
  # im.show()
  buf.close()

def upload_predictions(dataframe, dbx_ob, path):

    df_string = dataframe.to_csv(index=False)
    db_bytes = bytes(df_string, 'utf8')
    dbx_ob.files_upload(
        f=db_bytes,
        path=path + "/Future Sales.csv",
        mode=dropbox.files.WriteMode.overwrite
    )

@app.route('/')
def predict_forecast():
    filepath = str(request.args.get('filepath'))
    days=int(request.args.get('days'))
    access_token= str(request.args.get('token'))

    print("\n\nPlease wait, future sales are predicting...\n")

    data = pd.read_csv(filepath)
    data, filename = preprocessing(data)

    dbx = dropbox.Dropbox(access_token)
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y%H:%M:%S")

    dbx.files_create_folder_v2("/forecast/" + dt_string)

    plotData(data, dbx, path="/forecast/" + dt_string)

    model = buildModel(data)
    predictions = predict(model, days)

    trendPlot(model, predictions, dbx, path="/forecast/" + dt_string)

    predictionPlot(predictions['ds'], predictions['yhat'], "Possible Future Sales", dbx, path="/forecast/" + dt_string, fileName="Prediction Plot 1")
    predictionPlot(predictions['ds'], predictions['yhat_upper'], "Max Possible Future Sales", dbx, path="/forecast/" + dt_string, fileName="Max Prediction Plot")

    predictions = predictions[['ds', 'yhat', 'yhat_upper']].round(decimals = 2)
    predictions.columns = ['Date', 'Quantity', 'Max Quantity']

    upload_predictions(predictions, dbx, path="/forecast/" + dt_string)

    return {'Success': "Forecast predicted !"}

if __name__ == "__main__":
    app.run()

