import mc, logger
import tv4xml, tv4mc

logger.EnablePlus(logger.Level.DEBUG)

items = tv4mc.SearchEpisodes("tintin")
mc.ShowDialogOk("hits", str(len(items)))
