# This is the Core library for the Observability UI project

 This library will contain all code: services, pipes, abstract classes, etc... etc...; that is share between the shell app and the mfe(s).

## How to use

The main module of this app is already imported in the `app.module.ts` of the shell application. That is all is needed in order to have the rest of the code shared between all the mfe(s).
> `CoreModule` and `CONFIG_TOKEN` **must not** be declared again in any mfe module!

## ConfigService and environment files
This library provide a `ConfigService` that is meant to be used in place of the `environment.ts` files. This way we can initialize the service using the `environment.ts` file that is provided by the shell app and use it across all the mfe(s).
This is done through the `CONFIG_TOKEN` reference in `app.module.ts` of the shell app.

An `AppConfiguration` interface is used to have a typed access to the fields in `environment.ts` using the `get` method in `ConfigService`.

### Add a new config field in the App
In order to add a new config field in the environment files.
- add the field and it's type in `libs/core/src/lib/config/app-configuration.ts`
- make sure that all environment files have the same field defined
- access it across the app only using `configService.get(fieldName)`

> Please note that the other environment files are still in use only to determine whether the app needs to run/build in with the production flag on or off.
