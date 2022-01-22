//Boot the server
s.boot;

//Set up the meter
s.meter;

//Create a plottree
s.plotTree;

// If necessary, reboot o quit
s.reboot;
s.quit

////////////////////////
// SETUP OSC --> LISTENS TO WEKINATOR OSC PORT. SENDS EITHER 1,2,3 VALUES

// NetAddr.localAddr    // retrieve the current IP and port
// n = NetAddr.new("127.0.0.1", 57120);    // create the NetAddr
// // create the OSCFunc
// o = OSCFunc({ arg msg, time, addr, recvPort; [msg, time, addr, recvPort].postln; }, '/wek/outputs');
//
// );
// o.play;
// o.free;    // remove the OSCFunc when you are done.
//
// OSCFunc.trace(true); // Turn posting on
// OSCFunc.trace(false); // Turn posting off

// EXTRACTING AUDIO FILES AND USING THEM FOR THE DRUMKIT
////////////////////////////////////////////////////////


// SNARE

~audio_snare = Buffer.read(s, "insert path here");
~audio_snare.play;

(
SynthDef.new(\audio_snare,{
	arg atk=0.01, rel=1, c1=1, c2=(-1), amp=1, buf, out=0;
	var sig, env;
	env = Env([0, 1, 0], [atk, rel], [c1, c2]).kr(2);
	// Playbuf is a sample playback oscillator
	// numChannels refers to whether the playback file is mono or stero
	// bufnum
	sig = PlayBuf.ar(2, buf);
	sig = sig * env;
	Out.ar(out, sig);
}).add;
)

y = Synth.new(\audio_snare);



