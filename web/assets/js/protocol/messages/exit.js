var Galaktia = Galaktia || {};                                            
Galaktia.Messages = Galaktia.Messages || {};                          
                                                                          
Galaktia.Messages.ExitRequest = new Class({                               
       Extends: Galaktia.Message,                                         
       type: 'ExitRequestMessage'                                         
});                                                                       
                                                                          
Galaktia.Messages.ExitNotification = new Class({                          
       Extends: Galaktia.Message,                                         
       type: 'ExitNotificationMessage',                                   
       attributes: ['id']                                                 
})                                                                        
                                                                          
Galaktia.Messages.ExitResponse = new Class({                              
       Extends: Galaktia.Message,                                         
       type: 'ExitResponseMessage'                                        
});