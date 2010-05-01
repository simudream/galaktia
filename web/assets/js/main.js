// Galaktia client main script
var Galaktia = {version: '0.2a', client: null};

// Application context setup
Galaktia.setup = function () {
	// log setup
	Galaktia.logger = new Log; // see: mootools Log
	// client + ui + view setup
	Galaktia.client = new Galaktia.Client();
	Galaktia.ui = new Galaktia.UIController();
	Galaktia.view = new Galaktia.CanvasView();
	Galaktia.log = Galaktia.ui.bindLog(Galaktia.logger);
			// returns a log callback to be used globally
	// welcome message
	Galaktia.log('Welcome Galaktia player! You may play with this '
			+ 'pre-release-candidate GUI by pressing these keys:'
			+ '\n\tE\tPrompts for login (Enter Request)'
			+ '\n\tS\tPrompts for chat (Say Request)'
			+ '\n\tM\tPrompts for walking (Move Request)'
			+ '\n\tH\tPrompts for attacking (Hit Request)'
			+ '\n\tX\tPrompts for logout (Exit Request)');
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
