from machine import I2C
from vl53l1x import VL53L1X
import sensor, image, time,json
from pyb import UART
import json
import struct ,pyb
#1:red 2:green 3:blue

def find_max(blobs):#return the max blob
    max_size=0
    for blob in blobs:
    if blob.pixels() > max_size:
        max_blob=blob
        max_size = blob.pixels()
        return max_blob
def send_data_packet(x, y):#串口发送函数定义
    temp = struct.pack("<bbii", #格式为俩个字符俩个整型
    0xAA, #帧头1
    0xAE, #帧头2
    int(x), # up sample by 4 #数据1
    int(y)) # up sample by 4 #数据2
    uart.write(temp) #串口发送
    print(x,y)

def compareBlob(blob1,blob2):#比较色块后返回最大值
    tmp = blob1.pixels() - blob2.pixels()
    if tmp == 0:
        return 0;
    elif tmp > 0:
        return 1;
    else:
        return -1;

threshold_index = 0

#红绿蓝色环阈值

objthresholds=[(42, 76, 5, 35, -3, 88),

            (53, 66, -23, -5, 17, -5),
            
            (49, 61, -12, 18, -27, -3)]
graythreshold=[(100,255)]#二值化阈值

sensor.reset()

sensor.set_pixformat(sensor.RGB565)

sensor.set_framesize(sensor.QVGA)

sensor.skip_frames(time = 1000)

sensor.set_auto_gain(False) # must be turned off for color tracking

sensor.set_auto_whitebal(False) # must be turned off for color tracking

clock = time.clock()

A=7 #串口接收执行代码初始值

i= 1 #二维码发送触发代码值初始值

r=0

red_threshold_01 = (29, 47, 50, 72, 34, 57)#红色色块阈值

green_threshold_01=(18, 72, -60, -26, 16, 43)#绿色色块阈值

blue_threshold_01=(8, 58, -17, 23, -54, -16) #蓝色色块阈值

uart =UART(3,115200)

while(True):

clock.tick()

img = sensor.snapshot()

if( uart.any() ):

    print("range: mm ")
    
    r=uart.readline()
    
    
    print(r)
    
    if r==b'1':

        A=1
        print('A=1')
    if r==b'2':
        A=2
        print('A=2')
    if r==b'3':

        A=3
        print('A=3')

    if r==b'4':
        A=4
        print('A=4')

    if r==b'5':
        A=5
        print('A=5')

    if r==b'6':
        A=6
        print('A=6')
    if r==b'7':
        A=7
        print('A=6')
    #else:
       # A=0

if i==1:#二维码识别
     img.lens_corr(1.8) # strength of 1.8 is good for the 2.8mm lens.
     for code in img.find_qrcodes():
        print(code.payload())
        led = pyb.LED(1)
        led.on()
        output_str=code.payload()
        uart.write(output_str+'\r\n')
        #print('send:',output_str)
        led.off()
        i=1
if(A==1):#红色色块识别

    blobs1= img.find_blobs([red_threshold_01],area_threshold=150)
    if blobs1:
    #如果找到了目标颜色
        led = pyb.LED(1)
        led.on()
        max_blob=find_max(blobs1)
        print('sum :', len(blobs1))
        img.draw_rectangle(max_blob.rect())
        img.draw_cross(max_blob.cx(), max_blob.cy())
        send_data_packet(max_blob.cx()-120,max_blob.cy()-160)

        led.off()
        #output_str=json.dumps([max_blob.cx(),max_blob.cy()]) #方式2
        print('send red blob')
        #uart.write(output_str+'\r\n')

if(A==2):#绿色色块识别

    blobs2=img.find_blobs([green_threshold_01],area_threshold=150)
    if blobs2:
        led = pyb.LED(2)
        led.on()
        #如果找到了目标颜色
        max_blob=find_max(blobs2)
        print('sum :', len(blobs2))
        img.draw_rectangle(max_blob.rect())
        img.draw_cross(max_blob.cx(), max_blob.cy())
        send_data_packet(max_blob.cx()-120,max_blob.cy()-160)

        led.off()
        #output_str=json.dumps([max_blob.cx(),max_blob.cy()]) #方式2
        print('send green blob')




if(A==3):#蓝色色块识别

    blobs3=img.find_blobs([blue_threshold_01],area_threshold=150)
    if blobs3:

        led = pyb.LED(3)
        led.on()
    #如果找到了目标颜色
        max_blob=find_max(blobs3)
        #print('sum :', len(blobs3))
        img.draw_rectangle(max_blob.rect())
        img.draw_cross(max_blob.cx(), max_blob.cy())
        send_data_packet(max_blob.cx()-120,max_blob.cy()-160)

        led.off()
        #output_str=json.dumps([max_blob.cx(),max_blob.cy()]) #方式2
        print('send blue blob')



