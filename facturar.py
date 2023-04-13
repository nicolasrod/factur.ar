import os
import subprocess

from calendar import monthrange
from datetime import datetime

from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

# TODO: otros tipos de facturas, de notas de credito, unidades!
# TODO: otra forma de pago

FACT_C = "2"
CONCEPTO_SERVICIOS = "2"
CONSUMIDOR_FINAL = "5"


def doctype(t):
    DOCS = {
        "CUIT": "80",
        "CUIL": "86",
        "CDI": "87",
        "CIEXT": "91",
        "DNI": "96",
        "PP": "94",
    }
    return DOCS.get(t.upper().strip(), DOCS["DNI"])


def doc_is_cuit(doc):
    return doc in ["80", "86"]


def dir_snapshot(folder, ftype=".pdf"):
    return (
        folder,
        ftype,
        list(filter(lambda x: x.lower().endswith(ftype), os.listdir(folder))),
    )


def dir_diff(t1):
    t2 = dir_snapshot(t1[0], t1[1])

    try:
        return os.path.join(folder, list(set(t2[2]) - set(t1[2]))[0])
    except:
        return None


def as_list(x):
    if type(x) is list:
        return x
    return [x]


def date_range():
    start = datetime.now().replace(day=1)
    res = monthrange(start.year, start.month)[1]
    end = datetime.now().replace(day=res)
    return start.strftime("%d/%m/%Y"), end.strftime("%d/%m/%Y")


def click_id(h, id_):
    it = h.find_element(By.ID, id_)
    it.click()


def type_text(h, id_, val, by_=By.ID, tab=False):
    it = h.find_element(by_, id_)
    it.clear()
    it.send_keys(val)

    if tab:
        it.send_keys(webdriver.Keys.TAB)


def select(h, id_, by_=By.ID, index=None, value=None):
    it = Select(h.find_element(by_, id_))

    if index is not None:
        it.select_by_index(index)
    else:
        it.select_by_value(value)


def click_if_value(h, els, val):
    for el in as_list(els):
        for it in h.find_elements(By.TAG_NAME, el):
            if it.get_attribute("value") == val:
                it.click()
                break


def conectar_AFIP(usuario, clave, nombre, driverapp="chromedriver"):
    h = webdriver.Chrome(driverapp)
    h.implicitly_wait(2)

    h.get(
        "https://auth.afip.gov.ar/contribuyente_/login.xhtml?action=SYSTEM&system=rcel"
    )

    if not h.current_url.startswith("https://auth.afip.gov.ar/contribuyente_/"):
        raise Exception("Error!")

    type_text(h, "F1:username", usuario)
    click_id(h, "F1:btnSiguiente")
    type_text(h, "F1:password", clave)
    click_id(h, "F1:btnIngresar")
    sleep(1)

    click_if_value(h, "input", nombre)
    return h


def fill_pagina(h, ft, download_dir, aceptar_factura=True):
    if ft.get("start_date", None) is None and ft.get("end_date", None) is None:
        sdate, edate = date_range()
    else:
        sdate = ft["start_date"]
        edate = ft["end_date"]

    click_id(h, "btn_gen_cmp")
    select(h, "puntodeventa", index=1)
    select(h, "universocomprobante", value=ft.get("tipo_comprobante", FACT_C))
    click_if_value(h, "input", "Continuar >")

    select(h, "idconcepto", value=ft.get("concepto_factura", CONCEPTO_SERVICIOS))
    type_text(h, "fsd", sdate)
    type_text(h, "fsh", edate)
    click_if_value(h, "input", "Continuar >")

    select(h, "idivareceptor", value=ft.get("iva_receptor", CONSUMIDOR_FINAL))
    select(h, "idtipodocreceptor", value=doctype(ft["tipo_doc"]))
    type_text(h, "nrodocreceptor", str(ft["nro_doc"]), tab=True)

    if doc_is_cuit(ft["tipo_doc"]):
        sleep(2)
    else:
        type_text(h, "razonsocialreceptor", ft["nombre"])

    type_text(h, "domicilioreceptor", ft["domicilio"])
    type_text(h, "email", ft["email"])
    click_id(h, "formadepago7")  # otra

    if ft.get("nro_comprobante", None) is not None:
        type_text(h, "cmpAsociadoPtoVta", ft.get("sucursal", "00001"), by_=By.NAME)
        type_text(h, "cmpAsociadoNro", ft["nro_comprobante"], by_=By.NAME)

    click_if_value(h, "input", "Continuar >")

    ln = 1
    for it in ft["lineas"]:
        if ln > 1:
            click_if_value(h, "input", "Agregar línea descripción")

        type_text(h, f"detalle_descripcion{str(ln)}", it["descripcion"])
        type_text(h, f"detalle_cantidad{str(ln)}", str(it["horas"]))
        type_text(h, f"detalle_precio{str(ln)}", str(it["precio"]))

        ln += 1

    click_if_value(h, "input", "Continuar >")

    pdf = None
    if aceptar_factura:
        t1 = dir_snapshot(download_dir)

        click_id(h, "btngenerar")
        h.switch_to.alert.accept()
        sleep(1)

        click_if_value(h, ["button", "input"], "Imprimir...")
        sleep(1)

        pdf = dir_diff(t1)

        click_if_value(h, ["button", "input"], "Menú Principal")
        sleep(1)

    return pdf


def generar_factura(h, ft, download_dir, aceptar_factura=True):
    return fill_pagina(h, ft, download_dir, aceptar_factura)


def anular_factura(h, ft, download_dir):
    ft["tipo_comprobante"] = "4"  # Nota de Credito
    return fill_pagina(h, ft, download_dir)

