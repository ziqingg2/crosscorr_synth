% Kenny Huang & Gary Gong
% xcorr
clc; clear; close all;

% reading the files
[signal, fs_signal] = audioread("vega_mono.wav");
[signal1,    ~    ] = audioread("audio_test1.wav");
[synth,  ~] = audioread("invention_g.wav");
[synth1, ~] = audioread("star.wav");
signal  = signal(:,1);
signal1 = signal1(:,1);
synth   = synth(:,1);
synth1  = synth1(:,1);

% % checking for same sample rates b/w hrirs and signal
% % if sample rates don't match, converts signal to corresponding fs of hrir
% if fs_signal ~= fs_signal1
%     fprintf("sample rates of hrirs and binaural signal don't match\n");
%     fprintf("converting signal to same sample rate as hrir...\n");
%     % determine a rational number P/Q, s.t. P/Q times original fs
%     % equals fs of hrir within some specified tolerance
%     [P, Q] = rat(44100/fs_signal);
%     abs(P/Q*fs_signal - 44100);
%     signal = resample(signal, P, Q);
%     signal1 = resample(signal, P, Q);
%     fs = fs_signal;
%     fprintf("done!\n\n");
% else % if fs == fs_HRIR then pass
%     fs = fs_signal;
% end

[cc, lags] = xcorr(signal, synth);
conv_cc = real(ifft(fft(cc) .* fft([signal; zeros(length(cc)-length(signal),1)])));
conv_cc = conv_cc ./ max(abs(conv_cc));
audiowrite("convolved.wav", conv_cc, fs_signal)

[cc1, lags1] = xcorr(signal1, synth1);
conv_cc1 = real(ifft(fft(cc1) .* fft([signal1; zeros(length(cc1)-length(signal1),1)])));
conv_cc1 = conv_cc1 ./ max(abs(conv_cc1));
audiowrite("convolved1.wav", conv_cc1, fs_signal)

figure()
plot(lags, cc)
