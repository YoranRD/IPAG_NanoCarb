from textwrap import wrap
import os

statinfo = os.stat("../Exemples_Raw_Image/Manta_2021_07_05_12_15_01.raw")
size = statinfo.st_size
print(size)

with open("../Exemples_Raw_Image/Manta_2021_07_05_12_15_01.raw", 'rb') as f:
    comment = f.read(256)
    nom_cam = f.read(16)
    version_cam = f.read(16)
    freq = f.read(32)
    ti = f.read(32)
    
    print("Comment : ", comment)
    print("\nnom_cam : ", nom_cam)
    print("\nversion_cam : ", version_cam)
    print("\nfreq : ", freq)
    print("\nti : ", ti)

    for i in range(512):
        data = f.read(16).hex()
        data = " ".join(wrap(data, 2))
        print(data)

    print("\n")
    f.seek(size-4096)
    end = f.read(4096)

    print(end)