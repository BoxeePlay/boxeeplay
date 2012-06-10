boxee.onDocumentLoaded = function()
{
	boxeeLoadCommon();
	if (boxee.getVersion() >= 7)
		boxeeLoadNew();
	else
		boxeeLoadOld();
}

function boxeeLoadCommon()
{
	boxee.log("Loading common boxee configuration.");
	//boxee.showNotification("Loading common boxee configuration.", ".", 2);
	boxee.enableLog(true);
	boxee.renderBrowser = true;
	boxee.autoChoosePlayer = false;
	browser.execute('$f().setVolume(100);');

	boxee.onPause = function()
	{
		browser.execute("$f().pause()");
	}
	 
	boxee.onPlay = function()
	{
		browser.execute("$f().play()");
	}
	 
	//Standard short Boxee MOVIE seek time is 30 seconds
        //Short SHOW seek time seems to be 10 seconds, let's use that
	boxee.onSkip = function() {
		browser.execute('$f().seek($f().getTime()+10)')
		sendProgress()
	}
	
	//Standard long Boxee MOVIE seek time is 10 minutes
        //Long SHOW seek time seems to be 3 minutes, let's use that
	boxee.onBigSkip = function() {
		browser.execute('$f().seek($f().getTime()+180)')
		sendProgress()
	}
	 
	boxee.onBack = function() {
		browser.execute('$f().seek($f().getTime()-10)')
		sendProgress()
	}
	 
	boxee.onBigBack = function() {
		browser.execute('$f().seek($f().getTime()-180)')
		sendProgress()
	   
	}
    
    boxee.onSeekTo = function(millis) {
		browser.execute('$f().seek(' + millis/1000 + ')')
    }
	boxee.log("Finished loading common boxee configuration.");
	//boxee.showNotification("Finished loading common boxee configuration.", ".", 2);
}

function boxeeLoadNew()
{
	boxee.log("Loading configuration for boxee >= 1.0.");
	//boxee.showNotification("Loading configuration for boxee >= 1.0.", ".", 2);
	boxee.apiMinVersion = 7.0;
	boxee.showOSDOnStartup = false;
	boxee.setMode(boxee.LOCKED_PLAYER_MODE);
	boxee.realFullScreen = true;
	playerState.canPause = true;
	playerState.canSeek = true;
    playerState.canSeekTo = true;
	boxee.onUpdateState = function()
	{
		playerState.isPaused = browser.execute('$f().isPaused()') == 'true';
		playerState.time     = parseFloat(Number(browser.execute('$f().getTime();')));
		playerState.duration = parseFloat(Number(browser.execute('$f().getClip().fullDuration;')));
        playerState.canPause = true;
        playerState.canSeek = true;
        playerState.canSeekTo = true;
	}
	boxee.isPaused = false;
	boxee.log("Finished loading configuration for boxee >= 1.0.");
	//boxee.showNotification("Finished loading configuration for boxee >= 1.0.", ".", 2);
}

function boxeeLoadOld()
{
	boxee.log("Loading configuration for boxee < 1.0.");
	//boxee.showNotification("Loading configuration for boxee < 1.0.", ".", 2);
	boxee.setCanSetVolume(true);
	boxee.setCanSkip(true);
	boxee.setCanPause(true);
	boxee.notifyPlaybackResumed();
	 
	boxee.onSetVolume = function(vol)
	{
	//Not OK TEST more
	   //var vol = volume/100;
	   browser.execute('$f().setVolume('+vol+');');
	   //browser.execute('$f().setVolume(100);');
	   
	}
	doUpdates();
	boxee.log("Finished loading configuration for boxee < 1.0.");
	//boxee.showNotification("Finished loading configuration for boxee < 1.0.", ".", 2);
}

function doUpdates() {
	duration = parseFloat(Number(browser.execute('$f().getClip().fullDuration')));
    ctime = parseFloat(Number(browser.execute('$f().getTime()')));
    if (parseInt(ctime) >= parseInt(duration)-1) //-1 because of the polling delay
		boxee.notifyPlaybackEnded();
	boxee.setDuration(duration);
    boxee.notifyCurrentTime(ctime);
	boxee.notifyCurrentProgress(Math.round(ctime/duration*100));
    setTimeout(doUpdates,500);
}

