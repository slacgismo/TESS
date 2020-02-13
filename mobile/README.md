## Required Software

Install the following prescribed versions. You can _possibly_ have a more-recent version of these, however, these are the versions we know are currently working.

app             | version | install notes |
----------------| -------:| ------------- |
node            | 8.12.0  | Install using _one of_: <br />1. **NVM**: [Node Version Manager (nvm)](https://github.com/creationix/nvm) and explicitly install node8 the same way we do it in production: `nvm install 8` - **_check which version we are running_** with `cat ~/mobile/.nvmrc`. You can set node8 as the default with `nvm use 8.12`<br />2. **BREW**:  `brew install node@8.12.0` or `brew install node` (this will install the latest version, which might not work) * |
yarn             | 1.17.3   | Use Homebrew via `brew install yarn`, or `brew upgrade yarn` if you already have it installed |
watchman        | 4.9.0   | `brew install watchman`|
react-native-cli| 2.0.1   | `yarn global add react-native-cli` |
Xcode           | 11.1    | [Apple App Store](https://itunes.apple.com/us/app/xcode/id497799835) |
Android Studio  | 3.5     | [React Native Android Studio Walkthrough](https://facebook.github.io/react-native/docs/getting-started.html#2-install-the-android-sdk) |
Java JDK     | 8+    | [JDK - 8](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) |
cocoapods | 1.8.3+ | https://guides.cocoapods.org/using/getting-started.html

## Running the project

Get into the project
```bash
cd tess
```

Install the needed dependencies:
```bash
yarn install
cd ios
pod install
```

(You may need to open a new shell to ensure that the newly installed software is your environment PATH.)

Run instructions for iOS (assuming you are on the root dir of the repo):
```bash
cd SlacGismo/TESS/mobile/tess && npx react-native run-ios
```    

or:

- Open `tess/ios/tess.xcworkspace` in Xcode or run `xed -b ios`
- Hit the Run button

If you get an error regarding `simctl` not being found, check out https://stackoverflow.com/questions/29108172/xcrun-unable-to-find-simctl for some ideas on how to fix it. Most like `Xcode->Preferences->Locations` needs to have `Command line tools` set.

Run instructions for Android:
```bash
# Have an Android emulator running (quickest way to get started), or a device connected.
cd SlacGismo/TESS/mobile/tess && npx react-native run-android
```
