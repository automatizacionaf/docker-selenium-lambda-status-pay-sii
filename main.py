from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException
import io
import os
import json
import boto3
import time

url_sii = os.environ['url_sii']
xget_test = os.environ['xget_test']
sqsDataManager = os.environ['sqsDataManager']
close_session = os.environ['close_session']
tableSii = os.environ['tableSii']

# Crea un client S3
S3_Client = boto3.client('s3')
# Crea un cliente de SQS
sqs_client = boto3.client('sqs')
# Crea un cliente dynamodb para SII
dynamodb = boto3.resource('dynamodb')
Sii = dynamodb.Table(tableSii)

def is_alert_present(self):
    try:
        alert = self.switch_to.alert
        #alert = browser.switch_to_alert()
        alert.accept()
        return True
    except:
        try:
            boton =  self.find_element(By.XPATH, '/html/body/div[1]/div/div/div[3]/button')   # Finding the referenced element
            boton.click()

        except:
            print("Sin Ventana Emergente")
        
    return False


def handler(event=None, context=None):
    print('PaySiix')
    try: 
        linea = 0
        prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": r"/tmp",
        "directory_upgrade": True
        }

        options = webdriver.ChromeOptions()
        options.binary_location = '/opt/chrome/chrome'
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")
        driver = webdriver.Chrome("/opt/chromedriver",
                                options=options)
        driver.implicitly_wait(15)
        nombreMes = ['','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        print(url_sii)
        print(event)
# iniciar ciclo pa consultar si pago
        cantidad = len(event['Records'])
        for pos in range(0,cantidad):
            linea = 0
            if (event.get("Records")): 
                body = json.loads(event['Records'][pos]['body'])
                cliente = body['cliente']
                sii_user = body['sii_user']
                sii_pass = body['sii_pass']
                ano = body['ano']
                mes = body['mes']
            else:
                cliente = event["cliente"]
                sii_user = event['sii_user']
                sii_pass = event['sii_pass']
                ano = event['ano']
                mes = event['mes']
            
            
            keyPeriodo = str(ano)+str(mes);

            mesLetra = nombreMes[int(mes)]
            driver.get(url_sii)
            linea += 1
            user = driver.find_element(By.ID, 'rutcntr')
            linea += 1
            password = driver.find_element(By.ID, 'clave')
            enviar = driver.find_element(By.ID, 'bt_ingresar')
            user.clear()
            linea += 1
            # Usuario para Ingerasar al SII
            user.send_keys(sii_user)
            linea += 1
            # user.send_keys(Keys.TAB)
            password.clear()
            linea += 1
            # Clave de acceso para descargar facturas y Boletas
            password.send_keys(sii_pass)
            linea += 1
            enviar.send_keys(Keys.RETURN)
            time.sleep(4)
            linea += 1
            #driver.execute_script("window.open('');")
            #time.sleep(2)
            #driver.switch_to.window(driver.window_handles[1])
            # Aqui verificar si existe ventena y cerrar
            try:
                driver.switch_to.alert.accept()
            except UnexpectedAlertPresentException:
                driver.switch_to.alert.accept()
            
            if is_alert_present(driver):
                print('Ventana cerrada')
            time.sleep(2)
            driver.get(xget_test)  # Aqui linea 8
            time.sleep(4)
            linea += 1
            content = driver.page_source
            linea += 1
            content = driver.find_element(By.TAG_NAME, 'pre').text
            linea += 1
        # Validad que exista contenido
            parsed_json = json.loads(content)
            print('respuesta xget_test:',parsed_json)
            linea += 1
            if (parsed_json.get("glosaRespuesta")): 
                print('Cierto', parsed_json['glosaRespuesta'])
                if (parsed_json['glosaRespuesta'] == 'Error: Autenticacion'):
                    print("Error de Autenticacion o error de clave")

            if (parsed_json.get("data")): 
                #print(parsed_json)
                print('Mes: ', parsed_json['data']['response']['data']['detalle'][mesLetra][1]['mes'])
                linea += 1
                print('Año: ', parsed_json['data']['response']['data']['detalle'][mesLetra][1]['columna'])
                linea += 1
                print('Rut: ', parsed_json['data']['response']['data']['detalle'][mesLetra][1]['datosDeclaracion']['rut'])
                linea += 1
                print('Folio: ', parsed_json['data']['response']['data']['detalle'][mesLetra][1]['datosDeclaracion']['folio'])
                linea += 1

                response = {
                    'rut': parsed_json['data']['response']['data']['detalle'][mesLetra][1]['datosDeclaracion']['rut'],
                    'month': parsed_json['data']['response']['data']['detalle'][mesLetra][1]['mes'],
                    'year': parsed_json['data']['response']['data']['detalle'][mesLetra][1]['columna'],
                    'folio': parsed_json['data']['response']['data']['detalle'][mesLetra][1]['datosDeclaracion']['folio']
                }
                linea += 1
                valorFolio = parsed_json['data']['response']['data']['detalle'][mesLetra][1]['datosDeclaracion']['folio']
                linea += 1
                response = Sii.update_item(
                    Key={
                        'cliente': cliente,
                        'periodorut': keyPeriodo+sii_user
                    },
                    UpdateExpression='set #newPeriodo = :valPeriodo, #newRut = :valRut, #newAttr = :val',
                    ExpressionAttributeNames={ 
                        '#newPeriodo': 'periodo',
                        '#newRut': 'rut',
                        '#newAttr': 'folio'
                    },
                    ExpressionAttributeValues={
                        ':val': valorFolio,
                        ':valPeriodo': keyPeriodo,
                        ':valRut': sii_user
                    },
                    ConditionExpression= 'attribute_exists(#newAttr) OR attribute_not_exists(#newAttr)'
                )
                print('respuesta:', response)
                ## El nombre de la cola SQS FIFO
                #queue_name = sqsDataManager
#
                ## El identificador de grupo de mensajes
                #group_id = cliente
#
                ## El identificador de mens
                #message_id = sii_user
#
                ## El mensaje que deseas enviar
                #message_body = {
                #    "cliente": cliente,
                #    "rut": sii_user,
                #    "periodo": keyPeriodo,
                #    "folio": valorFolio,
                #    "dato": "PagoSii"
                #}
                #linea += 1
                ## Envía el mensaje a la cola SQS
                #response = sqs_client.send_message(
                #    QueueUrl=queue_name,
                #    #//MessageGroupId=group_id,
                #    #//MessageDeduplicationId=message_id,
                #    MessageBody=json.dumps(message_body),
                #    DelaySeconds = 4
                #)
                linea += 1
                print('Respuesta SQS y Folio: ',valorFolio, response)
                linea += 1
            driver.get(close_session)

        linea += 1

        driver.close()
        driver.quit()
        
        return
    except Exception as err:
        print("Error:", err)
        try:
            print('Error buscar: ', sii_user, 'Linea: ', linea)
        except:
            print('Error buscar: sin rut Linea: ', linea)
        # Quiero una foto guardar en S3
        # Returns and base64 encoded string into image
        #driver.save_screenshot('./image.png')
        screenshot = driver.get_screenshot_as_png()
        in_memory_file = io.BytesIO(screenshot)
        fileName = sii_user+'.png'
        S3_Client.upload_fileobj(in_memory_file, 'ajfr-taxsmart-dev-storage', fileName)
        return
