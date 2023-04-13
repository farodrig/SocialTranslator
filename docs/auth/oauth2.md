# OAuth2

Open Authorization (OAuth) is an open standard for access delegation, commonly used as a way for Internet users 
to grant websites or applications access to their information on other websites but without giving them the passwords.

The system support access through this standard to the different api endpoints described in 
[Community](../api/community.md) and [Translator](../api/translator.md).
To be able to use it you must add the token given by the endpoints in the Authorization header with the 
format {Authorization: Bearer <your_token>}.

To apply the standard the library used was [django-oauth-toolkit](https://github.com/evonove/django-oauth-toolkit).

Access token have a 10 minutes lifetime.

Refresh token have a 1 day lifetime.


## Endpoints

#### /auth/oauth2/token/ (get Token)

Takes a set of user credentials and client credentials and returns an 
access and refresh token pair to prove the authentication of those 
credentials.

- Method: POST
- Authorization:
    - Type: Basic Auth
    - Username: Client ID
    - Password: Client Secret
- Request Type: JSON
- Request example:

    ```
    {
        "grant_type": "password",
        "username": "string",
        "password": "string"
    }
    ```
    
- Response Type: JSON
- Response example:

    ```
    {
        "access_token": "string",
        "refresh_token": "string",
        "token_type": "Bearer",
        "expires_in": int TIME_IN_MILISECONDS,
        "scope": "write read"
    }
    ```


#### /auth/oauth2/token/ (refresh Token)

Takes a set of client credentials and access/refresh token and returns an 
access and refresh token pair to prove the authentication of those 
credentials.

- Method: POST
- Authorization:
    - Type: Basic Auth
    - Username: Client ID
    - Password: Client Secret
- Request Type: JSON
- Request example:

    ```
    {
        "grant_type" : "refresh_token",
        "refresh_token" : "string"
    }
    ```
    
- Response Type: JSON
- Response example:

    ```
    {
        "access_token": "string",
        "refresh_token": "string",
        "token_type": "Bearer",
        "expires_in": int TIME_IN_MILISECONDS,
        "scope": "write read"
    }
    ```


#### /auth/oauth2/revoke_token/

Takes a set of client credentials and access/refresh token and revoke the 
given token.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
        "token" : "string",
        "client_id" : "string"
        "client_secret" : "string"    
    }
    ```
    
- Response Type: HTTP_CODE (200 if the token was revoked)