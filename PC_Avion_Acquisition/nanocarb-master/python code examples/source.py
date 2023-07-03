#!/usr/bin/python3

from cru_fw_connect import cru_fw_connect  
from google_cal_connect import google_cal_connect
import datetime
import time
import _thread
import yaml
import socket
import json
import mysql.connector

import cru_logger
from json_server import json_server 

################################################################################
# global vars...
logger = None
LOOP_PERIOD = None

JSON_CMD_TCP_IP = ''
JSON_CMD_TCP_PORT = 0
JSON_DATA_UDP_IP = ''
JSON_DATA_UDP_PORT = 0
FIRMWARE_JSON_CMD_TCP_IP = ''
FIRMWARE_JSON_CMD_TCP_PORT = 0

json_tcp_cmd_srv = None
json_data_udp = None
firmware_json_tcp_cmd = None

scheduler_enabled = True
pending_campaign = None
state_campaign = None
campaigns_list = None

################################################################################
def HandleCampaignsScheduling():    

    logger.info("Starting scheduler daemon. Loop period is " + str(LOOP_PERIOD) + " sec")
    global campaigns_list
    global scheduler_enabled
    global pending_campaign
    global state_campaign

    global json_data_udp
    global firmware_json_tcp_cmd

    # First of all we need to fetch the Cru nickname from SQL DB. Nickname is required to match ITS calendar events
    mydb = mysql.connector.connect(host="localhost", port="3306", user="root", password="Skib0tn2019", database="K2PI")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT CruNickName FROM Data_Harvest")
    res = mycursor.fetchone()
    cru_nickname = res[0]
    
    # google cal stuff : if everything goes well, connect to google cal and update events list in Json File     
    gcal = google_cal_connect(cru_nickname, minimum_duration=3*LOOP_PERIOD, minimum_interval=2*LOOP_PERIOD)              
    last_google_update = None
    if gcal.update_json_file_of_events() == True:        
        last_google_update = datetime.datetime.now()
        
    # Even if Google connection failed, read back events from the Json File (because it could exist from previous attempts) 
    campaigns_list = gcal.get_events_list_from_json_file()
    
    # Even if list is empty, update info/data towards Cru_Gui (UDP broadcast)
    json_data_udp.sendto(bytes(json.dumps({ "Calendar_ScheduledCampaigns" : { "Campaigns" : campaigns_list } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
                    
    while (1):        
        loopTimeLap = datetime.datetime.now()
        
        # update info/data towards Cru_Gui (UDP broadcast)
        if scheduler_enabled :
            json_data_udp.sendto(bytes(json.dumps({ "Calendar_Status" : { "State" : "Activated" } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
        else :
            json_data_udp.sendto(bytes(json.dumps({ "Calendar_Status" : { "State" : "Deactivated" } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))

                            
        if campaigns_list and scheduler_enabled :
            # Note: events list is sorted by ascendant time !
            # Find the next pending event => the next to be started or the one currently running 
            # 1. Find out first event in the list with EndTime not elapsed
            # 2. For this event if StartTime not elapsed => Event is not started yet 
            #                   if  StartTime is elapsed => Event is running
            pending_campaign = None
            state_campaign = None
            next_change_delay = -1
            for cp in campaigns_list :  
                cp_end = datetime.datetime.strptime(cp['end_str'], '%Y-%m-%dT%H:%M:%S')      
                if loopTimeLap < cp_end:
                    pending_campaign = cp
                    log_msg = "Pending campaign is : From " + pending_campaign['start_str'] + " to " + pending_campaign['end_str'] #+ " (" + pending_campaign['duration'] + " sec) - config : " + pending_campaign['config']
                    logger.debug(log_msg)
                    cp_start = datetime.datetime.strptime(cp['start_str'], '%Y-%m-%dT%H:%M:%S')
                    if loopTimeLap > cp_start:
                        state_campaign = "RUNNING"
                        next_change_delay = (cp_end - loopTimeLap).total_seconds()
                    else:
                        state_campaign = "WAITING"
                        next_change_delay = (cp_start - loopTimeLap).total_seconds()
                    # update info/data towards Cru_Gui (UDP broadcast)
                    json_data_udp.sendto(bytes(json.dumps({ "Calendar_PendingCampaign" : { "Campaign" : pending_campaign } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
                    break
            
            # TO DO AND CHECK : in order to speedup computing, we could remove previous passed events from campaigns_list
            #         store the index of the pendig_event and remove all items whose index is smaller
            #         for i in range(0,idx) campaigns_list.pop(i)
             
            if pending_campaign != None and state_campaign != None and next_change_delay > 0 :
                # if next change will occure soon, ie in a shorter time than the loop period, we are waiting for it right here           
                if next_change_delay > 0 and next_change_delay < (LOOP_PERIOD + 1):
                    time.sleep(next_change_delay)
                    # change from RUNNING to WAITING (end of campaign)
                    if state_campaign == "RUNNING":
                        log_msg = "Pending campaign is ending : " + pending_campaign['start_str'] + " - " + pending_campaign['end_str'] 
                        logger.info(log_msg)
                        firmware_json_tcp_cmd.stop_campaign_and_PMs()
                        state_campaign = "WAITING"
                        time.sleep(1)
                    # change from WAITING to RUNNING (begining of campaign)
                    elif state_campaign == "WAITING":
                        log_msg = "New campaign is starting : " + pending_campaign['start_str'] + " - " + pending_campaign['end_str'] 
                        logger.info(log_msg)                        
                        # check if it's a "DummyCampaign", in this case Firmware won't power ON the PM's !
                        tmp_config_str = json.loads(pending_campaign['config'])
                        if (tmp_config_str['CM_Comments'] == "DummyCampaign"):
                            firmware_json_tcp_cmd.start_campaign_and_PMs(pending_campaign, DummyCampaign=True)
                        else:
                            firmware_json_tcp_cmd.start_campaign_and_PMs(pending_campaign, DummyCampaign=False)
                        state_campaign = "RUNNING"
                        time.sleep(1)
                        
            # At any iteration loop, we (sanity) check that Firmware state if in line with the events scheduling...
            if  firmware_json_tcp_cmd.get_campaign_state() == "Running" and state_campaign == "WAITING":
                logger.warning("Firmware said that campaign is running whereas it should not... let's stop measures.")
                firmware_json_tcp_cmd.stop_campaign_and_PMs()
                time.sleep(1)
                    
            elif  firmware_json_tcp_cmd.get_campaign_state() == "Idle" and state_campaign == "RUNNING":
                # need to recalculate duration
                pending_campaign_end = datetime.datetime.strptime(pending_campaign['end_str'], '%Y-%m-%dT%H:%M:%S')
                updated_duration = pending_campaign_end - loopTimeLap;
                force_restart_campaign = pending_campaign
                force_restart_campaign['duration'] = str(int(updated_duration.total_seconds()))
                log_msg = "Firmware said it is idle whereas campaign should be runnning : " + force_restart_campaign['start_str'] + " - " + force_restart_campaign['end_str']
                logger.warning(log_msg)
                log_msg = "Let's start the measures. Remaining duration is " + force_restart_campaign['duration'] + " seconds"
                logger.warning(log_msg)
                # check if it's a "DummyCampaign", in this case Firmware won't power ON the PM's !
                tmp_config_str = json.loads(force_restart_campaign['config'])
                if (tmp_config_str['CM_Comments'] == "DummyCampaign"):
                    firmware_json_tcp_cmd.start_campaign_and_PMs(force_restart_campaign, DummyCampaign=True)
                else:
                    firmware_json_tcp_cmd.start_campaign_and_PMs(force_restart_campaign, DummyCampaign=False)
                # update info/data towards Cru_Gui (UDP broadcast)
                json_data_udp.sendto(bytes(json.dumps({ "Calendar_PendingCampaign" : { "Campaign" : force_restart_campaign } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
                time.sleep(1)
                
            elif  firmware_json_tcp_cmd.get_campaign_state() == "Running" and state_campaign == "RUNNING":
                logger.debug("Campaign is running...")
                
            elif  firmware_json_tcp_cmd.get_campaign_state() == "Idle" and state_campaign == "WAITING":
                logger.debug("No Campaign running...")

        else:
            if campaigns_list == None:
                logger.debug("Campaign list is empty")
            if not scheduler_enabled :
                logger.debug("Scheduler is disabled")
                    
        # try to download new events from the web every 2 hours
        # if so it will update the 'cru_events.json' file and we willupdate the events list
        # we compare last_google_update versus 'loopTimeLap' in to avoid to call 'datetime.now()' too often (might be time consuming ?)
        if not last_google_update or (loopTimeLap - last_google_update) > datetime.timedelta(hours = 2):
            if gcal == None:
               gcal = google_cal_connect(minimum_duration=3*LOOP_PERIOD, minimum_interval=2*LOOP_PERIOD)              
            if gcal.update_json_file_of_events() == True:
                campaigns_list = gcal.get_events_list_from_json_file()
                last_google_update = loopTimeLap
                # update info/data towards Cru_Gui (UDP broadcast)
                json_data_udp.sendto(bytes(json.dumps({ "Calendar_ScheduledCampaigns" : { "Campaigns" : campaigns_list } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))

        # loop every 'LOOP_PERIOD'
        remainingTime = LOOP_PERIOD - (datetime.datetime.now() - loopTimeLap).total_seconds()
        time.sleep(remainingTime)


################################################################################
def HandleJsonCommands(request):
    global campaigns_list
    global scheduler_enabled
    global pending_campaign
    global state_campaign

    global json_data_udp
    global JSON_DATA_UDP_IP
    global JSON_DATA_UDP_PORT

    if request['Command'] == 'Calendar_trigStatus' :
        logger.info("Received Command Calendar_trigStatus on Json socket")
        if scheduler_enabled :
            json_data_udp.sendto(bytes(json.dumps({ "Calendar_Status" : { "State" : "Activated" } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
        else :
            json_data_udp.sendto(bytes(json.dumps({ "Calendar_Status" : { "State" : "Deactivated" } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
        return {"ReturnCode " : "RC_OK" }

    elif request['Command'] == 'Calendar_trigCampaigns' :
        logger.info("Received Command  Calendar_trigCampaigns on Json socket")
        json_data_udp.sendto(bytes(json.dumps({ "Calendar_ScheduledCampaigns" : { "Campaigns" : campaigns_list } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
        json_data_udp.sendto(bytes(json.dumps({ "Calendar_PendingCampaign" : { "Campaign" : pending_campaign } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
        return {"ReturnCode " : "RC_OK" }

    elif request['Command'] == 'Calendar_Activate' :
        logger.info("Received Command Calendar_Activate on Json socket")
        CalMode = str(request['Parameters']['OnOff'])
        if CalMode.lower() == 'on' : 
            scheduler_enabled = True
            json_data_udp.sendto(bytes(json.dumps({ "Calendar_Status" : { "State" : "Activated" } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
        else :
            scheduler_enabled = False
            json_data_udp.sendto(bytes(json.dumps({ "Calendar_Status" : { "State" : "Deactivated" } }), "utf-8"), (JSON_DATA_UDP_IP, JSON_DATA_UDP_PORT))
        return {"ReturnCode " : "RC_OK", "Answer" : ""}


################################################################################
if __name__ == "__main__":
    
    # Logger parameters
    logger = cru_logger.setup_logger()
    logger.info("Starting cru_calendar...")

    # Calendar YAML config file loading
    with open("./cru_calendar.yaml", 'r') as stream:
       try:
           logger.debug('Trying to parse yaml config file')
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

    # Init connection to cru firmware 
    firmware_json_tcp_cmd = cru_fw_connect("ws://" + str(FIRMWARE_JSON_CMD_TCP_IP) + ":" + str(FIRMWARE_JSON_CMD_TCP_PORT))

    # Init Json Data/Status UDP broadcast      
    json_data_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Init Json Command TCP server
    json_tcp_cmd_srv = json_server(callback_request_handler=HandleJsonCommands, socket_ipaddress=JSON_CMD_TCP_IP, socket_port=JSON_CMD_TCP_PORT)
    
    # Start Scheduler stuff     
    try:
        _thread.start_new_thread(HandleCampaignsScheduling, ())
    except:
        logger.critical("Could not start thread for campaign's scheduler")
     
    # Start Json commands Websocket server      
    logger.info("Starting Json commands server...")
    json_tcp_cmd_srv.StartJsonServer() # blocking call, infinite loop
    logger.critical("Should not reach this point !!")





