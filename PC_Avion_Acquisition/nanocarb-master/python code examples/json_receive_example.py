#!/usr/bin/python3
# /usr/bin/env python3
# -*- Coding: UTF-8 -*-
import asyncio
import json
import websockets

class json_server:
    
    def __init__(self, callback_request_handler, socket_ipaddress, socket_port):        
        self.call_back_json_request = callback_request_handler
        self.SOCKET_IP = socket_ipaddress
        self.SOCKET_PORT = socket_port
        
    async def RequestHandler(self, websocket, path):
        try:
            message = await websocket.recv()
            # Parse the request as JSON
            request = json.loads(message)
            # Treat the request
            answer = self.call_back_json_request(request)
            # send the request
            return_message = json.dumps(answer) #, separators=(',', ':'))
            await websocket.send(return_message)

        except json.decoder.JSONDecodeError:
            # Happens when the clients sends anything other than JSON
            #self.logger.error("Invalid or corrupted frame : Not a JSON Format.")
            await websocket.send(json.dumps({"result" : "Error", "error_message" : "Not a JSON Format" }))

        except KeyError:
            # Happens when the client data with the wrong format, usually due to a typo in the code
            #self.logger.error("Error in JSON Format")
            await websocket.send(json.dumps({"result" : "Error", "error_message" : "Error in JSON Format" }))


    def StartJsonServer(self, ipaddress=None, port=None):
        try:
            if ipaddress != None:
                self.SOCKET_IP = ipaddress        
            if port != None:
                self.SOCKET_PORT = port

            #self.logger.debug("Starting server with ip = " + str(self.SOCKET_IP) + ", port = " + str(self.SOCKET_PORT))
            start_server = websockets.serve(self.RequestHandler, self.SOCKET_IP, self.SOCKET_PORT)
            asyncio.get_event_loop().run_until_complete(start_server)
            #self.logger.info("Server running.")            
            asyncio.get_event_loop().run_forever()

        except Exception as e:
            #self.logger.error('Unable to start Json socket server.')
            #self.logger.error(e)
            
            
################################################################################
if __name__ == "__main__":
    
    # Init Json Command TCP server
    json_tcp_cmd_srv = json_server(callback_request_handler=HandleJsonCommands, socket_ipaddress="127.0.0.1", socket_port=9010)
    
    # Start Json commands Websocket server      
    json_tcp_cmd_srv.StartJsonServer() # blocking call, infinite loop
    #logger.critical("Should not reach this point !!")


