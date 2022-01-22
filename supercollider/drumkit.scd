//Boot the server
s.boot;

//Set up the meter
s.meter;

//Create a plottree
s.plotTree;

// If necessary, reboot o quit
s.reboot;
s.quit


/////// KICKDRUM ///////
////////////////////////
////////////////////////

(
SynthDef.new(\kick, {
	arg freqA=500, freqB=50, freqC=10, freqDur1=0.01, freqDur2=0.2, freqC1=1, freqC2=(-1),
	atk=0.01, rel=1, c1=1, c2=(-12), amp=1, pan=0, out=0;
	var sig, env, freqSweep;
	freqSweep = Env([freqA, freqB, freqC], [freqDur1, freqDur2], [freqC1, freqC2]).ar;
	//the kr(2) will fre the synth when the envelope is completed
	env = EnvGen.kr(
		Env.new(
			[0,1,0],
			[atk, rel],
			[c1, c2]
		),
		doneAction:2
	);
	sig = SinOsc.ar(freqSweep, pi/2);
	//scale it with our envelope
	sig = sig * env;
	sig = Pan2.ar(sig, pan, amp);
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\kick);
x = Synth.new(\kick, [\rel, 1]);


/////// SNARE ///////
/////////////////////
/////////////////////


(
SynthDef.new(\snare, {
	arg freqA = 500, freqB = 30, freqC = 10,
	freqDur1=0.01, freqDur2=2, freqC1=1, freqC2=(-1),
	atk=0.01, rel=0.6, c1=1, c2=(-50),
	amp = 1, pan=0, out=0, gate=10;
	var ini_sig, sig, env, freqSweep, snapOsc, snapEnv, snapNoise;
	freqSweep = EnvGen.kr(
		Env.new(
			[freqA, freqB, freqC],
			[freqDur1, freqDur2],
			[freqC1, freqC2]
		),
		doneAction:0
	);
	env = EnvGen.kr(
		Env.new(
			[0,1,0],
			[atk, rel],
			[c1, c2],
		),
		//gate,
		doneAction:2
	);
	ini_sig = Pulse.ar(300);
	sig = {LPF.ar(ini_sig,(freqSweep) + 10)};
	sig = sig * env;
	//define the "snapping sound
	snapOsc = {
		BPF.ar(HPF.ar(PinkNoise.ar(1), 500), 5000)};
	snapEnv = {
		Line.ar(1, 0, 0.25, doneAction:0)};
	snapNoise = (snapOsc * snapEnv);
	sig = sig + snapNoise;
	Out.ar(out, Pan2.ar(sig, 0));
}).add;
)
x = Synth.new(\snare);


/////// CLAP ///////
////////////////////
////////////////////

//freqenv:
Env( [0, 0, 1, 0], [0.01, 0, 0.04], [1, -1]).plot;


(
SynthDef.new(\clap, {
	arg freqDur1=0.01, freqDur2=0, freqDur3=0.1, freqC1=1, freqC2=(-1),
	atk=0.01, rel=0.7, c1=1, c2=(-15), pan=0, amp=1, gate=1, clap_freq, out=0;
	var sig, env, clapNoise;

	// define the clapNoise
	clapNoise = {BPF.ar(LPF.ar(WhiteNoise.ar(1),7000), clap_freq)};

	//layers 7 different "clap sounds" to get a more "fatter" sound
	sig = {Mix.arFill(7,
				{arg i; EnvGen.ar(
					Env.new(
						[0, 0, 1, 0],
				        [freqDur1 * i, freqDur2, freqDur3],
				        [freqC1, freqC2]),
			) * clapNoise * 0.5
	})};
	env = EnvGen.kr(
				Env.new(
					[0, 1, 0],
					[atk, rel],
			        [c1, c2],
				),
				doneAction:2;
			);

	sig  = sig * env;
	sig = Pan2.ar(sig, pan, amp);
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\clap, [\clap_freq, 4000]);


// LOADING IN OTHER SAMPLES USER PLAYBUF
////////////////////////////////////////

///// RIM TR808 ////
////////////////////
////////////////////

~rimshot = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Rim Shot.wav");
~rimshot.play;

(
SynthDef.new(\rimshot, {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, rate, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf)*rate);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\rimshot, [\buf, ~rimshot.bufnum, \rate, 10.midiratio]);


//// CRASH TR808 ////
////////////////////
////////////////////

~crash = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Crash.wav");
~crash.play;

(
SynthDef.new(\crash, {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, rate, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf)*rate);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\crash, [\buf, ~crash.bufnum, \rate, 2.midiratio]);


// HAT OPEN TR808 //
////////////////////
////////////////////

~hat_open = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Hat Open.wav");
~hat_open.play;

(
SynthDef.new(\hat_open, {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, rate, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf)*rate);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\hat_open, [\buf, ~hat_open.bufnum, \rate, 1.midiratio]);

/// HAT CLOSED TR808
////////////////////
////////////////////

~hat_closed = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Hat Closed.wav");
~hat_closed.play;

(
SynthDef.new(\hat_closed, {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, rate, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf)*rate);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\hat_closed, [\buf, ~hat_closed.bufnum, \rate, 2.midiratio]);

//// TOM TR808 /////
////////////////////
////////////////////

~tom = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Tom M.wav");
~tom.play;

(
SynthDef.new(\tom, {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, rate, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf)*rate);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\tom, [\buf, ~tom.bufnum, \rate, 2.midiratio]);


// COWBELL TR808 ///
////////////////////
////////////////////

~cowbell = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Cowbell.wav");
~cowbell.play;

(
SynthDef.new(\cowbell, {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, rate, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf)*rate);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\cowbell, [\buf, ~cowbell.bufnum, \rate, -6.midiratio]);



//// CONGA TR808 ///
////////////////////
////////////////////

~conga = Buffer.read(s, "C:\\Users\\s157874\\Documents\\FMP\\Samples Supercollider\\Conga.wav");
~conga.play;

(
SynthDef.new(\conga, {
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, rate, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	sig = PlayBuf.ar(2, buf, BufRateScale.kr(buf)*rate);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

x = Synth.new(\conga, [\buf, ~conga.bufnum, \rate, 2.midiratio]);


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

/*
s.boot;

(
SystemClock.sched(
	0.5,
	o = OSCdef.new(\playSound, {
		arg msg;
		if( msg[1] == 1, {msg.postln;});
		msg.postln;
	}, '/wek/outputs');
);
)


(
SystemClock.sched(
	o = OSCdef.new(\playSound, {
	arg msg, time;
	time.postln;
	Synth.new(\hat_open, [\buf, ~hat_open.bufnum, \rate, msg[1].midiratio]);
	}, '/wek/outputs');
	0.75);
)






















