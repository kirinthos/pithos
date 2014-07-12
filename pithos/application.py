#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: nil; -*-
### BEGIN LICENSE
# Copyright (C) 2010-2012 Kevin Mehall <km@kevinmehall.net>
#This program is free software: you can redistribute it and/or modify it
#under the terms of the GNU General Public License version 3, as published
#by the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranties of
#MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
#PURPOSE.  See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import sys
import logging
import argparse
from gi.repository import Gtk, Gio, GLib

from .pithosconfig import get_ui_file, get_media_file, VERSION
from .pithos import PithosWindow
from .plugin import load_plugins
from . import settings

class PithosApplication(Gtk.Application):
    def __init__(self):
        # Use org.gnome to avoid conflict with existing dbus interface net.kevinmehall
        Gtk.Application.__init__(self, application_id='org.gnome.pithos',
                                flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.window = None
        self.stations = None
        self.prefs = None
        self.options = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # Setup appmenu
        builder = Gtk.Builder()
        builder.add_from_file(get_ui_file('menu'))
        menu = builder.get_object("app-menu")
        self.set_app_menu(menu)

        action = Gio.SimpleAction.new("stations", None)
        action.connect("activate", self.stations_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("preferences", None)
        action.connect("activate", self.prefs_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.about_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.quit_cb)
        self.add_action(action)

    # FIXME: do_local_command_line() segfaults?
    def do_command_line(self, args):
        Gtk.Application.do_command_line(self, args)

        parser = argparse.ArgumentParser()
        parser.add_argument("-v", "--verbose", action="count", default=0, dest="verbose", help="Show debug messages")
        parser.add_argument("-t", "--test", action="store_true", dest="test", help="Use a mock web interface instead of connecting to the real Pandora server")
        self.options = parser.parse_args(args.get_arguments()[1:])

        # First, get rid of existing logging handlers due to call in header as per
        # http://stackoverflow.com/questions/1943747/python-logging-before-you-run-logging-basicconfig
        logging.root.handlers = []

        #set the logging level to show debug messages
        if self.options.verbose > 1:
            log_level = logging.DEBUG
        elif self.options.verbose == 1:
            log_level = logging.INFO
        else:
            log_level = logging.WARN

        logging.basicConfig(level=log_level, format='%(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s')

        self.do_activate()

        return 0

    def do_activate(self):
        prefs = settings.load_preferences()

        have_login = False
        if prefs['username'] and prefs['password']:
            have_login = True
        
        if not self.window:
            logging.info("Pithos %s" %VERSION)
            
            builder = Gtk.Builder()
            builder.add_from_file(get_ui_file('main'))

            self.window = builder.get_object("pithos_window")
            self.window.set_application(self)
            self.window.finish_initializing(builder, self.options, have_login, self)

        if not have_login:
            self.prefs_cb(is_startup=True)
        else:
            self.window.present()

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)
        self.quit()

    def stations_cb(self, action, param):
        if not self.stations:
            builder = Gtk.Builder()
            builder.add_from_file(get_ui_file('stations'))    
            
            self.stations = builder.get_object("stations_dialog")
            self.stations.finish_initializing(builder, self.window)
            self.stations.set_transient_for(self.window)
            self.stations.show_all()
        
        self.stations.present()

    def prefs_cb(self, *ignore, is_startup=False):
        if not self.prefs:
            builder = Gtk.Builder()
            builder.add_from_file(get_ui_file('preferences'))

            self.prefs = builder.get_object("preferences_pithos_dialog")
            self.prefs.finish_initializing(builder, is_startup)
            self.prefs.set_transient_for(self.window)
            self.prefs.connect('response', self.prefs_response_cb)
            self.prefs.connect('close', self.prefs_close_cb, is_startup)             
            self.prefs.show()

        self.prefs.present()

    def prefs_response_cb(self, dialog, response):
        if not self.window.pandora:
            self.window.init_connection()

        if response == Gtk.ResponseType.OK:
            self.window.reload_preferences()

        self.prefs = None
        dialog.destroy()
        self.window.present()
    
    def prefs_close_cb(self, dialog, is_startup):
        if is_startup:
            self.quit()

    def about_cb(self, action, param):
        builder = Gtk.Builder()
        builder.add_from_file(get_ui_file('about'))

        about = builder.get_object("about_pithos_dialog")
        about.finish_initializing(builder)
        about.set_transient_for(self.window)
        about.set_version(VERSION)
        about.present()

    def quit_cb(self, action, param):
        self.quit()

def main():
    app = PithosApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == '__main__':
    main()