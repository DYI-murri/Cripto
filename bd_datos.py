import sqlite3
conn = sqlite3.connect('data.db', check_same_thread=False)
C = conn.cursor()

# Base de datos
# Tabla
# Campo/Columnas
# Tipo de datos

# ------------------------------------------- TABLA DE DATOS ---------------------------------------

def crear_tabla():
    C.execute('''CREATE TABLE IF NOT EXISTS tbldato(
        email       text,
        simbolo     text, 
        tiempo      text, 
        api_key     text, 
        api_secret  text, 
        monto       text, 
        operaciones text, 
        inversion   text)''')

def agregar_datos(email,simbolo,tiempo,api_key,api_secret,monto,operaciones,inversion):
    C.execute('INSERT INTO tbldato(email,simbolo,tiempo,api_key,api_secret,monto,operaciones,inversion) VALUES(?,?,?,?,?,?,?,?)',(email,simbolo,tiempo,api_key,api_secret,monto,operaciones,inversion))
    conn.commit()

def verificar_cuenta_datos(email):
    C.execute('SELECT email FROM tbldato WHERE email = ?',(email,))
    data = C.fetchall()
    return data

def visualizar_datos():
    C.execute('SELECT * FROM tbldato')
    data = C.fetchall()
    return data

def editar_datos_unicos(email):
    C.execute('SELECT email FROM tbldato WHERE email = ?',(email,))
    data = C.fetchall()
    return data

def obtener_datos_todos(email): #obtener_clave
    C.execute('SELECT * FROM tbldato WHERE email="{}"'.format(email))
    # C.execute('SELECT * FROM tbldatos WHERE clave=?',(clave))
    data = C.fetchall()
    return data

def actualizar_datos(email,new_simbolo,new_tiempo,new_api_key,new_api_secret,new_monto,new_operaciones,new_inversion):
    C.execute('UPDATE tbldato SET simbolo=?,tiempo=?,api_key=?,api_secret=?,monto=?,operaciones=?,inversion=? WHERE email=?',(new_simbolo,new_tiempo,new_api_key,new_api_secret,new_monto,new_operaciones,new_inversion,email))
    conn.commit()
    data = C.fetchall()
    return data

def eliminar_datos(email):
    C.execute('DELETE FROM tbldato WHERE email="{}"'.format(email))
    conn.commit()


# ------------------------------------------- CREACIÓN DE USUARIO ---------------------------------------

def crear_tabla_usuario():
    C.execute("""CREATE TABLE IF NOT EXISTS tbldatosusuario(        
        tipo        text        not null,
        telefono    text        not null, 
        email       text        not null  primary key, 
        password    text        not null)""")

def registrar_usuario(tipo,telefono,email,password): 
    C.execute("INSERT INTO tbldatosusuario(tipo,telefono,email,password) VALUES (?,?,?,?)",(tipo,telefono,email,password))
    conn.commit()

def crear_administrador():
    C.execute("INSERT INTO tbldatosusuario(tipo,telefono,email,password) VALUES ('Admin','7717292053','20200744@uthh.edu.mx','Eduardo18')")
    conn.commit()

def visualizar_datos_usuario():
    C.execute('SELECT tipo,email FROM tbldatosusuario')
    data = C.fetchall()
    return data

def visualizar_datos_usuario_unicos():
    C.execute('SELECT tipo,telefono,email FROM tbldatosusuario')
    data = C.fetchall()
    return data

def eliminar_toda_la_tabla():
    C.execute('DELETE FROM tbldatosusuario')
    conn.commit()

def verficar_cuenta(email,password):
    C.execute('SELECT email,password FROM tbldatosusuario WHERE email = ? AND password = ?',(email,password))
    data = C.fetchall()
    return data

def verificar_correo(email):
    C.execute('SELECT email FROM tbldatosusuario WHERE email = ?',(email,))
    data = C.fetchall()
    return data

def tipo_cuenta(email):
    C.execute('SELECT tipo FROM tbldatosusuario WHERE email = ?',(email,))
    data = C.fetchall()
    return data


def recuperar_contra(email):
    C.execute('SELECT password FROM tbldatosusuario WHERE email = ?',(email,))
    data = C.fetchall()
    return data


def ver_usuarios():
    C.execute('SELECT * FROM tbldatosusuario')
    data = C.fetchall()
    return data   

def obtener_telefono(email):
    C.execute('SELECT telefono FROM tbldatosusuario WHERE email = ?',(email,))
    data = C.fetchall()
    return data

# def selecionar_datos(email):
#     C.execute('SELECT * FROM tbldatosusuario WHERE email = ?',(email,))
#     data = C.fetchall()
#     return data   

