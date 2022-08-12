from shlex import join
from ClsBot import Bot
from bd_datos import visualizar_datos,editar_datos_unicos,obtener_datos_todos,actualizar_datos,eliminar_datos, crear_tabla,agregar_datos,verificar_correo,verificar_cuenta_datos
# Libreria para datos
import pandas as pd, numpy as np,time
# Libreria para pagina web
import streamlit as st
# Libreria para graficos
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Libreria para conexion a binance
import os
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
# Libreria para tiempo
from datetime import datetime
from dateutil import relativedelta
# Libreria par ayahoo finance
from pandas_datareader import data
#Librerias para tabla de grafico
from websocket import WebSocketApp
import json
import mplfinance as mpf
# Objeto de la clase
bt = Bot()

def main():
    # Titulo de pagina
    st.set_page_config(
        page_title='Trading bot',
        page_icon= '🤖',
        layout='wide'
    )

    # Ocultar main
    ocultar_main = """
    <style>  
        .css-j7qwjs {
            display: none;
        }
    </style>
    """

    # Ocultamos la clase main
    st.markdown(ocultar_main, unsafe_allow_html=True)

    correo = st.sidebar.text_input('Ingrese su Correo')
    correo_unico = verificar_correo(correo)
    if correo_unico:
        st.sidebar.success("Correo validado con exito.")
    # Menu
    menu = ["Añadir datos","Visualizar datos","Editar datos","Activar Bot","Gráfico  de Vela","Eliminar datos"] # ,"Eliminar_datos"
    elegir = st.sidebar.selectbox("Menu", menu)
    
    # Información
    st.sidebar.text("Acerca")
    st.sidebar.info("Aplicación web para inversionistas en criptomonedas. El uso de este software es bajo su responsabilidad.")

    # Boton cerrar sesión 
    if len(correo)==0:
        print("Ingrese el correo.")
    else:
        verificar = verificar_cuenta_datos(correo)
        # st.sidebar.write(verificar)
        if verificar:
            st.sidebar.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">', unsafe_allow_html=True) 
            st.sidebar.markdown('<br><br><br><a class="btn btn-outline-secondary" href="http://localhost:8501" type="button" style="color:black">Cerrar Sesión</a>', unsafe_allow_html=True)    
    
    # Programacion de menu a elegir
    if elegir == "Añadir datos":     
        # Ingresamos los datos
        st.markdown("<center><h3 style='color:black;'>Añadir datos:</h3></center>", unsafe_allow_html=True)
        # Ingresamos simbolo y tiempo
        if len(correo)==0:
            st.warning("Ingrese el correo.")
        else:
            verificar = verificar_cuenta_datos(correo)
            email = correo
            if verificar:
                st.warning("Ya existen datos para este correo.")
                Cuenta_unica = obtener_datos_todos(email) 
                st.write(Cuenta_unica)
            else:
                if correo_unico:
                    st.success("Correo confirmado correctamente.")
                    simbolo = st.selectbox("Selecciona el simbolo:", ['','BTC/USDT','ETH/USDT','XRP/USDT','DOGE/USDT','BNB/USDT'])
                    tiempo = st.selectbox("Selecciona el tiempo:", ['','5m','15m','30m','1h'])
                    # Validación de tiempo y simbolo
                    if len(simbolo)==0 and len(tiempo)==0:
                        st.warning("Selecciona el simbolo y tiempo")
                    elif len(simbolo)==0:
                        st.warning("Selecciona el tiempo")
                    elif len(tiempo)==0:
                        st.warning("Selecciona el simbolo")
                    # Ingresamos api_key  y api_secret 
                    api_key = st.text_input('Ingrese su Api_key: ')
                    api_secret = st.text_input('Ingrese su Api_Secret: ')
                    # Validación de Conexión a binance y saldo actual.
                    if len(api_key)==0 and len(api_secret)==0:
                        st.warning("Ingresa su api_key y api_secret")
                    elif len(api_key)==0:
                        st.warning("Ingresa su api_key")
                    elif len(api_secret)==0:
                        st.warning("Ingresa su api_secret")
                    else:
                        # Conexion a binancia       
                        client = Client(api_key,api_secret)
                        try:
                            # Verificacion si se conecto con exito
                            client.get_account()
                            st.success("Conectado con exito a Binance.")
                            # Valores 
                            valor1 = simbolo[:-5]
                            valor2 = ''
                            if valor2 == 'BTC/USDT' or valor2 == 'ETH/USDT' or valor2 == 'XRP/USDT' or valor2 == 'BNB/USDT':
                                valor2 = simbolo[-3:]
                            else:
                                valor2 = simbolo[-4:]
                            # Obtiene el dinero actual en la cuenta ingresada
                            bnb_balance1 = client.get_asset_balance(asset=valor1)
                            bnb_balance2 = client.get_asset_balance(asset=valor2)
                            # Visualización de dinero
                            st.write("Dinero disponible en su cuenta:")
                            st.write(valor1+": {:.8f}".format(float(bnb_balance1['free'])))
                            st.write(valor2+": {:.2f}".format(float(bnb_balance2['free'])))
                            # Monto a invertir en USDT y verificación si tiene el monto en su cuenta
                            monto = st.number_input(label="Ingrese su monto a invertir en USDT:  Ejemplo: 10.30 debe tener dos digitos despues del punto.",step=1.,format="%.2f")
                            if monto <= 0: 
                                st.warning("Ingrese el monto.")
                            else:
                                if  monto <= float(bnb_balance2['free']) and monto > 0: # monto <= float(bnb_balance1['free']) 
                                    if monto >= 12.04:
                                        st.success("Dinero disponible en tu cuenta.")
                                        operaciones = st.number_input(label="Ingrese la cantidad de operaciones a realizar: ",step=1)
                                        if operaciones == 0:
                                            inversion = 0
                                        else:
                                            inversion = round(monto/operaciones, 2)
                                        # Cantidad destinanda a compra y venta
                                        if inversion >= 12.04:
                                            st.markdown(f"<label>Cantidad para compra y venta: {inversion}</label>", unsafe_allow_html=True)
                                            # Botón
                                            if st.button("Añadir datos"):
                                                crear_tabla()
                                                agregar_datos(email,simbolo,tiempo,api_key,api_secret,monto,operaciones,inversion)
                                                st.success("Datos Añadidos correctamente.")
                                                
                                    else:
                                        st.warning("Dinero minimo para invertir es 12.04")
                                else:
                                    st.error("No tienes suficiente dinero en tu cuenta.")

                        except BinanceAPIException:
                            st.error("Error de conexión, verifique sus datos.")
                else:
                    st.warning("Verifique su correo.")



    elif elegir ==  "Visualizar datos": 
        st.markdown("<center><h3 style='color:black;'>Visualizar datos añadidos:</h3></center>", unsafe_allow_html=True)
        if len(correo)==0:
            st.warning("Ingrese el correo.")
        else:
            verificar = verificar_cuenta_datos(correo)
            if verificar:
                #  Visualizamos los datos
                result = obtener_datos_todos(correo)
                st.write(result)
                df = pd.DataFrame(result,columns=['correo','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
        
                st.write("Datos")
                st.dataframe(df)



    elif elegir ==  "Editar datos":   
        st.markdown("<center><h3 style='color:black;'>Editar datos añadidos:</h3></center>", unsafe_allow_html=True)  
        if len(correo)==0:
            st.warning("Ingrese el correo.")
        else:
            verificar = verificar_cuenta_datos(correo)
            if verificar:
                result = obtener_datos_todos(correo)
                df = pd.DataFrame(result,columns=['correo','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
                with st.expander("Datos"):
                    st.dataframe(df)
                
                # st.write(editar_datos_unicos())
                lista_registros = [i[0] for i in editar_datos_unicos(correo)]
                # st.write(lista_registros)
                seleccionar_registro = st.selectbox("Registro a editar clave:",lista_registros)
                select_result = obtener_datos_todos(seleccionar_registro)
                st.write(select_result)
                if select_result:
                    # Datos actuales
                    email = select_result[0][0] 
                    simbolo = select_result[0][1] 
                    tiempo = select_result[0][2] 
                    api_key = select_result[0][3] 
                    api_secret = select_result[0][4]
                    monto = select_result[0][5] 
                    operaciones = select_result[0][6] 
                    inversion = select_result[0][7]  
                    # Ingresamos nuevo simbolo y tiempo
                    new_simbolo = st.selectbox(simbolo, ['','BTC/USDT','ETH/USDT','XRP/USDT','DOGE/USDT','BNB/USDT'])
                    new_tiempo = st.selectbox(tiempo, ['','5m','15m','30m','1h'])
                    # Validación de tiempo y simbolo
                    if len(new_simbolo)==0 and len(new_tiempo)==0:
                        st.warning("Selecciona el nuevo simbolo y tiempo")
                    elif len(new_simbolo)==0:
                        st.warning("Selecciona el nuevo tiempo")
                    elif len(new_tiempo)==0:
                        st.warning("Selecciona el nuevo simbolo")
                    # Ingresamos el nuevo api_key  y api_secret 
                    new_api_key = st.text_input(api_key)
                    new_api_secret = st.text_input(api_secret)
                    # Validación de Conexión a binance y saldo actual.
                    if len(new_api_key)==0 and len(new_api_secret)==0:
                        st.warning("Ingresa su api_key y api_secret")
                    elif len(new_api_key)==0:
                        st.warning("Ingresa su api_key")
                    elif len(new_api_secret)==0:
                        st.warning("Ingresa su api_secret")
                    else:
                        # Conexion a binancia       
                        client = Client(new_api_key,new_api_secret)
                        try:
                            # Verificacion si se conecto con exito
                            client.get_account()
                            st.success("Conectado con exito a Binance.")
                            # Valores 
                            valor1 = new_simbolo[:-5]
                            valor2 = ''
                            if valor2 == 'BTC/USDT' or valor2 == 'ETH/USDT' or valor2 == 'XRP/USDT' or valor2 == 'BNB/USDT':
                                valor2 = new_simbolo[-3:]
                            else:
                                valor2 = new_simbolo[-4:]
                            # Obtiene el dinero actual en la cuenta ingresada
                            bnb_balance1 = client.get_asset_balance(asset=valor1)
                            bnb_balance2 = client.get_asset_balance(asset=valor2)
                            # Visualización de dinero
                            st.write("Dinero disponible en su cuenta:")
                            st.write(valor1+": {:.8f}".format(float(bnb_balance1['free'])))
                            st.write(valor2+": {:.2f}".format(float(bnb_balance2['free'])))
                            # Monto a invertir en USDT y verificación si tiene el monto en su cuenta
                            new_monto = st.number_input(monto,step=1.,format="%.2f")
                            if new_monto <= 0: 
                                st.warning("Ingrese el monto.")
                            else:

                                if new_monto <= float(bnb_balance2['free']) and new_monto > 0: 
                                    if new_monto >= 12.04: 
                                        st.success("Dinero disponible en tu cuenta.")
                                        new_operaciones = st.number_input(operaciones,step=1)
                                        if new_operaciones == 0:
                                            new_inversion = 0
                                        else:
                                            new_inversion = round(new_monto/new_operaciones, 2)
                                        # Cantidad destinanda a compra y venta
                                        if new_inversion >= 12.04:
                                            st.markdown(f"<label>Cantidad para compra y venta: {new_inversion}</label>", unsafe_allow_html=True)
                                            # Botón
                                            if st.button("Actualizar datos"):
                                                actualizar_datos(correo,new_simbolo,new_tiempo,new_api_key,new_api_secret,new_monto,new_operaciones,new_inversion)
                                                st.success("Datos Actualizados correctamente")
                                                result2 = obtener_datos_todos(correo)
                                                df2 = pd.DataFrame(result2,columns=['correo','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
                                                with st.expander("Datos Actualizados"):
                                                    st.dataframe(df2)
                                        else:
                                            st.error("El minimo de inversion debe ser 12.04")
                                    else:
                                        st.warning("Dinero minimo para invertir es 12.04")
                                else:
                                    st.error("No tienes suficiente dinero en tu cuenta.")   
                        except BinanceAPIException:
                            st.error("Error de conexión, verifique sus datos.")

    
                

    elif elegir ==  "Activar Bot":
        st.markdown("<center><h3 style='color:black;'>Activar bot:</h3></center>", unsafe_allow_html=True)
        if len(correo)==0:
            st.warning("Ingrese el correo.")
        else:
            #  Visualizamos los datos
            result = obtener_datos_todos(correo)
            # Visualizamos DataFrame
            df = pd.DataFrame(result,columns=['correo','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
            # st.write(result)
            with st.expander("Datos"):
                st.dataframe(df)
            # Covertir a dataframe ---> lo borre Notas
            email = result[0][0] 
            simbolo = result[0][1] 
            tiempo = result[0][2] 
            api_key = result[0][3] 
            api_secret = result[0][4]
            monto = result[0][5] 
            operaciones = result[0][6] 
            inversion = result[0][7]
            status = st.radio("Estatus del Bot: ", ("Inactivo","Activo"))
            st.write("Estado: "+status)

            while status == "Activo":
                new_symbol = bt.obtener_simbolo(simbolo)
                # MOVIMIENTO IGUAL A 1 PARA PRIMERO COMPRAR ANTES DE VENDER
                movimiento = 1
                bt.vender_comprar(simbolo,new_symbol,api_key,api_secret,inversion,movimiento,tiempo)

                if status == "Inactivo":    
                    return
            
            

    elif elegir ==  "Gráfico de Vela":
        st.markdown("<center><h3 style='color:black;'>Gráfico de Vela</h3></center>", unsafe_allow_html=True)
        if len(correo)==0:
            st.warning("Ingrese el correo.")
        else:
            verificar = verificar_cuenta_datos(correo)
            if verificar:
                result = obtener_datos_todos(correo)
                # Visualizamos DataFrame
                # df = pd.DataFrame(result,columns=['correo','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
                simbolo = result[0][1] 
                tiempo = result[0][2] 

                with st.expander("Datos"):
                    # st.write(df)
                    st.write("Simbolo: "+simbolo)
                    st.write("Tiempo: "+tiempo)
                # Grafico
                # estado_grafico = st.radio("Estado del grafico: ", ("Desactivado","Activado"))
                # st.write("Estado: "+ estado_grafico)
                # if estado_grafico == "Activado":
                title = simbolo
                st.markdown(f"<center><h5 style='color:black;'>Precio de {title}</h5></center>", unsafe_allow_html=True)
                data = bt.obtieneDatosGrafico(simbolo,tiempo)
                fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.01) 
                fig.add_trace(go.Candlestick(x=data.index.values,open=data['open'],high=data['high'],low=data['low'],close=data['close'],))
                fig.update_layout(autosize=True,width=1030,height=450,margin=dict(l=10,r=10,b=0,t=0,pad=2))
                st.plotly_chart(fig)  
                
                st.markdown(f"<center><h4 style='color:black;'>Datos Recientes de {simbolo}</h4></center>", unsafe_allow_html=True)
                estado_datos = st.radio("Activar datos Nuevos: ", ("Apagado","Encendido"))
                st.write("Estado: "+estado_datos)
                if estado_datos == "Encendido":
                    if tiempo == '5m':
                        url = "wss://stream.binance.com:9443/ws/btcusdt@kline_5m"
                    elif tiempo == '15m':
                        url = "wss://stream.binance.com:9443/ws/btcusdt@kline_15m"
                    elif tiempo == '30m':
                        url = "wss://stream.binance.com:9443/ws/btcusdt@kline_30m"
                    elif tiempo == '1h':
                        url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1h"
                    def on_message(ws, msg):
                        tick=json.loads(msg)
                        data = pd.DataFrame()
                        if tick['k']['x']:
                            # Sacamos fecha (datetime)
                            timestamp = tick['E']
                            timestamp = str(timestamp)
                            timestamp = list(timestamp)
                            timestamp = timestamp[:10]
                            timestamp = "".join(timestamp)
                            timestamp = int(timestamp)
                            fecha = datetime.fromtimestamp(timestamp)
                            # Datos: Open, High, low, close, volume
                            cripto_open = tick['k']['o']
                            cripto_high=tick['k']['h']
                            cripto_low=tick['k']['l']
                            cripto_close=tick['k']['c']
                            cripto_volume=tick['k']['v']
                            # Lo convetimos a dataframe
                            df = pd.DataFrame({
                            'datetime': [fecha],
                            'open': [cripto_open],
                            'high': [cripto_high],
                            'low': [cripto_low],
                            'close': [cripto_close],
                            'volume': [cripto_volume]})
                            # Concatemos los datos nuevos 
                            data = pd.concat([df, data], ignore_index = True)
                            data.set_index("datetime", inplace = True)
                            # Imprimimos en pantalla
                            st.table(data)
                    ws= WebSocketApp(url, on_message=on_message) 
                    ws.run_forever()  
                    if estado_datos == "Apagado":
                        return

    elif elegir ==  "Eliminar datos":   
        st.markdown("<center><h3 style='color:black;'>Eliminar datos añadidos:</h3></center>", unsafe_allow_html=True)  
        if len(correo)==0:
            st.warning("Ingrese el correo.")
        else:
            verificar = verificar_cuenta_datos(correo)
            if verificar:    
                result = obtener_datos_todos(correo)
                # st.write(result)
                df = pd.DataFrame(result,columns=['correo','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
                with    st.expander("Datos"):
                    st.dataframe(df)
                lista_registros = [i[0] for i in editar_datos_unicos(correo)]
                # st.warning("Deseas eliminar : {}".format(lista_registros))

                seleccionar_registro = st.selectbox("Registro a eliminar:",lista_registros)
                if st.button("Eliminar registro"):
                    eliminar_datos(seleccionar_registro)
                    st.success("Datos eliminados correctamente.")
                    st.info("Puedes agregar nuevos datos en menú, añadir datos.")

            
if __name__ == "__main__":
    main()