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
			'left': this.move.bind(this, [-1, -1]),
			'right': this.move.bind(this, [1, 1]),
			'up': this.move.bind(this, [-1, 1]),
			'down': this.move.bind(this, [1, -1]),
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
		if (!host) {
			Galaktia.log('Login cancelled');
			return;
		}
		var onConnect = this.send.bind(this, ['Enter', {
			username: this.prompt('Username:', 'walter'),
			password: this.prompt('Password:', 'i<3w4Lt3r1N4')
		}]);
		Galaktia.client.connect(host, onConnect);
	},

	// Sends a SayRequestMessage. Prompts for chat message text.
	say: function () {
		this.send('Say', {
			text: this.prompt('Chat message:')
		});
	},

	// Sends a MoveRequestMessage to position given by offset (dx, dy).
	move: function (dx, dy) {
		this.send('Move', {
			x: Galaktia.dao.position.x + dx,
			y: Galaktia.dao.position.y + dy
		});
		// XXX Simulate controller action after MoveResponseMessage:
		var character = Galaktia.dao.character;
		var oMap = [6, 7, 4, 5, character.orientation, 1, 0, 3, 2];
		character.orientation = oMap[(dx + 1) + 3 * (dy + 1)];
		Galaktia.view.render();
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
	// see logged messages in the GUI "console".
	// Returned callback accepts the log message string and an optional
	// log level key such as 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL',
	// etc. (defaults to 'INFO').
	bindLog: function (logger) {
		var console = new Element('textarea', {disabled: 'disabled'});
		console.addClass('console');
		console.inject($('canvas'), 'after');
		var scroll = new Fx.Scroll(console);
		return function (message, level) {
			if ($type(message) != 'string') {
				message = JSON.encode(message);
			}
			level = (level || 'INFO').toUpperCase();
			var now = new Date().format('%H:%M:%S');
			record = [now, level, message].join(' ');
			logger.log(record);
			var value = console.getProperty('value');
			value += record + '\n';
			console.setProperty('value', value);
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
