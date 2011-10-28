import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado import template
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
default_room = Room('lobby')
session.add(default_room)
rooms = { 'lobby' : default_room }
socket_to_room = {}

class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
  def send_message_to_all_in_room(self, room, message):
    global sockets
    for socket in sockets:
      if socket in socket_to_room.keys() and room == socket_to_room[socket]:
        socket.write_message(json.dumps({
            'type' : 'message',
            'message' : message,
        }))
  
  def open(self):
    sockets.append(self)
    print "%d sockets" % len(sockets)

  def send_rooms_update(self):
    html = template.Loader(settings['template_path']).load("room_list.html").generate(rooms=session.query(Room).all())
    for socket in sockets:
      socket.write_message(json.dumps({
        'type' : 'update',
        'id' : 'room_list',
        'html' : html
      }))

  def on_message(self, message_json):
    global sockets
    message = json.loads(message_json)
    if message['type'] == 'new_message':
      m = Message(message['message'])
      session.add(m)
      socket_to_room[self].messages.append(m)
      self.send_message_to_all_in_room(socket_to_room[self], message['message'])
    elif message['type'] == 'room_request':
      try:
        room = rooms[message['room']]
      except:
        room = Room(message['room'])
        session.add(room)
        self.send_rooms_update()
        rooms[message['room']] = room
      socket_to_room[self] = room
      messages = [message.message for message in room.messages]
      self.write_message(json.dumps({
          'type' : 'history',
          'messages' : messages
      }))

  def on_close(self):
    global sockets
    sockets.remove(self)
    if self in socket_to_room.keys():
      del socket_to_room[self]
    print "%d sockets" % len(sockets)

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render(
        "chat.html",
        room_name="lobby",
        rooms=session.query(Room).all()
    )

class RoomHandler(tornado.web.RequestHandler):
  def get(self, room_name):
    self.render(
        "chat.html",
        room_name=room_name,
        rooms=session.query(Room).all()
    )

application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/room/(.*)", RoomHandler),
  (r"/websocket", MyWebSocketHandler),
], **settings)

if __name__ == "__main__":
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
