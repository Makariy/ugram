
### Message structure
- text: the message text as a normal string 
- date: the date the message was sent 
- type: the type of the message:  
    - text: text message, could have attachments (files, images, videos)
    - voice: voice message 
    - circle_video: circle video  
    - sticker: sticker alone 


### Attachment structure 
- file_url: url on which the attachment data is stored 
- type: the type of the attachment:
    - image 
    - video 
    - file 
    - voice 
    - circle_video
    - sticker 


## Messaging architecture
The message is sent via the HTTP API, validated and added to the messages table 
in the database. After that, a notification about the sent message is pushed to the 
queue.

There is a worker which maintains WebSocket connections with users and pulls from 
the queue. The moment it gets the notification from the queue, it looks up the 
connected users to which the message is destined. For every one of those users it 
sends the notification about the new message.

The same process happens with the message delete/patch/etc, group 
create/delete/patch/etc.


User must open the connection in background the moment he opens the messenger. The 
notifications will have all the information about the event it notifies about, so 
the user would be able to identify which state of his app to modify. 

The connection will be established directly to the worker application and the worker 
will maintain a lookup table which maps the user id to the WebSocket connection. 
The notification for multiple users will be executed in several tasks which would 
consume the users to which it must send the notification to via a queue. 

If a user has just opened the application and still had not established the 
connection but there was a notification sent, there could be an inconsistency. 
So the idea is to first establish the connection, then retrieve the last messages 
and if in between this process there is a message sent over the connection then 
store it in a buffer until the last messages are loaded and after that, merge 
the last messages with the buffer. This process must work both with the messages 
inside a chat, the groups overview and other places were it could be necessary.


