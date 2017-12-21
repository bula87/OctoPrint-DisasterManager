# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class disaster_manager(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin):
    def on_after_startup(self):
        self._logger.info("Disaster!")

__plugin_name__ = "Disaster Manager"
__plugin_implementation__ = disaster_manager()
