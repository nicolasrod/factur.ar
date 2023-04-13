# Factur.AR

Herramientas para generar facturas via la interfaz de la AFIP usando Selenium.

# Uso

```python
import facturar

# Creamos un diccionario con los datos de la factura
f = dict(
    tipo_doc="DNI",
    nro_doc=21222323,
    nombre="Mi nombre es X",
    domicilio="Ravignani 1233",
    email="some@email.com",
    lineas=[
        dict(horas=6, precio=1500, descripcion="Horas de Servicios"),
        dict(horas=4, precio=3000, descripcion="Horas de Servicios de otra cosa"),
        dict(horas=16, precio=5000, descripcion="Horas de nada"),
    ],
    start_date=None,
)

# Nos conectamos con la clave de AFIP
h = facturar.conectar_AFIP(
    "222222200",
    "clave de AFIP",
    nombre="NOMBRE EXACTO DE FACTURADOR (ejemplo MARTINEZ CLAUDIO)",
)

# Mandamos a generar la factura y el nombre del archivo pdf con la factura
# lo va a retornar monitoreando la carpeta de descargas, en este caso 
# /home/usuario/Downloads

pdf = facturar.generar_factura(h, f, "/home/usuario/Downloads", aceptar_factura=False)
print(pdf)
```

En el repositorio hay una aplicación de ejemplo llamada *facturador_json.py* que toma un archivo JSON con la descripción de factura(s) y generar los 
comprobantes automaticamente.

```
$ python3 facturador_json.py datos.json
```

Los datos necesarios para conectarse a la AFIP se encuentran en el archivo *facturador_json.conf*.
