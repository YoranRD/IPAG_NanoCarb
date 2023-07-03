import os
import json
import asyncio
import websockets
import time

async def _send_msg(uri, msg):    
    async with websockets.connect(uri) as websocket:
        await websocket.send(msg)
        reply = await websocket.recv()                
        return reply 

class json_client:
    
    def __init__(self, uri):
        self.uri = uri
        
    def send(self, msg):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        res = loop.run_until_complete(_send_msg(self.uri, msg))  
        return json.loads(res)

        
    def SendCommand(self, cmd, params):
        # it's the end of the campaign, send a stop command
        try :         
            # be sure that there is no pending campaign 
            self.send(json.dumps({"Command" : cmd, "Parameters" : params}))
                                            
        except Exception as e:
            print (message)  
            self.logger.error("failed to communicate with firmware")
            
################################################################################
if __name__ == "__main__":
    
    # Init Json Command TCP server
    json_websock_ex = json_client("ws://127.0.0.1:9020")
    
    json_websock_ex.SendCommand("Start", {"myparam1" : [4,7,30], "myparam2" : "hello"} )
        
