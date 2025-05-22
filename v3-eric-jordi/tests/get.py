import asyncio
from pysnmp.hlapi.v3arch.asyncio import *


async def run():
    snmpEngine = SnmpEngine()

    # usm_data = UsmUserData('juan', 
    #                      authProtocol=usmNoAuthProtocol,
    #                      privProtocol=usmNoPrivProtocol)


    # 2. AuthNoPriv
    #usm_data = UsmUserData('eric', '12345678', 
     #                     authProtocol=usmHMACMD5AuthProtocol,
      #                   privProtocol=usmNoPrivProtocol)

    usm_data = UsmUserData('jordimu', '12345678', 'privacidad1234',
                        authProtocol=usmHMACSHAAuthProtocol,
                        privProtocol=usmDESPrivProtocol)

    iterator = get_cmd(
        snmpEngine,
        usm_data,  # Using SNMPv3 USM user data instead of CommunityData
        await UdpTransportTarget.create(("192.168.56.103", 161)),
        ContextData(),
        #ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)),
        #ObjectType(ObjectIdentity("SNMPv2-MIB", "sysUpTime", 0)),
        ObjectType(ObjectIdentity("1.3.6.1.2.1.1.4.0")),  # sysContact
    )

    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print(
            "{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:
            print(" = ".join([x.prettyPrint() for x in varBind]))

    snmpEngine.close_dispatcher()


asyncio.run(run())