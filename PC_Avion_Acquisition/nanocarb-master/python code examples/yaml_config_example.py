#!/usr/bin/python3

import yaml


################################################################################
# global vars...
LOOP_PERIOD = None
JSON_CMD_TCP_IP = ''
JSON_CMD_TCP_PORT = 0
JSON_DATA_UDP_IP = ''
JSON_DATA_UDP_PORT = 0
FIRMWARE_JSON_CMD_TCP_IP = ''
FIRMWARE_JSON_CMD_TCP_PORT = 0


################################################################################
if __name__ == "__main__":
    
    # Calendar YAML config file loading
    with open("./config_file.yaml", 'r') as stream:
       try:
           config = yaml.safe_load(stream)            
           JSON_CMD_TCP_IP = config['module_settings']['JSON_CMD_TCP_IP']
           JSON_CMD_TCP_PORT = config['module_settings']['JSON_CMD_TCP_PORT']            
           JSON_DATA_UDP_IP = config['module_settings']['JSON_DATA_UDP_IP']
           JSON_DATA_UDP_PORT = config['module_settings']['JSON_DATA_UDP_PORT']            
           FIRMWARE_JSON_CMD_TCP_IP = config['module_settings']['FIRMWARE_JSON_CMD_TCP_IP']
           FIRMWARE_JSON_CMD_TCP_PORT = config['module_settings']['FIRMWARE_JSON_CMD_TCP_PORT']
           LOOP_PERIOD = config['module_settings']['LOOP_PERIOD']
       except yaml.YAMLError as exc:
           logger.error("Error reading config file. It may be of the wrong format. See YAML specs for more info")






