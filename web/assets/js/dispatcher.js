/**
 * Class: DispatcherController
 * ---------------------------
 * Request handler that dispatches messages to corresponding controllers.
 */
Galaktia.DispatcherController = new Class({

	Implements: [Events],

	routes: new Hash({
		EnterResponseMessage:
			new Galaktia.EnterResponseController(),
		EnterNotificationMessage:
			new Galaktia.EnterNotificationController(),
		SayResponseMessage:
			new Galaktia.SayResponseController(),
		SayNotificationMessage:
			new Galaktia.SayNotificationController(),
		MoveResponseMessage:
			new Galaktia.MoveResponseController(),
		MoveNotificationMessage:
			new Galaktia.MoveNotificationController(),
		HitResponseMessage:
			new Galaktia.HitResponseController(),
		HitNotificationMessage:
			new Galaktia.HitNotificationController(),
		ExitResponseMessage:
			new Galaktia.ExitResponseController(),
		ExitNotificationMessage:
			new Galaktia.ExitNotificationController(),
	}), // TODO: auto-detect controllers?

	initialize: function ()	{
		this.routes.each(function (controller, type) {
			var handler = controller.handle.bind(controller);
			this.addEvent(type, handler);
		}.bind(this));
	},

	handle: function (message) {
		var type = (message.__class__ || '').split(':').pop();
		if (!this.routes.has(type)) {
			Galaktia.log('No controller to dispatch message: '
					+ JSON.encode(message), 'ERROR');
		}
		this.fireEvent(type, [message]);
	}

});
