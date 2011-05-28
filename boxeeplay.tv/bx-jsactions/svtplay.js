function bplog(str)
{
    if (true) {
        boxee.log(str);
        boxee.showNotification(str, ".", 2);
    }
}

bplog("Loading Boxee control script.");

try {
    boxeeSetupCommon();
    if (boxee.getVersion() < 7.0) {
        boxeeSetup40();
    } else if (boxee.getVersion() < 7.1) {
        boxeeSetup70();
    } else {
        boxeeSetup70();
    }
} catch(err) {
    boxee.showNotification(err+"", ".", 5);
}

function boxeeSetupCommon()
{
    bplog("Loading common boxee configuration.");

    boxee.enableLog(true);
    boxee.renderBrowser = false;
    boxee.autoChoosePlayer = true;
    
    bplog("Finished loading common boxee configuration.");
}

function boxeeSetup40()
{
    bplog("Loading configuration for boxee 0.9.");

    boxee.setCanSkip(true);
    boxee.setCanPause(true);
    boxee.notifyPlaybackResumed();
    boxee.setDefaultCrop(0,0,0,25);

    bplog("Finished loading configuration for boxee 0.9.");
}

function boxeeSetup70()
{
    bplog("Loading configuration for boxee 1.");

    boxee.apiMinVersion = 7.0;
    boxee.setMode(boxee.LOCKED_PLAYER_MODE);
    boxee.realFullScreen = true;
    boxee.showOSDOnStartup = false;

    playerState.canSetFullScreen = true;
    playerState.canPause = true;
    playerState.canSeek = false;
    playerState.canSeekTo = true;
 
//    playerState.isPaused = false;

    bplog("Finished loading configuration for boxee 1.");
}

// ############### SETUP -> LOAD #################

boxee.onDocumentLoaded = function()
{
    try {
        boxeeLoadCommon();
        if (boxee.getVersion() <= 4.0) {
            boxeeLoad40();
        } else if (boxee.getVersion() <= 7.0) {
            boxeeLoad70();
        } else {
            boxeeLoad70();
        }
    } catch(err) {
        boxee.showNotification(err+"", ".", 5);
    }
};

function boxeeLoadCommon() {
    bplog("Loading functionality for boxee common.");

    //TODO: volume 100
    //TODO: auto-quality
    //TODO: extensions
    var updateInterval = setInterval(doUpdates, 500);

    bplog("Finished loading functionality for boxee common.");
}
function boxeeLoad40() {
    bplog("Loading functionality for boxee 0.9.");

    browser.execute('var player=document.getElementsByTagName("object")[1];');
    
    boxee.onPlay = function() {
        browser.execute('player.resume();');
    };
    boxee.onPause = function() {
        browser.execute('player.pause();');
        //bplog(browser.execute('player.getDebugText();'));
    };

    boxee.onSkip = function() {
        bplog("onSkip");
        try {
            browser.execute('player.seek(10,true,true);');
        } catch(err) {
            bplog(err);
        }
        bplog("onSkip klar");
    };
    boxee.onBigSkip = function() {
        browser.execute('player.seek(120,true,true);');
    };
    boxee.onBack = function() {
        browser.execute('player.seek(-10,true,true);');
    };
    boxee.onBigBack = function() {
        browser.execute('player.seek(-120,true,true);');
    };

    bplog("Finished loading functionality for boxee 0.9.");
}
function boxeeLoad70() {
    bplog("Loading functionality for boxee 1.");

    boxee.getWidgets()[1].setActive();

    boxee.onPlay = function() {
        boxee.getWidgets()[1].executeJS('this.resume()');
    };
    boxee.onPause = function() {
        boxee.getWidgets()[1].executeJS('this.pause()');
        //bplog(browser.execute('player.getDebugText()'));
    };

    boxee.onSeekTo = function(millis) {
        bplog(millis);
        boxee.getWidgets()[1].executeJS('this.seek('+ millis/1000 +')');
    };
    
    boxee.onUpdateState = function()
    {
        try {
            playerState.canSetFullScreen = true;
            playerState.canPause = true;
            playerState.canSeek = true;
            playerState.canSeekTo = true;

            var debug = boxee.getWidgets()[1].executeJS('this.getDebugText()');
            
            var duration = parseDuration(debug);
            var time = parseTime(debug);

            bplog("Duration: " + duration);
            bplog("Time: " + time);

            playerState.duration = duration;
            playerState.time = time;
        } catch(err) {
            bplog(err+"");
        }
    };

    bplog("Finished loading functionality for boxee 1.");
}

var doUpdates=function() {
    //bplog("doUpdates start");

    if (boxee.getVersion() < 7) {
        var debug = browser.execute('player.getDebugText();');
    } else {
        var debug = boxee.getWidgets()[1].executeJS('this.getDebugText();');
    }
    var duration = parseDuration(debug);
    var time = parseTime(debug);

    if (duration > 0.0) {
        if ((duration - time) <= 1) {
            boxee.notifyPlaybackEnded();
        }
    }

    if (boxee.getVersion() < 7) {
        boxee.setDuration(duration);
        boxee.notifyCurrentTime(time);
        if (duration > 0.0) {
            boxee.notifyCurrentProgress(100*time/duration);
        }
    }

    //bplog("Current time: " + time);
    //bplog("Duration: " + duration);
    //bplog("Progress: " + progress + "%");

    //bplog("doUpdates end");
}

function parseTime(debug)
{
    var time=0.0;
    if (/position\:.*?(\d+.*?)$/im.test(debug)) {
        time = parseFloat(debug.match(/position\:.*?(\d+.*?)$/im)[1]);
    }
    return time;
}
function parseDuration(debug)
{
    var duration = 0.0;
    if (/totalTime\:.*?(\d+.*?)$/im.test(debug)) {
        duration = parseFloat(debug.match(/totalTime\:.*?(\d+.*?)$/im)[1]);
    }
    return duration;
}

bplog("Finished loading Boxee control script.");
