// Galaktia client main script
var Galaktia = {version: '0.2.0', client: null};

// Application context setup
Galaktia.setup = function () {
	// log setup
	Galaktia.logger = new Log; // see: mootools Log
	// client + dao + ui setup
	Galaktia.client = new Galaktia.Client();
	Galaktia.dao = new Galaktia.SceneObjectDAO();
	Galaktia.ui = new Galaktia.UIController();
	// console setup (Galaktia.log is a global function accepting messages)
	Galaktia.log = Galaktia.ui.bindLog(Galaktia.logger);
};

// Main script
// NOTE: No mootools functions should be assumed in the global execution
// context until all *.js files are loaded, i.e., on domready event.
// In addition, some dependencies may only be resolved after Galaktia.setup().
if (MooTools.version == '1.2.4') {
	window.addEvent('domready', Galaktia.setup);
} else {
	var s = !MooTools ? 'MooTools missing' :
			'Incompatible MooTools version: ' + MooTools.version;
	alert('FATAL: Cannot initialize Galaktia client: ' + s);
}
