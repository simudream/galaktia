/**
 * Class: CanvasView
 * -----------------
 * Renders the current map view (tiles, characters, etc.) on a canvas element.
 */
Galaktia.CanvasView = new Class({

	images: [
		'images/walter.png',
		'images/humano.png',
	],

	// CanvasView contructor
	initialize: function (message) {
		this.canvas = $('canvas');
		this.size = this.canvas.getSize();
		this.images = new Asset.images(this.images, {
                	onComplete: this.resize.bind(this)
        	});
		// window resize event handling (delayed)
		var timer = null;
		window.addEvent('resize', function () {
			$clear(timer);
			timer = this.resize.delay(500, this);
		}.bind(this));
	},

	// Resizes canvas to fit in given size or parent size
	resize: function (width, height) {
		var size = this.canvas.getParent().getSize();
		this.size = {x: width || size.x, y: height || size.y};
		this.canvas.setProperty('width', this.size.x.toString());
		this.canvas.setProperty('height', this.size.y.toString());
		this.render();
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
		var semiLength = 20;
		for (var x = -semiLength; x <= semiLength; x++) {
			for (var y = -semiLength; y <= semiLength; y++) {
				this.drawTile(x, y);
			}
		}
		// sprite
		this.drawSprite(Galaktia.dao.character);
		ctx.restore(); // finish
	},

	// Draws a tile on given coords
	drawTile: function (x, y) {
		//if (x * x + y * y > 20 * 20) return;
		var ctx = this.canvas.getContext('2d');
		var tl = 40;
		var tx = (this.size.x) / 2;
		var ty = (this.size.y) / 2;
		ctx.save(); // start
		ctx.fillStyle = '#090';
		ctx.translate(tx, ty);
		ctx.scale(1, 0.5);
		ctx.rotate(Math.PI / 4);
		ctx.fillRect((x - 0.5) * tl, (y - 0.5) * tl, tl, tl);
		ctx.strokeStyle = '#060';
		ctx.lineWidth = 1.0;
		ctx.strokeRect((x - 0.5) * tl, (y - 0.5) * tl, tl, tl);
		ctx.restore(); // finish
	},

	// Draws a sprite on given coords
	drawSprite: function (character) {
		// TODO: most character attrs are ignored here and hard-coded
		var ctx = this.canvas.getContext('2d');
		var img = this.images[1];
		var w = img.width / 15; // animation frames (15 columns)
		var h = img.height / 8; // orientation (8 rows)
		var tx = (this.size.x - w) / 2;
		var ty = (this.size.y - h * 1.75) / 2;
		var size = img.getDimensions();
		ctx.save(); // start
		ctx.drawImage(img, w * character.animation,
				h * character.orientation, w, h, tx, ty, w, h);
		character.animation = (character.animation + 1) % 15;
		ctx.restore(); // finish
	}

});
