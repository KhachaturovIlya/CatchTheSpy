package app.ui.main;

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
        // Следующий экран подключим, когда он появится:
        // navigation.showInPrimary(Screen.NEXT);
    }

    @FXML
    private void onExit() {
        Platform.exit();
    }
}