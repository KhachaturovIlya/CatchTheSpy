package app.ui.main;

import app.core.navigation.NavigationManager;
import app.core.navigation.Screen;
import javafx.fxml.FXML;
import javafx.stage.Stage;

public class HelpController {
    private final NavigationManager navigation;

    public HelpController(NavigationManager navigation) {
        this.navigation = navigation;
    }

    @FXML
    private void onClose() {
        navigation.closeWindow(Screen.HELP);
    }
}
