import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def snmpbulkwalk(version, community, agent, mib, oid,
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

    objects = bulk_walk_cmd(
        snmpEngine,
        user_or_community,
        await UdpTransportTarget.create((agent, 161)),
        ContextData(),
        0,
        1,
        ObjectType(ObjectIdentity(oid)),
        lexicographicMode=False
    )

    varBindsArray = []

    async for errorIndication, errorStatus, errorIndex, varBinds in objects:
        if errorIndication:
            print(f"Error: {errorIndication}")
            break
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex}")
            break
        else:
            for varBind in varBinds:
                print(" = ".join([x.prettyPrint() for x in varBind]))
                varBindsArray.append(tuple(x.prettyPrint() for x in varBind))

    snmpEngine.close_dispatcher()
    return varBindsArray