import asyncio
SCAN_CMD = 'nmcli  --terse --fields active,ssid,signal,security device wifi list --rescan yes'
# RESCAN_CMD = 'nmcli device wifi rescan'
CONNECT_CMD = '''nmcli  device wifi connect "{0}" password "{1}"'''
DISCONNECT_CMD = '''nmcli con down id "{0}"'''
# OFF_CMD = 'nmcli radio '
class WiFiManager:
    def __init__(self):
        pass
    async def sendCmd(self,cmd):
        # print('cmd:',cmd)
        proc = await asyncio.create_subprocess_shell(cmd,shell=True, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        res,err = await proc.communicate()
        return res.decode('utf-8')
    def scan(self):
        # asyncio.run(self.sendCmd(RESCAN_CMD))
        res=asyncio.run(self.sendCmd(SCAN_CMD)).split('\n')
        return res
        # dt=[]
        # old_connect=''
        # for item in res:
        #     if len(item)>0:
        #         val = item.split(':')
        #         temp = {
        #             'status':val[0],
        #             'ssid':val[1],
        #             'signal':val[2]+'%',
        #             'security':val[3]
        #         }
        #         if temp not in dt:
        #             dt.append(temp)
        #         if val[0]=='yes':
        #             old_connect=val[1]
        # return dt,old_connect
    def connectWifi(self,ssid,password):
        res= asyncio.run(self.sendCmd(CONNECT_CMD.format(ssid,password)))
        # print(res)
        # if len(res)
        # if res.find('successfully')>=0:
        #     return 1
        # else:
        #     return 0
        return res

    def disconnectWifi(self,ssid):
        return asyncio.run(self.sendCmd(DISCONNECT_CMD.format(ssid)))

    async def sleep(self,time):
        await asyncio.sleep(time)
    def delay(self,t):
        asyncio.run(self.sleep(t))


# wifi = WiFiManager()
# res,old=wifi.scan()
# print(res,old)
# if len(old)>0:

#     r=wifi.disconnectWifi(old)
#     print(r)
#     wifi.delay(5)
# print("connect to wifi:",res[1])
# dt = wifi.connectWifi(res[1]['ssid'],"aiot1234@")
# dt = wifi.connectWifi('Sonmaster','12345678')
# dt = wifi.connectWifi('AIoT Tang 1_5G',"aiot1234@")
# print(dt)
    