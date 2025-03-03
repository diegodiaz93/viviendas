import requests
from bs4 import BeautifulSoup
import os
import smtplib
import urllib3
from email.mime.text import MIMEText

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL de la página
URL = "https://www.prygesa.es/obra-nueva/madrid/simancas/julian-camarillo-passivhaus-peraleda-urban-s-coop"

response = requests.get(URL, verify=False)

# Función para enviar un email si hay pisos disponibles
def enviar_notificacion(pisos, asunto, cuerpo):
    remitente = "diegoeroee@gmail.com"
    destinatario = "diegoeroee@gmail.com"
    mensaje = MIMEText(cuerpo)
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    # Obtener la contraseña del secreto de GitHub
    password = os.environ.get("EMAIL_PASSWORD")
    
    if password is None:
        print("Error: La contraseña no está definida.")
        return

    # Configuración del servidor SMTP de Google Gmail
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.starttls()
    smtp.login("diegoeroee@gmail.com", password)  # Usar la contraseña de aplicación
    response = smtp.sendmail(remitente, destinatario, mensaje.as_string())
    print(response)
    smtp.quit()

    print("📩 Notificación enviada a tu correo.")

# Función para enviar correo informativo si no hay pisos de 2 habitaciones
def enviar_no_hay_piso_2_habitaciones():
    asunto = "❌ Mala suerte: No se encontraron pisos de 2 habitaciones"
    cuerpo = f"¡Parece que hoy no hay suerte! No se han encontrado pisos de 2 habitaciones en {URL}.\n\nRevisa más tarde."
    enviar_notificacion([], asunto, cuerpo)

# Obtener el contenido HTML
response = requests.get(URL, verify=False)
soup = BeautifulSoup(response.text, "html.parser")

tabla = soup.find("table", {"id": "tablepress-249"})

if tabla:
    viviendas = []

    for fila in tabla.find_all("tr")[1:]:
        columnas = fila.find_all("td")

        if len(columnas) >= 6:
            dormitorios = columnas[0].text.strip()  # Número de habitaciones
            tipologia = columnas[1].text.strip()
            superficie = columnas[2].text.strip()
            vinculaciones = columnas[3].text.strip()
            coste = columnas[4].text.strip()
            plano_url = columnas[5].find("a")["href"] if columnas[5].find("a") else "No disponible"

            viviendas.append({
                "Dormitorios": dormitorios,
                "Tipología": tipologia,
                "Superficie": superficie,
                "Vinculaciones": vinculaciones,
                "Coste": coste,
                "Plano": plano_url
            })

    viviendas_filtradas = [v for v in viviendas if v["Dormitorios"] in ["1", "2"]]

    pisos_2_habitaciones = []

    if viviendas_filtradas:
        for v in viviendas_filtradas:
            print(f"Dormitorios: {v['Dormitorios']} | Tipología: {v['Tipología']} | Superficie: {v['Superficie']} | Coste: {v['Coste']} | Plano: {v['Plano']}")
            if v["Dormitorios"] == "2":
                # Agregar piso de 2 habitaciones a la lista
                pisos_2_habitaciones.append(f"Tipología: {v['Tipología']} | Superficie: {v['Superficie']} | Coste: {v['Coste']} | Plano: {v['Plano']}")

        # Si hay pisos de 2 habitaciones, enviar notificación
        if pisos_2_habitaciones:
            enviar_notificacion(pisos_2_habitaciones, "✅ ¡Nuevo piso disponible de 2 habitaciones!", 
                                f"Se han encontrado nuevos pisos de 2 habitaciones:\n\n" + "\n".join(pisos_2_habitaciones) + f"\n\nRevisar en {URL}")
        else:
            # Si no hay pisos de 2 habitaciones, enviar mensaje informativo
            enviar_no_hay_piso_2_habitaciones()
    else:
        print("🚫 No hay pisos disponibles de 1 ni 2 habitaciones.")
        enviar_no_hay_piso_2_habitaciones()
else:
    print("❌ No se encontró la tabla con id='tablepress-249'")
