s.boot;
(
b = Buffer.alloc(s,2048,1);
c = Buffer.alloc(s,2048,1);
d = Buffer.read(s,"C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Clap.wav");
)

//Set up the meter
s.meter;

//Create a plottree
s.plotTree;

(
SynthDef("help-morph", { arg out=0, bufnumA=0, bufnumB=1;
    var inA, chainA, inB, chainB, chain;
    inA = Pulse.ar(180, LFCub.kr(1, 0, 0.1, 0.3), 0.5);
    inB = VarSaw.ar(190, 0, LFCub.kr(0.8, 0, 0.4, 0.5), 0.5);
    chainA = FFT(bufnumA, inA);
    chainB = FFT(bufnumB, inB);
    chain = PV_Morph(chainA, chainB, MouseX.kr);
    Out.ar(out, IFFT(chain).dup);
}).play(s,[\out, 0, \bufnumA, b.bufnum, \bufnumB, c.bufnum ]);
)

(
SynthDef("help-morph2", { arg out=0, bufnumA=0, bufnumB=1, soundBufnum=2;
    var inA, chainA, inB, chainB, chain;
    inA = Mix(Formant.ar([120, 180], [1200, 2000], [240, 360], 0.2));
    inB = PlayBuf.ar(1, soundBufnum, BufRateScale.kr(soundBufnum), loop: 1);
    chainA = FFT(bufnumA, inA);
    chainB = FFT(bufnumB, inB);
    chain = PV_Morph(chainA, chainB, MouseX.kr);
    Out.ar(out,  IFFT(chain).dup);
}).play(s,[\out, 0, \bufnumA, b.bufnum, \bufnumB, c.bufnum, \soundBufnum, d.bufnum]);
)

Platform.userExtensionDir;
Platform.systemExtensionDir;


//////////////////////////////////////
/////////////////////////////////////

// MORPH TWO SOUNDS

s.boot;
s.reboot;

(
b = Buffer.alloc(s,2048,2);
c = Buffer.alloc(s,2048,2);
d = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Cowbell.wav");
e = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Hat Open.wav");
)

(
SynthDef("morph", {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, bufnumA=0, bufnumB=1, soundBufnumA=2, soundBufnumB=3, rate, out=0;
	var sig_crash, sig_hihat, env, inA, chainA, inB, chainB, chain;
	env = Env([0, 1, 0], [atk, rel], [c, c2]).kr(2);
	sig_crash = PlayBuf.ar(2, soundBufnumA, BufRateScale.kr(soundBufnumA));
	sig_hihat = PlayBuf.ar(2, soundBufnumB, BufRateScale.kr(soundBufnumB));
	inA = sig_crash * env;
    inB = sig_hihat * env;
    chainA = FFT(bufnumA, inA);
    chainB = FFT(bufnumB, inB);
    chain = PV_Morph.new(chainA, chainB, 0.2);
	Out.ar(out, IFFT(chain).dup);
}).play(s, [\out, 0, \bufnumA, b.bufnum, \bufnumB, c.bufnum, \soundBufnumA, d.bufnum, \soundBufnumB, e.bufnum ]);
)

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// SETUP OSC --> LISTENS TO WEKINATOR OSC PORT. SENDS EITHER 1,2,3 VALUES

NetAddr.localAddr    // retrieve the current IP and port
n = NetAddr.new("127.0.0.1", 57120);    // create the NetAddr

o = OSCFunc({ arg msg, time, addr, recvPort; msg.postln; }, '/wek/outputs');

);
o.play;
o.free;    // remove the OSCFunc when you are done.

OSCFunc.trace(true); // Turn posting on
OSCFunc.trace(false); // Turn posting off


o = OSCdef.new(\playSound, {
	arg msg;
	if( msg[1] == 1, {
		Synth.new(\kick);
	});
	if( msg[1] == 2, {
		Synth.new(\snare);
	});
	if( msg[1] == 2, {
		Synth.new(\clap);
	});
}, '/wek/outputs');

o.freeAll;
o.play;
o.free;


