# Community API

This API is oriented for older adults apps, in order to allow old people to communicate with his communities
without needing to know how to use each one of the social networks.

To be able to use any of these endpoints you need first have a valid token provided by the authentication endpoints 
(either [JWT](../auth/jwt.md) or [OAuth2](../auth/oauth2.md))

The documentation for this API and his endpoints can be found [here](https://socialtranslator.dcc.uchile.cl/docs/#/community).

## Endpoints

#### [/community/configure/](https://socialtranslator.dcc.uchile.cl/docs/#!/community/community_configure_create)

Allow to configure a Social Network Translator for a specific user.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "user": "string",
      "social": "string",
      "auth_code": "string OPTIONAL"
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

#### [/community/sendMessage/](https://guarded-retreat-96811.herokuapp.com/docs/#!/community/community_sendMessage_create)



- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
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
    
    
#### [/community/check/networks/](https://socialtranslator.dcc.uchile.cl/docs/#!/community/community_check_networks_create)

Allow to check the social network status for a specific user.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "user": "string"
    }
    ```
    
- Response Type: JSON
- Response example:

    ```
    {
      "string SOCIAL_ID": {
        "detail": "string TEXT_MESSAGE",
        "code": 200 | 404
      },
      ...
    }
    ```


#### [/community/check/messages/](https://socialtranslator.dcc.uchile.cl/docs/#!/community/community_check_messages_create)

Allow to check for new messages to a specific user.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "user": "string"
    }
    ```
    
- Response Type: JSON
- Response example:

    ```
    {
        "news": boolean,
        "count": integer
    }
    ```

#### [/community/getMessages/](https://socialtranslator.dcc.uchile.cl/docs/#!/community/community_getMessages_create)

Allow to get new messages to a specific user.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "user": "string",
      "acks": [
        "string ID_MESSAGE_RECEIVED OPTIONAL"
      ]
    }
    ```
    
- Response Type: JSON
- Response example:

    ```
    [
      {
        "id": integer,
        "kind": "input | output",
        "ack": boolean,
        "content": "string TEXT_MESSAGE",
        "file": "string URL",
        "timestamp": "datetime",
        "fromUser": integer,
        "toUser": integer,
        "through": "string SOCIAL NETWORK"
      },
      ...
    ]
    ```
    
#### [/community/register/communication/](https://socialtranslator.dcc.uchile.cl/docs/#!/community/community_register_communication_create)

Allow to register an interaction between two users through a specific social network.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "fromUser": "string",
      "toUser": "string",
      "through": "string"
    }
    ```
    
- Response Type: JSON
- Response example:

    ```    
    {
        "detail": "string SOME_MESSAGE",
    }    
    ```