# Overview
Tool to upload ipa files to TestFlight.\
(It's mostly just a wrapper for `fastline pilot upload` but with some nice helper thingies)

This was/is built with Unity Cloud Build in mind so it works smoothly with that.\
Of course it is simple to run locally or in some other build system.

Please ignore all the TODOS. I will get there soon I promise xo

TODO:
* Add license to project and files
* allow env to be overridden by command line args
* Auto increase build number
* figure out how python modules/packages/paths work\
(currently using `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` in a few places)
* Try authenticate without key file
* if above doesn't work: delete old key file. maybe even add a warning if it already exists?
* add some way to specify what version of this tool to use
* UPM?

# Quick Start
1. Create API key ([See: Creating Your API Key](#creating-your-api-key))
2. Set parameters/environment variables (See: [passing variables](#passing-variables) and [variables docs](#variables))
3. Run `bash upload_to_testflight.sh` ([See: Running](#running))

# Running
Simply call
```
$ bash upload_to_testflight.sh
```

# Variables
These can be passed either as command line arguments or as environment variables.\
CLI arguments override environment variables if both exist.

| CLI Name | ENV Name | Type | Required (Default) | Description |
|-|-|-|-|-|
| `--api-key-issuer-id` | `API_KEY_ISSUER_ID` | `string` | ✅ | Identifies the issuer who created the authentication token.<br>Look for "*Issuer ID*" on [the page you made the API key on](https://appstoreconnect.apple.com/access/integrations/api).
| `--api-key-id`| `API_KEY_ID` | `string` | ✅ | Look for "*Key ID*" on your key in [the page you made the API key on](https://appstoreconnect.apple.com/access/integrations/api).
| `--api-key-content`| `API_KEY_CONTENT` | `string` | ✅ |  The raw text contents of your API key.<br>Downloaded from [the page you made the API key on](https://appstoreconnect.apple.com/access/integrations/api).
| `--output-directory`| `OUTPUT_DIRECTORY`| `path`/`string` | ✅ | The folder containing the output file.<br>**(Unity Cloud Build automatically sets this)**
| `--changelog`| `CHANGELOG` | `string` | ✅ | Release notes text for this TestFlight upload.<br>Passed to Fastlane as the `changelog` value.
| `--groups`| `GROUPS` | `string` | ❌ | Who the build is sent to. Even when empty, it is still available to internal testers.<br>See Fastlane `groups` parameter: https://docs.fastlane.tools/actions/upload_to_testflight/#parameters
| `--max-upload-attempts`| `MAX_UPLOAD_ATTEMPTS` | `int` | ❌ (10) | Maximum times to retry the upload.<br>(Occasionally fastlane fails for no reason. The only way around is to retry. If you're curious check this out: https://github.com/fastlane/fastlane/issues/21535)
| `--attempt-timeout` | `ATTEMPT_TIMEOUT` | `float` | ❌ (300) | Max time each individual upload attempt can run for **in seconds** (so default is 5 minutes).

# Passing Environment Variables
## Locally (.env file)
Put your variables in a .env file in your project root.\
(But DON'T COMMIT IT to version control. It's going to contain sensitive information.)

See [example.env](example.env)

## Unity Cloud Build (Environment Variables)
Go to your configuration > Advanced Settings and scroll down until you see the "Environment variables" section.

Important: Some of the required variables are automatically set by UCB.

## Command Line Arguments (TODO)
Alternatively, everything can be passed as arguements to the run script.

TODO: Implement this. No functionality for it exists yet.


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
