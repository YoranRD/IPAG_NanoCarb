from inspect import FrameInfo
import sys
import aravis
import struct
from datetime import datetime, date, time, timezone

nbImg = 100
fileName = "test1.raw"
frameRate = 20
IT = 1000

tab1 = []

start = datetime.now()
start = start.timestamp()*1000

ids = aravis.get_device_ids() #List visible cameras
print (len(ids), "cameras available.")

cam = aravis.Camera(ids[1]) #get the first camera
stop = datetime.now()
stop = stop.timestamp()*1000

print(round(stop-start,3))

start = datetime.now()
start = start.timestamp()*1000

# print("Cam ID : ", cam.get_feature('DeviceID'))

 # print ("Old FPS : ", cam.get_feature('FrameRate'))
cam.set_feature("FrameRate", frameRate)
# print ("New FPS : ", cam.get_feature('FrameRate'))

# print("Old IT :", cam.get_feature('IntegrationTime'))
cam.set_feature("IntegrationTime", IT)
# print("New IT :", cam.get_feature('IntegrationTime'))


# print ("New FPS : ", cam.get_feature('FrameRate'))


#print("PixelFormat : ", cam.get_feature('PixelFormat'))
#print("Width : ", cam.get_feature('Width'))
#print("Height : ", cam.get_feature('Height'))

stop = datetime.now()
stop = stop.timestamp()*1000

print(round(stop-start,3))
cam.start_acquisition_continuous(nb_buffers=10)
f = open(fileName, "wb")

# Skip first header #
f.seek(1024, 1)

idImg = 0

begin = datetime.now()
begin = begin.timestamp()*1000

for i in range (nbImg):
    timestamp_ns, frameId, frame = cam.pop_frame() # get frame from camera

    if i == 10:
        print(timestamp_ns)
    
    start = datetime.now()
    start = start.timestamp()*1000

    # Write headers #
    # Timestamp #
    f.write(struct.pack('Q', timestamp_ns))
    ts = timestamp_ns/1.0e9
    dt = datetime.fromtimestamp(ts)
    f.write(struct.pack('H', dt.year))
    f.write(struct.pack('H', dt.month))
    f.write(struct.pack('H', dt.day))
    f.write(struct.pack('H', dt.hour))
    f.write(struct.pack('H', dt.minute))
    f.write(struct.pack('H', dt.second))
    f.write(struct.pack('H', round(dt.microsecond/1000)))

    # Frame ID #
    f.write(struct.pack('I', frameId))
    f.write(struct.pack('I', idImg))

    # T_FPA #
    t_fpa = struct.pack('d', cam.get_feature("TemperatureFPA"))
    f.write(t_fpa)

    # T_Engine #
    t_engine = struct.pack('d', cam.get_feature("TemperatureEngine"))
    f.write(t_engine)

    # Skip the rest of header to have a 1024 size #
    f.seek(978, 1)

    f.write(frame.data)

    idImg += 1
    stop = datetime.now()
    stop = stop.timestamp()*1000
    tab1.append(round(stop-start, 3))

end = datetime.now()
end = end.timestamp()*1000

totalTime = end-begin

print("Total Time (s) : ", round(totalTime/1000, 3))
print("Calculated FPS : ", round(nbImg/(totalTime/1000), 2))

print("Min : ", min(tab1))
print("Avg : ", round(sum(tab1)/len(tab1), 3))
print("Max : ", max(tab1))
    

f.close()
cam.stop_acquisition()