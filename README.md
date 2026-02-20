# Overview
Tool to upload `.ipa` files to TestFlight.\
(This package is now mostly a Unity Cloud Build adapter around `pyliot`.)

This package is built with Unity Cloud Build in mind so it works smoothly there, but it is also easy to run locally or in other CI systems.

# Requirements
* Python 3
* git
* fastlane (`pilot`)
* network access during install (to fetch `pyliot` from GitHub)

# Running In Unity Cloud Build
1. Create API key ([See: Creating Your API Key](#creating-your-api-key))
2. Put this package somewhere in your project.
3. Set environment variables in UCB (See: [passing variables](#passing-variables) and [variables docs](#variables))
3. Add `upload_to_testflight.sh` as a post build script in UCB.

# Running Locally
Similar to above, but:
* You have to run archive in xcode to create the `.ipa` file (UCB does this for you).
* You have to call the `upload_to_testflight.sh` script yourself after archiving.
* Variables are passed environment variables. (See below)

Put envionment variables in a `.env` file at project root.

Your `.env` file must contain:
* All required variables
* `OUTPUT_DIRECTORY` which points to the folder that your `.ipa` is stored in
 must also contain all the required variables and 

See [example.env](example.env)

(yes you could pass them some other way - maybe via bash wrapper? Who knows? The world is your oyster.)

# Variables

| Variable | Type | Required (Default) | Description |
|-|-|-|-|
| `APP_STORE_CONNECT_API_KEY_ISSUER_ID` | `string` | ✅ | Identifies the issuer who created the authentication token.<br>Look for "Issuer ID" on [the App Store Connect API page](https://appstoreconnect.apple.com/access/integrations/api). |
| `APP_STORE_CONNECT_API_KEY_ID` | `string` | ✅ | Look for "Key ID" on your key in [the App Store Connect API page](https://appstoreconnect.apple.com/access/integrations/api). |
| `APP_STORE_CONNECT_API_KEY_CONTENT` | `string` | ✅ | The raw text contents of your API key (`.p8` contents). |
| `CHANGELOG_PATH` | `Path` | ✅ | Path to the file containing release notes for the build. |
| `GROUPS` | `comma-separated string` | ❌ | Tester groups to distribute to (`groupA,groupB`). If empty, build still goes to internal testers. |
| `MAX_UPLOAD_ATTEMPTS` | `int` | ❌ (10) | Maximum retry attempts for upload. |
| `ATTEMPT_TIMEOUT` | `int` | ❌ (600) | Max time each upload attempt can run in seconds. |

# Creating Your API Key
This is how the upload script authenticates with App Store Connect.

Create here: https://appstoreconnect.apple.com/access/integrations/api\
Apple docs: https://developer.apple.com/documentation/appstoreconnectapi/creating-api-keys-for-app-store-connect-api

Once you've created and downloaded it (`.p8`), store it securely.
If you open it in a text editor, it should look like this:
```text
-----BEGIN PRIVATE KEY-----
<key-content>
-----END PRIVATE KEY-----
```
