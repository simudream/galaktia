var Galaktia = Galaktia || {};                                            
Galaktia.Messages = Galaktia.Messages || {};      

Galaktia.Messages.HitRequest = new Class({                               
    Extends: Galaktia.Message,                                         
    type: 'HitRequestMessage',
    attributes: ['character_id']
});

Galaktia.Messages.HitResponse = new Class({                               
    Extends: Galaktia.Message,                                         
    type: 'HitResponseMessage',
    attributes: ['result']
});

Galaktia.Messages.HitNotification = new Class({                               
    Extends: Galaktia.Message,                                         
    type: 'HitNotificationMessage',
    attributes: ['hitting_character_id', 'hit_character_id', 'result']
});