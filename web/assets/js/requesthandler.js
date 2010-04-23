var Galaktia = Galaktia || {};

Galaktia.RequestHandler = new Class({
	initialize: function(protocolSocket, screenSocket) {
		this.protocolSocket = protocolSocket;
		this.screenSocket = screenSocket;

		var handler = this.handleIncoming.bind(this);
		var register = function(socket) {
			socket.registerHandler(handler);
		};
		register(protocolSocket);
		register(screenSocket);

	},
	defaultHandler: function() {
		//Stub
	},
	handleIncoming: function(message) {
	
		var handler = this.incomingHandler || this.defaultHandler;
		var results = handler(message);

		results.each(function(returnMessage) {
			this.handleOutgoing(returnMessage);
		});
	},
	handleOutgoing: function(message) {
		
		if ( message instanceof Galaktia.Protocol.Message ) {
			
			this.protocolSocket.send(message);
		} else if ( messsage instanceof Galaktia.Screen.Message ) {

			this.screenSocket.send(message);
		} else {
		
			throw new Exception("Ooops. Cant handle this kind of message");
		}
	},
	registerListenHandler: function(handler) {
		
		if ( $type(handler) == 'function' ) {
			
			this.incomingHandler = handler;
		}
	}
});