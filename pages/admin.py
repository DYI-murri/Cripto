import pandas as pd
# Tabla de usuarios
from bd_datos import visualizar_datos_usuario_unicos,visualizar_datos
# Libreria para pagina web
import streamlit as st

def main():
    # Titulo de pagina
    st.set_page_config(
        page_title='Administrador',
        page_icon= '💲',
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

    st.sidebar.markdown("<center><h1 style='color:black;'>Administrador</h1></center>", unsafe_allow_html=True)
    
    # Ocultamos la clase main y boton
    st.markdown(ocultar_main, unsafe_allow_html=True)
    # Menu
    menu = ["Visualizar Tabla de Usuario","Visualizar Tabla de datos de Usuario"]  
    elegir = st.sidebar.selectbox("Tablas",menu)

    st.sidebar.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">', unsafe_allow_html=True) 
    st.sidebar.markdown('<br><br><br><br><br><br><br><br><br><br><br><br><a class="btn btn-outline-secondary" href="http://localhost:8501" type="button" style="color:black">Cerrar Sesión</a>', unsafe_allow_html=True)    

    if elegir == "Visualizar Tabla de Usuario":
        st.markdown("<center><h1 style='color:black;'>Tabla de Usuarios</h1></center>", unsafe_allow_html=True)
        datos = visualizar_datos_usuario_unicos()
        usuario = pd.DataFrame(datos,columns=['Tipo','Telefono','Correo'])
        st.table(usuario)

    elif elegir == "Visualizar Tabla de datos de Usuario":
        st.markdown("<center><h1 style='color:black;'>Tabla de Datos</h1></center>", unsafe_allow_html=True)
        dato = visualizar_datos()
        datos_bot = pd.DataFrame(dato,columns=['email','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
        st.table(datos_bot)
        


if __name__ == "__main__":
    main()