#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# This file is part of pyAlienFX.
#
#    pyAlienFX is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyAlienFX is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyAlienFX.  If not, see <http://www.gnu.org/licenses/>.
#
#    This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#    To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter
#    to Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.
#


import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib
from gi.repository import Gtk as gtk

import pyAlienFX
from AlienFX.AlienFXConfiguration import *

PING_FREQUENCY = 10  # seconds

_BASE = os.path.dirname(os.path.abspath(__file__))


class pyAlienFX_Indicator:
    """The indicator class that takes care of creating the menu then loading it
    through the appindicator library on Ubuntu Unity. To do: Gnome!"""

    def __init__(self):
        """Init creation of the gtk.Menu and binding to the appindicator"""
        self.colormap = {
            "White": "FFFFFF",
            "Yellow": "FFFF00",
            "Purple": "FF00FF",
            "Cyan": "00FFFF",
            "Red": "FF0000",
            "Green": "00FF00",
            "Blue": "0000FF",
        }
        icon_off = os.path.join(_BASE, "images", "indicator_off.png")
        icon_on = os.path.join(_BASE, "images", "indicator_on.png")

        self.ind = appindicator.Indicator.new(
            "pyAlienFX",
            icon_off,
            appindicator.IndicatorCategory.APPLICATION_STATUS,
        )
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon(icon_on)

        self.gui = pyAlienFX.pyAlienFX_GUI()
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        """GTK creation of the menu items"""
        self.menu = gtk.Menu()

        self.light_on = gtk.MenuItem(label="Lights On")
        self.light_on.connect("activate", self.lights_on)

        self.light_off = gtk.MenuItem(label="Lights Off")
        self.light_off.connect("activate", self.lights_off)

        self.all_color_selection = gtk.MenuItem(label="Change All Lights")
        self.color_menu = gtk.Menu()
        for c in self.colormap.keys():
            item = gtk.MenuItem(label=c)
            item.connect("activate", self.on_AlienFX_Color_Clicked, c)
            self.color_menu.append(item)
        self.all_color_selection.set_submenu(self.color_menu)

        self.editor = gtk.MenuItem(label="Configuration Editor")
        self.editor.connect("activate", self.launch_editor)

        self.quit_item = gtk.MenuItem(label="Quit")
        self.quit_item.connect("activate", self.quit)

        self.menu.append(self.editor)
        self.menu.append(self.light_on)
        self.menu.append(self.light_off)
        self.menu.append(self.all_color_selection)
        self.menu.append(self.quit_item)
        self.menu.show_all()

    def launch_editor(self, widget):
        """Launch the configuration editor window!"""
        self.gui.main()

    def on_AlienFX_Color_Clicked(self, widget, c):
        """Apply a single colour profile to all zones."""
        self.configuration = AlienFXConfiguration()
        self.configuration.Create(
            "default",
            self.gui.computer.name,
            self.gui.selected_speed,
            "default.cfg",
        )
        for zone in self.gui.computer.regions.keys():
            self.configuration.Add(self.gui.computer.regions[zone])
            self.configuration.area[zone].append(
                self.gui.computer.default_mode,
                self.colormap[c],
                self.colormap[c],
            )
        self.gui.configuration = self.configuration
        self.gui.Set_Conf(Save=True)

    def lights_on(self, widget):
        print("Light on")
        if not self.gui.lights:
            print("Re-Activating Lights")
            print(self.gui.configuration)
            self.gui.Set_Conf(Save=False)
        self.gui.lights = True

    def lights_off(self, widget):
        print("Light off")
        if self.gui.lights:
            self.gui.controller.Reset(self.gui.computer.RESET_ALL_LIGHTS_OFF)
        self.gui.lights = False

    def main(self):
        self.check_daemon()
        GLib.timeout_add(PING_FREQUENCY * 1000, self.check_daemon)
        gtk.main()
        self.gui.controller.Bye()

    def check_daemon(self):
        print("Check Daemon")
        ping = self.gui.controller.Ping()
        if ping == True:
            self.ind.set_status(appindicator.IndicatorStatus.ATTENTION)
        else:
            self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)

    def quit(self, widget):
        try:
            self.gui.controller.Bye()
        except Exception:
            print("No daemon to kill")
        sys.exit(0)


if __name__ == "__main__":
    indicator = pyAlienFX_Indicator()
    indicator.main()
