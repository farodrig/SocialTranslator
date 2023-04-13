# Translator API

This API is oriented to be used for other apps, in order to communicate with their clients
without needing to know how to use each one of the social networks.

To be able to use any of these endpoints you need first have a valid token provided by the authentication endpoints 
(either [JWT](../auth/jwt.md) or [OAuth2](../auth/oauth2.md))

The documentation for this API and his endpoints can be found [here](https://socialtranslator.dcc.uchile.cl/docs/#/translator).

## Endpoints


#### [/translator/sendMessage/](https://socialtranslator.dcc.uchile.cl/docs/#!/translator/translator_sendMessage_create)

Allows to send a message from a specific user, to a specific user, through an specific social network. 
'fromUser' and 'toUser' must be the username in the specified social network.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "through": "string",
      "fromUser": "string",
      "toUser": "string",
      "content": "string TEXT_MESSAGE"
      "file": FILE_MESSAGE
    }
    ```
    
- Response Type: JSON
- Response example:

    ```    
    {
        "detail": "string SOME_MESSAGE",
    }    
    ```



#### [/translator/configure/](https://socialtranslator.dcc.uchile.cl/docs/#!/translator/translator_configure_create)

Allow to configure a Social Network Translator for a specific user

- Method: GET
- Request Type: JSON
- Request example:

    ```
    {
      "username": "string",
      "social": "string",
      "auth_code": "string"
    }
    ```

- Response Type: JSON
- Response example:

    ```
    {
        "detail": "string SOME_MESSAGE",
        "redirectURL": "URL_TO_REDIRECT_USER OPTIONAL"
    }
    ```
    

#### [/translator/auth/{social}/](https://socialtranslator.dcc.uchile.cl/docs/#!/translator/translator_auth_read)

Receive authentication callback from oauth2 authentication systems. For example, Gmail.

- Method: GET
- Request Type: Query
- Request example:

    ```
    /translator/auth/gmail/?state=1234&code=1234
    ```

- Response Type: JSON
- Response example:

    ```
    {
        "detail": "string SOME_MESSAGE",
        "redirectURL": "URL_TO_REDIRECT_USER OPTIONAL"
    }
    ```


#### [/translator/push-notif/{social}/](https://socialtranslator.dcc.uchile.cl/docs/#!/translator/translator_configure_create)

Receive push notifications from different social networks

- Method: GET
- Request Type: JSON
- Request example: Depends on the source
- Response Type: JSON
- Response example:

    ```
    {
        "detail": "string SOME_MESSAGE",
        "redirectURL": "URL_TO_REDIRECT_USER OPTIONAL"
    }
    ```