import boto3
import requests
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import pandas as pd

url = "https://bank.gov.ua/NBU_Exchange/exchange_site?start=20210101&end=20211231&valcode=eur&sort=exchangedate&order=desc&json"
response = requests.get(url)
data = response.json()

BUCKET_NAME = 'clotbucket'

FILE_NAME = 'EUR_UAH_exchange.csv'
s3 = boto3.client('s3')

csv_buffer = StringIO()
csv_buffer.write(",".join(str(name) for name in data[0].keys()))
for row in data:
    csv_buffer.write(",".join(str(val) for val in row.values()) + "\n")
csv_buffer.seek(0)

s3.put_object(Bucket=BUCKET_NAME, Key=FILE_NAME, Body=csv_buffer.getvalue().encode('utf-8'))

response = s3.get_object(Bucket='clotbucket', Key='EUR_UAH_exchange.csv')

data = response['Body'].read().decode('utf-8')

df_eur = pd.read_csv(StringIO(data))

response = s3.get_object(Bucket='clotbucket', Key='USD_UAH_exchange.csv')

data = response['Body'].read().decode('utf-8')

df_usd = pd.read_csv(StringIO(data))

plt.plot(df_usd['exchangedate'], df_usd['rate'], label='USD')
plt.plot(df_eur['exchangedate'], df_eur['rate'], label='EUR')

plt.title('Курс валют відносно гривні')
plt.xlabel('Дата')
plt.ylabel('Курс')

plt.legend()
plt.show()

buf = BytesIO()
plt.savefig(buf, format='jpeg')

buf.seek(0)
img_data = buf.getvalue()

s3.put_object(Bucket='clotbucket', Key='exchange_usd_eur_uah.jpg', Body=img_data)