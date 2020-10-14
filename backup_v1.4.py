#!/usr/bin/python
# Scrip v 1.3 para backup cisco device

# Importo libreria y modulos
import sys
import time
import paramiko
import os
import cmd
import logging
from datetime import datetime 

# Cargo la config desde un file central
from config import TIMEOUT, BKP_DIR, FILENAME_PREFIX
from config import USER, PASSWORD, SECRET, LOG_LEVEL, DEVICES_INVENTORY

# Tomo la fecha y hora actual
CURRENT_DATE=datetime.today().strftime('%Y%m%d-%H%M%S') # para el filename

# weekday = 0=Lunes 1=Martes 2=Miercoles 3=Jueves 4=Viernes 5=Sabado 6=Domingo
weekday = datetime.weekday(datetime.today())

# Formato del logging que escriba en consola
logging.basicConfig(level=LOG_LEVEL,  #filename="log.backup", > Si quiero escribir en un log                                                                                                                                                           
                    format='%(asctime)s %(levelname)s %(message)s')

# Defino la funcion para hacer backup
def do_backup(ip, USER, PASSWORD, SECRET):
	logging.info("Haciendo backup de %s ..." % (ip))
	try:
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(ip, username=USER, password=PASSWORD, timeout=TIMEOUT)
		# Comandos SSH paaso a paso
		# Invoco al cliente 
		chan = client.invoke_shell()
		time.sleep(2)
		# Clave enable secret
		chan.send('enable\n')
		chan.send(SECRET +'\n')
		time.sleep(1)
		# Terminal lenght for no paging 
		chan.send('term len 0\n')
		time.sleep(1)
		# Ejecuto comando sh run y escribo en archivo el output
		chan.send('sh run\n')
		time.sleep(10)
		output = chan.recv(99999)
		# Termino conexion ssh de paramiko
		client.close()
		# devuelvo todo el output
		return output
	except Exception as e:
		return "Error connecting to host %s: %s" % (ip, e)

# Bucle para repetir instruccion
f = open(DEVICES_INVENTORY)
for ip in f.readlines():
	ip = ip.strip()
	FULL_BKP_DIR="%s/%s" % (BKP_DIR, ip)
	if not os.path.exists(FULL_BKP_DIR):  #Con este If si el directorio no esta creado lo creamos
		os.makedirs(FULL_BKP_DIR)         #Con este If si el directorio no esta creado lo creamos
	output = do_backup(ip, USER, PASSWORD, SECRET) #Esta variable llama a la funcion definida do_backup
	if datetime.now().day == 1: # Si Es 1ero, lo guardamos como mensual
		month = datetime.now().month
		bkp_type="monthly.%s" % (month)
	elif weekday == 6: # Si es domingo, lo guardamos como semanal, con el nro de semana del mes.
		day_of_month = datetime.now().day
		week_number = (day_of_month - 1) // 7 + 1	#Calculo para saber que numero de semana es dentro del mes, esto me va  a devolver 1 2 3 o 4	
		bkp_type="weekly.%s" % (week_number)
	else:
		# Si no es ninguno de los casos anteriores, es un dia de la semana comun
		# Asi que lo guardamos como daily + nombre del dia de la semana
		now = datetime.now()
		day = (now.strftime("%A")) #Pasa el dia de la semana en formato texto
		bkp_type="daily.%s" % (day)
	filename = "%s/%s.cfg" % (FULL_BKP_DIR,bkp_type) #Armado del string final
	print(filename)
	ff = open(filename, 'wb') #Abro el archivo open si en modo append (si el file existe lo sobrescribo) y sino lo creo
	ff.write(output) #Escribo el contenido de la variable ouput
	ff.close() #Cierro el archivo de backup
	logging.info("Backup para %s creado en %s" % (ip, filename))
logging.info("Backup de todos los switches realizados")



