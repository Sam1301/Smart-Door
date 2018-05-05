import time
from pyfingerprint.pyfingerprint import PyFingerprint
import RPi.GPIO as gpio
import picamera
import os

# LCD connected pins
RS = 18
EN = 23
D4 = 24
D5 = 25
D6 = 8
D7 = 7

enrol = 5  # enroll fingerprint push button pin
delet = 6  # delete fingerprint push button pin
inc = 13  # increment push button pin
dec = 19  # decrement push button pin
led = 26  # led pin

HIGH = 1
LOW = 0

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

# setup LCD interfacing
gpio.setup(RS, gpio.OUT)
gpio.setup(EN, gpio.OUT)
gpio.setup(D4, gpio.OUT)
gpio.setup(D5, gpio.OUT)
gpio.setup(D6, gpio.OUT)
gpio.setup(D7, gpio.OUT)

# setup push buttons
gpio.setup(enrol, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(delet, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(inc, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(dec, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(led, gpio.OUT)

try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if (f.verifyPassword() == False):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('Exception message: ' + str(e))
    exit(1)


def begin():
  lcdcmd(0x33)
  lcdcmd(0x32)
  lcdcmd(0x06)
  lcdcmd(0x0C)
  lcdcmd(0x28)
  lcdcmd(0x01)
  time.sleep(0.0005)


def lcdcmd(ch):
  gpio.output(RS, 0)
  gpio.output(D4, 0)
  gpio.output(D5, 0)
  gpio.output(D6, 0)
  gpio.output(D7, 0)
  if ch & 0x10 == 0x10:
    gpio.output(D4, 1)
  if ch & 0x20 == 0x20:
    gpio.output(D5, 1)
  if ch & 0x40 == 0x40:
    gpio.output(D6, 1)
  if ch & 0x80 == 0x80:
    gpio.output(D7, 1)
  gpio.output(EN, 1)
  time.sleep(0.005)
  gpio.output(EN, 0)
  # Low bits
  gpio.output(D4, 0)
  gpio.output(D5, 0)
  gpio.output(D6, 0)
  gpio.output(D7, 0)
  if ch & 0x01 == 0x01:
    gpio.output(D4, 1)
  if ch & 0x02 == 0x02:
    gpio.output(D5, 1)
  if ch & 0x04 == 0x04:
    gpio.output(D6, 1)
  if ch & 0x08 == 0x08:
    gpio.output(D7, 1)
  gpio.output(EN, 1)
  time.sleep(0.005)
  gpio.output(EN, 0)


def lcdwrite(ch):
  gpio.output(RS, 1)
  gpio.output(D4, 0)
  gpio.output(D5, 0)
  gpio.output(D6, 0)
  gpio.output(D7, 0)
  if ch & 0x10 == 0x10:
    gpio.output(D4, 1)
  if ch & 0x20 == 0x20:
    gpio.output(D5, 1)
  if ch & 0x40 == 0x40:
    gpio.output(D6, 1)
  if ch & 0x80 == 0x80:
    gpio.output(D7, 1)
  gpio.output(EN, 1)
  time.sleep(0.005)
  gpio.output(EN, 0)
  # Low bits
  gpio.output(D4, 0)
  gpio.output(D5, 0)
  gpio.output(D6, 0)
  gpio.output(D7, 0)
  if ch & 0x01 == 0x01:
    gpio.output(D4, 1)
  if ch & 0x02 == 0x02:
    gpio.output(D5, 1)
  if ch & 0x04 == 0x04:
    gpio.output(D6, 1)
  if ch & 0x08 == 0x08:
    gpio.output(D7, 1)
  gpio.output(EN, 1)
  time.sleep(0.005)
  gpio.output(EN, 0)


def lcdclear():
  lcdcmd(0x01)


def lcdprint(Str):
  l = 0
  l = len(Str)
  for i in range(l):
    lcdwrite(ord(Str[i]))


def setCursor(x, y):
    if y == 0:
        n = 128+x
    elif y == 1:
        n = 192+x
    lcdcmd(n)


def takePictureAndMail():
       camera = picamera.PiCamera()
       camera.capture('intruder.jpg')
       os.system("python /home/pi/sendNotify.py")


def enrollFinger():
    lcdcmd(1)
    lcdprint("Enrolling Finger")
    time.sleep(2)
    print('Waiting for finger...')
    lcdcmd(1)
    lcdprint("Place Finger")
    while (f.readImage() == False):
        pass
    f.convertImage(0x01)
    result = f.searchTemplate()
    positionNumber = result[0]
    if (positionNumber >= 0):
        print('Template already exists at position #' + str(positionNumber))
        lcdcmd(1)
        lcdprint("Finger ALready")
        lcdcmd(192)
        lcdprint("   Exists     ")
        time.sleep(2)
        return
    print('Remove finger...')
    lcdcmd(1)
    lcdprint("Remove Finger")
    time.sleep(2)
    print('Waiting for same finger again...')
    lcdcmd(1)
    lcdprint("Place Finger")
    lcdcmd(192)
    lcdprint("   Again    ")
    while (f.readImage() == False):
        pass
    f.convertImage(0x02)
    if (f.compareCharacteristics() == 0):
        print "Fingers do not match"
        lcdcmd(1)
        lcdprint("Finger Did not")
        lcdcmd(192)
        lcdprint("   Matched   ")
        time.sleep(2)
        return
    f.createTemplate()
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    lcdcmd(1)
    lcdprint("Stored at Pos:")
    lcdprint(str(positionNumber))
    lcdcmd(192)
    lcdprint("successfully")
    print('New template position #' + str(positionNumber))
    time.sleep(2)


def searchFinger():
    try:
        print('Waiting for finger...')
        while(f.readImage() == False):
            #pass
            time.sleep(.5)
            return
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        accuracyScore = result[1]
        if positionNumber == -1:
            takePictureAndMail()
            print('No match found!')
            lcdcmd(1)
            lcdprint("No Match Found")
            time.sleep(2)
            return
        else:
            print('Found template at position #' + str(positionNumber))
            gpio.output(led, HIGH)
            lcdcmd(1)
            lcdprint("Found at Pos:")
            lcdprint(str(positionNumber))
            time.sleep(2)

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)


def deleteFinger():
    positionNumber = 0
    count = 0
    lcdcmd(1)
    lcdprint("Delete Finger")
    lcdcmd(192)
    lcdprint("Position: ")
    lcdcmd(0xca)
    lcdprint(str(count))
    while gpio.input(enrol) == True:   # here enrol key means ok
        if gpio.input(inc) == False:
            count = count+1
            if count > 1000:
                count = 1000
            lcdcmd(0xca)
            lcdprint(str(count))
            time.sleep(0.2)
        elif gpio.input(dec) == False:
            count = count-1
            if count < 0:
                count = 0
            lcdcmd(0xca)
            lcdprint(str(count))
            time.sleep(0.2)
    positionNumber = count
    if f.deleteTemplate(positionNumber) == True:
        print('Template deleted!')
        lcdcmd(1)
        lcdprint("Finger Deleted")
        time.sleep(2)


begin()
lcdcmd(0x01)
lcdprint("Smart Door")
time.sleep(3)
flag = 0
lcdclear()

while 1:
    gpio.output(led, HIGH)
    lcdcmd(1)
    lcdprint("Place Finger")
    if gpio.input(enrol) == 0:
        gpio.output(led, LOW)
        enrollFinger()
    elif gpio.input(delet) == 0:
        gpio.output(led, LOW)
        while gpio.input(delet) == 0:
            time.sleep(0.1)
        deleteFinger()
    else:
        searchFinger()
