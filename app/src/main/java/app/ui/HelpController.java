package app.ui;

import app.core.navigation.NavigationManager;
import app.core.navigation.Screen;
import javafx.fxml.FXML;

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
