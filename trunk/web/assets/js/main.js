// Galaktia client main script
var Galaktia = {version: '0.2a', client: null};

// Application context setup
Galaktia.setup = function () {
	// log setup
	Galaktia.logger = new Log; // see: mootools Log
	// client + ui + view + dao setup
	Galaktia.client = new Galaktia.Client();
	Galaktia.ui = new Galaktia.UIController();
	Galaktia.view = new Galaktia.CanvasView();
	Galaktia.dao = new Galaktia.SceneObjectDAO();
	// console setup (Galaktia.log is a global function accepting messages)
	Galaktia.log = Galaktia.ui.bindLog(Galaktia.logger);
	// welcome message
	Galaktia.log('Welcome Galaktia player! You may play with this '
			+ 'pre-release-candidate GUI by pressing these keys:'
			+ '\n\tE\tPrompts for login (Enter Request)'
			+ '\n\tS\tPrompts for chat (Say Request)'
			+ '\n\tH\tPrompts for attacking (Hit Request)'
			+ '\n\tX\tPrompts for logout (Exit Request)'
			+ '\n\t\u2190\u2191\u2192\u2193'
			+ '\tFor walking (Move Request)');
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
