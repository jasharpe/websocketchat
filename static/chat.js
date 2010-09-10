$(document).ready(function() {
  var ws = new WebSocket("ws://" + window.location.host + "/websocket");  
  ws.onopen = function() {  
    var text_box = $("#box");
    text_box.attr("disabled", "");
  };  
  ws.onmessage = function (e) {
    var message = JSON.parse(e.data);
    if (message["type"] == "message") {
      var text_area = $("#area");
      text_area.text(text_area.text() + "\n" + message["message"]);
    } else {
      alert("Unknown message type " + message.type);
    }
  };  
  ws.onclose = function() {
    // attempt to reconnect?
  };

  var box = $("#box");
  box.keypress(function(e) {
    if (event.keyCode == '13') {
      ws.send(JSON.stringify({
          "type" : "request_card",
          "message" : box.val()
      }));
      box.val("");
    }
  });
});
