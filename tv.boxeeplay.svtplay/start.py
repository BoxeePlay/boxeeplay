import mc, svtplay, actions, logger

'''
here we can do some pre launch processing if we wish.
checking authentication or pre-loading content, anything we need.
'''
logger.EnablePlus(logger.Level.TRACEIN)

mc.ActivateWindow(14000)
actions.home()
