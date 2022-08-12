# Base de datos
from audioop import add
from bd_datos import crear_tabla_usuario,registrar_usuario,verficar_cuenta,verificar_correo,tipo_cuenta,ver_usuarios
import pandas as pd
# Libreria para pagina web
import streamlit as st

def main():
    # Titulo de pagina
    st.set_page_config(
        page_title='Login',
        page_icon= '👥',
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
    # Ocultamos la clase main y boton
    st.markdown(ocultar_main, unsafe_allow_html=True)
    # Menu
    menu = ["Inicio Sesión", "Registro"]
    elegir = st.sidebar.selectbox("Menu",menu)

    if elegir == "Inicio Sesión":
        st.markdown("<center><div style='background-color:rgb(0, 149, 255);text-align:center;border-radius:15px;justify-content:center;display:grid;'><h1 style='color:white;font-weight:cursive;font-size:50px;'>Inicio Sesión</h1></div></center><br>", unsafe_allow_html=True)
        email = st.text_input("Correo")
        password = st.text_input("Contraseña",type='password')

        # Olvido contraseña
        st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">', unsafe_allow_html=True)
        st.markdown('<a href="https://dyi-murri-cripto-login-w6ra2m.streamlitapp.com/contra">¿Olvidaste tu contraseña?</a>', unsafe_allow_html=True)    

        # Validacion de inputs
        if len(email) == 0 and len(password) == 0:
            st.warning("Ingresa el correo y su contraseña")
        elif len(email) == 0:
            st.warning("Ingresa el correo")
        elif len(password) == 0:
            st.warning("Ingresa su contraseña")
        else:
            if st.button("Verificar Datos"):
                crear_tabla_usuario()
                result = verficar_cuenta(email,password)
                if result:
                    st.success("Datos correctos.")
                    tipo_de_cuenta = tipo_cuenta(email)
                    tipo_de_cuenta = tipo_de_cuenta[0][0] 
                    st.write("Tipo de cuenta: ",tipo_de_cuenta)
                    if tipo_de_cuenta == "Admin":
                        # Boton
                        st.markdown('<a class="btn btn-outline-success" href="https://dyi-murri-cripto-login-w6ra2m.streamlitapp.com/admin" role="button" style="color:green">Administrar página</a>', unsafe_allow_html=True)    
                    else:   
                        # Boton
                        st.markdown('<a class="btn btn-outline-success" href="https://dyi-murri-cripto-login-w6ra2m.streamlitapp.com/Bot" role="button" style="color:green">Ingresar a Bot</a>', unsafe_allow_html=True)    
                else:
                    st.error("Datos Incorrectos Usuario/Contraseña")
                    st.info("Si aún no se registra, en el menú tendrá una opción para ello.")

        # datos = ver_usuarios()
        # usuarios = pd.DataFrame(datos,columns=['Tipo','Teléfono','Correo','Contraseña'])
        # st.table(usuarios)
        
        # dato = visualizar_datos()
        # datos_bot = pd.DataFrame(dato,columns=['email','simbolo','tiempo','api_key','api_secret','monto','operaciones','inversion'])
        # st.table(datos_bot)


    
    elif elegir == "Registro":
        st.markdown("<center><div style='background-color:rgb(0, 149, 255);text-align:center;border-radius:15px;justify-content:center;display:grid;'><h1 style='color:white;font-weight:cursive;font-size:50px;'>Registro</h1></div></center><br>", unsafe_allow_html=True)
        new_tipo = st.selectbox("Tipo", ['Inversor'])
        telefono = st.text_input("Teléfono")
        new_email = st.text_input("Correo")
        new_password = st.text_input("Contraseña",type='password')
        # Validacion de inputs
        if len(new_tipo) == 0 and len(new_email) == 0 and len(new_password) == 0 and len(telefono) == 0:
            st.warning("Ingresa el tipo de usuario, el teléfono, el correo y contraseña")
        elif len(new_email) == 0 and len(new_password) == 0 and len(telefono) == 0:
            st.warning("Ingresa su correo, su email y contraseña")
        elif len(new_email) == 0 and len(telefono) == 0:
            st.warning("Ingresa el correo y su teléfono")
        elif len(new_email) == 0 and len(new_password) == 0:
            st.warning("Ingresa el correo y su contraseña")
        elif len(new_tipo) == 0 and len(new_email) == 0:
            st.warning("Ingresa el tipo y su correo")
        elif len(new_tipo) == 0:
            st.warning("Ingresa el tipo de usuario")
        elif len(new_email) == 0:
            st.warning("Ingresa su correo")
        elif len(new_password) == 0:
            st.warning("Ingresa su contraseña")
        elif len(telefono) == 0:
            st.warning("Ingresa su teléfono")
        elif len(telefono) < 10 or  len(telefono) >10:
            st.warning("Ingrese un teléfono valido.")    
        elif len(new_password) < 8:
            st.warning("Ingrese una contraseña con 8 o más caracteres.")
        elif new_email[-10:] != "@gmail.com":
            st.warning("Correo invalidó, utiliza un correo Gmail.")   
        else:
            if st.button("Registrar Datos"):
                crear_tabla_usuario()
                datos = verificar_correo(new_email)
                if datos:
                    st.warning("Correo ya usado, intente con uno diferente.")
                else:
                    crear_tabla_usuario()
                    registrar_usuario(new_tipo,telefono,new_email,new_password)
                    st.success("Datos registrados correctamente.")
                    st.info("Dirígete al menú e Inicia sesión.")
                    # st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">', unsafe_allow_html=True)
                    # st.markdown('<a class="btn btn-outline-success" href="https://dyi-murri-cripto-login-w6ra2m.streamlitapp.com/Bot" role="button" style="color:green">Añadir datos a Bot</a>', unsafe_allow_html=True)
                    
  
if __name__ == "__main__":
    main()
