/**
 * Class: CanvasView
 * -----------------
 * Renders the current map view (tiles, characters, etc.) on a canvas element.
 */
Galaktia.CanvasView = new Class({

	// CanvasView contructor
	initialize: function (message) {
		this.canvas = $('canvas');
		this.images = new Asset.images(['images/walter.png'], {
                	onComplete: this.render.bind(this)
        	}); // TODO: better assets handling
	},

	// Renders the whole canvas
	render: function () {
		var ctx = this.canvas.getContext('2d');
		var w = this.canvas.getProperty('width').toInt();
		var h = this.canvas.getProperty('height').toInt();
		ctx.save() // start
		// background
		ctx.fillStyle = '#000';
		ctx.fillRect(0, 0, w, h);
		// tiles
		var dim = 18;
		for (var x = 0; x < dim; x++) {
			for (var y = 0; y < dim; y++) {
				this.drawTile(x, y);
			}
		}
		// sprite
		this.drawSprite(0, 0);
		ctx.restore(); // finish
	},

	// Draws a tile on given coords
	drawTile: function (x, y) {
		var ctx = this.canvas.getContext('2d');
		var tl = 40;
		var tx = (x + 11) * tl;
		var ty = (y - 7) * tl;
		ctx.save(); // start
		ctx.fillStyle = '#090';
		ctx.scale(1, 0.5);
		ctx.rotate(Math.PI / 4);
		ctx.fillRect(tx, ty, tl, tl);
		ctx.strokeStyle = '#060';
		ctx.lineWidth = 1.0;
		ctx.strokeRect(tx, ty, tl, tl);
		ctx.restore(); // finish
	},

	// Draws a sprite on given coords
	drawSprite: function (x, y) {
		var ctx = this.canvas.getContext('2d');
		ctx.save(); // start
		ctx.drawImage(this.images[0], 482, 308);
				// TODO: DAOs for scene objects and map data
		ctx.restore(); // finish
	}

});
