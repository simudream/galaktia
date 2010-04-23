var Galaktia = Galaktia || {};
Galaktia.Protocol = Galaktia.Protocol || {};

Galaktia.Protocol.JSONSocket = new Class({
	initialize: function(url) {
		
		this.url = url;
		this.ws = new WebSocket(this.url);
		this.handler = function(message) {};
	},
	registerListenHandler: function(handler) {
	
		if ( $type(handler) == 'function' ) {
			
			this.handler = handler;
			this.ws.onmessage = function(message) {
				
				handler(JSON.parse(message.data));
			};
		}
	},
	send: function(message) {
		
		if ( message instanceof Galaktia.Message ) {
			
			message = message.normalize();
		}
		
		this.ws.send(JSON.stringify(message));
	},
	reopen: function(url) {
		
		if ( this.ws.readyState != WebSocket.CLOSED ) {
			
			this.ws.close();
		}
		
		this.url = url || this.url;
		this.ws = new WebSocket(this.url);
		this.registerListenHandler(this.handler);
	}
});