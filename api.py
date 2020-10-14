import flask
from flask import jsonify, abort, send_from_directory
import os
import os.path
from glob import glob
from pathlib import Path, PurePosixPath

from config import TIMEOUT, BKP_DIR, FILENAME_PREFIX, USER, PASSWORD, SECRET
                      
app = flask.Flask(__name__)
app.config["DEBUG"] = True


def backup_check(device, file):
    """ Funcion para controlar el estado de los backups """
    # En base a los parametros, armo el path completo al archivo
    full_file_path = "%s/%s/%s" % (BKP_DIR, device, file)
    # Si el archivo adentro tiene la cadena 'end', significa que se bajo todo el archivo desde el switch
    # Si tiene la cadena 'Error', falló al intentar hacer el backup
    # Si no tiene 'end' o 'error', fallamos porque pasó algo inesperado.
    if 'end' in open(full_file_path).read():
        return "OK"
    elif 'Error' in open(full_file_path).read():
        return "ERROR"
    else: 
        return "UNKNOWN"


@app.route('/', methods=['GET'])
def home():
    """ Home """
    content = """
    <h1>API de switches disponibles</h1>
    <p><a href='/list-devices'>/list-devices/</a> - Listar todos los dispositivos disponibles para backup.</p>
    <p><a href='/list-backups/x.x.x.x'>/list-backups/IP</a> - Listar todos los backups disponibles para un switch en particular.</p>
    <p><a href='/get-backup/x.x.x.x/daily.X'>/get-backup/ip/archivo</a> - Descargarse el archivo de backup para de un device en particular.</p>
    """
    return content


@app.route('/list-devices', methods=['GET'])
def list_devices():
    """ Listar todos los devices incluidos en el backup """
    backups = glob("%s/*/" % (BKP_DIR))
    devices = []
    tmp = {}
    for dir in backups:
        device=(PurePosixPath(dir).name)
        tmp = {
                'ip': str(device)
        }
        devices.append(tmp)
    return jsonify({'devices': devices})


@app.route('/list-backups/<string:ip>', methods=['GET'])
def list_backups(ip):
    """ Listar todos los backups disponibles para un device en particular """
    backups = glob("%s/%s/*" % (BKP_DIR, ip))
    bkp_files = []
    tmp = {}
    for file in backups:
        file_name=(PurePosixPath(file).name)
        file_status=backup_check(ip,file_name)
        tmp = {
                'file': str(file_name),
                'status': file_status,
        }
        bkp_files.append(tmp)
    return jsonify({'backups': bkp_files})


@app.route('/get-backup/<string:ip>/<string:file>', methods=['GET'])
def get_backup(ip, file):
    """ Recuperar un backup particular """
    try:
        file_dir="%s/%s" % (BKP_DIR, ip)
        return send_from_directory(file_dir, filename=file, as_attachment=True)
    except FileNotFoundError:
        abort(404)

app.run()
