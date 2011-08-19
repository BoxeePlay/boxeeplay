var player = null;
var audioX;
var qualityX;
var globalBitrate = -1;
var setVolFn = "";
    setVolFn += "var setVolume = function() {";
    setVolFn += "var prnt = document.playerSwf;";
    setVolFn += "if (typeof(prnt) === 'undefined') {return 'FAILURE';};";
    setVolFn += "var outHTML = prnt.outerHTML;";
    setVolFn += "var flashvars = outHTML.match(/name=\\\"flashvars\\\".*value=\\\"(.+)\\\"/)[1];";
    setVolFn += "var flashvars_new = flashvars + '&amp;initVolume=1&amp;useCookie=false';";
    setVolFn += "outHTML = outHTML.replace(flashvars,flashvars_new);";
    setVolFn += "prnt.outerHTML = outHTML.replace(/name=\\\"flashvars\\\".*value=\\\".+\\\"/g,'name=\"flashvars\" value=\"'+flashvars_new+'\"');";
    setVolFn += "return 'SUCCESS';";
    setVolFn += "};";

function bplog(str)
{
    boxee.log(str);
    //boxee.showNotification(str, ".", 1);
}

boxee.enableLog(true);
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
    bplog(err);
    boxee.showNotification(err, ".", 5);
}

function boxeeSetupCommon()
{
    bplog("Loading common boxee configuration.");

    boxee.renderBrowser = true;
    
    boxee.onPlay = function() {
        runPlayerFunction('resume();');
    };
    boxee.onPause = function() {
        runPlayerFunction('pause();');
        //bplog(runPlayerFunction('getDebugText();'));
    };

    boxee.onSkip = function() {
        runPlayerFunction('seek(10,true,true);');
    };
    boxee.onBigSkip = function() {
        runPlayerFunction('seek(120,true,true);');
    };
    boxee.onBack = function() {
        runPlayerFunction('seek(-10,true,true);');
    };
    boxee.onBigBack = function() {
        runPlayerFunction('seek(-120,true,true);');
    };

//  ###### 7.0 Specifics ######
    boxee.onSeekTo = function(millis) {
        //bplog(millis);
        runPlayerFunction('seek('+ millis/1000 +');');
    };
    
    boxee.onUpdateState = function()
    {
        try {
            playerState.canSetFullScreen = true;
            playerState.canPause = true;

            var debug = runPlayerFunction('getDebugText();');
            if (!isLive(debug)) {
                playerState.canSeek = true;
                playerState.canSeekTo = true;
            }
            
            var duration = parseDuration(debug);
            var time = parseTime(debug);

            if (debug !== "") {
                bplog("Duration: " + duration);
                bplog("Time: " + time);

                playerState.duration = duration;
                playerState.time = time;
            } else {
                bplog("Could not get debug text.");
                playerState.duration = 100;
                playerState.time = 0;
            }
        } catch(err) {
            bplog(err);
        }
    };

    bplog("Finished loading common boxee configuration.");
}

function boxeeSetup40()
{
    bplog("Loading configuration for boxee 0.9.");

    boxee.setCanPause(true);
    boxee.setDefaultCrop(0,0,0,26);
    boxee.autoChoosePlayer = true;

    bplog("Finished loading configuration for boxee 0.9.");
}

function boxeeSetup70()
{
    bplog("Loading configuration for boxee 1.");

    boxee.apiMinVersion = 7.0;
    boxee.setMode(boxee.PLAYER_MODE);
//    boxee.showOSDOnStartup = false;

    playerState.canSetFullScreen = true;
    playerState.canPause = true;
 
    bplog("Finished loading configuration for boxee 1.");
};

// ############### SCRIPT FLOW AFTER SETUP #################

boxee.onDocumentLoading = function()
{
    browser.execute(setVolFn);

    setVolume();
}

function setVolume()
{
//    bplog("setting volume to 1.");
    if (browser.execute('typeof(setVolume)') == 'undefined') {
        browser.execute(setVolFn);
        bplog("reloaded setVolume function");
    }
    browser.execute(setVolFn);
    var result = browser.execute('setVolume()');
    bplog("result from setvolume: " + result);

    if (result !== 'SUCCESS') {
        setTimeout(setVolume, 200);
//        bplog("New setVolume in 0.2s");
    }
    else {
        bplog("Volume was set.");
        onVidLoaded();
    }
}

