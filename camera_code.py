from tkinter import Label
import tensorflow_hub as hub
import cv2
import tensorflow as tf
import pandas as pd
import pyttsx3
import threading
import time
import PySimpleGUI as sg


alarm_sound = pyttsx3.init()
voices = alarm_sound.getProperty('voices')
alarm_sound.setProperty('voice', voices[0].id)
alarm_sound.setProperty('rate', 150)

def voice_alarm(alarm_sound: pyttsx3.Engine,text):
    alarm_sound.say(f'{text} detected')
    alarm_sound.runAndWait()
    time.sleep(5)
   


detector = hub.load("https://tfhub.dev/tensorflow/efficientdet/lite2/detection/1")
labels = pd.read_csv('labels.csv',sep=';',index_col='ID')
labels = labels['OBJECT (2017 REL.)']

cap = cv2.VideoCapture(0)

width = 640
height = 420

# Define the window's contents
layout = [  [sg.Text("Project")],     # Part 2 - The Layout
            [sg.Button('open camera')] ]

# Create the window
window = sg.Window('Window Title', layout)      # Part 3 - Window Defintion

while(True):
    # Display and interact with the Window
    event, values = window.read()                   # Part 4 - Event loop or Window.read call


    #Capture frame-by-frame
    ret, frame = cap.read()
    
    #Resize to respect the input_shape
    inp = cv2.resize(frame, (width , height ))

    #Convert img to RGB
    rgb = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)

    #Is optional but i recommend (float convertion and convert img to tensor image)
    rgb_tensor = tf.convert_to_tensor(rgb, dtype=tf.uint8)

    #Add dims to rgb_tensor
    rgb_tensor = tf.expand_dims(rgb_tensor , 0)
    
    boxes, scores, classes, num_detections = detector(rgb_tensor)
    
    pred_labels = classes.numpy().astype('int')[0]
    
    pred_labels = [labels[i] for i in pred_labels]
    pred_boxes = boxes.numpy()[0].astype('int')
    pred_scores = scores.numpy()[0]
    for score, (ymin,xmin,ymax,xmax), label in zip(pred_scores, pred_boxes, pred_labels):
        if score < 0.5:
            continue  
        score_txt = f'{100 * round(score,0)}'
        rgb = cv2.rectangle(rgb,(xmin, ymax),(xmax, ymin),(0,255,0),3)      
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(rgb,label,(xmin, ymax-10), font, 0.5, (255,0,0), 1, cv2.LINE_AA)
        cv2.putText(rgb,score_txt,(xmax, ymax-10), font, 0.5, (255,0,0), 1, cv2.LINE_AA)
        if label != 'person':
            alarm = threading.Thread(target=voice_alarm, args=(alarm_sound,label))
            alarm.start()
    rgb = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    cv2.imshow('object detection',rgb)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
alarm_sound.stop()
cv2.destroyAllWindows()


# Finish up by removing from the screen
window.close()   