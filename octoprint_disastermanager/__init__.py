# coding=utf-8
from __future__ import absolute_import

__author__ = "Wojciech Koprowski <koprowski.wojciech@gmail.com> based on work by Sven Lohrmann <malnvenshorn@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2017 Wojciech Koprowski - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.settings import valid_boolean_trues
from octoprint.events import Events

from .filamentCounter import filamentCounter

class disaster_manager(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.EventHandlerPlugin):

    def __init__(self):
        self.filamentCounter_ = None
        self.lastPrintState_ = None
        self.filamentCounterEnabled_ = False
        self.pauseEnabled_ = False

    def on_after_startup(self):
        self._logger.info("Disaster!")

    def initialize(self):
        self.filamentCounter_ = filamentCounter()
        self.filamentCounter_.set_g90_extruder(self._settings.getBoolean(["feature", "g90InfluencesExtruder"]))

    def get_settings_defaults(self):
        return dict(enableFilamentCounter=True)

    def on_settings_save(self, data):
        self.filamentCounter_.set_g90_extruder(self._settings.getBoolean(["feature", "g90InfluencesExtruder"]))

########### EVENTS


    def on_event(self, event, payload):
        if event == Events.PRINTER_STATE_CHANGED:
            self.on_printer_state_changed(payload)

    def on_printer_state_changed(self, payload):
        if payload['state_id'] == "PRINTING":
            if self.lastPrintState == "PAUSED":
                # resuming print from pause state
                self.filamentCounter_.reset_extruded_length()
            else:
                # starting new print
                self.filamentCounter_.reset()
            
            self.filamentCounterEnabled_ = self._settings.getBoolean(["enableFilamentCounter"])
            self._logger.debug("Printer State: %s" % payload["state_string"])
            self._logger.debug("Odometer: %s" % ("On" if self.filamentCounterEnabled_ else "Off"))

        elif self.lastPrintState == "PRINTING":
            # print state changed from printing to something else => update filament usage
            self._logger.debug("Printer State: %s" % payload["state_string"])
            if self.filamentCounterEnabled_:
                self.filamentCounterEnabled_ = False  # disabled because we don't want to track manual extrusion

        # update last print state
        self.lastPrintState = payload['state_id']

    def checkFilamentMovement(self):
        printer_profile = self._printer_profile_manager.get_current_or_default()
        extrusionFromGcode = self.filamentCounter_.get_extrusion_gcode()
        extrusionFromSensor = self.filamentCounter_.get_extrusion_sensor()
        numTools = min(printer_profile['extruder']['count'], len(extrusion))
        currentTool = filamentCounter_.get_current_tool();

        for tool in xrange(0, numTools):
            self._logger.info("Filament used based on Gcode: {length} mm (tool{id})"
                              .format(length=str(extrusionFromGcode[tool]), id=str(tool)))

            self._logger.info("Filament used based on sensor: {length} mm (tool{id})"
                              .format(length=str(extrusionFromSensor[tool]), id=str(tool)))
            
        return (extrusionFromGcode[currentTool]-extrusionFromSensor[currentTool] > 10)

    # Protocol hook
    def filament_counter(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if self.filamentCounterEnabled_:
            self.filamentCounter_.parse(gcode, cmd)
            if self.pauseEnabled_ and not self.checkFilamentMovement():
                self._logger.info("Filament stuck, pausing print")
                self._printer.pause_print()

    # Check plugin version -> update if needed
    def get_version_info(self):
        return dict(
            disastermanager=dict(
                displayName="Disaster Manager",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="bula87",
                repo="OctoPrint-DisasterManager",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/bula87/OctoPrint-DisasterManager/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "Disaster Manager"
__plugin_implementation__ = disaster_manager()

__plugin_hooks__ = { "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_version_info,
                     "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.filament_counter }

