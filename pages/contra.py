import pandas as pd
import pywhatkit
import datetime
# Base de datos
from bd_datos import verificar_correo,recuperar_contra,obtener_telefono
# Libreria para pagina web
import streamlit as st

def main():
    # Titulo de pagina
    st.set_page_config(
        page_title='Recuperar contraseña',
        page_icon= '🔐',
        layout='wide'
    )
    # Ocultar main
    ocultar_main = """
    <style>  
        .css-10xlvwk {
            display: none;
        }
        .css-9s5bis {
            display: none;
        }
        .css-fblp2m {
            display: none;
        }
    </style>
    """
    
    # Ocultamos la clase main y boton
    st.markdown(ocultar_main, unsafe_allow_html=True) 
    st.markdown("<center><div style='background-color:rgb(0, 149, 255);text-align:center;border-radius:15px;justify-content:center;display:grid;'><h1 style='color:white;font-weight:cursive;font-size:50px;'>Recuperar contraseña</h1></div></center><br>", unsafe_allow_html=True)
    # st.markdown("<center><h1 style='color:black;'>Recuperar contraseña</h1></center>", unsafe_allow_html=True)
    st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">', unsafe_allow_html=True) 
    st.markdown('<a class="btn btn-outline-secondary" href="http://localhost:8501" type="button" style="color:black;">Regresar a inicio</a>', unsafe_allow_html=True)    
   
    st.info("Requerimientos: Conexión a internet y vinculación a whatsapp web con su teléfono registrado.")
    correo = st.text_input('Ingrese su correo')
    correo_unico = verificar_correo(correo)
    if len(correo) == 0:
        st.warning("Ingresa el correo.")
    else:
        if correo_unico:
            st.success("Correo validado con exito.")
            telefono = obtener_telefono(correo)
            telefono = telefono[0][0]
            signo = "+52"
            telefono = signo+str(telefono)
            st.write("Teléfono registrado: ",telefono)
            st.info("Al dar clic en el botón debera esperar 1 minuto.")
            if st.button("Enviar contraseña"):
                contra = recuperar_contra(correo)
                contra = contra[0][0]
                contra = str(contra)
                # st.write("Contraseña: ",contra)
                # Hora y minuto
                ahora = datetime.datetime.today()

                tiempo_futuro = ahora + datetime.timedelta(minutes=1)
                tiempo_futuro = str(tiempo_futuro)
                tiempo_futuro = list(tiempo_futuro)

                validar_hora = tiempo_futuro[11]
                validar_minuto = tiempo_futuro[14]

                if validar_hora == '0':
                    hora = tiempo_futuro[12]
                    hora = "".join(hora)
                    if validar_minuto == '0':
                        minuto = tiempo_futuro[15]
                        minuto = "".join(minuto)
                    else:
                        minuto = tiempo_futuro[14:16]
                        minuto = "".join(minuto)     
                else:
                    hora = tiempo_futuro[11:13]
                    hora = "".join(hora)
                    if validar_minuto == '0':
                        minuto = tiempo_futuro[15]
                        minuto = "".join(minuto)
                    else:
                        minuto = tiempo_futuro[14:16]
                        minuto = "".join(minuto)

                hora = int(hora)
                minuto = int(minuto)
                pywhatkit.sendwhatmsg(telefono, 
                            "---- Trading Bot ---- Correo:"+correo+", Contraseña: "+contra,
                            hora,minuto)

                st.success("Contraseña enviada a su telefono")
                st.markdown('<a class="btn btn-outline-secondary" href="http://localhost:8501" type="button" style="color:black">Iniciar Sesión</a>', unsafe_allow_html=True)    
    
            # st.write("Hora: ",hora)
            # st.write("Minuto: ",minuto)

        else:
            st.warning("Correo no registrado.")
            
if __name__ == "__main__":
    main()