## Gtasks-Ha 2205 a Google Tasks Custom Component for Home Assistant
Forked from https://github.com/myntath/gtasks-ha
Working with Home Assistant 2024.4 and later.

You will probably also want to install the lovelace card to make best use of this. [lovelace-gtasks-card](https://github.com/myntath/lovelace-gtasks-card)

## Before installation
Create a create a credentials.json (type Desktop) from [Google API](https://console.developers.google.com/apis/credentials)

If you haven't done this before detailed instructions are below but you may be able to skip some of these steps if you have previously setup some Google API Authorisations
1. Go to [Google API](https://console.developers.google.com/apis/credentials)
2. Click '+ CREATE CREDENTIALS' (in blue near top of the screen) and select OAuth client ID
3. If you haven't created a project you will be given an option to do so, click that.
   - Give the project any name.
   - Location can be left as is.
5. If you haven't configured the consent screen before you will be asked to do that now.
   - Choose User Type External and then continue. (Internal may also be OK but is only available to Google Workspace users)
   - Enter any App Name you want.
   - Enter any User support email you want.
   - Enter any Developer email you want.
   - Leave other fields empty.
   - You do not need to enter any scopes. Just click SAVE AND CONTINUE
   - Add your google account as a test user then click SAVE AND CONTINUE.
   - After reaching the summary click 'back to dashboard'.
   - Click 'Publish App'.
   - Return to the credentials page and click '+ CREATE CREDENTIALS' again and select OAuth client ID.
6. Choose 'Desktop app' for the Application type and choose any name and press CREATE
7. In the popup click 'DOWNLOAD JSON' a file called 'client_secret_XXXXXXXXXXXXXXXXXXXXXXXXX.apps.googleusercontent.com.json' will be saved. Rename this 'credentials.json' or another name.
8. Click 'Enabled APIs & Services' in the left bar.
9. Search for 'Google tasks API' and select this result and click 'Enable'

## Installation

### Using HACS (Recommended)

1. Add this repo as a custom repository in HACS.
2. Install through HACS.
3. Restart HACS.
4. Upload your credentials.json file to a directory that HA can read. i.e. `./custom_components/gtasks/credentials.json`.
5. Restart Home Assistant.
6. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "GTasks".
7. Enter the path to your credentials.json file and a writable path for the component to store information.
8. Click the authorisation URL.
9. Authenticate and once you reach a 404 page not found look at the url and copy and paste the code between 'code=' and '&scope='.

### Manually

1. Open the directory for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory there, you need to create it.
3. In the `custom_components` directory create a new directory called `gtasks`.
4. Download _all_ the files from the `custom_components/gtasks/` directory in this repository.
5. Place the files you downloaded in the new directory you created.
6. Upload your credentials.json file to a directory that HA can read. i.e. `./custom_components/gtasks/credentials.json`.
7. Restart Home Assistant.
8. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "GTasks".
9. Enter the path to your credentials.json file and a writable path for the component to store information.
10. Click the authorisation URL.
11. Authenticate and once you reach a 404 page not found look at the url and copy and paste the code between 'code=' and '&scope='.

Using your HA configuration directory as a starting point you should now also have this:

```text
custom_components/gtasks/translations/en.json
custom_components/gtasks/__init__.py
custom_components/gtasks/binary_sensor.py
custom_components/gtasks/config_flow.py
custom_components/gtasks/const.py
custom_components/gtasks/manifest.json
custom_components/gtasks/sensor.py
```


## Tips

- If the Google refresh token is revoked or otherwise not working you may need to delete the component and setup again. This can happen if you change your password or through various other means. In addition make sure you delete the 'token.pickle' file which was created in your writable path.

- If the refresh token is being revoked every 7 days make sure that in Google OAuth you have set the publishing status of your Google OAuth consent screen to 'In production'.
If the status is still in testing then the token expires after 7 days.

- Your OAuth Client ID must be type 'Desktop'.

- When doing the google authorization you will be returned to a localhost page (page not found) look in the address to get the 'code' and
use the code to setup the integration. 
 
- If you have a service running on localhost you may need to temporarily halt it or else look at the request headers when you finish the google authorisation.

- If you need further help you can post in here or else at https://community.home-assistant.io/t/custom-component-google-tasks-revived/548380
