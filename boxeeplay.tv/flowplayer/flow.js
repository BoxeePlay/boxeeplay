boxee.enableLog(true);
boxee.renderBrowser = true;
boxee.autoChoosePlayer = false;
boxee.notifyPlaybackResumed()

hasActive = false;
hasSet = false;

var duration = 0;
/*
duration = Math.round(Number(browser.execute('$f().getClip().duration')));
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
	//duration = Math.round(Number(browser.execute('$f().getTime()')));
	
    ctime = Math.round(Number(browser.execute('$f().getTime()')));
    //if (ctime >= duration) { boxee.notifyPlaybackEnded(); }
    progress = Math.round((ctime/duration)*100);
    boxee.notifyCurrentTime(ctime);
    boxee.notifyCurrentProgress(progress);
    setTimeout(doUpdates,500);
}

function sendProgress() {
    ctime = Math.round(Number(browser.execute('$f().getTime()')));
    if (ctime >= duration) { boxee.notifyPlaybackEnded(); }
    progress = Math.round((ctime/duration)*100);
    boxee.notifyCurrentTime(ctime);
    boxee.notifyCurrentProgress(progress);
}

function checkForLoad() {
	var check = browser.execute("checkIfLoaded();");
	
	browser.execute('document.getElementById("debugWin").innerHTML = "'+check+'";');
	
	if (check == "yes") {

		duration = Number(browser.execute('$f().getClip().duration'));
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

_findPlayer = setInterval(function()
{
   if (!hasSet)
   {
      boxee.getWidgets().forEach(function(widget)
      {
         if (widget.getAttribute("id") == 'fms_api')
         {
            boxee.renderBrowser=false;
            widget.setCrop(0, 0, 0, 31);
            boxee.notifyConfigChange(widget.width, widget.height-31);
            widget.setActive(true);
            boxee.setCanPause(true);
            boxee.setCanSkip(true);
            boxee.setCanSetVolume(true);
			hasSet = true;
            clearInterval(_findPlayer);
         }
      });
   }
}, 1000);



setTimeout(function(){
	browser.execute('document.getElementById("debugWin").innerHTML = "Calling Load";');
	checkForLoad();
},1000);



//Init check for load
//setTimeout("checkForLoad();",2000);

boxee.onPause = function()
{
//OK
   browser.execute("$f().pause()");
}
 
boxee.onPlay = function()
{
//OK
   browser.execute("$f().play()");
}
 
boxee.onSkip = function() {
   //OK
   browser.execute('$f().seek($f().getTime()+60)')
   sendProgress()
}
 
boxee.onBigSkip = function() {
   //OK
	browser.execute('$f().seek($f().getTime()+60)')
	sendProgress()
}
 
boxee.onBack = function() {
	//OK
   browser.execute('$f().seek($f().getTime()-60)')
   sendProgress()
}
 
boxee.onBigBack = function() {
   //OK
	browser.execute('$f().seek($f().getTime()-60)')
	sendProgress()
   
}
 
boxee.onSetVolume = function(vol)
{
//Not OK TEST more
   //var vol = volume/100;
   browser.execute('$f().setVolume('+vol+');');
   //browser.execute('$f().setVolume(100);');
   
}