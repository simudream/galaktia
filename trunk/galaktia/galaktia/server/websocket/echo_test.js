// web socket handlers for echo_test.html

function log (msg) {
	var log = $('#log').attr('value');
	$('#log').attr('value', log + msg + '\n');
}

$(window).load(function () {
	var ws = null;
	$('#connect').click(function (e) {
		if (ws) {
			ws.close();
			ws = null;
			$('#connect').attr('value', 'Connect');
		} else {
			var connection = $('#connection').attr('value');
			ws = new WebSocket(connection);
			ws.onopen = function (e) {
				log('Connected to: ' + connection);
			};
			ws.onmessage = function (e) {
				log('Received message: ' + e.data);
			};
			ws.onclose = function (e) {
				log('Disconnected from: ' + connection);
				$('#connect').click();
			};
			$('#connect').attr('value', 'Disconnect');
		}
	});
	$('#send').click(function (e) {
		if (ws) {
			var text = $('#message').attr('value');
			ws.send(text);
			log('Sent message: ' + text);
		} else {
			log('Cannot send message: No web socket connection');
		}
	});
});
