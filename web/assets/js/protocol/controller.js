var Galaktia = Galaktia || {};

Galaktia.Controller = new Class({
	messages: [],
	initialize: function(dispatcher) {
	
		for ( prop in this ) {
			
			if ( $type(this[prop]) == 'function' && prop.substr(0, 2) == 'on' ) {
				
				var messageName = prop.toString();
				dispatcher.addTypeHandler(messageName.substr(2), this[messageName].bind(this));
				
				messages.push(messageName);
			}
		}
	}
});