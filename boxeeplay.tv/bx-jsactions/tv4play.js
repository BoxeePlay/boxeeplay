/*
	Control script for TV4 Play
	F     - Full screen
	ESC   - Leave full screen
	SPACE - Play/Pause
	Arrow Right - Skip forward
	Arrow Left - Skip backwards
	Arrow Up - Volume Up
	Arrow Down - Volume Down
*/

boxee.onDocumentLoaded = function()
{
    boxee.showNotification("onDocumentLoaded", ".", 3);

	// set the api min version to 7.0, for default browser settings
	boxee.apiMinVersion = 7.0;	 
}
 
// callback executed just before the Boxee OSD is made visible
boxee.onUpdateState = function() {
    boxee.showNotification("onUpdateState", ".", 3);
}
 
// callback function executed when user presses play on osd/remote
boxee.onPlay = function() {
	boxee.showNotification("onPlay", ".", 3);
}
 
// callback function executed when user presses pause on osd/remote
boxee.onPause = function() {
	boxee.showNotification("onPause", ".", 3);
}
 
// callback function executed when user presses small skip on osd/remote
boxee.onSkip = function() {
	boxee.showNotification("onSkip", ".", 3);
}
 
// callback function executed when user presses big skip on osd/remote
boxee.onBigSkip = function() {
	boxee.showNotification("onBigSkip", ".", 3);
}
 
// callback function executed when user presses small back on osd/remote
boxee.onBack = function() {
	boxee.showNotification("onBack", ".", 3);
}
 
// callback function executed when user presses big back on osd/remote
boxee.onBigBack = function() {
	boxee.showNotification("onBigBack", ".", 3);
}
