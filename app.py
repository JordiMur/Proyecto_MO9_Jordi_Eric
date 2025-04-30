from flask import Flask, render_template, request
import asyncio

# Importación de funciones SNMP
from FuncionesSNMP.snmpget import snmpget
from FuncionesSNMP.snmpnext import snmpnext
from FuncionesSNMP.snmpbulkwalk import snmpbulkwalk
from FuncionesSNMP.snmpset import snmpset

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultat', methods=['POST'])
def resultat():
    version = int(request.form['version'])
    community = request.form['community']
    agent = request.form['agent']
    oid = request.form['oid']
    operacio = request.form['operacio']
    new_value = request.form.get('new_value', '')

    # Afegeix ".0" si no és un walk
    if operacio != 'bulkwalk' and not oid.endswith('.0'):
        oid += '.0'

    # Ejecutar operación SNMP según selección
    resultat = None

    if operacio == 'get':
        resultat = asyncio.run(snmpget(version, community, agent, '', oid))

    elif operacio == 'next':
        resultat = asyncio.run(snmpnext(version, community, agent, '', oid))

    elif operacio == 'bulkwalk':
        resultat = asyncio.run(snmpbulkwalk(version, community, agent, '', oid))

    elif operacio == 'set':
        # Intenta convertir a entero, si no, lo deja como string
        try:
            new_value = int(new_value)
        except ValueError:
            pass
        resultat = asyncio.run(snmpset(version, community, agent, '', oid, new_value))

    if resultat is None:
        resultat = ["No s'ha pogut obtenir resultat"]

    return render_template('resultat.html', resultat=resultat)


if __name__ == '__main__':
    app.run(debug=True)