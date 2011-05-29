import mc, tvseries, logger

listItems = tvseries.GetChannels()
listItems[0].Dump()
url = tvseries.GetSeriesUrlForChannel(listItems[0])
mc.LogInfo("tvseries: url- " + url)
seriesItems = tvseries.GetSeries(url)
seriesItems[0].Dump()
url = tvseries.GetEpisodesUrlForSerie(seriesItems[0])
mc.LogInfo("tvseries: url- " + url)
episodeItems = tvseries.GetEpisodes(url)
episodeItems[0].Dump()