if(A==4):#红色色环识别
    img.binary([objthresholds[0]])
    img.dilate(2)

    blobs=img.find_blobs(graythreshold,pixels_threshold=2525,area_threashold=1600,merge=True)
    if blobs:
        led = pyb.LED(1)
        led.on()
        bigBlob=blobs[0]
        #print('1')
        for blob in blobs:
            if compareBlob(bigBlob,blob) == -1:
                bigBlob=blob
            img.draw_rectangle(bigBlob.rect())
            #print(bigBlob.cx(),bigBlob.cy())
            #output_str="[%d,%d]" % (bigBlob.cx(),bigBlob.cy())
            #output_str=json.dumps([judge(bigBlob.cx()),judge(bigBlob.cy()),bigBlob.cx(),bigBlob.cy()])
            #uart.write(output_str+'\r\n')
            send_data_packet(bigBlob.cx()-120,bigBlob.cy()-160)

            led.off()
            #print('you send:',bigBlob.cx()-120)
        #uart.write(data_out)

if(A==5):#绿色色环识别
    img.binary([objthresholds[1]])
    img.bilateral(2, color_sigma=0.1, space_sigma=1)
    img.dilate(3)

    blobs=img.find_blobs(graythreshold,pixels_threshold=2025,area_threashold=1600,merge=True)
    if len(blobs)==1:
        led = pyb.LED(2)
        led.on()
        bigBlob=blobs[0]
        for blob in blobs:
            if compareBlob(bigBlob,blob)==-1:
                bigBlob=blob
            img.draw_rectangle(bigBlob.rect())
            #output_str=json.dumps([judge(bigBlob.cx()),judge(bigBlob.cy()),bigBlob.cx(),bigBlob.cy()])
            send_data_packet(bigBlob.cx()-120,bigBlob.cy()-160)

            led.off()
       # uart.write(data_out)
        #print(data_out)

if(A==6):#蓝色色环识别
    img.binary([objthresholds[2]])
    img.bilateral(2, color_sigma=0.1, space_sigma=1)
    img.dilate(3)

    blobs=img.find_blobs(graythreshold,pixels_threshold=2025,area_threashold=1600,merge=True)
    if len(blobs)==1:
        led = pyb.LED(2)
        led.on()
        bigBlob=blobs[0]
        for blob in blobs:
            if compareBlob(bigBlob,blob)==-1:
                bigBlob=blob
            img.draw_rectangle(bigBlob.rect())
            #output_str=json.dumps([judge(bigBlob.cx()),judge(bigBlob.cy()),bigBlob.cx(),bigBlob.cy()])
            send_data_packet(bigBlob.cx()-120,bigBlob.cy()-160)

            led.off()
       # uart.write(data_out)
        #print(data_out)

if(A==7):#红绿蓝三色块顺序识别
     blobs1= img.find_blobs([red_threshold_01],area_threshold=150)
     blobs2=img.find_blobs([green_threshold_01],area_threshold=150)
     blobs3=img.find_blobs([blue_threshold_01],area_threshold=150)
     #if max_blob1.cx()< max_blob2.cx() < max_blob3.cx():
        #print('sadf')
     if blobs1 and blobs2 and blobs3:
        max_blob1=find_max(blobs1)
        img.draw_cross(max_blob1.cx(), max_blob1.cy())
        max_blob2=find_max(blobs2)
        img.draw_cross(max_blob2.cx(), max_blob2.cy())
        max_blob3=find_max(blobs3)
        img.draw_cross(max_blob3.cx(), max_blob3.cy())
        led = pyb.LED(3)
        led.on()
        if max_blob1.cx()< max_blob2.cx() < max_blob3.cx():

            output_str="[%d]" % (123) #方式1
            uart.write(output_str+'\r\n')

        if max_blob1.cx() < max_blob3.cx() < max_blob2.cx():
            output_str="[%d]" % (132) #方式1
            #uart.write('132')
            uart.write(output_str+'\r\n')

        if max_blob2.cx() < max_blob1.cx() < max_blob3.cx():
            output_str="[%d]" % (213) #方式1
            #uart.write('213')
            uart.write(output_str+'\r\n')

        if max_blob2.cx()< max_blob3.cx() < max_blob1.cx():
            #uart.write('231')
            output_str="[%d]" % (231) #方式1
            uart.write(output_str+'\r\n')

        if max_blob3.cx() < max_blob2.cx() < max_blob1.cx():
            #uart.write('321')
            output_str="[%d]" % (321) #方式1
            uart.write(output_str+'\r\n')

        if max_blob3.cx()< max_blob1.cx()  < max_blob2.cx():
            output_str="[%d]" % (312)
            #uart.write('312')
            uart.write(output_str+'\r\n')
        led.off()
       # uart.write(data_out)
#print(clock.fps())