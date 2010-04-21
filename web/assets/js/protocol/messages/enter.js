var Galaktia = Galaktia || {};                                            
var Galaktia.Messages = Galaktia.Messages || {};      

Galaktia.Messages.EnterRequest = new Class({                               
    Extends: Galaktia.Message,                                         
    type: 'EnterRequestMessage',
    attributes: ['username', 'password']
});

Galaktia.Messages.EnterResponse = new Class({
	Extends: Galaktia.Message
	type: 'EnterResponseMessage',
	attributes: ['x', 'y', 'character', 'map_data']
});

Galaktia.Messages.EnterNotification = new Class({
	Extends: Galaktia.Messsage,
	type: 'EnterNotificationMessage',
	attributes: ['x', 'y', 'character']
});