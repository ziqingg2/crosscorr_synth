clc; clear; close all;

% recording the files
Fs        = 48000; 
nBits     = 16; 
nChannels = 1; 
ID        = -1; % default audio input device 
recObj = audiorecorder(Fs, nBits, nChannels, ID);
disp('Start speaking.')
recordblocking(recObj, 10);
disp('End of Recording.');
% play(recObj);
audio_output = getaudiodata(recObj);
audiowrite("audio_test1.wav", audio_output, Fs)
