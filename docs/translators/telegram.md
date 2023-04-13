# TelegramTranslator

## Configuration

In the configuration process for this translator 
(which can be reached using the configure endpoint in [Community](../api/community.md) or [Translator](../api/translator.md)), 
the first request mustn't have the field "auth_code".

After completing this first request, telegram'll send a authorization code to the user's telegram app.

This code must be used in the field "auth_code" in a second request to the configuration endpoint.

Telegram'll provide an access token for that user, which has an indeterminate duration.