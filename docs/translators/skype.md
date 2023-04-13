# SkypeTranslator

## Configuration

In the configuration process for this translator 
(which can be reached using the configure endpoint in [Community](../api/community.md) or [Translator](../api/translator.md)), 
the "auth_code" field in the request must contain the password used to login in skype.

The access token given by this process'll be valid for 24 hours. 
After this time, the configuration process must be done again (with the user password).