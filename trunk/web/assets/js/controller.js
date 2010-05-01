/**
 * Class: Controller
 * -----------------
 * Abstract base class for controllers that handle messages.
 */
Galaktia.Controller = new Class({

	handle: function (message) {
		Galaktia.log('Not yet implemented: Handling message: '
				+ JSON.encode(message));
	}

});

// Custom controller implementations -- TODO
Galaktia.EnterResponseController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.EnterNotificationController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.SayResponseController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.SayNotificationController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.MoveResponseController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.MoveNotificationController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.HitResponseController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.HitNotificationController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.ExitResponseController = new Class({
	Extends: Galaktia.Controller
});
Galaktia.ExitNotificationController = new Class({
	Extends: Galaktia.Controller
});

