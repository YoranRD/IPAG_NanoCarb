from textwrap import wrap
import os

def writeImgRawFrom(nameTo, nameFrom, seek, length):
    with open(nameFrom, 'rb') as f1:
        f1.seek(seek)
        with open(nameTo, 'wb') as f2:
            for i in range(int(length/2)):
                data1 = f1.read(1)
                data2 = f1.read(1)
                f2.write(data2)
                f2.write(data1)

def printHex(f, seek, length):
    f.seek(seek)
    for i in range(int(length/16)):
        data = f.read(16).hex()
        data = " ".join(wrap(data, 2))
        print(data)
    print("\n")


def printImgHeader(f, seek):
    f.seek(seek)
    print("tps : ")
    print(f.read(8).hex()+"\n")
    print("Année : ")
    print(f.read(2).hex() + "\n")
    print("Mois : ")
    print(f.read(2).hex() + "\n")
    print("Jour : ")
    print(f.read(2).hex() + "\n")
    print("Heure : ")
    print(f.read(2).hex() + "\n")
    print("Minute : ")
    print(f.read(2).hex() + "\n")
    print("Seconde : ")
    print(f.read(2).hex() + "\n")
    print("Milliseconde : ")
    print(f.read(2).hex() + "\n")
    print("id_img : ")
    print(f.read(4).hex() + "\n")
    print("index_img : ")
    print(f.read(4).hex() + "\n")
    print("T_FPA : ")
    print(f.read(8).hex() + "\n")
    print("T_Engine : ")
    print(f.read(8).hex() + "\n")
    print("T_front : ")
    print(f.read(8).hex() + "\n")
    print("T_stirling : ")
    print(f.read(8).hex() + "\n")



"""
statinfo = os.stat('../Exemples_Raw_Image/NANOCARBCO2_2021_07_05_12_14_59.raw')
size = statinfo.st_size
with open("../Exemples_Raw_Image/NANOCARBCO2_2021_07_05_12_14_59.raw", 'rb') as f:
    printHex(f, 1024, 2048)
    printImgHeader(f, 1024+656384*5000)

    f.seek(0)
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

    

#writeImgRawFrom('test_img_1_header-img.raw', '../Exemples_Raw_Image/NANOCARBCO2_2021_07_05_12_14_59.raw', 1024, 1024)



statinfo = os.stat('../python-aravis/python-aravis-master/test1.raw')
size = statinfo.st_size
with open('../python-aravis/python-aravis-master/test1.raw', 'rb') as f:
    printHex(f, 1024, 2048)
    printImgHeader(f, 1024+656384*50)

    f.seek(0)
    comment = f.read(256)
    nom_cam = f.read(16)
    version_cam = f.read(16)
    freq = f.read(32)
    ti = f.read(32)
    
"""

with open('../Acquisition/video_files/testHeader.raw', 'rb') as f:
    printHex(f, 0, 1024)
    printImgHeader(f, 0)