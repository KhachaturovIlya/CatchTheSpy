package app;

import app.core.navigation.NavigationManager;
import app.core.navigation.Screen;
import javafx.application.Application;
import javafx.stage.Stage;

public class App extends Application {
    @Override
    public void start(Stage stage) {
        NavigationManager navigation = new NavigationManager(stage);

        stage.setTitle("Catch the spy");
        stage.setMinWidth(480);
        stage.setMinHeight(320);

        stage.setMaximized(true);

        navigation.showInPrimary(Screen.START);
        stage.show();
    }
}