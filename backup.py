from flask import Flask, render_template
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#Define GPIO output pins
FRONTM= 7
FRONTM2= 10
FRONTME= 8

BACKM= 22
BACKM2= 24
BACKME= 15

TURNM= 16
TURNM2= 18
TURNME= 13

#Define GPIO output/input Distance Sensor pins BOARD
F_TRIGGER = 38
F_ECHO = 40

R_TRIGGER = 33
R_ECHO = 31

L_TRIGGER = 37
L_ECHO = 35


#Setup GPIO

#Distance Sensors
GPIO.setup(F_TRIGGER, GPIO.OUT)
GPIO.setup(F_ECHO, GPIO.IN)

GPIO.setup(R_TRIGGER, GPIO.OUT)
GPIO.setup(R_ECHO, GPIO.IN)

GPIO.setup(L_TRIGGER, GPIO.OUT)
GPIO.setup(L_ECHO, GPIO.IN)

#Motor Control
GPIO.setup(FRONTM,GPIO.OUT)
GPIO.setup(FRONTM2,GPIO.OUT)
GPIO.setup(FRONTME,GPIO.OUT)

GPIO.setup(BACKM, GPIO.OUT)
GPIO.setup(BACKM2, GPIO.OUT)
GPIO.setup(BACKME, GPIO.OUT)

GPIO.setup(TURNM, GPIO.OUT)
GPIO.setup(TURNM2, GPIO.OUT)
GPIO.setup(TURNME, GPIO.OUT)

#Pulse Width Modulation at 100 Frequency
pwm = GPIO.PWM(FRONTME, 100)
pwmB = GPIO.PWM(BACKME, 100)
pwmT = GPIO.PWM(TURNME, 100)

pwm.start(0)
pwmB.start(0)
pwmT.start(0)

killSwitch = False
MAXDIST = 75 #IN centimeters

@app.route("/Motor_On",methods=["POST"])
def Motor_On():

        #Set gears going forward with no turning motion
        GPIO.output(FRONTM,GPIO.HIGH)
        GPIO.output(FRONTM2,GPIO.LOW)
        GPIO.output(FRONTME,GPIO.HIGH)

        GPIO.output(BACKM, GPIO.LOW)
        GPIO.output(BACKM2, GPIO.HIGH)
        GPIO.output(BACKME, GPIO.HIGH)

        GPIO.output(TURNME, GPIO.HIGH)

        GPIO.output(F_TRIGGER, GPIO.LOW)
        GPIO.output(R_TRIGGER, GPIO.LOW)
        GPIO.output(L_TRIGGER, GPIO.LOW)
        time.sleep(1)

        forward(killSwitch, MAXDIST)

@app.route('/Motor_Off',methods=["POST"])
def Motor_Off():


        #Motor off button pressed--> stop motion of car and turn off all distance sensors
        killSwitch = True
        forward(killSwitch,MAXDIST)
        pwm.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        pwmT.ChangeDutyCycle(0)
        GPIO.output(F_TRIGGER, GPIO.LOW)
        GPIO.output(R_TRIGGER, GPIO.LOW)
        GPIO.output(L_TRIGGER, GPIO.LOW)

        GPIO.output(FRONTME, GPIO.LOW)
        GPIO.output(BACKME, GPIO.LOW)
        GPIO.output(TURNME, GPIO.LOW)

        return "ok"


@app.route('/Destination_Reached',methods=["POST"])
def Destination_Reached():

        #Destination Reached Button has been pressed turn off all motors, stop any motion, cleanup GPIO
        killSwitch= True
        forward(killSwitch, MAXDIST)
        pwm.stop()
        pwmB.stop()
        pwmT.stop()
        GPIO.output(F_TRIGGER, GPIO.LOW)
        GPIO.output(R_TRIGGER, GPIO.LOW)
        GPIO.output(L_TRIGGER, GPIO.LOW)
        GPIO.output(FRONTME, GPIO.LOW)
        GPIO.output(BACKME, GPIO.LOW)
        GPIO.output(TURNME, GPIO.LOW)
        GPIO.cleanup()


        return "ok"


@app.route('/',methods=["GET"])
def home():
        return render_template('index.html', title="Motor On")


def forward(killSwitch, MAXDIST):#killSwitch=False, MAXDIST= 75cm

    # MOVE FORWARD
    while killSwitch == False:

        pwm.ChangeDutyCycle(53)
        pwmB.ChangeDutyCycle(100)
        pwmT.ChangeDutyCycle(0)
        time.sleep(1)

        # Call the moveback function to check if the sensor is too close to an object in front of it.
        right, left = moveBack(MAXDIST)
        if (right ==False) and (left == False):
            EitherDirection(MAXDIST)

    if killSwitch:
        GPIO.output(FRONTME, GPIO.LOW)
        GPIO.output(BACKME, GPIO.LOW)
        GPIO.output(TURNME, GPIO.LOW)


