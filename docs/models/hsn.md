# HasSocialNetwork

This model represent that a user have an account in a specific social 
network. It's useful to get the username or alias.

```
class HasSocialNetwork(models.Model):
    user = integer
    social = string
    username = string
    alias = string
```
- user: The User's pk that send the message
- social: The social network's pk that send the message
- username: The User's username in the specific Social Network
- alias: The User's alias in the specific Social Network. Optional