function onVidLoaded()
{
    try {
        for (var w1 in boxee.getWidgets())
        {
            var widg = boxee.getWidgets()[w1];
            /* dumper
            for (var w in widg)
            {
                bplog(w1 + " :: " + w + " = " + widg[w]);
            }
            */
            if (boxee.getVersion() < 7) {
                if (/initVolume=1/.test(widg.getAttribute('flashvars'))) {
                    player = widg;
                    break;
                }
            } else {
                if (typeof(widg) === 'object') {
                    var dbg = widg.executeJS('this.getDebugText();');
                    if (/SVTPlayer/.test(dbg)) {
                        player = widg;
                        break;
                    }
                }
            }
        }

        if (player !== null) {
            bplog("Player widget found. x=" + player.x + ", y=" + player.y + ", width=" + player.width + ", height="+player.height);
            boxeeLoadCommon();
        } else {
            bplog("Player widget not found, waiting...");
            setTimeout(onVidLoaded,500);
        }

    } catch(err) {
        bplog(err);
    }
};

function boxeeLoadCommon() {
    try{
        var debug = runPlayerFunction("getDebugText();");
        var state = getState(debug);
        if (state.indexOf("playing") === -1) {
            bplog("boxeeLoadCommon: player not loaded. state = " + state);
            setTimeout(boxeeLoadCommon,500);
        } else {
            bplog("boxeeLoadCommon: player was loaded. state = " + state);
            var hasSubs = hasSubtitles(debug);
            var volume = parseVolume(debug);
            var dynamic = isDynamic(debug);
            var hasdyn = hasDynamic(debug);
            var live = isLive(debug);
            audioX = player.width - 110 - ((hasSubs) ? 30 : 0) - ((hasDynamic) ? 30 : 0);
            bplog((hasSubs) ? "Subtitles available." : "No subtitles available.");
            qualityX = audioX + 30;
            bplog("Volume: " + volume);

            if (!live) {
                if (boxee.getVersion() < 7) {
                    boxee.setCanSkip(true);
                } else {
                    playerState.canSeek = true;
                    playerState.canSeekTo = true;
                }
            }
            else if (boxee.getVersion() < 7)
            {
                boxee.renderBrowser = false;
            }

            //TODO: volume 100      -0.9 CHECK  -1.0 CHECK
            //TODO: auto-quality    -0.9 CHECK  -1.0 CHECK
            //TODO: fullscreen      -0.9 CHECK  -1.0 CHECK
            //TODO: live            -0.9 CHECK  -1.0 CHECK

            if (hasdyn && !dynamic)
            {
                autoQualityClick();
            }

            setTimeout(function(){player.click(player.width-30,player.height-10);}, 300);
            
            var updateInterval = setInterval(doUpdates, 500);

            bplog("Finished loading functionality for boxee common.");
        }
    }
    catch (err) {
        bplog(err);
        bplog("Ungraceful exit from boxeeLoadCommon");
    }
}

function doUpdates() {
    //bplog("doUpdates start");

    var debug = runPlayerFunction("getDebugText();");

    if (debug != "") { //Or we will run soon again
        var duration = parseDuration(debug);
        var time = parseTime(debug);
        var state = getState(debug);
        var bitrate = (hasDynamic(debug)) ? parseBitrate(debug) : parseDatarate(debug);
        //bplog(state);

        if (state === 'complete' || state === 'stopped') {
            boxee.notifyPlaybackEnded();
        }

        if (bitrate !== globalBitrate) {
            globalBitrate = bitrate;
            // boxee.showNotification("Current stream: \"" + getCurrentStream(debug) + "\"",".",2);
            var dynLim = parseDynamicLimit(debug);
            var extra = "";
            if (dynLim >= 0) {
                extra = " (" + dynLim + ")";
            }
            var msg = "Spelar nu upp i " + bitrate + "kbps." + extra;
            bplog(msg);
            boxee.showNotification(msg,".",3);
        }

        if (boxee.getVersion() < 7) {
            boxee.setDuration(duration);
            boxee.notifyCurrentTime(time);
            if (duration > 0.0) {
                boxee.notifyCurrentProgress(100*time/duration);
            }
        }
    }
    else {
        bplog("doUpdates retreived empty debug text...");
    }
}


