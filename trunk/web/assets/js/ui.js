/**
 * Class: UIController
 * -------------------
 * Register event handlers on user interface to trigger corresponding
 * function calls on Galaktia components such as client and view.
 * Provides I/O facilities to display alert, confirm and prompt dialogs.
 * Responsible for managing HTML elements.
 */
Galaktia.UIController = new Class({

	keyboard: null, // Keyboard (mootools)

	// UIController contructor
	initialize: function () {
		var events = {
			'e': this.enter.bind(this),
			's': this.say.bind(this),
			'm': this.move.bind(this),
			'h': this.hit.bind(this),
			'x': this.exit.bind(this)
		};
		this.keyboard = new Keyboard({events: events});
	},

	// Connects client and sends an EnterRequestMessage.
	// Prompts for input of: host, username, password.
	enter: function () {
		var host = this.prompt('Host (web socket server URL):',
				'ws://localhost:8880');
		var onConnect = this.send.bind(this, ['Enter', {
			username: this.prompt('Username:', 'walter'),
			password: this.prompt('Password:', 'i<3w4Lt3r1N4')
		}]);
		if (host) {
			Galaktia.client.connect(host, onConnect);
		} else {
			Galaktia.log('Login cancelled');
		}
	},

	// Sends a SayRequestMessage. Prompts for chat message text.
	say: function () {
		this.send('Say', {
			text: this.prompt('Chat message:')
		});
	},

	// Sends a MoveRequestMessage. Prompts for absolute coords.
	move: function () {
		this.send('Move', {
			x: this.prompt('X coordinate:', '0').toInt(),
			y: this.prompt('Y coordinate:', '0').toInt()
		});
	},

	// Sends a HitRequestMessage. Prompts for input of character ID.
	hit: function () {
		this.send('Hit', {
			character_id: this.prompt('Character ID:', '0').toInt()
		});
	},

	// Sends an ExitRequestMessage, given prior confirmation
	exit: function () {
		if (this.confirm('Are you sure you want to quit?')) {
			this.send('Exit', {});
			Galaktia.client.disconnect();
		}
	},

	// Sends a generic message (type determines class, data is any object)
	send: function (type, data) {
		var namespace = 'galaktia.controller.' + type.toLowerCase();
		data.__class__ = namespace + ':' + type + 'RequestMessage';
		Galaktia.client.send(data);
	},

	// Returns a callback function that can be called globally to
	// see logged messages in an UI console-like display.
	// Returned callback can accept a string and an optional log level
	// key such as 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL', etc.
	bindLog: function (logger) {
		var scroll = new Fx.Scroll('log-output');
		return function (message, level) {
			if ($type(message) != 'string') {
				message = JSON.encode(message);
			}
			level = (level || 'INFO').toUpperCase();
			var now = new Date().format('%H:%M:%S');
			record = [now, level, message].join(' ');
			logger.log(record);
			var value = $('log-output').getProperty('value');
			value += record + '\n';
			$('log-output').setProperty('value', value);
			scroll.toBottom();
			// TODO: log output should not grow infinitely
		};
	},

	// Displays an alert dialog
	alert: function (message) {
		// TODO: implement via HTML, not JS alert dialog
		alert(message);
	},

	// Displays an confirm dialog and returns resulting boolean
	confirm: function (message) {
		// TODO: implement via HTML, not JS confirm dialog
		return confirm(message);
	},

	// Displays a prompt dialog and returns the string entered by
	// user (or null on cancel), set by default as the value arg.
	prompt: function (message, value) {
		// TODO: implement via HTML, not JS prompt dialog
		return prompt(message || '', value || '');
	}

});
