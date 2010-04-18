var Galaktia = Galaktia || {};

Galaktia.Message = new Class({
	type: '',
	attributes: [],
	normalize: function() {
		var normal = {};
		
		for ( key in attributes ) {
			
			normal[attributes[key]] = this[attributes[key]];
		}
		
		return normal;
	}
});