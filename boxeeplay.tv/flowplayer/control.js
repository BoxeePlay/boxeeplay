boxee.enableLog(true);
boxee.renderBrowser = false;
boxee.autoChoosePlayer = true;
boxee.setDefaultCrop(0,0,0,22);
boxee.notifyPlaybackResumed()

hasActive = false;

var duration = 0;
/*
duration = Math.round(Number(browser.execute('flowplayer().getClip().duration')));
boxee.setDuration(parseFloat(duration);
*/

/*
//player = 'document.ep_player[0]';
duration = 0;
 
function checkPlayerEnd() {
   if (duration > 0) {
       ctime = Math.round(Number(browser.execute(player+'.getCurrentTime()')));
       if (ctime >= duration) { boxee.notifyPlaybackEnded(); }
       progress = Math.round((ctime/duration)*100);
       boxee.notifyCurrentTime(ctime);
       boxee.notifyCurrentProgress(progress);
   }
   else {
       browser.execute(player+'.playVideo();');
       duration = Number(browser.execute(player+'.getVideoDuration()'));
       boxee.setDuration(duration);
   }
   setTimeout(checkPlayerEnd,500);
}
*/


function doUpdates() {
	//duration = Math.round(Number(browser.execute('flowplayer().getTime()')));
	
    ctime = Math.round(Number(browser.execute('flowplayer().getTime()')));
    //if (ctime >= duration) { boxee.notifyPlaybackEnded(); }
    progress = Math.round((ctime/duration)*100);
    boxee.notifyCurrentTime(ctime);
    boxee.notifyCurrentProgress(progress);
    setTimeout(doUpdates,500);
}

function sendProgress() {
    ctime = Math.round(Number(browser.execute('flowplayer().getTime()')));
    if (ctime >= duration) { boxee.notifyPlaybackEnded(); }
    progress = Math.round((ctime/duration)*100);
    boxee.notifyCurrentTime(ctime);
    boxee.notifyCurrentProgress(progress);
}

function checkForLoad() {
	var check = browser.execute("checkIfLoaded();");
	
	browser.execute('document.getElementById("debugWin").innerHTML = "'+check+'";');
	
	if (check == "yes") {
		duration = Number(browser.execute('flowplayer().getClip().duration'));
		if (duration>0) {
			boxee.setDuration(parseFloat(duration));
			doUpdates();
		} else {
			setTimeout(checkForLoad,1000);
		}
		
		browser.execute('document.getElementById("debugWin").innerHTML = "'+duration+'";');
		
	} else {
		setTimeout(checkForLoad,1000);
		
	}
	
}

setTimeout(function(){
	browser.execute('document.getElementById("debugWin").innerHTML = "Calling Load";');
	checkForLoad();
},1000);


//Init check for load
//setTimeout("checkForLoad();",2000);


if(boxee.getVersion() > 3.4)
{
   boxee.setCanPause(true);
   boxee.setCanSkip(true);
   boxee.setCanSetVolume(true);
}
 
boxee.onPause = function()
{
//OK
   browser.execute("flowplayer().pause()");
}
 
boxee.onPlay = function()
{
//OK
   browser.execute("flowplayer().play()");
}
 
boxee.onSkip = function() {
   //OK
   browser.execute('flowplayer().seek(flowplayer().getTime()+60)')
   sendProgress()
}
 
boxee.onBigSkip = function() {
   //OK
	browser.execute('flowplayer().seek(flowplayer().getTime()+60)')
	sendProgress()
}
 
boxee.onBack = function() {
	//OK
   browser.execute('flowplayer().seek(flowplayer().getTime()-60)')
   sendProgress()
}
 
boxee.onBigBack = function() {
   //OK
	browser.execute('flowplayer().seek(flowplayer().getTime()-60)')
	sendProgress()
   
}
 
boxee.onSetVolume = function(volume)
{
//Not OK TEST more
   var vol = volume/100;
   //browser.execute('flowplayer().setVolume('+vol+');');
   //browser.execute('flowplayer().setVolume(100);');
   
}