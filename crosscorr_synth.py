#Correlation/Convolution Synthesizer
#Ziqing(Gary) Gong
#Dec 15 2022
#---------------------------------------------------------------
#This project is a ASCII keyboard synthesizer that performs
#convolution and cross-correlation on a user-selected human voice
#with short musical clips.

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
from math import cos,pi,sin
import pyaudio, struct
import tkinter as Tk
from tkinter import filedialog
import numpy as np
import scipy.signal
import wave

#function defination
#quit program
def fun_quit():
  global CONTINUE
  print('Good bye')
  CONTINUE = False

#file opener
def open_file():
    global first_file
    filename = filedialog.askopenfilename(initialdir="/User/zq/desktop",title="Select An Audio File", filetypes=(("wav files", "*.wav"), ("aif files", "*.aif*"), ("mp3 files", "*.mp3")))
    first_file = wave.open(filename,'rb');
    return first_file;

#check and record key press
keys = np.array(['a','w','s','e','d','f','t','g','y','h','u','j'])
play_clips = [False] * 12
def press_key(event):
    global CONTINUE
    global KEYPRESS
    print('You pressed ' + event.char)
    for i in range(0,12):
        if event.char == keys[i]:
            play_clips[i] = True;
            KEYPRESS = True
    if event.char == 'q':
        fun_quit()
    
#variables
MAXVALUE = 2**15-1  # Maximum allowed output signal value for 16-bit audio
RATE = 48000
BLOCKLEN = 4096
CONTINUE = True
KEYPRESS = False

# Initialize plot window for audio output plotting:
fig = plt.figure(1)
plt.ylim(-10000, 10000)

plt.xlim(0, BLOCKLEN)
plt.xlabel('Time (n)')
n = np.arange(0, BLOCKLEN)
y_d = BLOCKLEN * [0]

[g3] = plt.plot([],[],'green')
g3.set_linestyle('solid')
g3.set_label('output')
g3.set_xdata(n)
g3.set_ydata(y_d)
plt.legend()


# Define Tkinter root
root = Tk.Tk()
root.title('Cross-Correlation/Convolution Synthesizer')
root.geometry("800x800")
root.bind("<Key>",press_key)

canvas = FigureCanvasTkAgg(fig,master = root)
canvas.draw()
  
# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack(side='bottom', fill='both', expand=1)


# Define widgets
B_quit = Tk.Button(root, text = 'quit', command = fun_quit)
B_open = Tk.Button(root, text = 'open', command = open_file)

# Place widgets
B_quit.pack(side = Tk.BOTTOM, fill = Tk.X)
B_open.pack(side = Tk.TOP, fill = Tk.X)

# Create Pyaudio object
p = pyaudio.PyAudio()
stream = p.open(
  format = pyaudio.paInt16,  
  channels = 1, 
  rate = RATE,
  input =   False,
  output = True
  )

#audio files to process correlating to each of the 12 keys
#all files are 48k/16-bits
files = np.array(
    [
    wave.open('Audio/baroque.wav','rb'),#a
    wave.open('Audio/marimba.wav','rb'),#w
    wave.open('Audio/violin.wav','rb'), #s
    wave.open('Audio/flute.wav','rb'),  #e
    wave.open('Audio/chords.wav','rb'), #d
    wave.open('Audio/sax.wav','rb'),    #f
    wave.open('Audio/voco.wav','rb'),   #t
    wave.open('Audio/lute.wav','rb'),   #g
    wave.open('Audio/piano.wav','rb'),  #y
    wave.open('Audio/choir.wav','rb'),  #h
    wave.open('Audio/e_piano.wav','rb'),#u
    wave.open('Audio/guitar.wav','rb')  #j
    ]
    )
    
#audio blocks for each audio file in files[]
input_blocks = np.array(
    [
    files[0].readframes(BLOCKLEN),
    files[1].readframes(BLOCKLEN),
    files[2].readframes(BLOCKLEN),
    files[3].readframes(BLOCKLEN),
    files[4].readframes(BLOCKLEN),
    files[5].readframes(BLOCKLEN),
    files[6].readframes(BLOCKLEN),
    files[7].readframes(BLOCKLEN),
    files[8].readframes(BLOCKLEN),
    files[9].readframes(BLOCKLEN),
    files[10].readframes(BLOCKLEN),
    files[11].readframes(BLOCKLEN),
    ]
    )

#initializing the voice file to be cross correlated with other music files
first_file = open_file()
first_block = first_file.readframes(BLOCKLEN)

#output blocks for each cross-correlation with each audio clip
output_blocks = [BLOCKLEN * [0]] * 12

#extracting features of the input voice signal
WIDTH = first_file.getsampwidth()
num_frames = first_file.getnframes()
num_block = (int)(num_frames / BLOCKLEN)

#hanning window for each audio block
w = np.hanning(BLOCKLEN)

print('* Start')
print('Press keys a,w,s,e,d,f,t,g,y,h,u,j for sound')
print('Press "q" to quit')

while CONTINUE:
  plt.ion()
  root.update()
  x = struct.unpack('h' * BLOCKLEN, first_block)
  if KEYPRESS and CONTINUE:
    for i in range(0,12):
        if (play_clips[i]):
            x2 = struct.unpack('h' * BLOCKLEN, input_blocks[i])
            
            #compute cross-correlation in the frequency domain
            X = np.fft.fft(x[::-1])
            X2 = np.fft.fft(x2);
            #multiply the spectrums of x and x2 (x2 backwards)
            output_blocks[i] = np.real(np.fft.ifft(X * X2))
            #convolve the cross-correlation again with the original signal (x)
            
            #(I discovered that an extra process of convolution with the original signal (using the current block length) would remove many of the musical/tonal aspect with audio files, so I commented it out for now)
            
            #output_blocks[i] = np.real(np.fft.ifft(np.fft.fft(output_blocks[i]) * X))

            #normalize output
            output_blocks[i] = output_blocks[i] * 6000 / max(abs(output_blocks[i])) * w
    
    #summing output for each clip played
    final_output = BLOCKLEN * [0]
    for i in range(0,12):
        if (play_clips[i]):
            for k in range(0,BLOCKLEN):
                final_output[k] += output_blocks[i][k]
    
    #update plot - correlation
    g3.set_ydata(final_output)
    canvas.draw()
    
    #clipping output
    final_output = np.clip(final_output,-MAXVALUE,MAXVALUE)
    final_output = final_output.astype(int)
    output_bytes = struct.pack('h' * BLOCKLEN, *final_output)
    
    #to output device
    stream.write(output_bytes);
    
    #update audio block
    num_block -= 1
    

    if (num_block == 0):
        for i in range(0,12):
            play_clips[i] = False;
            KEYPRESS = False
            num_block = (int)(num_frames / BLOCKLEN)
            first_file.rewind()
#            for b in range(12):
#                files[b].rewind()
    else:
        first_block = first_file.readframes(BLOCKLEN)
        for m in range(0,12):
            input_blocks[m] = files[m].readframes(BLOCKLEN)

        #looping audio
        if len(first_block) != WIDTH * BLOCKLEN:
            first_file.rewind()
            first_block = first_file.readframes(BLOCKLEN)
        for b in range(12):
            if len(input_blocks[b]) != WIDTH * BLOCKLEN:
                files[b].rewind()
                input_blocks[b] = files[b].readframes(BLOCKLEN)

print('* Finished')

plt.close()
stream.stop_stream()
stream.close()
for i in range(12):
    files[i].close()
p.terminate()
