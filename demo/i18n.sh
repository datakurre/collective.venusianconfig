#!/bin/bash

i18ndude rebuild-pot --pot src/venusianconfigdemo/locales/venusianconfigdemo.pot --merge src/venusianconfigdemo/locales/manual.pot --create venusianconfigdemo src/venusianconfigdemo

i18ndude sync --pot src/venusianconfigdemo/locales/venusianconfigdemo.pot src/venusianconfigdemo/locales/*/LC_MESSAGES/venusianconfigdemo.po
