This is designed for Unity Cloud Build but can be run locally too. Hell, without a lot of work it could be used for non Unity projects.

To run in UCB, all you need to do is get the API key and pass it to the upload script.\
Keep reading to find out how.

TODO:
* allow env to be overridden by command line args
* Auto increase build number
* figure out how python modules/packages/paths work\
(currently using `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` in a few places)
* Delete old key file. maybe even add a warning if it already exists?

# Quick Start 
Simply call
```
$ bash upload_to_testflight.sh
```
# Required Environment Variables
Put these all in a .env file in your project root but DON'T COMMIT IT to version control. It's going to contain sensitive information.\
See [example.env](example.env) (TODO update this)

(For Unity Cloud Build, go to your configuration > Advanced Settings and scroll down)

## API Key
The following variables all relate to your App Store Connect API Key.\
[See the following section on creating it](#creating-your-api-key)

| Variable | Type | Required | Default | Description |
|-|-|-|-|-|
| `APP_STORE_CONNECT_API_KEY_ISSUER_ID` | `string` | Yes | - | Identifies the issuer who created the authentication token.<br>Look for "*Issuer ID*" on [the page you made the API key on](https://appstoreconnect.apple.com/access/integrations/api).
| `APP_STORE_CONNECT_API_KEY_KEY_ID` | `string` | Yes | - | Look for "*Key ID*" on your key in [the page you made the API key on](https://appstoreconnect.apple.com/access/integrations/api).
| `APP_STORE_CONNECT_API_KEY_ALL_CONTENT` | `string` | Yes | - | The raw text contents of your API key.<br>Downloaded from [the page you made the API key on](https://appstoreconnect.apple.com/access/integrations/api).

## Other 

| Variable | Type | Required | Default | Description |
|-|-|-|-|-|
| `OUTPUT_DIRECTORY`| `path`/`string` | Yes | - | The folder containing the output file.<br>(Unity Cloud Build automatically sets this)
| `GROUPS` | `string` | No | - | Who the build is sent to. Even when empty, it is still available to internal testers.<br>See Fastlane `groups` parameter: https://docs.fastlane.tools/actions/upload_to_testflight/#parameters
| `MAX_UPLOAD_ATTEMPTS` | `int` | No | 10 | Maximum times to retry the upload.<br>(Occasionally fastlane fails for no reason. The only way around is to retry. If you're curious check this out: https://github.com/fastlane/fastlane/issues/21535)
| `TIMEOUT_PER_ATTEMPT` | `float` | No | 300 | Max time each individual upload attempt can run for **in seconds** (so default is 5 minutes).

# Creating Your API Key 
This is how the upload script is able authenticate with App Store Connect.

Create here: https://appstoreconnect.apple.com/access/integrations/api\
Bonus points if you check out the docs: https://developer.apple.com/documentation/appstoreconnectapi/creating-api-keys-for-app-store-connect-api

Once you've created and downloaded it (it's a .p8). Save it somewhere secure. This is sensitive.\
If you open it in a text editor, it should look like this.
```
-----BEGIN PRIVATE KEY-----
Accordingtoallknownlawsofaviationthereisnowayabeeshouldbeabletof
lyItswingsaretoosmalltogetitsfatlittlebodyoffthegroundThebeeofco
ursefliesanywaybecausebeesdontcarewhathumansthinkisimpossibleYel
lowblack
-----END PRIVATE KEY-----