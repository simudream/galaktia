/**
 * Class: GalaktiaClient
 * ---------------------
 * Responsible for sending requests triggered by UI events to the Galaktia
 * web socket server and updating UI views according to the received
 * responses, notifications and error messages.
 */
Galaktia.Client = new Class({

	socket: null, // WebSocket (HTML5)
	codec: null, // JSON (mootools)
	handler: null, // Galaktia.DispatcherController

	// GalaktiaClient constructor
	initialize: function () {
		this.socket = null; // until connect is called
		this.codec = JSON; // nice shortcut :)
		this.handler = new Galaktia.DispatcherController();
	},

	// Opens web socket to host and runs onConnect callback on success
	connect: function (host, onConnect) {
		try {
			this.socket = new WebSocket(host);
		} catch (e) {
			Galaktia.log('Your web browser does not support '
					+ 'web sockets', 'FATAL');
			return;
		}
		this.socket.onopen = function (e) {
			Galaktia.log('Connected to: ' + host);
			if ($type(onConnect) == 'function') {
				onConnect();
			}
		};
		this.socket.onmessage = function (e) {
			try {
				Galaktia.log('Received message: ' + e.data);
				var message = this.codec.decode(e.data);
				this.handler.handle(message);
			} catch (e) {
				Galaktia.log('Failed to receive message: '
						+ e.data);
			}
		}.bind(this);
		this.socket.onclose = function (e) {
			Galaktia.log('Disconnected from: ' + host);
			this.socket = null;
		}.bind(this);
	},

	// Closes web socket
	disconnect: function () {
		this.socket.close();
	},

	// Sends a message (regular object to be encoded in JSON)
	send: function (message) {
		if (this.socket) {
			try {
				var data = this.codec.encode(message);
				this.socket.send(data);
				Galaktia.log('Sent message: ' + data);
			} catch (e) {
				Galaktia.log('Failed to send message: ' + e);
			}
		} else {
			Galaktia.log('Cannot send message: No open socket');
		}
	}
});
