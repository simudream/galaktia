var Galaktia = Galaktia || {};
var Galaktia.Messages = Galaktia.Messages || {};

Galaktia.Messages.MoveRequest = new Class({
       Extends: Galaktia.Message,
       type: 'MoveRequestMessage',
       attributes: ['x', 'y']
});

Galaktia.Messages.MoveResponse = new Class({
       Extends: Galaktia.Message,
       type: 'MoveResponseMessage',
       attributes: ['x', 'y', 'map_data']
});

Galaktia.Messages.MoveNotification = new Class({
       Extends: Galaktia.Message,
       type: 'MoveNotificationMessage',
       attributes: ['map_data']
});
