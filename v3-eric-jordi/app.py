from flask import Flask, render_template, request
import asyncio

# Funciones SNMP
from FuncionesSNMP.snmpget import snmpget
from FuncionesSNMP.snmpnext import snmpnext
from FuncionesSNMP.snmpbulkwalk import snmpbulkwalk
from FuncionesSNMP.snmpset import snmpset

# Conexión a base de datos
from db import get_connection

app = Flask(__name__)

# Página principal con OIDs desde la base de datos
@app.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT oid, traduccio FROM oids ORDER BY traduccio ASC")
    oids = cursor.fetchall()
    conn.close()
    return render_template('index.html', oids=oids)

# Resultado operación SNMP
@app.route('/resultat', methods=['POST'])
def resultat():
    # Se mapea el valor recibido a la versión SNMP
    version_str = request.form['version']
    if version_str == 'v1':
        version = 0  # mpModel 0 para SNMPv1
    elif version_str == 'v2c':
        version = 1  # mpModel 1 para SNMPv2c
    elif version_str == 'v3':
        version = 3  # Usaremos el 3 para diferenciar SNMPv3
    else:
        return "Versión SNMP no soportada", 400

    agent = request.form['agent']
    oid = request.form['oid']
    operacio = request.form['operacio']
    new_value = request.form.get('new_value', '')

    # Para operaciones que no sean bulkwalk se asegura que el OID finalice con ".0"
    if operacio != 'bulkwalk' and not oid.endswith('.0'):
        oid += '.0'

    # Para SNMPv1 y SNMPv2c se utiliza la comunidad; para SNMPv3 se recogen las credenciales
    community = request.form.get('community', '')
    username = auth_password = priv_password = encryption_method = v3_mode = None
    if version == 3:
        username = request.form.get('username', '')
        v3_mode = request.form.get('v3_mode', 'noauth')
        auth_password = request.form.get('auth_password', '')
        priv_password = request.form.get('priv_password', '')
        encryption_method = request.form.get('encryption_method', 'des')

    resultat = None
    if operacio == 'get':
        resultat = asyncio.run(snmpget(
            version, community, agent, '', oid,
            username, auth_password, priv_password, encryption_method, v3_mode
        ))
    elif operacio == 'next':
        resultat = asyncio.run(snmpnext(
            version, community, agent, '', oid,
            username, auth_password, priv_password, encryption_method, v3_mode
        ))
    elif operacio == 'bulkwalk':
        resultat = asyncio.run(snmpbulkwalk(
            version, community, agent, '', oid,
            username, auth_password, priv_password, encryption_method, v3_mode
        ))
    elif operacio == 'set':
        try:
            new_value = int(new_value)
        except ValueError:
            pass
        resultat = asyncio.run(snmpset(
            version, community, agent, '', oid, new_value,
            username, auth_password, priv_password, encryption_method, v3_mode
        ))

    if resultat is None:
        resultat = ["No s'ha pogut obtenir resultat"]

    return render_template('resultat.html', resultat=resultat)

# Listado de traps
@app.route("/trap", methods=["GET", "POST"])
def traps():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT trap_id, date_time, transport FROM notifications"
    filters = []
    params = []

    if request.method == "POST":
        from_datetime = request.form.get("from_datetime")
        to_datetime = request.form.get("to_datetime")

        if from_datetime and to_datetime:
            filters.append("date_time BETWEEN %s AND %s")
            params.extend([from_datetime, to_datetime])
        elif from_datetime:
            filters.append("date_time >= %s")
            params.append(from_datetime)
        elif to_datetime:
            filters.append("date_time <= %s")
            params.append(to_datetime)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY date_time DESC"
    cursor.execute(query, params)
    traps = cursor.fetchall()
    conn.close()

    return render_template("traps.html", traps=traps)

# Detalle de un trap
@app.route('/trap/<int:trap_id>')
def trap_detail(trap_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT oid, type, CONVERT(value USING utf8) AS value 
        FROM varbinds 
        WHERE trap_id = %s
    """, (trap_id,))
    varbinds = cursor.fetchall()
    conn.close()
    return render_template("trap_detail.html", trap_id=trap_id, varbinds=varbinds)

if __name__ == '__main__':
    app.run(debug=True)