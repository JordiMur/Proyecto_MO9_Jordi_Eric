import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def snmpset(version, community, agent, mib, oid, new_value,
                  username=None, auth_password=None, priv_password=None,
                  encryption_method=None, v3_mode=None):
    snmpEngine = SnmpEngine()

    if version == 3:
        if v3_mode == "noauth":
            usm_data = UsmUserData(username)
        elif v3_mode == "auth":
            usm_data = UsmUserData(username, auth_password,
                                   authProtocol=usmHMACSHAAuthProtocol,
                                   privProtocol=usmNoPrivProtocol)
        elif v3_mode == "priv":
            privProtocol = usmDESPrivProtocol if encryption_method == "des" else usmAesCfb128Protocol
            usm_data = UsmUserData(username, auth_password, priv_password,
                                   authProtocol=usmHMACSHAAuthProtocol,
                                   privProtocol=privProtocol)
        user_or_community = usm_data
    else:
        user_or_community = CommunityData(community, mpModel=version)

    # Determinar el tipo de dato SNMP según el tipo de new_value
    ObjType = None
    if isinstance(new_value, bool):
        # Representa True/False como 1/0
        ObjType = ObjectType(ObjectIdentity(oid), Integer(1 if new_value else 0))
    elif isinstance(new_value, int):
        ObjType = ObjectType(ObjectIdentity(oid), Integer(new_value))
    elif isinstance(new_value, str):
        ObjType = ObjectType(ObjectIdentity(oid), OctetString(new_value))
    else:
        ObjType = ObjectType(ObjectIdentity(oid), OctetString(str(new_value)))

    iterator = set_cmd(
        snmpEngine,
        user_or_community,
        await UdpTransportTarget.create((agent, 161)),
        ContextData(),
        ObjType
    )

    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print("{} at {}".format(errorStatus.prettyPrint(),
                                   errorIndex and varBinds[int(errorIndex) - 1][0] or "?"))
    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))
        snmpEngine.close_dispatcher()
        return varBinds

    snmpEngine.close_dispatcher()
    return None