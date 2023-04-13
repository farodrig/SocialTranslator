# GmailTranslator

## Configuration

In the configuration process for this translator 
(which can be reached using the configure endpoint in 
[Community](../api/community.md) or [Translator](../api/translator.md)), 
a "redirectURL" field will be received in the response's JSON.

This field contains a URL that must be used to redirect the user to Google to authorize the application to read and 
send messages through Gmail.
Internally, Google'll send a push notification to the server to give an access token to Gmail's API.