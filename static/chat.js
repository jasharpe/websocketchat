$(document).ready(function() {
  var ws = new WebSocket("ws://" + window.location.host + "/websocket");  
  ws.onopen = function() {  
    var text_box = $("#box");
    ws.send(JSON.stringify({
        "type" : "room_request",
        "room" : room_name
    }));
  };  
  ws.onmessage = function (e) {
    var message = JSON.parse(e.data);
    if (message["type"] == "message") {
      var text_area = $("#area");
      if (text_area.text()) {
        text_area.text(text_area.text() + "\n" + message["message"]);
      } else {
         text_area.text(message["message"]);
      }
    } else if (message["type"] == "history") {
      var text_area = $("#area");
      text_area.text("");
      message["messages"].forEach(function(chat_message) {
        if (text_area.text()) {
          text_area.text(text_area.text() + "\n" + chat_message);
        } else {
          text_area.text(chat_message);
        }
      });
      $("#box").attr("disabled", "");
    } else if (message["type"] == "update") {
      $("#" + message["id"]).html(message["html"]);
    } else {
      alert("Unknown message type " + message.type);
    }
  };  
  ws.onclose = function() {
    // attempt to reconnect?
  };

  var box = $("#box");
  var part_msg = localStorage.getItem('partial_message');
  if (part_msg !== undefined) {
    box.val(part_msg);
  }
  box.keypress(function(e) {
    if (event.keyCode == '13') {
      ws.send(JSON.stringify({
          "type" : "new_message",
          "message" : box.val()
      }));
      box.val("");
    }
  });
  box.keyup(function(e) {
    localStorage.setItem('partial_message', box.val());
  });
});
