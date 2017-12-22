/*
 * View model for OctoPrint-DisasterManager
 *
 * Author: Wojciech Koprowski
 * License: AGPLv3
 */
$(function() {
    function DisastermanagerViewModel(parameters) {
        var self = this;
        
        self.settings = parameters[0];

        // this will hold the URL currently displayed by the iframe
        self.currentThreshold = ko.observable();

        // this will hold the URL entered in the text field
        self.newThreshold = ko.observable();

        // this will be called when the user clicks the "Go" button and set the iframe's URL to
        // the entered URL
        self.setThreshold = function() {
            self.currentThreshold(self.newThreshold());
        };

        // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its
        // dependencies have already been initialized. It is especially guaranteed that this method
        // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
        // the SettingsViewModel been properly populated.
        self.onBeforeBinding = function() {
            self.newThreshold(self.settings.settings.plugins.disastermanager.threshold());
            self.setThreshold();
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: DisastermanagerViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "settingsViewModel" ],
        // Elements to bind to, e.g. #settings_plugin_disastermanager, #tab_plugin_disastermanager, ...
        elements: [ "#tab_plugin_disastermanager" ]
    });
});
