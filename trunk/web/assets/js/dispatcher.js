var Galaktia = Galaktia || {};

Galaktia.Dispatcher = new Class({
	handlers: {},
	defaultHandler: function() {},
	initialize: function(socket) {
	
		socket || this.registerSocket(socket);
	},
	handler: function(message) {
		
		if ( $type(message) != 'object' ) return;
		
		var handler = this.getTypeHandler(message.type);
		delete message.type;
		
		handler(new Galaktia.Messages[message.type](message));
		
	},
	getTypeHandler: function(type) {
		
		return this.handlers[type] || this.defaultHandler;
	},
	addTypeHandler: function(type, handler) {
		
		if ( $type(handler) != 'function' ) return; 
		
		this.handlers[type] = handler;
	},
	addTypeHandlerList: function(handlerList) {
		
		if ( $type(handlerList) == 'object' ) {
			
			throw new Exception("Handler list must be an object mapping type to handler.");
		}
		
		for( type in handlerList ) {
			
			this.addTypeHandler(type, handlerList[type]);
		}
	},
	addDefaultHandler: function(handler) {
		
		if ( $type(handler) == 'function' ) {
			
			this.defaultHandler = handler;
		}
	},
	registerSocket: function(socket) {
		
		socket.registerListenHandler(this.handler.bind(this));
	}
});