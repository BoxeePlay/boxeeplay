import mc, inspect

''' --------------------------------------------------------------
Andreas Pehrson, 20110422

-- A simple logger facility for Boxee.

Handles file logging and notification passing to Boxee.

Level description:
    TRACEIN | Only BoxeeLog:Debug, prepended with "TRACEIN". Not intended to be used directly. Use BPTraceEnter instead.
    TRACEOUT| Only BoxeeLog:Debug, prepended with "TRACEOUT". Not intended to be used directly. Use BPTraceExit instead.
    NOTICE  | Only user notification.
    DEBUG   | Only BoxeeLog:Debug, prepended with "DEBUG".
    INFO    | UserNotification and BoxeeLog:Info, prepended with "INFO".
    WARNING | UserNotification and BoxeeLog:Info, prepended with "WARNING".
    ERROR   | UserNotification and BoxeeLog:Error, prepended with "ERROR".
    FATAL   | Immediate app termination and BoxeeLog:Error, prepended with "FATAL".


NB: It seems that Boxee always log messages as DEBUG?
    Setting prepend on all log levels for now.
    -------------------------------------------------------------- '''

# What to export, (what is imported when 'from logger import *')
__all__ = [ "Level", "Enable", "Disable", "EnablePlus", "DisableMinus", "IsEnabled", "BPLog", "BPTraceEnter", "BPTraceExit" ]

class Level:
    '''A basic enum class of available log levels.'''
    TRACEIN,TRACEOUT,NOTICE,DEBUG,INFO,WARNING,ERROR,FATAL=range(1,9)

# Storing of enabled log levels
Enabled = { }
# Initiate list
for i in range(1,9):
    Enabled[i] = False

def SetEnabled(lvl, b):
    '''Enable or disable the give level.'''
    if lvl == Level.TRACEIN:
        Enabled[Level.TRACEOUT] = b
    if lvl == Level.TRACEOUT:
        Enabled[Level.TRACEIN] = b
    Enabled[lvl] = b

def Enable(lvl):
    SetEnabled(lvl, True)

def Disable(lvl):
    SetEnabled(lvl, False)
    
def SetEnabledPlus(lvl, b):
    '''Enable the given level and all above, or
    Disable the given level and all below.
    '''
    if lvl == Level.TRACEOUT: #Either TRACEIN or TRACEOUT should work
        lvl = Level.TRACEIN
    if b:
        for i in range(lvl,9):
            Enable(i)
    else:
        for i in range(1,lvl+1):
            Disable(i)

def EnablePlus(lvl):
    SetEnabledPlus(lvl, True)

def DisableMinus(lvl):
    SetEnabledPlus(lvl, False)

def IsEnabled(lvl):
    if lvl in Enabled:
        return Enabled[lvl]
    return False

def BPLog(msg, lvl=Level.INFO):
    '''Actual logging occurs here, only on enabled levels.
    BPLog meaning BoxeePlayLogger.
    '''
    noteIcon   = { Level.NOTICE  : "noteNotice.png"
                 #, Level.DEBUG   : "noteDebug.png"
                 , Level.INFO    : "noteInfo.png"
                 , Level.WARNING : "noteWarn.png"
                 , Level.ERROR   : "noteError.png"
                 }
    logFunc    = { Level.TRACEIN : mc.LogDebug
                 , Level.TRACEOUT: mc.LogDebug
                 , Level.DEBUG   : mc.LogDebug
                 , Level.INFO    : mc.LogInfo
                 , Level.WARNING : mc.LogInfo
                 , Level.ERROR   : mc.LogError
                 , Level.FATAL   : mc.LogError
                 }
    logPrepend = { Level.TRACEIN : "TRACE, Entering scope of "
                 , Level.TRACEOUT: "TRACE, Exiting scope of "
                 , Level.DEBUG   : "DEBUG, "
                 , Level.INFO    : "INFO, "
                 , Level.WARNING : "WARNING, "
                 , Level.ERROR   : "ERROR, "
                 , Level.FATAL   : "FATAL, "
                 }

    if IsEnabled(lvl):

#        msg = "Name:" + __name__ + ",Module:" + __module__ + ",File:" + __file__ + " :: " + msg
        # Prepend log message if necessary
        if lvl in logPrepend:
            msg = logPrepend[lvl] + msg

        # Send notification to user
        if lvl in noteIcon:
            mc.ShowDialogNotification(msg, noteIcon[lvl])

        # Send message to log
        if lvl in logFunc:
            # Log message distinguisher for easy log file lookup
            msg = "BPLog: " + msg
            # Call Boxee log function
            logFunc[lvl](msg)

        # If FATAL, shut down app
        if lvl == Level.FATAL:
            #mc.GetApp().Close()     #Boxee main app stupidly enough crashes on memviolation when executing this
            mc.ActivateWindow(10482) #Until better times..

    # Let's report any unknown log level
    if lvl not in noteIcon and lvl not in logFunc:
        BPLog("UNDEFINED LOG LEVEL: " + str(lvl) + 
              ", with message: " + msg, Level.ERROR)

def BPTraceEnter(msg=""):
    '''Sugar for BPLog with level TRACEIN.
    An optional message (no need for it to be a string)
    may be provided. For instance the arguments provided
    to the traced function.'''
    BPTrace(msg, Level.TRACEIN)

def BPTraceExit(msg=""):
    '''Sugar for BPLog with level TRACEOUT.
    An optional message (no need for it to be a string)
    may be provided. For instance the arguments provided
    to the traced function.'''
    BPTrace(msg, Level.TRACEOUT)

def BPTrace(msg, level):
    '''BPTrace will inspect the call stack to see which
    function that called us and pass this on to the log.'''
    if IsEnabled(level):
      s = inspect.stack()
      if len(s) >= 2 and s[1][3].startswith('BPTrace'):
          depth = 2
      else:
          depth = 1
      called = len(s) >= depth + 2 #called at depth, caller at depth + 1
      
      f     = s[depth]
      fFile = str(f[1]).rsplit('\\')[-1]
      fRow  = str(f[2])
      fName = str(f[3])
      trace = "%s at %s:%s" % (fName, fFile, fRow)

      if called:
          caller   = s[depth + 1]
          callFile = str(caller[1]).rsplit('\\')[-1]
          callRow  = str(caller[2])
          callName = str(caller[3])
          trace += " called from %s at %s:%s" % (callName, callFile, callRow)
      BPLog("%s -> %s" % (trace, msg), level)

