import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# URL de la página
URL = "https://www.prygesa.es/obra-nueva/madrid/simancas/julian-camarillo-passivhaus-peraleda-urban-s-coop"

# Función para enviar un email si hay pisos disponibles
def enviar_notificacion(pisos):
    remitente = "diego-dc93@hotmail.es"
    destinatario = "diego-dc93@hotmail.es"
    asunto = "🏠 ¡Nuevo piso disponible de 2 habitaciones!"
    cuerpo = f"Se han encontrado nuevos pisos de 2 habitaciones:\n\n" + "\n".join(pisos) + f"\n\nRevisar en {URL}"
   
    mensaje = MIMEText(cuerpo)
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
   
    # Configuración del servidor SMTP de Outlook
    smtp = smtplib.SMTP("smtp.office365.com", 587)
    smtp.starttls()
    smtp.login(remitente, "rizpdfjeodhkjogi")
    smtp.sendmail(remitente, destinatario, mensaje.as_string())
    smtp.quit()
   
    print("📩 Notificación enviada a tu correo.")

# Obtener el contenido HTML
response = requests.get(URL)
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
            enviar_notificacion(pisos_2_habitaciones)
    else:
        print("🚫 No hay pisos disponibles de 1 ni 2 habitaciones.")
else:
    print("❌ No se encontró la tabla con id='tablepress-249'")