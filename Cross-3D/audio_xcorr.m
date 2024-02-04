% Kenny Huang & Gary Gong
% xcorr

clc; clear; close all;

load 'ReferenceHRTF.mat' hrtfData sourcePosition

hrtfData = permute(double(hrtfData),[2,3,1]);

sourcePosition = sourcePosition(:,[1,2]);

desiredAz  = [60; 300; 135;   0; 225;  60; 300; 135;   0; 225];
desiredAz1 = [30;  60;  90; 120; 150; 180; 210; 240; 270; 300];
desiredEl  = [0;    0;   0;   0;   0;   0;   0;   0;   0;   0];
desiredPosition  = [desiredAz  desiredEl];
desiredPosition1 = [desiredAz1 desiredEl];
interpolatedIR   = interpolateHRTF(hrtfData,sourcePosition,desiredPosition);
interpolatedIR1  = interpolateHRTF(hrtfData,sourcePosition,desiredPosition1);

leftIR   = squeeze(interpolatedIR(:,1,:));
leftIR1  = squeeze(interpolatedIR1(:,1,:));
rightIR  = squeeze(interpolatedIR(:,2,:));
rightIR1 = squeeze(interpolatedIR1(:,2,:));

% file reading for two sources
fileReader   = dsp.AudioFileReader('convolved.wav');
fileReader1  = dsp.AudioFileReader('convolved1.wav');
deviceWriter = audioDeviceWriter('SampleRate',fileReader.SampleRate);
leftFilter   = dsp.FIRFilter('NumeratorSource','Input port');
leftFilter1  = dsp.FIRFilter('NumeratorSource','Input port');
rightFilter  = dsp.FIRFilter('NumeratorSource','Input port');
rightFilter1 = dsp.FIRFilter('NumeratorSource','Input port');

durationPerPosition = 3;
durationPerPosition1 = 2;
samplesPerPosition  = durationPerPosition * fileReader.SampleRate;
samplesPerPosition  = samplesPerPosition  - rem(samplesPerPosition,fileReader.SamplesPerFrame);
samplesPerPosition1 = durationPerPosition1 * fileReader1.SampleRate;
samplesPerPosition1 = samplesPerPosition1 - rem(samplesPerPosition1,fileReader1.SamplesPerFrame);

sourcePositionIndex = 1;
samplesRead  = 0;
samplesRead1 = 0;
while ~isDone(fileReader)
    audioIn      = fileReader();
    audioIn1     = fileReader1();
    samplesRead  = samplesRead  + fileReader.SamplesPerFrame; % index tracker
    samplesRead1 = samplesRead1 + fileReader1.SamplesPerFrame; % index tracker
    
    % performing convolution
    leftChannel  = leftFilter(audioIn,leftIR1(sourcePositionIndex,:))   + 0.5 * leftFilter1(audioIn1,leftIR(sourcePositionIndex,:));
    rightChannel = rightFilter(audioIn,rightIR1(sourcePositionIndex,:)) + 0.5 * rightFilter1(audioIn1,rightIR(sourcePositionIndex,:));
    leftChannel  = leftChannel  * 20;
    rightChannel = rightChannel * 20;
    deviceWriter([leftChannel, rightChannel]);   % for playback
    
    if mod(samplesRead,samplesPerPosition) == 0
        sourcePositionIndex = randi(8);
    end
end

release(deviceWriter)
release(fileReader)
release(fileReader1)