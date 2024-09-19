#!/bin/sh

brew install mysql-client pkg-config
$ export PKG_CONFIG_PATH="$(brew --prefix)/opt/mysql-client/lib/pkgconfig"
pip3 install ultraimport urllib3 selenium==4.24.0 pandas mysqlclient==2.0.0 python-dotenv pyramid_chameleon