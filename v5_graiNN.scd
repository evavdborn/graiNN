s.boot;

(
{
	//setup network adress (this changes in RPi)
	NetAddr.new("127.0.0.1", 57120);    // create the NetAddr

	//wait for code to initilize
	0.5.wait;

	// import path to sample according to OSC message
	// KRUDER AND DORFMEISTER
	b = Buffer.readChannel(s, "/home/pi/Documents/samples/KD22.wav", channels:[0]);
	// ADAM BEYER
	c = Buffer.readChannel(s, "/home/pi/Documents/samples/adam_beyer.wav", channels:[0]);
	//
	d = Buffer.readChannel(s, "/home/pi/Documents/samples/aphex.wav", channels:[0]);
	//
	e = Buffer.readChannel(s, "/home/pi/Documents/samples/steve_reich.wav", channels:[0]);

	// wait for initilize
	0.5.wait;

	// Create Synthdef for Granular Synthesizer
	SynthDef.new(\gs, {
		arg sync=1, denGr=20, durGr=0.1, durRand=1, buf=0,
		pos=0, posSpeed=1, posRand=0, rate=1, panHz=0.1, grainEnv=(-1), pan=0, panRand=0,
		atk=1, sus=2, rel=1, c0=1, c1=(-1), out=0, amp=1;

		var sig, env, denCtrl, durCtrl, panCtrl, posCtrl;

		//ENVELOPE OF GRAINS
		env = EnvGen.ar(Env.new([0,1,0], [atk, sus, rel], [c0, c1]), doneAction:2);

		//DENSITY OF GRAIN (how many grains per second. Choose Impulse or Dust
		denCtrl = Select.ar(sync, [Dust.ar(denGr), Impulse.ar(denGr)]);

		//DURATION OF GRAINS
		durCtrl = durGr * LFNoise1.kr(100).exprange(1/durRand,durRand);

		//START POSITION (where to start in the audio file)
		posCtrl = Phasor.ar(0, posSpeed * BufRateScale.ir(buf), 0, BufSamples.ir(buf)-1);
		posCtrl = posCtrl + LFNoise1.kr(100).bipolar(posRand*SampleRate.ir);
		posCtrl = posCtrl / BufSamples.ir(buf);
		posCtrl = posCtrl + pos;

		//DO PANNING
		panCtrl = pan + LFNoise1.kr(panHz).bipolar(panRand);

		sig = GrainBuf.ar(
			2,
			denCtrl,
			durCtrl,
			buf,
			rate,
			posCtrl,
			2,
			panCtrl,
			grainEnv
		);

		sig = sig * env* amp;

		Out.ar(out, sig);
	}).add;

	// wait for initilize
	0.5.wait;

	// CREATE SYNTH FOR SAMPLE 1 //////////////////////
	Synth.new(\gs, [
		\buf, b,
		\sync, 1,
		// DENSITY GRAINS
		\denGr, 20,
		// DURATION GRAINS
		\durGr, 0,01,
		// POSSPEED
		\posSpeed, 0.5,
		\pos, 3,
		//PITCH IN MIDINOTES
		\rate, -30.midicps,
		\amp, 0.3,
		\sus, 5

	]);

	//wait for initilize
	0.5.wait;

	// CREATE SYNTH FOR SAMPLE 2 //////////////////////
	Synth.new(\gs, [
		\buf, c,
		\sync, 1,
		// DENSITY GRAINS
		\denGr, 20,
		// DURATION GRAINS
		\durGr, 0,01,
		// POSSPEED
		\posSpeed, 0.5,
		\pos, 1,
		//PITCH IN MIDINOTES
		\rate, -1.midicps,
		\amp, 0.3,
		\sus, 5

	]);

		//wait for initilize
	0.5.wait;

	// CREATE SYNTH FOR SAMPLE 3 //////////////////////
	Synth.new(\gs, [
		\buf, d,
		\sync, 1,
		// DENSITY GRAINS
		\denGr, 20,
		// DURATION GRAINS
		\durGr, 0,01,
		// POSSPEED
		\posSpeed, 0.5,
		\pos, 1,
		//PITCH IN MIDINOTES
		\rate, 2.midicps,
		\amp, 0.3,
		\sus, 5

	]);

		// CREATE SYNTH FOR SAMPLE 4 //////////////////////
	Synth.new(\gs, [
		\buf, e,
		\sync, 1,
		// DENSITY GRAINS
		\denGr, 20,
		// DURATION GRAINS
		\durGr, 0,01,
		// POSSPEED
		\posSpeed, 0.5,
		\pos, 1,
		//PITCH IN MIDINOTES
		\rate, -2.midicps,
		\amp, 0.3,
		\sus, 5

	]);

	//wait for initilize
	0.5.wait;

	// CREATE A PATTERN FOR SAMPLE 1
	~p1 = Pbind(
	\instrument, \gs,
	\buf, b,
	\sync, 1,
	\denGr, Pdefn(\dengrEngine, 20),
	\durGr, Pdefn(\durGrEngine, 0.02),
	\posSpeed, Pdefn(\posSpeedEngine, 5),
	\pos, Pdefn(\posEngine, 1),
	\rate, Pdefn(\rateEngine, -30.midicps),
	\amp, 0.3,
	\sus, 5
	);

	//wait for initilize
	0.5.wait;

	// CREATE A PATTERN FOR SAMPLE 2
	~p2 = Pbind(
	\instrument, \gs,
	\buf, c,
	\sync, 1,
	\denGr, Pdefn(\dengrEngine, 20),
	\durGr, Pdefn(\durGrEngine, 0.02),
	\posSpeed, Pdefn(\posSpeedEngine, 5),
	\pos, Pdefn(\posEngine, 1),
	\rate, Pdefn(\rateEngine, -1.midicps),
	\amp, 0.3,
	\sus, 5
	);

	//wait for code to initilize
	0.5.wait;

	// CREATE A PATTERN FOR SAMPLE 3
	~p3 = Pbind(
	\instrument, \gs,
	\buf, d,
	\sync, 1,
	\denGr, Pdefn(\dengrEngine, 20),
	\durGr, Pdefn(\durGrEngine, 0.02),
	\posSpeed, Pdefn(\posSpeedEngine, 5),
	\pos, Pdefn(\posEngine, 1),
	\rate, Pdefn(\rateEngine, -1.midicps),
	\amp, 0.3,
	\sus, 5
	);

	//wait for code to initilize
	0.5.wait;

	// CREATE A PATTERN FOR SAMPLE 3
	~p4 = Pbind(
	\instrument, \gs,
	\buf, e,
	\sync, 1,
	\denGr, Pdefn(\dengrEngine, 20),
	\durGr, Pdefn(\durGrEngine, 0.02),
	\posSpeed, Pdefn(\posSpeedEngine, 5),
	\pos, Pdefn(\posEngine, 1),
	\rate, Pdefn(\rateEngine, -20.midicps),
	\amp, 0.3,
	\sus, 5
	);
	//wait for code to initilize
	0.5.wait;

	//setup OSC communication
	OSCdef.new(\play,
		{
			arg msg, time, addr, recvPort,
			def_val_Dens=20, def_val_Dur=1, def_val_PosSpeed=5, def_val_rate=(-40), def_val_pos = 10,
			//range is the half of the ...
			ran_den=20, ran_dur=14, ran_posSpeed=10, ran_rate=10, ran_pos=5;
			var msg_Dens, msg_Dur, msg_Pos, msg_PosSpeed, msg_Rate;

			postln("Incoming OSC message: ");
			msg.postln;

			// Recalcultate messages
			postln("Recalculate messages: ");

			msg_Dens = (msg[1] * (-1));
			msg_Dens = msg_Dens + msg[2];
			msg_Dens = msg_Dens * ran_den;
			msg_Dens = msg_Dens + def_val_Dens;
			msg_Dens = round(msg_Dens);

			msg_Dur = (msg[3] * (-1));
			msg_Dur = msg_Dur + msg[4];
			msg_Dur = msg_Dur + def_val_Dur;
			msg_Dur.postln;
			msg_Dur = msg_Dur.linexp(0, 1, 0.01, 1);
			msg_Dur.postln;

			msg_Rate = (msg[5] * (-1));
			msg_Rate = msg_Rate + msg[6];
			msg_Rate = msg_Rate * ran_rate;
			msg_Rate = msg_Rate + def_val_rate;
			msg_Rate = round(msg_Rate);

			msg_Pos = (msg[7] * (-1));
			msg_Pos = msg_Pos + msg[8];
			msg_Pos = msg_Pos * ran_pos;
			msg_Pos = msg_Pos + def_val_pos;
			msg_Pos = round(msg_Pos);

			msg_PosSpeed = (msg[9] * (-1));
			msg_PosSpeed = msg_PosSpeed + msg[10];
			msg_PosSpeed = msg_PosSpeed * ran_posSpeed;
			msg_PosSpeed = msg_PosSpeed + def_val_PosSpeed;
			msg_PosSpeed = round(msg_PosSpeed);

			Pdefn(\dengrEngine, msg_Dens);
			Pdefn(\durGrEngine, msg_Dur);
			Pdefn(\rateEngine, msg_Rate.midicps);
			Pdefn(\posEngine, msg_Pos);
			Pdefn(\posSpeedEngine, msg_PosSpeed);

			[msg_Dens, msg_Dur, msg_Rate, msg_Pos, msg_PosSpeed, msg_Rate].postln;

	}, '/granular');

	//wait to inilialize
	0.5.wait;

	//START/STOP ENGINE
	OSCdef.new(\on_off,
		{
			arg msg;
			// check message for sample 1
			if(msg[1] == 'start_sample_1', {
				msg.postln;
				// initialize clock
				t = TempoClock(20/60).permanent_(true);
				t.schedAbs(t.nextBar, {t.beats.postln;1});
				//start sample 1
				~sample1 = ~p1.play(t);
				0.1.wait;
			});

			if(msg[1] == 'stop_sample_1', {
				// stop sample 1
				t.stop;
			});

			// check message for sample 2
			if(msg[1] == 'start_sample_2', {
				msg.postln;
				u = TempoClock(20/60).permanent_(true);
				u.schedAbs(u.nextBar, {u.beats.postln;1});
				~sample2 = ~p2.play(u);
				0.1.wait;
			});

			if(msg[1] == 'stop_sample_2', {
				u.stop;
			});

			//check messages for sample 3
			if(msg[1] == 'start_sample_3', {
				msg.postln;
				v = TempoClock(20/60).permanent_(true);
				v.schedAbs(v.nextBar, {v.beats.postln;1});
				~sample3 = ~p3.play(v);
				0.1.wait
			});

			if(msg[1] == 'stop_sample_3', {
				v.stop;
			});

			// check messages for sample 4
			if(msg[1] == 'start_sample_4', {
				msg.postln;
				w = TempoClock(20/60).permanent_(true);
				w.schedAbs(w.nextBar, {w.beats.postln;1});
				~sample4 = ~p4.play(w);
				0.1.wait;
			});

			if(msg[1] == 'stop_sample_4', {
				w.stop;
			});
	}, '/on_off');

	/// here comes an if statement when to stop playing.

}.fork;
)