// ##################### UTILITIES #######################

function parseTime(debug) {
    var time=0.0;
    if (/position\:.*?(\d+.*?)$/im.test(debug)) {
        time = parseFloat(debug.match(/position\:.*?(\d+.*?)$/im)[1]);
    }
    return time;
}
function parseDuration(debug) {
    var duration = 0.0;
    if (/totalTime\:.*?(\d+.*?)$/im.test(debug)) {
        duration = parseFloat(debug.match(/totalTime\:.*?(\d+.*?)$/im)[1]);
    }
    return duration;
}
function isLive(debug) {
    var live = debug.match(/isLive\: (.*)$/m)[1];
    //bplog("isLive: " + live);
    return (live == "true");
}
function isDynamic(debug) {
    var dyn = debug.match(/isAutoBitrate\: (.*)$/m)[1];
    //bplog("isDynamic: " + dyn);
    return (dyn == "true");
}
function hasDynamic(debug) {
    var dyn = debug.match(/isDynamicStream \: (.*)$/m)[1];
    return (dyn == "true");
}
function isFullscreen(debug) {
    var dispstate = debug.match(/displayState\: (.*)$/m)[1];
    //bplog("displaystate: " + dispstate);
    return (dispstate == "fullScreen");
}

function hasSubtitles(debug) {
    return /subtitle \: (.+)$/m.test(debug);
}
function parseVolume(debug) {
    if (/^volume\:(.+)$/m.test(debug))
        return parseFloat(debug.match(/^volume\:(.+)$/m)[1]);
    else
        return 0.0;
}
function getState(debug) {
    var regex = /^state\: (.*)$/m
    if (regex.test(debug))
        return debug.match(regex)[1];
    else
        return "undefined";
}
function parseBitrate(debug) {
    try {
        var regex =/NetStream\.Play\.[Start|Transition].* (.+)\.$/mg;
        var stream = debug.match(regex);
        stream = regex.exec(stream[stream.length - 1])[1];
        var bitrate = debug.match(new RegExp(stream + " \\((.*)\\)$","m"))[1];
//        boxee.showNotification(bitrate + " (" + parseDynamicLimit(debug) + ")", ".", 1);
        return parseInt(bitrate);
    }
    catch(err) {
        bplog(err);
        return -1;
    }
}
function parseDynamicLimit(debug) {
    try {
        return debug.match(/maxBitrate\: (.*)$/m)[1]
    }
    catch(err) {
        bplog(err);
        return -1;
    }
}
function getCurrentStream(debug) {
    try {
        return debug.match(/currentStreamname\: (.*)$/m)[1];
    }
    catch(err) {
        bplog(err);
        return "Not found";
    }
}
function parseDatarate(debug) {
    try {
        var drate = debug.match(/videodatarate \: (.*)$/m)[1];
        return drate;
    }
    catch(err) {
        bplog(err);
        return -1;
    }
}

function runPlayerFunction(fn) {
    if (boxee.getVersion() <= 4.0) {
//        bplog(browser.execute('typeof(player)'));
        if (browser.execute('typeof(player)') == "undefined") {
            bplog("JS-player was undefined.");
            browser.execute('var player = document.getElementsByTagName("object")[1];');
        }
        return browser.execute('player.'+fn);
    } else {
        try {
            if (typeof(player) === 'undefined') {
                player = boxee.getActiveWidget();
//                player = boxee.getWidgets()[0];
            }
            return player.executeJS('this.'+fn);
        } catch(err) {
            bplog("Player widget does not yet exist. Cannot run " + fn);
            bplog(err);
        return "";
        }
    }
}
function autoQualityClick() {
    var x = qualityX; var y = player.height-10;
    player.click(x, y);
    setTimeout(function() {player.click(player.width/2+80,player.height/2-43);bplog("Automatisk bitrate vald.");},200);
//    boxee.showNotification("Clicked at " + x + ", " + y, ".", 2);
}

bplog("Finished loading Boxee control script.");
