// Galaktia client main script

var Galaktia = {version: '0.2a', client: null};

// Global functions (convenience shortcuts)
Galaktia.handle = function (message) {
	var output = Galaktia.client.dispatcher.handle(message);
	$each(output, Galaktia.handle); // recursive call
};
Galaktia._getClassName = function (id) { // tmp helper function
	var namespace = 'galaktia.controller.' + id.toLowerCase();
	return namespace + ':' + id + 'RequestMessage';
}
Galaktia.setup = function () {
	Galaktia.client = new Galaktia.Client();
	// TODO: Separation of Concerns:
	// - UI setup / gets / sets
	// - Message creation / sending
	$('login').addEvent('click', function (e) {
		var host = $('host').getProperty('value');
		var username = $('username').getProperty('value');
		var password = $('passwd').getProperty('value');
		var request = {
			username: username,
			password: password,
			__class__: Galaktia._getClassName('Enter')
		};
		Galaktia.client.connect(host, function () {
			Galaktia.client.send(request);
		});
	});
	$('chat').addEvent('click', function (e) {
		var text = $('text').getProperty('value');
		var request = {
			text: text,
			__class__: Galaktia._getClassName('Say')
		};
		Galaktia.client.send(request);
	});
	$('walk').addEvent('click', function (e) {
		var x = $('x').getProperty('value');
		var y = $('y').getProperty('value');
		var request = {
			x: x,
			y: y,
			__class__: Galaktia._getClassName('Move')
		};
		Galaktia.client.send(request);
	});
	$('attack').addEvent('click', function (e) {
		var who = $('who').getProperty('value');
		var request = {
			character_id: who,
			__class__: Galaktia._getClassName('Hit')
		};
		Galaktia.client.send(request);
	});
	$('logout').addEvent('click', function (e) {
		var request = {
			__class__: Galaktia._getClassName('Exit')
		};
		Galaktia.client.send(request);
		Galaktia.client.disconnect();
	});
	$('send').addEvent('click', function (e) {
		var data = $('message').getProperty('value');
		Galaktia.client.socket.send(data);
	});
};

// Galaktia Client
// Responsible for sending requests triggered by UI events to the Galaktia
// web socket server and updating UI views according to the received
// responses, notifications and error messages.
Galaktia.Client = new Class({

	socket: null,
	ui: null,

	connect: function (host, onconnect) {
		var c = this;
		this.socket = new WebSocket(host);
		this.socket.onopen = function (e) {
			c.log('Connected to: ' + host);
			if (onconnect) {
				onconnect();
			}
		};
		this.socket.onmessage = function (e) {
			try {
				c.log('Received message: ' + e.data);
				var message = JSON.decode(e.data);
				c.handle(message);
			} catch (e) {
				c.log('Failed to receive message: ' + e.data);
			}
		}
		this.socket.onclose = function (e) {
			c.log('Disconnected from: ' + host);
			c.socket = null;
		};
	},

	disconnect: function () {
		this.socket.close();
	},

	send: function (message) {
		if (this.socket) {
			try {
				var data = JSON.encode(message);
				this.socket.send(data);
				this.log('Sent message: ' + data);
			} catch (e) {
				this.log('Failed to send message: ' + e);
			}
		} else {
			this.log('Cannot send message: No open socket');
		}
	},

	handle: function (message) {
		this.log('Handling message... ' + message);
	},

	log: function (message) {
		var log = $('log').getProperty('value');
		$('log').setProperty('value', log + message + '\n');
				// TODO: grows infinitely
	}
});

// Main script
if (MooTools.version == '1.2.3') {
	window.addEvent('domready', Galaktia.setup);
} else {
	var s = MooTools ? 'MooTools missing' : 'Check MooTools version: '
			+ MooTools.version;
	alert('FATAL: Cannot initialize Galaktia client: ' + s);
}
