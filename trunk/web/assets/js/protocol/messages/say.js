var Galaktia = Galaktia || {};                                            
Galaktia.Messages = Galaktia.Messages || {};      

Galaktia.Messages.SayRequest = new Class({                               
    Extends: Galaktia.Message,                                         
    type: 'SayRequestMessage',
    attributes: ['text']
});

Galaktia.Messages.SayResponse = new Class({                               
    Extends: Galaktia.Message,                                         
    type: 'SayResponseMessage'
});

Galaktia.Messages.SayNotification = new Class({                               
    Extends: Galaktia.Message,                                         
    type: 'SayNotificationMessage',
    attributes: ['character_id', 'text']
});