package app.ui;

import app.core.navigation.NavigationManager;
import app.core.navigation.Screen;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.stage.StageStyle;

public class StartController {
    private final NavigationManager navigation;

    public StartController(NavigationManager navigation) {
        this.navigation = navigation;
    }

    @FXML
    private void onHelp() {
        navigation.openWindow(Screen.HELP, "Help", StageStyle.TRANSPARENT);
    }

    @FXML
    private void onStart() {
        navigation.showInPrimary(Screen.SCAN);
    }

    @FXML
    private void onExit() {
        Platform.exit();
    }
}