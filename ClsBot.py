# Importamos las librerias para datos
from re import I
import ccxt, pandas as pd, numpy as np, time
from datetime import datetime,timedelta
from dateutil import relativedelta
# import datetime
# Libreria para los graficos
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.pyplot import title
import plotly.offline as pyoff
import plotly.graph_objects as go
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Libreria para escalar datos
from sklearn.preprocessing import MinMaxScaler
# Librerias para crear el modelo 
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
# Libreria de metricas
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn.metrics import mean_squared_log_error
# Libreria para conexion a binance
import os
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
# Libreria para pagina web
import streamlit as st
# Libreria par ayahoo finance
from pandas_datareader import data

class Bot:
    msec = 1000 # MiliSegundos
    minute = 60 * msec # minutos
    hour = 60 * minute # Hora

    exchange = ccxt.binance({ # De donde extraemos los datos
            'enableRateLimit':True, 
        })
    now = exchange.milliseconds() # tiempo actual

    data = pd.DataFrame
    df = pd.DataFrame

    # def __init__(self):
    #     print("*** Iniciando Programa *** \n")
    #     print("")
    
    def get_candles(self, symbol, timeframe, limit, from_timestamp):    
        try: 
            candles = self.exchange.fetch_ohlcv(
            symbol = symbol, 
            timeframe = timeframe,
            limit = limit,
            since = from_timestamp,       
            )  
            header = ['timestamp','open','high','low','close','volume']
            df = pd.DataFrame(candles, columns = header)
            # Transformamos el timestamp a datetime año/dia/mes hora/minuto/
            df.insert(1,'datetime', [datetime.fromtimestamp(d/1000) for d in df.timestamp])
            return df.sort_values(by='timestamp', ascending=False) 
        except:
            print('No more data')
            pass 
        
    def save_candles(self, symbol, timeframe, limit, from_timestamp):
        data = pd.DataFrame()
        while(from_timestamp < self.now):
            candles = self.get_candles(symbol, timeframe, limit, from_timestamp)
    #         print(candles)
            if(len(candles)) > 0:
                from_timestamp = int(candles['timestamp'].iloc[0]+ self.minute)
            else:
                from_timestamp += self.hour * 1000
            data = pd.concat([candles, data], ignore_index = True)    
        return data

    def obtieneDatos(self,simbolo,tiempo):
        print('\n *** OBTENIENDO DATOS *** \n')
        import datetime
        ahora = datetime.datetime.utcnow()
        dias = ahora - datetime.timedelta(days=309)
        dias = str(dias)
        dias = list(dias)
        dias = dias[:10]
        dias = "".join(dias)
        self.symbol = simbolo
        self.data = self.save_candles(
            self.symbol, 
            timeframe = tiempo,
            limit = 1000,
            from_timestamp = self.exchange.parse8601(dias+'00:00:00') 
            )
        print('Informacion Obtenida Correctamente')
        print('Tamaño del DataFrame: ' , self.data.shape)
        self.data.sort_values(by='datetime', ascending=True, inplace=True)
        # Agregamos el datetime como indice
        self.data.set_index("datetime", inplace = True)
        # Eliminamos columna
        self.data.drop(['timestamp'], axis = 'columns', inplace=True)
        return self.data

    def prepararColumna(self, nombre_columna):
        self.df = self.data.copy()
        # Seleccionamos las columnas
        self.df = self.df[[nombre_columna]]
        # Convertimos a float el campo precio
        self.df[nombre_columna] = self.df[nombre_columna].astype(float, errors = 'raise')
        return self.df
    
    def preparaColumnas(self):
        # self.columna_close = 'close'
        self.columna_open = 'open'
        # self.df_close = self.prepararColumna(self.columna_close)
        # print(self.df_close[:3],"\n")
        self.df_open = self.prepararColumna(self.columna_open)
        # print(self.df_open[:3])

    def next_predict(self, df, cantidad_tiempo,nombre_columna,tiempo_pred):
        # Eliminamos el indice
        df = df.reset_index()
        if cantidad_tiempo > 0 :
            df_final = pd.DataFrame()
            for k in range(cantidad_tiempo):
                print("Prediccion numero: ",k+1,"/",cantidad_tiempo)
                # Tipo de prediccion
                if tiempo_pred == '5m':
                    next_five_minute = (datetime.strptime(str(list(df['datetime'])[-1]), '%Y-%m-%d %H:%M:%S') + relativedelta.relativedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
                elif tiempo_pred == '15m':
                    next_five_minute = (datetime.strptime(str(list(df['datetime'])[-1]), '%Y-%m-%d %H:%M:%S') + relativedelta.relativedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
                elif tiempo_pred == '30m':
                    next_five_minute = (datetime.strptime(str(list(df['datetime'])[-1]), '%Y-%m-%d %H:%M:%S') + relativedelta.relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                elif tiempo_pred == '1h':
                    next_five_minute = (datetime.strptime(str(list(df['datetime'])[-1]), '%Y-%m-%d %H:%M:%S') + relativedelta.relativedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

                df = df.append(pd.DataFrame(data={'datetime': [next_five_minute], nombre_columna: [0]}))

                df_diff = df.copy()
                df_diff['prev_precio'] = df_diff[nombre_columna].shift(1)
                df_diff = df_diff.dropna()
                df_diff['diff'] = (df_diff[nombre_columna] - df_diff['prev_precio'])
                df_supervised = df_diff.drop(['prev_precio'],axis=1)

                for inc in range(1,cantidad_tiempo+1):
                    field_name = 'lag_' + str(inc) 
                    df_supervised[field_name] = df_supervised['diff'].shift(inc)

                df_supervised = df_supervised.dropna().reset_index(drop=True) 
                df_model = df_supervised.drop([nombre_columna,'datetime'],axis=1)
                train_set, test_set = df_model[:-1].values, df_model[-1:].values

                scaler = MinMaxScaler(feature_range=(-1, 1))
                scaler = scaler.fit(train_set)

                train_set = train_set.reshape(train_set.shape[0], train_set.shape[1])
                test_set = test_set.reshape(test_set.shape[0], test_set.shape[1])
                train_set_scaled = scaler.transform(train_set)
                test_set_scaled = scaler.transform(test_set)

                X_train, y_train = train_set_scaled[:, 1:], train_set_scaled[:, 0:1]
                X_train = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
                X_test, y_test = test_set_scaled[:, 1:], test_set_scaled[:, 0:1]
                X_test = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])

                model = Sequential()
                model.add(LSTM(4, batch_input_shape=(1, X_train.shape[1], X_train.shape[2]), stateful=True))
                model.add(Dense(1))
                model.compile(loss='mean_squared_error', optimizer='adam')
                epocas = 1
                model.fit(X_train, y_train, epochs=epocas, batch_size=1, verbose=1, shuffle=False)

                y_pred = model.predict(X_test,batch_size=1)
                y_pred = y_pred.reshape(y_pred.shape[0], 1, y_pred.shape[1])

                pred_test_set = []
                for index in range(0,len(y_pred)):
                    pred_test_set.append(np.concatenate([y_pred[index], X_test[index]], axis=1))

                pred_test_set = np.array(pred_test_set) 
                pred_test_set = pred_test_set.reshape(pred_test_set.shape[0], pred_test_set.shape[2]) 
                pred_test_set_inverted = scaler.inverse_transform(pred_test_set)

                result_list = []
                sales_dates = list(df[-2:].datetime)
                df = df.rename(columns={nombre_columna: 'precio'})
                act_sales = list(df[-2:].precio)
                df = df.rename(columns={'precio': nombre_columna})
                
                result_dic = {}
                result_dic['pred_value'] = int(act_sales[0])
                result_dic['datetime'] = sales_dates[0]
                result_list.append(result_dic)

                for index in range(0,len(pred_test_set_inverted)):
                    result_dict = {}
                    result_dict['pred_value'] = int(pred_test_set_inverted[index][0] + act_sales[index])
                    result_dict['datetime'] = sales_dates[index+1]
                    result_list.append(result_dict)

                df_result = pd.DataFrame(result_list)
                if k == 0:
                    df_final['pred_value'] = list(df_result['pred_value'])
                    df_final['datetime'] = list(df_result['datetime'])
                else:
                    df_final = df_final.append(pd.DataFrame(data={'pred_value': [list(df_result['pred_value'])[-1]], 'datetime': [list(df_result['datetime'])[-1]]}))
                df = df[:-1]
                df = df.append(pd.DataFrame(data={'datetime':[next_five_minute], nombre_columna:[list(df_result['pred_value'])[-1]]}))
                df = df.reset_index().drop('index', axis=1)
            # Resultados.  
            if cantidad_tiempo == 1:
                df_price_pred = pd.concat([df,df_final], axis=1, sort=False)
            else:
                # df_price_pred = pd.concat([df,df_final], axis=1, sort=False)
                df_price_pred = pd.merge(df,df_final,on='datetime',how='left')
            return df_price_pred
        else:
            print("El numero a predecir debe ser mayor a Cero")
    
    def predecir(self,tiempo):    
        # self.cantidad_tiempo = int(input("Ingrese la cantidad de valores a predecir: ")) 
        self.cantidad_tiempo = 1
        # self.df_price_pred_close = self.next_predict(self.df_close, self.cantidad_tiempo,self.columna_close,tiempo)
        self.df_price_pred_open = self.next_predict(self.df_open, self.cantidad_tiempo,self.columna_open,tiempo)

    def ordena_Datos(self, df_columna,df_price_pred):
        df_pred = df_price_pred.iloc[-self.cantidad_tiempo:,[0,1]]
        print("\n Ultimos valores reales:")
        print(df_columna.tail(3))
        return df_pred

    def mostrarDatos(self):
        # self.df_pred_close = self.ordena_Datos(self.df_close, self.df_price_pred_close)
        self.df_pred_open = self.ordena_Datos(self.df_open, self.df_price_pred_open)

    def unir_predicciones(self):
        self.df_pred = self.df_pred_open.copy()
        # self.df_pred[self.columna_close] = self.df_pred_close[self.columna_close]
        print('Valores Predichos \n',self.df_pred)
        return self.df_pred

    def obtieneDatosGrafico(self,simbolo,tiempo):
        print('\n *** OBTENIENDO DATOS PARA GRAFICO*** \n')
        import datetime
        ahora = datetime.datetime.utcnow()
        mes = ahora - datetime.timedelta(days=30)
        mes = str(mes)
        mes = list(mes)
        mes = mes[:10]
        mes = "".join(mes)
        # print(mes)
        self.symbol = simbolo
        self.data = self.save_candles(
            self.symbol, 
            timeframe = tiempo,
            limit = 1000,
            from_timestamp = self.exchange.parse8601(mes+'00:00:00') 
        )
        print('Informacion Obtenida Correctamente')
        print('Tamaño del DataFrame: ' , self.data.shape)
        self.data.sort_values(by='datetime', ascending=True, inplace=True)
        # Agregamos el datetime como indice
        self.data.set_index("datetime", inplace = True)
        # Eliminamos columna
        self.data.drop(['timestamp'], axis = 'columns', inplace=True)
        return self.data
    def obtener_simbolo(self,simbolo):
        characters = '/'
        new_symbol = ''
        for x in range(len(characters)):
            new_symbol = simbolo.replace(characters[x],"")
        return str(new_symbol)
    
    # COMPRAR O VENDER DEPENDIENDO LA PREDICCION REALIZADA
    def vender_bitcoin(self,new_simbolo,api_key,secret_key,inversion):
        # Simbolo
        var1 = new_simbolo[:-4]
        if new_simbolo == 'BTCUSDT':
            yahoo_simbolo = 'USDT-BTC'
        elif new_simbolo == 'ETHUSDT':
            yahoo_simbolo = 'USDT-ETH'
        elif new_simbolo == 'DOGEUSDT':
            yahoo_simbolo = 'DOGE-ETH'    
        elif new_simbolo == 'BNBUSDT':
            yahoo_simbolo = 'BNB-ETH'
        # Fecha
        import datetime
        ahora = datetime.datetime.utcnow()
        ayer = ahora - datetime.timedelta(days=1)
        ayer = str(ayer)
        ayer = list(ayer)
        ayer = ayer[:10]
        ayer = "".join(ayer)
        # Obtener valores
        precio = data.DataReader(yahoo_simbolo, data_source = 'yahoo', start = ayer) 
        precio = precio.reset_index()
        print(precio)
        precio = precio['Close']
        precio = str(precio)
        precio = list(precio)
        precio = precio[19:27]
        precio = "".join(precio)
        # Inversión en BTC
        new_inversion = float(inversion) * float(precio)
        new_inversion = str(new_inversion)
        new_inversion = list(new_inversion)
        new_inversion = new_inversion[:6]
        new_inversion = "".join(new_inversion)
        st.write("Precio a vender en USDT: "+inversion)
        st.write("Precio a vender en "+var1+": "+new_inversion)

        client = Client(api_key,secret_key)
        try:
            buy_limit = client.create_order(
                symbol=new_simbolo, # Simbolo que queremos adquirir la moneda
                side='SELL', # Simbolo para comprar
                type='MARKET', # Tipo de Orden Limit(Tipo de orden que espera a que el mercado este en el precio del bitcoin establecido)
                quantity = new_inversion) # Fraccion de criptomoneda que queremos vender
            st.success("Venta realizada con exito")
        except BinanceAPIException as e:
            # Manejo de errores
            st.warning(e)
        except BinanceOrderException as e:
            # Manejo de errores
            st.warning(e)
 
    def comprar_bitcoin(self,new_simbolo,api_key,secret_key,inversion):
        # Simbolo
        var = new_simbolo[:-4]
        if new_simbolo == 'BTCUSDT':
            yahoo_simbolo = 'USDT-BTC'
        elif new_simbolo == 'ETHUSDT':
            yahoo_simbolo = 'USDT-ETH'
        elif new_simbolo == 'DOGEUSDT':
            yahoo_simbolo = 'DOGE-ETH'    
        elif new_simbolo == 'BNBUSDT':
            yahoo_simbolo = 'BNB-ETH'
        # Fecha
        import datetime
        ahora = datetime.datetime.utcnow()
        ayer = ahora - datetime.timedelta(days=1)
        ayer = str(ayer)
        ayer = list(ayer)
        ayer = ayer[:10]
        ayer = "".join(ayer)
        # Obtener valores
        precio = data.DataReader(yahoo_simbolo, data_source = 'yahoo', start = ayer) 
        precio = precio.reset_index()
        print(precio)
        precio = precio['Close']
        precio = str(precio)
        precio = list(precio)
        precio = precio[19:27]
        precio = "".join(precio)
        # Inversión en BTC
        new_inversion = float(inversion) * float(precio)
        new_inversion = str(new_inversion)
        new_inversion = list(new_inversion)
        new_inversion = new_inversion[:6]
        new_inversion = "".join(new_inversion)
        st.write("Precio a comprar en USDT: "+inversion)
        st.write("Precio a comprar en "+var+": "+new_inversion)

        client = Client(api_key,secret_key)
        try:
            buy_limit = client.create_order(
                symbol=new_simbolo, # Simbolo que queremos adquirir la moneda
                side='BUY', # Simbolo para comprar
                type='MARKET', # Tipo de Orden Limit(Tipo de orden que espera a que el mercado este en el precio del bitcoin establecido)
                quantity = new_inversion) # Fraccion de criptomoneda que queremos comprar
            st.success("Compra realizada con exito")
        except BinanceAPIException as e:
            # error handling goes here
            st.warning(e)
        except BinanceOrderException as e:
            # error handling goes here
            st.warning(e)  

    def vender_comprar(self,simbolo,new_simbolo,api_key,secret_key,inversion, movimiento_act,tiempo):
        movimiento = 0
        client = Client(api_key,secret_key)

        data_actual = self.obtieneDatos(simbolo, tiempo)
        st.markdown("<center><h4 style='color:black;'>Precio actual:</h4></center>", unsafe_allow_html=True)
        st.table(data_actual.tail(1))

        self.preparaColumnas()
        self.predecir(tiempo)

        self.mostrarDatos()
        df_pred = self.unir_predicciones()
        fecha = (datetime.strptime(str(list(df_pred['datetime'])[-1]), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'))
        st.markdown("<center><h4 style='color:black;'>Predicción a futuro:</h4></center>", unsafe_allow_html=True)
        st.table(df_pred)

        real_open = float(list(data_actual['open'])[-1])
        
        num_open = float(list(self.df_pred[self.columna_open])[-1])
        # num_close = float(list(self.df_pred[self.columna_close])[-1])

        if(num_open  < real_open): # Si la predicción open es menor a real open Es Recomendado vender
            st.write("Fecha: ",fecha,", Open Predict: ",str(num_open),", Open Actual: ",str(real_open)) 
            st.write("Recomendado vender")
            movimiento = 1
        # EN ESTE PUNTO SE DETERMINA EL TIPO DE MOVIMIENTO

        elif(num_open > real_open):# Si cuando abre es menor a cuando cierra Es Recomendado comprar 
            st.write("Fecha: ",fecha,", Open Predict: ",str(num_open),", Open Actual: ",str(real_open))
            st.write("Recomendado comprar")
            movimiento = 2
        # EN ESTE PUNTO SE DETERMINA EL TIPO DE MOVIMIENTO
        movimiento_fut = movimiento

        if movimiento_act == movimiento_fut:
            movimiento_act = movimiento_fut
            # SE OBTIENE LA HORA Y FECHA ACTUAL
            now = str(datetime.now())
            now =now[:-7]
            while now != fecha: # SE EVALUA SI LA FECHA ACTUAL ES DIFERENTE AL DE LA PREDICCION
                now = str(datetime.now())
                now =now[:-7]
            # CUANDO ES IGUAL ES PORQUE SE CUMPLIO LA FECHA-HORA Y SE VUELVE A LLAMAR A LA FUNCION
            self.vender_comprar(simbolo,new_simbolo,api_key,secret_key,inversion, movimiento_act,tiempo)
        else:
            if movimiento_act == 2:
                valor1 = simbolo[:-5]
                st.write("Dinero disponible en "+valor1+": ")
                bnb_balance_btc = client.get_asset_balance(asset=valor1)
                st.write(bnb_balance_btc)
                if float(bnb_balance_btc['free']) > 0:
                    self.vender_bitcoin(new_simbolo,api_key,secret_key,inversion)
                else:
                    st.warning("No tienes "+valor1+" para poder vender") 
            else:
                valor2 = simbolo[-4:]
                st.write("Dinero disponible en "+valor2+": ")
                bnb_balance_usdt2 = client.get_asset_balance(asset=valor2)
                st.write(bnb_balance_usdt2)
                if float(bnb_balance_usdt2['free']) > 0:
                    self.comprar_bitcoin(new_simbolo,api_key,secret_key,inversion)
                else:
                    st.warning("No tienes "+valor2+" para poder comprar")
        movimiento_act = movimiento_fut
        # SE OBTIENE LA HORA Y FECHA ACTUAL
        now = str(datetime.now())
        now =now[:-7]
        while now != fecha: # SE EVALUA SI LA FECHA ACTUAL ES DIFERENTE AL DE LA PREDICCION
            now = str(datetime.now())
            now =now[:-7]
        # CUANDO ES IGUAL ES PORQUE SE CUMPLIO LA FECHA-HORA Y SE VUELVE A LLAMAR A LA FUNCION
        self.vender_comprar(simbolo,new_simbolo,api_key,secret_key,inversion, movimiento_act, tiempo)        


            

    