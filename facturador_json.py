import json
import sys
import os

import facturar

try:
    facturas = sys.argv[1]
except:
    print(f"[-] Uso: {sys.argv[0]} archivo-de-facturas.json")
    sys.exit(1)

if not os.path.exists(facturas):
    print(f"[-] {facturas} no existe!")
    sys.exit(2)


config_name = os.path.splitext(sys.argv[0])[0] + ".conf"

if not os.path.exists(config_name):
    print(f"[-] Archivo de configuracion {config_name} no existe!")
    sys.exit(2)

with open(config_name) as f:
    config = json.load(f)

with open(facturas) as f:
    datos = json.load(f)

h = facturar.conectar_AFIP(config["usuario"], config["clave"], config["nombre_afip"])

for it in datos:
    facturar.generar_factura(h, it, config["dir_descargas"])
