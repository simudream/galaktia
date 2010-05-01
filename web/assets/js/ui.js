Galaktia.UIController = new Class({

	keyboard: null,

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

	say: function () {
		this.send('Say', {
			text: this.prompt('Chat message:')
		});
	},

	move: function () {
		this.send('Move', {
			x: this.prompt('X coordinate:', '0').toInt(),
			y: this.prompt('Y coordinate:', '0').toInt()
		});
	},

	hit: function () {
		this.send('Hit', {
			character_id: this.prompt('Character ID:', '0').toInt()
		});
	},

	exit: function () {
		if (this.confirm('Are you sure you want to quit?')) {
			this.send('Exit', {});
			Galaktia.client.disconnect();
		}
	},

	send: function (type, data) {
		var namespace = 'galaktia.controller.' + type.toLowerCase();
		data.__class__ = namespace + ':' + type + 'RequestMessage';
		Galaktia.client.send(data);
	},

	alert: function (message) {
		// TODO: implement via HTML, not JS alert dialog
		alert(message);
	},

	confirm: function (message) {
		// TODO: implement via HTML, not JS confirm dialog
		return confirm(message);
	},

	prompt: function (message, value) {
		// TODO: implement via HTML, not JS prompt dialog
		return prompt(message || '', value || '');
	}

});
