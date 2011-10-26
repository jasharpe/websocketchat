import tornado.web
import tornado.websocket
import tornado.httpserver
import json
import os
from db import get_session
from db.models import Message, Room

session = get_session()

settings = {
  "template_path" : os.path.join(os.path.dirname(__file__), "templates"),
  "static_path" : os.path.join(os.path.dirname(__file__), "static"),
}

sockets = []

class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
  def send_message_to_all(self, message):
    global sockets
    for socket in sockets:
      socket.write_message(json.dumps({
          'type' : 'message',
          'message' : message,
      }))
  
  def open(self):
    sockets.append(self)
    messages = [message.message for message in session.query(Message).order_by(Message.dt)]
    self.write_message(json.dumps({
        'type' : 'history',
        'messages' : messages
    }))
    print "%d sockets" % len(sockets)

  def on_message(self, message_json):
    global sockets
    message = json.loads(message_json)
    if message['type'] == 'request_card':
      m = Message(message['message'])
      session.add(m)
      self.send_message_to_all(message['message'])

  def on_close(self):
    global sockets
    sockets.remove(self)
    print "%d sockets" % len(sockets)

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render(
        "chat.html"
    )

application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/websocket", MyWebSocketHandler),
], **settings)

if __name__ == "__main__":
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
