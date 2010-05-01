// Galaktia client main script
var Galaktia = {version: '0.2a', client: null};

// Application context setup
Galaktia.setup = function () {
	// log setup
	Galaktia.logger = new Log;
	Galaktia.logger.enableLog();
	var scroll = new Fx.Scroll('log-output');
	Galaktia.log = function (message, level) {
		if ($type(message) != 'string') {
			message = JSON.encode(message);
		}
		level = (level || 'INFO').toUpperCase();
		var now = new Date().format('%H:%M:%S');
		record = [now, level, message].join(' ');
		Galaktia.logger.log(record);
		var value = $('log-output').getProperty('value');
		$('log-output').setProperty('value', value + record + '\n');
		scroll.toBottom();
		// TODO: log output should not grow infinitely
	};
	// client setup
	Galaktia.client = new Galaktia.Client();
	// view setup
	Galaktia.view = new Galaktia.CanvasView();
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
if (MooTools.version == '1.2.4') {
	window.addEvent('domready', Galaktia.setup);
} else {
	var s = !MooTools ? 'MooTools missing' :
			'Incompatible MooTools version: ' + MooTools.version;
	alert('FATAL: Cannot initialize Galaktia client: ' + s);
}
