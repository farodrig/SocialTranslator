# JWT

JSON Web Token (JWT) is a JSON-based open standard for creating access tokens.

The system support access through this standard to the different api endpoints described in [Community](../api/community.md) and [Translator](../api/translator.md).
To be able to use it you must add the token given by the endpoints in the Authorization header with the format {Authorization: JWT <your_token>}.

To apply the standard the library used was [django-rest-framework-simplejwt](https://github.com/davesque/django-rest-framework-simplejwt).

Access token have a 5 minutes lifetime.

Refresh token have a 1 day lifetime.


## Endpoints

#### [/auth/jwt/token/](https://socialtranslator.dcc.uchile.cl/docs/#!/auth/auth_jwt_token_create)

Takes a set of user credentials and returns an access and refresh JSON web token pair to prove the authentication of those credentials.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "username": "string",
      "password": "string"
    }
    ```
    
- Response Type: JSON
- Response example:

    ```
    {
      "refresh": "string",
      "access": "string"
    }
    ```


#### [/auth/jwt/token/refresh/](https://socialtranslator.dcc.uchile.cl/docs/#!/auth/auth_jwt_token_refresh_create)

Takes a refresh type JSON web token and returns an access type JSON web token if the refresh token is valid.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "refresh": "string"
    }
    ```
    
- Response Type: JSON
- Response example:

    ```
    {
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmMGZiNmZhYWUxNGQ0Njk5ODFkNjMwYTNkNjM5ZmExMiIsImV4cCI6MTUxNjMxNjc4NSwidG9rZW5fdHlwZSI6ImFjY2VzcyIsInVzZXJfaWQiOjF9.WwMaxb7UthfK_chRynaEQhH5CffxZgQBXtcrgndhxuw"
    }
    ```


#### [/auth/jwt/token/verify/](https://socialtranslator.dcc.uchile.cl/docs/#!/auth/auth_jwt_token_verify_create)

Takes a token and indicates if it is valid. This view provides no information about a token's fitness for a particular use.

- Method: POST
- Request Type: JSON
- Request example:

    ```
    {
      "token": "string"
    }
    ```
    
- Response Type: HTTP_CODE (200 if the token is valid)