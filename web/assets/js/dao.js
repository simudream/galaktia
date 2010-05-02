/**
 * Class: SceneObjectDAO
 * ---------------------
 * Holds all objects loaded in the current scene.
 */
Galaktia.SceneObjectDAO = new Class({

	position: {x: 0, y: 0}, // current position (center of displayed map)

	character: {
		id: 0,
		x: 0,
		y: 0,
		skin: 'humano',
		orientation: 3,
		animation: 0
	}, // current player character (at center of displayed map)

	// characters: [],

	// tiles: [],

	// Returns object of given type at given coordinates
	get: function (x, y, type) {
		throw new Exception('Not yet implemented!'); // TODO
	},

	// Same as get but returns all objects matching given criterias
	filter: function (x, y, type) {
		throw new Exception('Not yet implemented!'); // TODO
	},

	// TODO: methods: add? remove?

});
