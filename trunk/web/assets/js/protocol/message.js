var Galaktia = Galaktia || {};

Galaktia.Message = new Class({
	type: '',
	attributes: [],
	normalize: function() {
		var normal = {};
		
		for ( var i = 0; i < attributes.length; i++ ) {
			
			normal[attributes[i]] = this[attributes[i]];
		}
		
		normal.type = this.type;
		return normal;
	},
	intialize: function(literal) {
		
		var values;
		if ( $defined(literal) ) {
			
			values = $extend(this.defaultValues, literal);
		} else {
			
			values = this.defaultValues;
		}
		
		$each(values, function(value, prop){
			
			this[prop] = value;
		});
	}
});