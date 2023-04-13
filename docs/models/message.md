# Message

This model represent a message in the database.

```
class Message(models.Model):
    KIND_CHOICES = (
        ('input', 'Recibido'),
        ('output', 'Enviado')
    )

    fromUser = integer
    toUser = integer
    through = string
    kind = string KIND_CHOICES
    ack = boolean
    content = string
    file = string
    timestamp = datetime
```

- fromUser: The User's pk that send the message
- toUser: The User's pk that will received the message
- through: The social network's pk that send the message
- kind: Indicate if the message arrived to the app or was send from the app
- ack: Indicate if the message was already send or received
- content: The text message to send
- file: The file message to send.
- timestamp: It's the datetime when the message was added to the database. It's automatic.
