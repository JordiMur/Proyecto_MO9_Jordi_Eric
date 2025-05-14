# db.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="192.168.56.103",
        user="mib_ej",
        password="1234",
        database="net_snmp"
    )

# Connexió a la base de dades
mydb = get_connection()
cursor = mydb.cursor()

# Eliminar les dades existents
delete_oid = "DELETE FROM oids"
cursor.execute(delete_oid)

# Preparar consulta d'inserció
add_oid = """
    INSERT INTO oids (traduccio, oid)
    VALUES (%s, %s)
"""

# Obrir fitxer i inserir línies
with open("oids.txt", "r") as file:
    for line in file:
        fields = line.strip().split('\t\t\t')
        cursor.execute(add_oid, tuple(field.strip('"') for field in fields))

# Confirmar canvis i tancar connexió
mydb.commit()
cursor.close()
mydb.close()
