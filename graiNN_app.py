# import the necessary packages
from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import tkinter as tki
from tkinter import ttk, Label, HORIZONTAL, Frame, RIGHT, Toplevel, Canvas, CENTER
from tkinter.ttk import Progressbar
import tkinter.font as tkFont
import threading
import datetime
import imutils
import cv2
import argparse
import time
import imutils
from imutils.video import VideoStream
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc.dispatcher import Dispatcher
from typing import List, Any
from utils import add_default_args
import asyncio
import pyglet
from gpiozero import Button, LED
import RPi.GPIO as GPIO


pyglet.font.add_file("/usr/share/fonts/truetype/Input Mono Compressed Medium.ttf")

class graiNN_AppHandler:
    def __init__(self, vs, client1, client2):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = vs
        self.client1 = client1
        self.client2 = client2
        self.thread = None
        self.frame = None
        self.stopEvent = None
        self.modus = None
        # initialize the root window and image panel
        self.root = tki.Tk()
        #self.root.geometry('1024x720')
        # set background color to black
        self.panel = None
        self.counter = 1
        self.time_looped = 0
        self.training_type = "min"
        self.chosen_parameter = 1
        self.counter_min = 40
        self.counter_max = 540
        self.button_blue = Button(26, pull_up=False)
        self.toggle_up = Button(13)
        self.toggle_down = Button(4)
        self.frame4 = None
        self.frame5 = None
        self.example_num = None

        
        self.font_text = 'Input Mono Compressed'
        self.font_upper_text = 'Input Mono Compressed'
        
        #define toggle state
        self.toggle_up_U = None
        self.toggle_down_U = None
        
        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.switch, args=())
        self.thread.setDaemon(True)
        self.thread.start()

        # set a callback to handle when the window is closed
        self.root['bg'] = 'black'
        self.root.wm_attributes('-fullscreen', True)
        self.root.bind("<F11>", lambda event: self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen")))
        self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.wm_title("One-Man-Band Synth")
    
    # creates an OSC message bundle and sends it everytime a frame is initialized 
    def send_hands(self, detections: [landmark_pb2.NormalizedLandmarkList]):
        global num_detections
        if detections is None:
            self.client1.send_message("/mediapipe/hands", 0)
            num_detections = 0
            return num_detections
        
        num_detections = len(detections)
        # create bundle: [values, 0]
        builder = OscMessageBuilder(address="/mediapipe/hands")
        for detection in detections:
            for landmark in detection.landmark:
                builder.add_arg(landmark.x)
                builder.add_arg(landmark.y)
                builder.add_arg(landmark.z)
        msg = builder.build()
        self.client1.send(msg)
        return num_detections

    #send values to supercollider
    def send_sc(self, osc_message):
        print(osc_message)
        self.client2.send_message("/granular", osc_message)   # Send float message

    #recalculate the incoming osc messages
    def cal_density_min(self, osc_val1):
        density_min = (50 - (int(osc_val1 * 50)))
        return density_min
    
    def cal_density_max(self, osc_val2):
        density_max = (int((osc_val2) * 50))
        return density_max

    def cal_duration_min(self, osc_val3):
        duration_min = (50 - (int(osc_val3 * 50)))
        return duration_min
    
    def cal_duration_max(self, osc_val4):
        duration_max = (int((osc_val4) * 50))
        return duration_max

    def cal_position_min(self, osc_val7):
        position_min = (50 - (int(osc_val7 * 50)))
        return position_min
    
    def cal_position_max(self, osc_val8):
        position_max = (int((osc_val8) * 50))
        return position_max

    def cal_pitch_min(self, osc_val5):
        pitch_min = (50 - (int(osc_val5 * 50)))
        return pitch_min
    
    def cal_pitch_max(self, osc_val6):
        pitch_max = (int((osc_val6)* 50))
        return pitch_max

    def cal_speed_min(self, osc_val9):
        speed_min = (50 - (int(osc_val9 * 50)))
        return speed_min
    
    def cal_speed_max(self, osc_val10):
        speed_max = (int((osc_val10) * 50))
        return speed_max

    def set_bar(self, address_dis: str, *args: List[Any]) -> None:
        print("received func")
        address_dis = "/wek/outputs"
        
        global den_min
        global den_max
        global dur_min
        global dur_max
        global pit_min
        global pit_max
        global pos_min
        global pos_max
        global spe_min
        global spe_max

        if not len(args) == 10:
            print("length is wrong")
            print("length arguments: ", len(args))
            return 

        # Check that address starts with /wek/outputs
        if not address_dis == "/wek/outputs":  # Cut off the last character
            print("Could not find adress")
            return

        osc_val1 = args[0]
        osc_val2 = args[1]
        osc_val3 = args[2]
        osc_val4 = args[3]
        osc_val5 = args[4]
        osc_val6 = args[5]
        osc_val7 = args[6]
        osc_val8 = args[7]
        osc_val9 = args[8]
        osc_val10 = args[9]
        
        #send osc message
        osc_message = [osc_val1, osc_val2, osc_val3, osc_val4, osc_val5, osc_val6, osc_val7, osc_val8, osc_val9, osc_val10]
        self.send_sc(osc_message)

        den_min = self.cal_density_min(osc_val1)
        den_max = self.cal_density_max(osc_val2)
        dur_min = self.cal_duration_min(osc_val3)
        dur_max = self.cal_duration_max(osc_val4)
        pit_min = self.cal_pitch_min(osc_val5)
        pit_max = self.cal_pitch_max(osc_val6)
        pos_min = self.cal_position_min(osc_val7)
        pos_max = self.cal_position_max(osc_val8)
        spe_min = self.cal_speed_min(osc_val9)
        spe_max = self.cal_speed_max(osc_val10)

        print(f"Setting bar with {address_dis} values: {den_min}, {den_max}, {dur_min}, {dur_max}, {pos_min}, {pos_max}, {pit_min}, {pit_max}, {spe_min}, {spe_max}")
        return {'den_min':den_min, 'den_max':den_max, 'dur_min':dur_min, 'dur_max':dur_max,'pos_min':pos_min, 'pos_max':pos_max, 'pit_min':pit_min, 'pit_max':pit_max, 'spe_min':spe_min, 'spe_max':spe_max}

    def draw_bars(self, frame2):
        print("received function")
        style = ttk.Style()
        style.theme_use('alt')
        font_text = 'Input Mono Compressed'
        TROUGH_COLOR_MIN = 'white'
        BAR_COLOR_MIN = 'black'
        TROUGH_COLOR_MAX = 'black'
        BAR_COLOR_MAX = 'white'
        BORDER_COLOR = 'black'
        LENGTH_BAR = 50

        style.configure("bar_min.Horizontal.TProgressbar", troughcolor=TROUGH_COLOR_MIN, bordercolor=BORDER_COLOR, background=BAR_COLOR_MIN, lightcolor=BORDER_COLOR, darkcolor=BORDER_COLOR, borderwidth=0, thickness=20)
        style.configure("bar_max.Horizontal.TProgressbar", troughcolor=TROUGH_COLOR_MAX, bordercolor=BORDER_COLOR, background=BAR_COLOR_MAX, lightcolor=BORDER_COLOR, darkcolor=BORDER_COLOR, borderwidth=0, thickness=20)

        global pb1
        global pb2
        global pb3
        global pb4
        global pb5
        global pb6
        global pb7
        global pb8
        global pb9
        global pb10

        #Frame(height = 480,width = 800,bg = 'black').pack()  
        
        den_text = Label(frame2, text="density", fg='blue', bg='black', font=(font_text, 12))
        den_text.place(x=10, y=30)
        #bar "density_min"
        pb1 = ttk.Progressbar(frame2, style="bar_min.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, length = LENGTH_BAR, value = 50, mode = 'determinate')
        pb1.place(x=12, y=55)
        #bar "density_max"
        pb2 = ttk.Progressbar(frame2, style="bar_max.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, length = LENGTH_BAR, value = 0, mode = 'determinate')
        pb2.place(x=63, y=55)

        # Progressbar "duration"
        dur_text = Label(frame2, text="duration", fg='blue', bg='black', font=(font_text, 12))
        dur_text.place(x=10, y=100)
        #bar "duration_min"
        pb3 = ttk.Progressbar(frame2, style="bar_min.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, length = LENGTH_BAR, value = 50, mode = 'determinate')
        pb3.place(x=12, y=125)
        #bar "duration_max"
        pb4 = ttk.Progressbar(frame2, style="bar_max.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, length = LENGTH_BAR, value = 0, mode = 'determinate')
        pb4.place(x=63, y=125)

        # Progressbar "position"
        pos_text = Label(frame2, text="pitch", fg='blue', bg='black', font=(font_text, 12))
        pos_text.place(x=10, y=170)
        #bar "position_min"
        pb5 = ttk.Progressbar(frame2, style="bar_min.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, value = 50, length = LENGTH_BAR, mode = 'determinate')
        pb5.place(x=12, y=195)
        #bar "position_max"
        pb6 = ttk.Progressbar(frame2, style="bar_max.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, value = 0, length = LENGTH_BAR, mode = 'determinate')
        pb6.place(x=63, y=195)
        
        # Progressbar "pitch"
        pit_text = Label(frame2,text="position", fg='blue', bg='black', font=(font_text, 12))
        pit_text.place(x=10, y=240)
        #bar "pitch_min"
        pb7 = ttk.Progressbar(frame2, style="bar_min.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, value = 50, length = LENGTH_BAR,mode = 'determinate')
        pb7.place(x=12, y=265)
        #bar "pitch_max"
        pb8 = ttk.Progressbar(frame2, style="bar_max.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, value = 0, length = LENGTH_BAR,mode = 'determinate')
        pb8.place(x=63, y=265)

        # Progressbar "speed"
        spe_text = Label(frame2, text="speed", fg='blue', bg='black', font=(font_text, 12))
        spe_text.place(x=10, y=310)
        #bar "speed_min"
        pb9 = ttk.Progressbar(frame2, style="bar_min.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, value = 50, length = LENGTH_BAR, mode = 'determinate')
        pb9.place(x=12, y=335)
        #bar "speed_max"
        pb10 = ttk.Progressbar(frame2, style="bar_max.Horizontal.TProgressbar", orient = HORIZONTAL, maximum = 50, value = 0, length = LENGTH_BAR, mode = 'determinate')
        pb10.place(x=63, y=335)
    
    def update_bars(self, den_min, den_max, dur_min, dur_max, pit_min, pit_max, pos_min, pos_max, spe_min, spe_max):
        print("hellow updated")
        self.root.update_idletasks()
        print("updated idle tasks")
        pb1['value'] = den_min
        pb2['value'] = den_max
        pb3['value'] = dur_min
        pb4['value'] = dur_max  
        pb5['value'] = pit_min
        pb6['value'] = pit_max
        pb7['value'] = pos_min
        pb8['value'] = pos_max
        pb9['value'] = spe_min  
        pb10['value'] = spe_max
        time.sleep(0.01) 
        print("finished updated values")

    def get_probabilities(self, num_detections):
        if num_detections == 2:
            print("getting probabbilities")
            #self.server.handle_request()
            #print("handeled request")

        else:
            print("detections mismatch")
            return

    def simple_choice(self, num_detections):
        if num_detections == 2 and 'den_min' in globals():
            self.update_bars(den_min, den_max, dur_min, dur_max, pit_min, pit_max, pos_min, pos_max, spe_min, spe_max)
        else: 
            return

    def play_modus(self):
        print("switched to play modus")
        self.videoLoop()

    def map_modus(self):
        self.mapLoop()

    def switch(self):
        global toggle_down
        global toggle_up
        global toggle_down_U
        self.toggle_down_U = "true"
        global toggle_up_U
        self.toggle_up_U = "true"
        
        #initialize GPIO blue encoder
        self.blue_encoder_parameters()
        #initialize GPIO min and max parameters
        self.min_max_encoder()

        
        while True: 
            if self.toggle_up.is_pressed and self.toggle_up_U == "true":
                print("SWITCHLOOP: going into play modus")
                self.modus = "play"
                self.toggle_up_U = "false"
                self.videoLoop()

            elif self.toggle_down.is_pressed and self.toggle_down_U == "true":
                print("SWITCHLOOP: going into map modus!")
                self.modus = "map"
                self.toggle_down_U = "false"
                self.UI_loop()

    
    def videoLoop(self):
    # DISCLAIMER:
    # I'm not a GUI developer, nor do I even pretend to be. This
    # try/except statement is a pretty ugly hack to get around
    # a RunTime error that Tkinter throws due to threading
        #first draw all the empty bars once
        #start running wekinator
        self.example_num = None

        if self.modus == "play":
            # if play modus do this: 
            self.client1.send_message("/wekinator/control/startRunning", 0)
            time.sleep(0.5)
            frame2 = Frame(self.root, width=150, height=400, bg= "black")
            frame2.pack(side=RIGHT)
            self.draw_bars(frame2)
            time.sleep(0.5)
            
    
        elif self.modus == "map":
            self.time_looped = 1
            OUTPUT_VALUES = "/wekinator/control/outputs"
            START_RECORDING = "/wekinator/control/startRecording"
            STOP_RECORDING = "/wekinator/control/stopRecording"
            #decide to train for max or for min values
            
            if self.training_type == "min":
                #self.client1.send_message("/wekinator/control/outputs", [0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00])
                time.sleep(1)
            elif self.training_type == "max":
                #self.client1.send_message("/wekinator/control/outputs", [0.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00])
                time.sleep(1)
                
            print("send output min duration values")
            # start recording
            #self.client1.send_message(START_RECORDING, 0)
            
        while True:
             #start drawing the hands
            mp_drawing = mp.solutions.drawing_utils
            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                print(self.modus)
                
                if self.modus == "map":
                    if self.example_num == None and self.training_type == "min":
                        self.example_num = Label(self.frame4, text="0", fg='white', bg='blue', font=(self.font_text, 21))
                    
                    elif self.example_num == None and self.training_type == "max":
                        self.example_num = Label(self.frame5, text="0", fg='white', bg='blue', font=(self.font_text, 21))

                    else:
                        self.example_num.destroy()
                        self.time_looped = self.time_looped + 1
                        
                    if self.modus == "map":
                         if self.training_type == "min":
                            print("hey")
                            self.example_num = Label(self.frame4, text=str(self.time_looped), fg='white', bg='blue', font=(self.font_text, 21))
                            self.example_num.place(x=0, y=350)
                            
                         elif self.training_type == "max":
                            print("ha")
                            self.example_num = Label(self.frame5, text=str(self.time_looped), fg='white', bg='blue', font=(self.font_text, 21))
                            self.example_num.place(x=0, y=350)
                    
                if self.modus == "play" and self.toggle_down.is_pressed:
                    self.modus = "map"
                    frame2.destroy()
                    print("map_modus activated")
                    self.client1.send_message("/wekinator/control/stopRunning", 0)
                    self.counter = 1 
                    self.UI_loop()
                
                elif self.modus == "map" and self.toggle_up.is_pressed:
                    self.modus = "play"
                    print("map_modus activated")
                    self.client1.send_message("/wekinator/control/stopRecording", 0)
                    self.videoLoop()
                    
                else:
        
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                    self.frame = self.vs.read()
                    self.frame = imutils.resize(self.frame, width=600)
            
                    # OpenCV represents images in BGR order; however PIL
                    # represents images in RGB order, so we need to swap
                    # the channels, then convert to PIL and ImageTk format
                    self.frame = cv2.cvtColor(cv2.flip(self.frame, 1), cv2.COLOR_BGR2RGB)

                    # To improve performance, optionally mark the image as not writeable to pass by reference.
                    self.frame.flags.writeable = False
                    results = hands.process(self.frame)
                    
                    self.send_hands(results.multi_hand_landmarks)
                    #draw black screen over the videoloop
                    cv2.rectangle(self.frame, (0,0), (600,480), (0,0,0), -1)
                    cv2.rectangle(self.frame, (-1,-1), (600,480), (255, 255, 255), 2)
                    
                    if self.modus == "play":
                        print(self.modus)
                        self.get_probabilities(num_detections)
                        self.simple_choice(num_detections)
                        
                    #check if button is pressed and turn on led
                    #self.is_button_pressed()
                    
                    # returns the results of the multi_hand_landmarks 
                    # Draw the hand annotations on the image.
                    self.frame.flags.writeable = True
                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    #create image
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)
                    
                    # if the panel is not None, we need to initialize it
                    if self.panel is None:
                        self.panel = tki.Label(image=image)
                        self.panel.image = image
                        self.panel.pack(side="left", padx=20, pady=50)
            
                    # otherwise, simply update the panel
                    else:
                        self.panel.configure(image=image)
                        self.panel.image = image
                        self.panel.pack(side="left", padx=20, pady=0)
                    
                
                    if self.time_looped == 50:
                        self.client1.send_message("/wekinator/control/stopRecording", 0)
                        return
                   
    def blue_encoder_parameters(self):
        global blue_cod
        global blue_nod
        counter = 1
        blue_cod = 14
        blue_nod = 15
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(blue_cod, GPIO.IN)
        GPIO.setup(blue_nod, GPIO.IN)
        GPIO.add_event_detect(blue_cod, GPIO.RISING, callback=self.blue_encoder_decode, bouncetime=10)
        return
    
    def min_max_encoder(self):
        #GPIO.cleanup()
        global min_l
        global min_r
        global max_l
        global max_r
        counter_min = 0
        counter_max = 550
        min_l = 24
        min_r = 25
        max_l = 6
        max_r = 5
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(min_l, GPIO.IN)
        GPIO.setup(min_r, GPIO.IN)
        GPIO.setup(max_l, GPIO.IN)
        GPIO.setup(max_r, GPIO.IN)
        GPIO.add_event_detect(min_l, GPIO.RISING, callback=self.min_encoder_decode, bouncetime=10)
        GPIO.add_event_detect(max_l, GPIO.RISING, callback=self.max_encoder_decode, bouncetime=10)
        return
        
    def parameter_UI(self, frame1):
        time.sleep(0.2)
        frame1.tkraise()
        print("sketching paramters")
        #draw the panel above
        #define colour of text depending on scrolled thing"
        selected_bg = 'blue'
        not_selected_bg = 'black'
        selected_fg = 'white'
        not_selected_fg = 'blue'
        
        map_parameters_text = Label(frame1, text="map/parameters                                     ", fg='white', bg='black', font=(self.font_upper_text, 21,'underline'))
        map_parameters_text.place(x=15, y=5)

        #here draw the first 7 labels: 6 parameters and a next button
        density_text = Label(frame1, text=" density grains  ", fg='white', bg='blue', font=(self.font_text, 21))
        density_text.place(x=30, y=75)
        duration_text = Label(frame1, text=" duration        ", fg='blue', bg='black', font=(self.font_text, 21))
        duration_text.place(x=30, y=115)
        pitch_text = Label(frame1,text=" pitch           ", fg='blue', bg='black', font=(self.font_text, 21))
        pitch_text.place(x=30, y=155)
        position_text = Label(frame1, text=" position        ", fg='blue', bg='black', font=(self.font_text, 21))
        position_text.place(x=30, y=195)
        speed_text = Label(frame1, text=" speed           ", fg='blue', bg='black', font=(self.font_text, 21))
        speed_text.place(x=30, y=235)
        state = 1
        time.sleep(0.2)
        
        while True:
            if self.toggle_up.is_pressed:
                self.modus = "play"
                frame1.destroy()
                self.videoLoop()
                return
            
            elif self.button_blue.is_pressed:
                time.sleep(0.2)
                frame2 = Toplevel(self.root, width=800, height=480, bg= "black")
                frame2.attributes('-fullscreen', True)
                frame1.destroy()
                chosen_parameter = self.counter
                self.counter = 1 
                self.guide_UI(frame2)
                return
                
            else:
                time.sleep(0.5)
                self.update_parameters(density_text, duration_text, pitch_text, position_text, speed_text)
        
    def update_parameters(self, density_text, duration_text, pitch_text, position_text, speed_text):
        self.root.update_idletasks()
        print("updated parameters")
        
        if self.counter == 1:
            density_text['fg'] = 'white'
            density_text['bg'] = 'blue'
            duration_text['fg'] = 'blue'
            duration_text['bg'] = 'black'
            speed_text['fg'] = 'blue'
            speed_text['bg'] = 'black'
        
        elif self.counter == 2:
            duration_text['fg'] = 'white'
            duration_text['bg'] = 'blue'
            density_text['fg'] = 'blue'
            density_text['bg'] = 'black'
            pitch_text['fg'] = 'blue'
            pitch_text['bg'] = 'black'
        
        elif self.counter == 3:
            pitch_text['fg'] = 'white'
            pitch_text['bg'] = 'blue'
            duration_text['fg'] = 'blue'
            duration_text['bg'] = 'black'
            position_text['fg'] = 'blue'
            position_text['bg'] = 'black'
        
        elif self.counter == 4:
            position_text['fg'] = 'white'
            position_text['bg'] = 'blue'
            pitch_text['fg'] = 'blue'
            pitch_text['bg'] = 'black'
            speed_text['fg'] = 'blue'
            speed_text['bg'] = 'black'
        
        elif self.counter == 5:
            speed_text['fg'] = 'white'
            speed_text['bg'] = 'blue'
            position_text['fg'] = 'blue'
            position_text['bg'] = 'black'
            density_text['fg'] = 'blue'
            density_text['bg'] = 'black'
        else:
            return
            
    def guide_UI(self, frame2):
        print("guide ui")
        map_parameters_text = Label(frame2, text="map/duration                                       ", fg='white', bg='black', font=(self.font_upper_text, 21,'underline'))
        #map_parameters_text.grid(column=0,row=1)
        map_parameters_text.place(x=15, y=5)
        process_text = Label(frame2, text=" gesture-parameter mapping process:  ", fg='white', bg='black', font=(self.font_text, 21))
        process_text.place(x=30, y=75)
        step1_text = Label(frame2, text=" 1. set range of parameter", fg='white', bg='black', font=(self.font_text, 21))
        step1_text.place(x=30, y=115)
        step2_text = Label(frame2, text=" 2. generate examples min value", fg='white', bg='black', font=(self.font_text, 21))
        step2_text.place(x=30, y=155)
        step3_text = Label(frame2, text=" 3. generate examples max value", fg='white', bg='black', font=(self.font_text, 21))
        step3_text.place(x=30, y=195)
        step4_text = Label(frame2, text=" 4. train", fg='white', bg='black', font=(self.font_text, 21))
        step4_text.place(x=30, y=235)
        step5_text = Label(frame2, text=" 5. handgesture-sound mapping created!", fg='white', bg='black', font=(self.font_text, 21))
        step5_text.place(x=30, y=275)
        
        back_text = Label(frame2, text=" < back ", fg='white', bg='black', font=(self.font_text, 21))
        back_text.place(x=15, y=440)
        next_text = Label(frame2, text=" next > ", fg='white', bg='blue', font=(self.font_text, 21))
        next_text.place(x=660, y=440)
        
        while True:
            if self.toggle_up.is_pressed:
                frame2.destroy()
                self.modus = "play"
                self.videoLoop()
                return
            
            elif self.button_blue.is_pressed:
                time.sleep(0.2)
                frame3 = Toplevel(self.root, width=800, height=480, bg= "black")
                frame3.attributes('-fullscreen', True)
                frame2.destroy()
                self.counter = 1 
                self.range_UI(frame3)
                return
                
            else:
                # here create a new global counter 2 and set it to 1 or 2 
                time.sleep(0.2)
                #self.update_nav(back_text, next_text)
        
    def update_circles(self, circle_canvas, left_circle, right_circle, text_min, text_max):
        circle_canvas.coords(left_circle, self.counter_min, 40, self.counter_min + 20, 60)
        circle_canvas.coords(right_circle, self.counter_max, 40, self.counter_max + 20, 60)
        circle_canvas.coords(text_min, self.counter_min, 80)
        circle_canvas.coords(text_max, self.counter_max, 80)
        
    def range_UI(self, frame3):
        VALUE_MIN = "value min" 
        print("range ui")
        map_parameters_text = Label(frame3, text="map/duration/range                                 ", fg='white', bg='black', font=(self.font_upper_text, 21,'underline'))
        map_parameters_text.grid(column=0,row=1)
        map_parameters_text.place(x=15, y=5)
        
        range_text = Label(frame3, text=" set range for parameter: duration", fg='white', bg='black', font=(self.font_text, 21))
        range_text.place(x=30, y=75)
        
        back_text = Label(frame3, text=" < back ", fg='white', bg='black', font=(self.font_text, 21))
        back_text.place(x=15, y=440)
        next_text = Label(frame3, text=" next > ", fg='white', bg='blue', font=(self.font_text, 21))
        next_text.place(x=660, y=440)
        
        #draw two circles
        circle_canvas = Canvas(frame3, bg="black", height=100, width=600, highlightthickness=0)
        circle_canvas.create_line(50, 50, 550, 50, fill="blue", width=3)
        left_circle = circle_canvas.create_oval(40, 40, 60, 60, fill="#D3D3D3", width=0)
        text_min = circle_canvas.create_text(40, 80, text="min", fill="#D3D3D3", font=(self.font_text, 14))
        right_circle = circle_canvas.create_oval(540, 40, 560, 60, fill="#D3D3D3", width=0)
        text_max = circle_canvas.create_text(540, 80, text="max", fill="#D3D3D3", font=(self.font_text, 14))
        circle_canvas.pack()
        circle_canvas.place(x=100, y=200)

        while True:
            if self.toggle_up.is_pressed:
                frame3.destroy()
                self.modus = "play"
                self.videoLoop()
                return
            
            elif self.button_blue.is_pressed:
                time.sleep(0.2)
                self.frame4 = Frame(self.root, width=150, height=480, bg= "black")
                self.frame4.pack(side=RIGHT)
                frame3.destroy()
                self.counter = 1
                self.modus = "map"
                self.gen_min_UI()
                return
            
            #elif:
            #self.update_circles() 
            else:
                # here create a new global counter 2 and set it to 1 or 2 
                time.sleep(0.2)
                self.update_circles(circle_canvas, left_circle, right_circle, text_min, text_max)
        
    def gen_min_UI(self):
        VALUE = "0"
        print("gen_min")
        min_text = Label(self.frame4, text="MIN", fg='white', bg='black', font=(self.font_upper_text, 21,'underline'))
        min_text.place(x=0, y=5)
        count_down_text = Label(self.frame4, text="duration", fg='white', bg='black', font=(self.font_text, 16))
        count_down_text.place(x=0, y=50)
        count_down_5 = Label(self.frame4, text="5...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_5.place(x=0, y=230)
        time.sleep(1)
        count_down_5.destroy()
        count_down_4 = Label(self.frame4, text="4...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_4.place(x=0, y=230)
        time.sleep(1)
        count_down_4.destroy()
        count_down_3 = Label(self.frame4, text="3...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_3.place(x=0, y=230)
        time.sleep(1)
        count_down_3.destroy()
        count_down_2 = Label(self.frame4, text="2...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_2.place(x=0, y=230)
        time.sleep(1)
        count_down_2.destroy()
        count_down_1 = Label(self.frame4, text="1...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_1.place(x=0, y=230)
        time.sleep(1)
        count_down_1.destroy()
        #start training!
        
        self.training_type = "min"
        self.videoLoop()
        next_text = Label(self.frame4, text=" next > ", fg='white', bg='blue', font=(self.font_text, 21))
        next_text.place(x=0, y=430)
        
        print("done recording min") 
        
        while True:
            if self.toggle_up.is_pressed:
                self.frame4.destroy()
                self.modus = "play"
                self.videoLoop()
                return
            
            elif self.button_blue.is_pressed:
                self.frame5 = Frame(self.root, width=150, height=480, bg= "black")
                self.frame5.pack(side=RIGHT)
                self.frame4.destroy()
                self.counter = 1
                self.training_type == "max"
                self.modus = "map"
                self.gen_max_UI()
                return
        
            else:
                # here create a new global counter 2 and set it to 1 or 2 
                time.sleep(0.2)
                print("waiting for press")                 
    
    
    def gen_max_UI(self):
        VALUE = "0"
        print("gen_max")
        min_text = Label(self.frame5, text="MAX", fg='white', bg='black', font=(self.font_upper_text, 21,'underline'))
        min_text.place(x=0, y=5)
        count_down_text = Label(self.frame5, text="duration", fg='white', bg='black', font=(self.font_text, 16))
        count_down_text.place(x=0, y=50)
        
        #amount_samples_text = Label(frame5, text="0 samples", fg='white', bg='black', font=(self.font_text, 16))
        #amount_samples.place(x=0, y=275)

        count_down_5 = Label(self.frame5, text="5...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_5.place(x=0, y=230)
        time.sleep(1)
        count_down_5.destroy()
        count_down_4 = Label(self.frame5, text="4...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_4.place(x=0, y=230)
        time.sleep(1)
        count_down_4.destroy()
        count_down_3 = Label(self.frame5, text="3...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_3.place(x=0, y=230)
        time.sleep(1)
        count_down_3.destroy()
        count_down_2 = Label(self.frame5, text="2...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_2.place(x=0, y=230)
        time.sleep(1)
        count_down_2.destroy()
        count_down_1 = Label(self.frame5, text="1...", fg='white', bg='black', font=(self.font_text, 21))
        count_down_1.place(x=0, y=230)        
        time.sleep(1)
        count_down_1.destroy()
        #start training!
        
        self.training_type = "max"
        self.videoLoop()
        next_text = Label(self.frame5, text=" train > ", fg='white', bg='blue', font=(self.font_text, 21))
        next_text.place(x=0, y=430)
        
        print("done recording max") 
        
        while True:
            if self.toggle_up.is_pressed:
                self.frame5.destroy()
                self.modus = "play"
                self.videoLoop()
                return
            
            elif self.button_blue.is_pressed:
                frame6 = Toplevel(self.root, width=800, height=480, bg= "black")
                frame6.attributes('-fullscreen', True)
                self.frame5.destroy()
                self.counter = 1 
                self.train(frame6)
                return
        
            else:
                # here create a new global counter 2 and set it to 1 or 2 
                time.sleep(0.2)
                print("waiting for press")
    
    #def trainings_status(frame6):
        
    
    def train(self, frame6):
        self.training_type = "min"
        print("starting training")
        TRAIN = "/wekinator/control/train"
        map_parameters_text = Label(frame6, text="map/duration/train                                 ", fg='white', bg='black', font=(self.font_upper_text, 21,'underline'))
        #map_parameters_text.grid(column=0,row=1)
        map_parameters_text.place(x=15, y=5)
        training_text = Label(frame6, text="gesture-duration mapping:", fg='white', bg='black', font=(self.font_text, 21))
        training_text.place(x=30, y=75)
        
        #start trainingsprocess
        #self.client1.send_message(TRAIN, 0)
        time.sleep(0.2)
        #self.trainings_status(frame6)
        status_text = Label(frame6, text="training.  ", fg='white', bg='black', font=(self.font_text, 21))
        status_text.place(x=30, y=115)
        time.sleep(1)
        status_text.destroy()
        status_text2 = Label(frame6, text="training.. ", fg='white', bg='black', font=(self.font_text, 21))
        status_text2.place(x=30, y=115)
        time.sleep(1)
        status_text2.destroy()
        status_text3 = Label(frame6, text="training...", fg='white', bg='black', font=(self.font_text, 21))
        status_text3.place(x=30, y=115)
        time.sleep(10)
        
        #if training is done print the follwing
        status_text = Label(frame6, text="training done!", fg='white', bg='black', font=(self.font_text, 21))
        status_text.place(x=30, y=115)
        step2_text = Label(frame6, text="switch back to [play] to interact with your", fg='white', bg='black', font=(self.font_text, 21))
        step2_text.place(x=30, y=155)
        step3_text = Label(frame6, text="new mapping", fg='white', bg='black', font=(self.font_text, 21))
        step3_text.place(x=30, y=195)
        
        while True:
            if self.toggle_up.is_pressed:
                    frame6.destroy()
                    #stop training
                    self.time_looped = 0
                    self.modus = "play"
                    self.videoLoop()
                    return
            else:
                time.sleep(0.2)
        
    def blue_encoder_decode(self, blue_cod):
        global counter
        time.sleep(0.005)
        global Switch_A
        Switch_A = GPIO.input(blue_cod)
        global Switch_B
        Switch_B = GPIO.input(15)
                
        if (Switch_A == 1) and (Switch_B == 0):
            self.counter = self.counter + 1
            if self.counter == 6:
                self.counter = 1
            if self.counter == 0:
                self.counter = 5
            print("direction -> ", self.counter)
            while True:
                if Switch_B == 0:
                    Switch_B = GPIO.input(15)
                elif Switch_B == GPIO.input(15):
                    return
 
        elif (Switch_A == 1) and (Switch_B == 1):
            self.counter -= 1
            if self.counter == 6:
                self.counter = 1
            if self.counter == 0:
                self.counter = 5
            print("direction <- ", self.counter)
            while Switch_A == 1:
                Switch_A = GPIO.input(blue_cod)
            return
        else:
            return
        
    def min_encoder_decode(self, min_l):
        global counter_min
        time.sleep(0.005)
        global Switch_C
        Switch_C = GPIO.input(min_l)
        global Switch_D
        Switch_D = GPIO.input(25)
                
        if (Switch_C == 1) and (Switch_D == 0):
            self.counter_min = self.counter_min - 5
            if self.counter_min == -5:
                self.counter_min = 0
            print("direction -> ", self.counter_min)
            while True:
                if Switch_D == 0:
                    Switch_D = GPIO.input(25)
                elif Switch_D == GPIO.input(25):
                    return
 
        elif (Switch_C == 1) and (Switch_D == 1):
            self.counter_min = self.counter_min + 5
            if self.counter_min == - 5:
                self.counter_min = 0          
            print("direction <- ", self.counter_min)
            while Switch_C == 1:
                Switch_C = GPIO.input(min_l)
            return
        else:
            return
        
    def max_encoder_decode(self, max_l):
        global counter_max
        time.sleep(0.005)
        global Switch_E
        Switch_E = GPIO.input(max_l)
        global Switch_F
        Switch_F = GPIO.input(5)
                
        if (Switch_E == 1) and (Switch_F == 0):
            self.counter_max = self.counter_max + 5
            if self.counter_max == 555:
                self.counter_max = 550    
            print("direction -> ", self.counter_max)
            while True:
                if Switch_F == 0:
                    Switch_F = GPIO.input(5)
                elif Switch_F == GPIO.input(5):
                    return
 
        elif (Switch_E == 1) and (Switch_F == 1):
            self.counter_max = self.counter_max - 5
            print("direction <- ", self.counter_max)
            while Switch_E == 1:
                Switch_E = GPIO.input(max_l)
            return
        else:
            return
        
     
    
    def UI_loop(self):
        #define all the frames:
        global frame1
        frame1 = Toplevel(self.root, width=800, height=480, bg= "black")
        frame1.attributes('-fullscreen', True)
        #draw the first screen
        self.parameter_UI(frame1)
        #self.range_UI()
        #self.train_min_UI()
        #self.done_training_UI()
        
        """"
        while True:
            get_state()
            draw_state()
            get_gpio_button()
            get_gpio_encoders()
            
        """ 

    
    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        #self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
        print("quitted") 
        






