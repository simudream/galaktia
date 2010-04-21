var Galaktia = Galaktia || {};

Galaktia.Controller = new Class({
	initialize: function(dispatcher) {
	
		var messages = [];
		for ( prop in this ) {
			
			if ( $type(this[prop]) == 'function' && prop.substr(0, 2) == 'on' ) {
				
				messages.push(prop.toString());
			}
		}
		
		for( var i = 0; i < messages.length; i++ ) {
			
			var messageName = messages[i];
			dispatcher.addTypeHandler(messageName.substr(2), this[messageName].bind(this));
		}
	}
});