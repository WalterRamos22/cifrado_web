--Conexion desde python hacia el servidor--
import pyodbc

def conectar():
    conexion = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=192.168.1.44,1433;"
        "DATABASE=cifrado_web;"
        "UID=usuario1;"
        "PWD=1234;"
        "TrustServerCertificate=yes;"
    )
    return conexion
