## Gtasks-Ha a Google Tasks Custom Component for Home Assistant
Forked from original repo by [@BlueBlueBlob](https://github.com/blueblueblob)

You will probably also want to install the lovelace card to make best use of this. [lovelace-gtasks-card](https://github.com/myntath/lovelace-gtasks-card)

## Before installation
Create a create a credentials.json (type Desktop) from [Google API](https://console.developers.google.com/apis/credentials)

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

- If the Google refresh token is revoked or otherwise not working you may need to delete the component and setup again. This can happen if you change your password or through various other means.

- If the refresh token is being revoked every 7 days make sure that in Google OAuth you have set the publishing status of your Google OAuth consent screen to 'In production'.
If the statis is still in testing then the token expires after 7 days.

- Your OAuth Client ID must be type 'Desktop'.

- When doing the google authorization you will be returned to a localhost page (page not found) look in the address to get the 'code' and
use the code to setup the integration. 
 
- If you have a service running on localhost you may need to temporarily halt it or else look at the request headers when you finish the google authorisation.

- If you need further help you can post in here or else at https://community.home-assistant.io/t/custom-component-google-tasks-abandoned/141985/95
