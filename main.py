import os
import pandas as pd
pd.set_option('display.max_rows', None)
import numpy as np
from twelvedata import TDClient
import time
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 10)
from dotenv import load_dotenv
load_dotenv()

apikey = os.getenv('TWELVE_DATA_API_KEY')
td = TDClient(apikey = apikey)

# ヒストリカルデータを取得
def get_historical_data(symbol):
    interval = '5min' # 時間軸
    outputsize = 2000 # 最大取得件数
    start_date = '2021-09-16 06:00' # 取得開始日（「yyyy-MM-dd」 or 「yyyy-MM-dd hh:mm:ss」）
    end_date = '2021-09-17 05:59' # 取得終了日（「yyyy-MM-dd」 or 「yyyy-MM-dd hh:mm:ss」）
    timezone = 'Asia/Tokyo' # タイムゾーン

    res = td.time_series(symbol = symbol, interval= interval, outputsize = outputsize, start_date = start_date, end_date = end_date, timezone = timezone).as_json()
    
    df = pd.DataFrame(res).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)

    return df

# 各通貨の対数変化率を算出
def calc_logarithmic_change_rates(symbols):
    logarithmic_change_rates = []

    for symbol in symbols:
        print(f'Fetching {symbol} ...')
        
        historical_data = get_historical_data(symbol)
        logarithmic_change_rate = np.log(historical_data['close'] / historical_data['close'][0])
        
        logarithmic_change_rates.append(logarithmic_change_rate)

        time.sleep(8) # 無料プランにおけるTwelveDataのAPIコールは1分間に8件までなので間隔を空ける
    
    print('\n Finished !')
    
    return logarithmic_change_rates

# 通貨ペア一覧
symbols = [
    'USD/CAD', 'USD/CHF', 'USD/JPY',
    'EUR/USD', 'EUR/GBP', 'EUR/AUD', 'EUR/NZD', 'EUR/CAD', 'EUR/CHF', 'EUR/JPY',
    'GBP/USD', 'GBP/AUD', 'GBP/NZD', 'GBP/CAD', 'GBP/CHF', 'GBP/JPY',
    'AUD/USD', 'AUD/NZD', 'AUD/CAD', 'AUD/CHF', 'AUD/JPY',
    'NZD/USD', 'NZD/CAD', 'NZD/CHF',  'NZD/JPY',
    'CAD/CHF', 'CAD/JPY',
    'CHF/JPY'
]

usd_cad, usd_chf, usd_jpy, eur_usd, eur_gbp, eur_aud, eur_nzd, eur_cad, eur_chf, eur_jpy, gbp_usd, gbp_aud, gbp_nzd, gbp_cad, gbp_chf, gbp_jpy, aud_usd, aud_nzd, aud_cad, aud_chf, aud_jpy, nzd_usd, nzd_cad, nzd_chf, nzd_jpy, cad_chf, cad_jpy, chf_jpy = calc_logarithmic_change_rates(symbols)

# 各通貨単体の強さを算出
usd = ((eur_usd * (-1)) + (aud_usd * (-1)) + (gbp_usd * (-1)) + (nzd_usd * (-1)) + usd_cad + usd_chf + usd_jpy).fillna(method = "ffill")
eur = (eur_usd + eur_gbp + eur_aud + eur_nzd + eur_cad + eur_chf + eur_jpy).fillna(method = "ffill")
jpy = ((usd_jpy * (-1)) + (eur_jpy * (-1)) + (gbp_jpy * (-1)) + (aud_jpy * (-1)) + (nzd_jpy * (-1)) + (cad_jpy * (-1)) + (chf_jpy * (-1))).fillna(method = "ffill")
gbp = ((eur_gbp * (-1)) + gbp_usd + gbp_aud + gbp_nzd + gbp_cad + gbp_chf + gbp_jpy).fillna(method = "ffill")
aud = ((eur_aud * (-1)) + (gbp_aud * (-1)) + aud_usd + aud_nzd + aud_cad + aud_chf + aud_jpy).fillna(method = "ffill")
chf = ((usd_chf * (-1)) + (eur_chf * (-1)) + (gbp_chf * (-1)) + (aud_chf * (-1)) + (nzd_chf * (-1)) + (cad_chf * (-1)) + chf_jpy).fillna(method = "ffill")
cad = ((usd_cad * (-1)) + (eur_cad * (-1)) + (gbp_cad * (-1)) + (aud_cad * (-1)) + (nzd_cad * (-1)) + cad_chf + cad_jpy).fillna(method = "ffill")
nzd = ((eur_nzd * (-1)) + (gbp_nzd * (-1)) + (aud_nzd * (-1)) + nzd_usd + nzd_cad + nzd_chf + nzd_jpy).fillna(method = "ffill")

# 各通貨の強弱関係を描画
fig, ax = plt.subplots()

ax.plot(usd.index, usd, label = 'USD', color = 'orange', linewidth = 1)
ax.plot(eur.index, eur, label = 'EUR', color = 'red', linewidth = 1)
ax.plot(jpy.index, jpy, label = 'JPY', color = 'aqua', linewidth = 1)
ax.plot(gbp.index, gbp, label = 'GBP', color = 'limegreen', linewidth = 1)
ax.plot(aud.index, aud, label = 'AUD', color = 'blue', linewidth = 1)
ax.plot(chf.index, chf, label = 'CHF', color = 'brown', linewidth = 1)
ax.plot(cad.index, cad, label = 'CAD', color = 'blueviolet', linewidth = 1)
ax.plot(nzd.index, nzd, label = 'NZD', color = 'deeppink', linewidth = 1)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

ax.legend()
plt.show()
