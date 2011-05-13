import mc, logger
import tv4xml

logger.EnablePlus(logger.Level.DEBUG)

#categories = tv4xml.GetCategories()
#categoryId = categories[1].GetProperty("id")
#titles = tv4xml.GetTitles(categoryId)
episodes = tv4xml.GetEpisodes("1.1844489")
#item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
#item.SetLabel("Example")
#item.SetContentType("text/html")
#item.SetPath(tv4xml.GetVideoPath("1182789"))
#mc.GetPlayer().Play(item)
