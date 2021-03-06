Converting a Chrome App into a Progressive Web App with Caterpillar
===================================================================

This document describes how to convert your Chrome App into a progressive web
app which can run on the open web, using
[Caterpillar](https://github.com/chromium/caterpillar).

Caterpillar will help you convert your Chrome App into a progressive web app by
inserting JavaScript to substitute Chrome Apps APIs you might be using, and will
then generate a report telling you how well the automatic conversion went. If
your Chrome App wasn't completely converted automatically, the report will help
you finish the conversion.

## Usage Summary

```bash
./caterpillar.py config -i config.json
./caterpillar.py convert -c config.json my-chrome-app/ my-web-app/
```

This will convert an unpackaged Chrome App `my-chrome-app/` into a progressive
web app `my-web-app/` and generate a conversion report inside a subdirectory of
`my-web-app/` (depending on the configuration options you set).

## Installing Caterpillar

Clone it from the repository:

```bash
git clone https://github.com/chromium/caterpillar.git caterpillar
cd caterpillar
```

## Generating a configuration file
Caterpillar needs a JSON configuration file, and includes a tool to help you
generate one. To interactively generate a config file run:

```bash
./caterpillar.py config -i config.json
```

Caterpillar will prompt you to enter information about your Chrome App. If you
hit enter without typing anything, the default value (displayed in parentheses)
will be used. If you would rather just generate a config file with all the
default values, omit the `-i` flag.

There are three values you need to specify in the config file. These are:

- `start_url` &mdash; This is the relative URL of the home page of your Chrome
  App, usually whatever page launches when you open your Chrome App, e.g.
  index.html. This will be used as the home page of your website.
  app once it has been converted.
- `boilerplate_dir` &mdash; Subdirectory of your output web app where
  Caterpillar should store its own files in.
  to reference the root.
- `report_dir` &mdash; Subdirectory of your output web app where Caterpillar
  should output the conversion report.

## Running Caterpillar on your Chrome App
Say your Chrome App is called "My Chrome App" and is located in "~/my-chrome-
app", and you want to convert it into a web app stored in the folder "~/my-web-
app". Run Caterpillar:

```bash
./caterpillar.py convert -c config.json ~/my-chrome-app ~/my-web-app
```

Caterpillar will try to convert your Chrome App into a web app. It will also
output warnings if it finds something it can't convert. Finally, it will also
put a conversion report into a subdirectory of "~/my-web-app", with the
subdirectory name given in the config file.

## Conversion Report

The conversion report is an HTML document generated by Caterpillar during the
automatic conversion. It has four main sections:

- Summary
- General Warnings
- Polyfilled Chrome Apps APIs
- Missing Chrome Apps APIs

Throughout the report, the words "total", "partial", and "none" may be used to
describe how well some facet of your app was converted.

- "total" doesn't necessarily mean that everything will completely work.
  Instead, it means that we expect the Chrome Apps features used in your
  application to work well enough that your application remains usable.
- "partial" means up to two things:
    - There are some Chrome Apps features used by your app which haven't been
      automatically converted. You might be able to convert them manually.
    - There are some features used by your app that work in limited
      circumstances.
- "none" means that no conversion was attempted, or an error occurred.

### Summary

The summary section of the report gives a brief overview of how the conversion
went. This includes an indicator of whether your app was totally, partially, or
not converted, whether there were any warnings, and whether the Chrome Apps APIs
your app uses were filled in with open web equivalents.

### General Warnings

The general warnings section contains a list of all warnings generated by
Caterpillar while converting. These are generally things that failed to convert
or were skipped for some reason during conversion.

#### Possible warnings

Following is a non-exhaustive list of warnings that might be generated by
Caterpillar.

- "Failed to install dependency \`name\` with manager". A JavaScript dependency
  for your app failed to install automatically using the given dependency
  manager (e.g. npm or bower). You may need to install the listed dependency
  yourself.
- "Could not polyfill Chrome APIs: APIs". The listed Chrome Apps APIs couldn't
  be automatically substituted with open web equivalents. You may need to edit
  your app's code to not use the listed API.
- "Chrome Apps must have manifest version 2." The input app's manifest doesn't
  have manifest version 2, which is required for valid Chrome Apps. The input is
  either not a valid Chrome App or not a Chrome App at all.
- "Chrome Apps must include a name." The input app's manifest doesn't include
  the app's name. The input is either not a valid Chrome App or not a Chrome App
  at all.
- "Chrome Apps must include a version." The input app's manifest doesn't include
  the app's version. The input is either not a valid Chrome App or not a Chrome
  App at all.
- "Manifest member \`name\` will not be converted." A property in the manifest
  of your app has no open web equivalent, so Caterpillar has ignored it. This
  may break the output app if something important is ignored, so you should
  check that the skipped property is not important.
- "Configuration file \`file\` missing options: options". The config file given
  to Caterpillar is missing options that were meant to be included. You should
  add the missing options to the config file.
- "Configuration file \`file\` has unexpected options: options". The config file
  given to Caterpillar has options that weren't meant to be included. You should
  remove the extra options.

<!-- TODO(alger): Add the remaining sections.
### Polyfilled Chrome Apps APIs
### Missing Chrome Apps APIs -->