def moveBack(MD):

    GPIO.output(F_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)

    GPIO.output(F_TRIGGER, GPIO.LOW)
    while GPIO.input(F_ECHO) == 0:
        pulse_start_time = time.time()
    while GPIO.input(F_ECHO) == 1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    front_distance = round(pulse_duration * 17150, 2)

    # If the distance picked up by the front sensor is less than the maximum
    # distance, stop the car and put it in reverse
    if front_distance < MD:

        # Have to stop the car before putting it in reverse
        pwm.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        time.sleep(.5)

        # Switch Gears to Reverse
        GPIO.output(FRONTM, GPIO.LOW)
        GPIO.output(FRONTM2, GPIO.HIGH)

        GPIO.output(BACKM, GPIO.HIGH)
        GPIO.output(BACKM2, GPIO.LOW)

        time.sleep(.5)

        pwm.ChangeDutyCycle(70)
        pwmB.ChangeDutyCycle(100)

        time.sleep(3)

        pwm.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)

        GPIO.output(FRONTM, GPIO.HIGH)
        GPIO.output(FRONTM2, GPIO.LOW)

        GPIO.output(BACKM, GPIO.LOW)
        GPIO.output(BACKM2, GPIO.HIGH)

        time.sleep(.5)
        #Now check if something is on the let of it or right
        obstacleR = moveRight(MD)
        obstacleL = moveLeft(MD)

        return obstacleR, obstacleL
    else:
        return True, False

def moveRight(maxDist):

    #Activate Left Distance sensor to see if need to move right
    GPIO.output(L_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)

    while GPIO.input(L_ECHO) == 0:
        pulse_start_timeF = time.time()
    while GPIO.input(L_ECHO) == 1:
        pulse_end_timeL = time.time()

    pulse_durationR = pulse_end_timeL - pulse_start_timeF
    left_distance = round(pulse_durationR * 17150, 2)

    if left_distance < maxDist:
        #Object on left, stop car, go right, then left to go back to a forward position.
        GPIO.output(TURNM, GPIO.LOW)
        GPIO.output(TURNM2, GPIO.HIGH)
        GPIO.output(TURNME, GPIO.HIGH)

        pwm.ChangeDutyCycle(80)
        pwmB.ChangeDutyCycle(100)
        pwmT.ChangeDutyCycle(100)

        time.sleep(2)
        pwm.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        pwmT.ChangeDutyCycle(0)

        GPIO.output(TURNM, GPIO.LOW)
        GPIO.output(TURNM2, GPIO.HIGH)
        pwmT.ChangeDutyCycle(100)
        time.sleep(1)

        pwmT.ChangeDutyCycle(0)
        pwm.ChangeDutyCycle(50)
        pwmB.ChangeDutyCycle(100)
        time.sleep(1)

        pwm.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        return True  # True that there are things to the left of it
    else:

        return False  # False that there is nothing to the left of it.

def moveLeft(maxD):

    GPIO.output(R_TRIGGER, GPIO.HIGH)

    time.sleep(0.00001)

    GPIO.output(R_TRIGGER, GPIO.LOW)

    while GPIO.input(R_ECHO) == 0:
            pulse_start_time = time.time()

    while GPIO.input(R_ECHO) == 0:
            pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    right_distance = round(pulse_duration * 17150, 2)

    if right_distance < maxD:
            GPIO.output(TURNME, GPIO.HIGH)
            GPIO.output(TURNM, GPIO.LOW)
            GPIO.output(TURNM2, GPIO.HIGH)
            pwm.ChangeDutyCycle(50)
            pwmB.ChangeDutyCycle(100)
            time.sleep(2)

            pwm.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(0)

            GPIO.output(TURNM, GPIO.HIGH)
            GPIO.output(TURNM2, GPIO.LOW)
            pwm.ChangeDutyCycle(50)
            pwmB.ChangeDutyCycle(100)
            time.sleep(1)
            pwm.ChangeDutyCycle(0)
            pwmB.ChangeDutyCycle(0)

            GPIO.output(TURNME, GPIO.LOW)

            time.sleep(1)
            return True #True that there are things to the right of it
    else:
            return False #False that there is nothing to the right of it.


def EitherDirection(MaxiD):

        #Where there is something in the front of it but nothing to the left or right of it.
        # WHEN IN DOUBT JUST MOVE TO THE RIGHT IF THERE IS NOTHING ON EITHER SIDE
        GPIO.output(TURNM, GPIO.HIGH)
        GPIO.output(TURNM2, GPIO.LOW)
        pwm.ChangeDutyCycle(60)
        pwmB.ChangeDutyCycle(100)
        time.sleep(2)
        pwm.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)

        GPIO.output(TURNM, GPIO.LOW)
        GPIO.output(TURNM2, GPIO.HIGH)

        time.sleep(1)

        pwm.ChangeDutyCycle(30)
        pwmB.ChangeDutyCycle(50)

        time.sleep(1)

        pwm.ChangeDutyCycle(0)
        pwmB.ChangeDutyCycle(0)
        GPIO.output(TURNME, GPIO.LOW)

