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
	view: null, // Galaktia.CanvasView

	// UIController contructor
	initialize: function () {
		var events = {
			'enter': this.say.bind(this),
			'left': this.move.bind(this, [-1, -1]),
			'right': this.move.bind(this, [1, 1]),
			'up': this.move.bind(this, [-1, 1]),
			'down': this.move.bind(this, [1, -1]),
			'alt+h': this.hit.bind(this),
			'alt+x': this.exit.bind(this)
		};
		this.keyboard = new Keyboard({events: events});
		this.view = new Galaktia.CanvasView($('canvas'));
		$('login').addEvent('click', this.enter.bind(this));
		$('username').focus();
	},

	// Connects client and sends an EnterRequestMessage.
	// Prompts for input of: host, username, password.
	enter: function () {
		var host = $('host').getProperty('value');
		var username = $('username').getProperty('value');
		var password = $('password').getProperty('value');
		if (!(host && username && password)) {
			Galaktia.log('Cannot login: Missing required fields');
			return;
		}
		var callback = this.onConnect.bind(this, [username, password]);
		return Galaktia.client.connect(host, callback);
	},

	onConnect: function (username, password) {
		Galaktia.log('Remember these keyboard actions:'
			+ '\n\tEnter text in the prompt at bottom '
			+ 'to send a chat message (Say Request)'
			+ '\n\tPress the arrows (\u2190\u2191\u2192\u2193) '
			+ 'to walk (Move Request)'
			+ '\n\tPress Alt+H to attack (Hit Request)'
			+ '\n\tPress Alt+X or close the window to quit game '
			+ '(Exit Request)'
		);
		$('frontpage').setStyle('display', 'none');
		$('canvas').setStyle('display', 'block');
		this.view.render();
		$('prompt').focus();
		window.onbeforeunload = function (e) {
			return 'You are about to quit the game. You may '
					+ 'cancel to keep playing.';
		};
		window.addEvent('unload', this.exit.bind(this));
		return this.send('Enter', {username: username,
				password: password});
	},

	// Sends a SayRequestMessage. Prompts for chat message text.
	say: function () {
		if (!Galaktia.client.socket) { // XXX UI state hack
			return this.enter();
		} else {
			var text = $('prompt').getProperty('value');
			$('prompt').setProperty('value', '');
			return this.send('Say', {text: text});
		}
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
		this.view.render();
		return true;
	},

	// Sends a HitRequestMessage. Prompts for input of character ID.
	hit: function () {
		return this.send('Hit', {
			character_id: this.prompt('Character ID:', '0').toInt()
		});
	},

	// Sends an ExitRequestMessage, given prior confirmation
	exit: function () {
		this.send('Exit', {});
		Galaktia.client.disconnect();
		return true;
	},

	// Sends a generic message (type determines class, data is any object)
	send: function (type, data) {
		var namespace = 'galaktia.controller.' + type.toLowerCase();
		data.__class__ = namespace + ':' + type + 'RequestMessage';
		return Galaktia.client.send(data);
	},

	// Returns a callback function that can be called globally to
	// see logged messages in the GUI "console".
	// Returned callback accepts the log message string and an optional
	// log level key such as 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL',
	// etc. (defaults to 'INFO').
	bindLog: function (logger) {
		var console = $('console');
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
