# WhatsappTranslator

## Configuration

In the configuration process for this translator 
(which can be reached using the configure endpoint in [Community](../api/community.md) or [Translator](../api/translator.md)), 
a "redirectURL" field will be received in the response's JSON.

This field contains a URL where a QR image for whatsapp web login will 
be found.
This QR image must be scan using the user's Whatsapp application.

After scanning it, you can try to configure the social network again and a 
successful message must be returned.