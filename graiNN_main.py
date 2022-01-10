#first set display
import os
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')
    
# import the map app
#from Map_App import Map_Handler
#import the play app
from graiNN_app import graiNN_AppHandler

# import OSC libraries
from pythonosc import udp_client
from pythonosc.osc_server import BlockingOSCUDPServer, AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

# import all other dependencies
from typing import List, Any
import random
import imutils
from imutils.video import VideoStream
import argparse
import time
from gpiozero import Button, LED
import threading
from multiprocessing import Process

dispatcher = Dispatcher()

def default_handler(address, *args):  
    print(f"DEFAULT {address}: {args}")

def start_server():
    print("Start server")
    server = BlockingOSCUDPServer(("localhost", 1337), dispatcher)
    server.serve_forever()
    
def app():
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--picamera", type=int, default=-1,
        help="whether or not the Raspberry Pi camera should be used")
    args = vars(ap.parse_args())

    # initialize the video stream and allow the camera sensor to warmup
    print("[INFO] warming up camera...")

    # start videostream and set up UDP client with IP: 127.0.0.1 and port 7500
    vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
    client1 = udp_client.SimpleUDPClient("localhost", 7500)
    client2 = udp_client.SimpleUDPClient("127.0.0.1", 57120)

    print("Initialize hands handler")
    time.sleep(2) 
    # initialize all message handlers
    print("Initialize dispatcher")
    omb = play_AppHandler(vs, client1, client2)
    dispatcher.map("/wek/outputs", omb.set_bar)  
    dispatcher.set_default_handler(default_handler)
    
    print("Start server thread")
    thread = threading.Thread(target=start_server)
    thread.start()

    print("Start tkinter")
    omb.root.mainloop()
    
def is_button_pressed():
    #setup OSC sender to Supercollider. Which sound to send
    client_samples = udp_client.SimpleUDPClient("127.0.0.1", 57120)
    OSC_ADRESS = "/on_off"
    
    button1_pressed = "false"
    button2_pressed = "false"
    button3_pressed = "false"
    button4_pressed = "false"

    led_1 = LED(0)
    led_4 = LED(1)
    led_3 = LED(16)
    led_2 = LED(12)

    button1 = Button(17)
    button2 = Button(27)
    button3 = Button(23)
    button4 = Button(22)
    
    #buttons from left to right. When button is pressed in play mode, callback function to send OSC message
    while True:
        #send OSC message
        if led_1.value == 1 and button1_pressed == "false":
            print("OSC_M: Sending OSC button1 = pressed")
            client_samples.send_message(OSC_ADRESS, "start_sample_1")
            button1_pressed = "true"
        
        elif led_1.value == 0 and button1_pressed == "true":
            print("OSC_M: Sending OSC button1 = not pressed")
            client_samples.send_message(OSC_ADRESS, "stop_sample_1")
            button1_pressed = "false"
            
        elif led_2.value == 1 and button2_pressed == "false":
            print("OSC_M: Sending OSC button2 = pressed")
            client_samples.send_message(OSC_ADRESS, "start_sample_2")
            button2_pressed = "true"
        
        elif led_2.value == 0 and button2_pressed == "true":
            print("OSC_M: Sending OSC button1 = not pressed")
            client_samples.send_message(OSC_ADRESS, "stop_sample_2")
            button2_pressed = "false"

        elif led_3.value == 1 and button3_pressed == "false":
            print("OSC_M: Sending OSC button3 = pressed")
            client_samples.send_message(OSC_ADRESS, "start_sample_3")
            button3_pressed = "true"
        
        elif led_3.value == 0 and button3_pressed == "true":
            print("OSC_M: Sending OSC button1 = not pressed")
            client_samples.send_message(OSC_ADRESS, "stop_sample_3")
            button3_pressed = "false"
            
        elif led_4.value == 1 and button4_pressed == "false":
            print("OSC_M: Sending OSC button2 = pressed")
            client_samples.send_message(OSC_ADRESS, "start_sample_4")
            button4_pressed = "true"
        
        elif led_4.value == 0 and button4_pressed == "true":
            print("OSC_M: Sending OSC button4 = not pressed")
            client_samples.send_message(OSC_ADRESS, "stop_sample_4")
            button4_pressed = "false"
            
        button2.when_pressed = led_2.toggle
        button4.when_pressed = led_3.toggle
        button1.when_pressed = led_4.toggle
        button3.when_pressed = led_1.toggle
    
def main():
    proc1 = Process(target=app)
    proc1.start()
    print("started pocess 1")
    time.sleep(5)
    proc2 = Process(target=is_button_pressed)
    proc2.start()
    print("started process 2")
    
if __name__ == '__main__':
    main()
    
    
