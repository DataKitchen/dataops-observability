# Observability UI

Made with ❤ from DataKitchen

## Start the project
- install dependencies `yarn`
- start the shell and the micro frontends `yarn start`
- run mocks server with `yarn mocks` on another terminal
- open the browser at http://localhost:4200

## Unit tests
To run all unit tests `yarn test:ci`

To run only affected unit tests `yarn test:affected`

Watch mode can only be used to watch a single app.
I.e.: `yarn test shell --watch`


### ADDING/UPDATING environment variable
- Either add/edit a variable with command line or web ui tool.
Push or pull changes to the server accordingly (please refer to dotenv-vault documentation for more)
- Build env file with the following `yarn de-v build`
- Commit changes to`env.vault` file


## Run Locally a dist build
> Especially useful when need to debug Service Worker issues.

Service Worker will not be installed when app is running in dev mode so in order to debug Service Worker related issues or to simply develop new functionalities at SW level it is beneficial to run the app with it active.

- run `yarn build --configuration=dev` to build the app against your desired env.
- run `yarn nx run shell:set-environment --environment=dev` to set the desired config
- (possibly in another shell) run `npx http-server dist/shell`
- open your browser at http://localhost:8080 or where specified from custom options passed to `http-server`

### See App Update in action
Running `http-server` in another shell will allow you to run subsequent builds while it is serving the app. If you change something in the code, run a build (as described above) the SW in browser will detect the new version and prompt for an update.

### Force an App Update
It may happen that the application update mechanism breaks in order to force an app update you need to:
- go the "Application" tab of the chrome dev tools
- select "Service Worker" on the left side pane
- click "Unregister" (to make the browser download the newest version the the SW definition on refresh)
- go to localhost:8080 and start again

It may also be beneficial to check "Update on reload" checkbox.

Please bear in mind that the SW will be installed on a per url basis _including_ the port. Which means that if you had you app running on port 8080 and then change in to another port that will force a new SW installation.


TBD
add instructions on how to add a component and a shared library.
