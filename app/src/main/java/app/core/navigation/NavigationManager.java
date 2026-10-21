package app.core.navigation;

import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.input.MouseEvent;
import javafx.stage.Modality;
import javafx.stage.Stage;

import java.io.IOException;
import java.net.URL;
import java.util.EnumMap;
import java.util.Map;

import javafx.scene.paint.Color;
import javafx.stage.StageStyle;

public class NavigationManager {
    private static final String THEME = "/app/css/theme.css";

    private final Map<Screen, Stage> openWindows = new EnumMap<>(Screen.class);
    private final Stage primaryStage;
    private final ScalingPane primaryRoot = new ScalingPane();

    public NavigationManager(Stage primaryStage) {
        this.primaryStage = primaryStage;
    }

    public void showInPrimary(Screen screen) {
        showInPrimary(screen, null);
    }

    public void showInPrimary(Screen screen, Object data) {
        primaryRoot.setContent(load(screen, data));
        if (primaryStage.getScene() == null) {
            Scene scene = new Scene(primaryRoot, 640, 400);
            scene.getStylesheets().add(resource(THEME).toExternalForm());
            primaryStage.setScene(scene);
        }
    }

    public Stage openWindow(Screen screen, String title) {
        return openWindow(screen, title, StageStyle.DECORATED);
    }

    public Stage openWindow(Screen screen, String title, StageStyle style) {
        Stage existing = openWindows.get(screen);
        if (existing != null) {
            existing.toFront();
            return existing;
        }

        Scene scene = new Scene(load(screen));
        scene.getStylesheets().add(resource(THEME).toExternalForm());

        Stage stage = new Stage(style);

        if (style == StageStyle.TRANSPARENT) {
            scene.setFill(Color.TRANSPARENT);
            makeDraggable(scene, stage);
        }

        stage.initOwner(primaryStage);
        stage.initModality(Modality.WINDOW_MODAL);
        stage.setTitle(title);
        stage.setScene(scene);
        stage.setResizable(false);
        stage.setOnHidden(e -> openWindows.remove(screen));
        openWindows.put(screen, stage);

        stage.show();
        return stage;
    }

    public void closeWindow(Screen screen) {
        Stage stage = openWindows.get(screen);
        if (stage != null) stage.close();
    }

    private Parent load(Screen screen) {
        return load(screen, null);
    }

    @SuppressWarnings("unchecked")
    private Parent load(Screen screen, Object data) {
        FXMLLoader loader = new FXMLLoader(resource(screen.fxml()));
        loader.setControllerFactory(this::createController);
        try {
            Parent root = loader.load();
            if (data != null && loader.getController() instanceof ScreenParameter<?> receiver) {
                ((ScreenParameter<Object>) receiver).onShow(data);
            }
            return root;
        } catch (IOException e) {
            throw new IllegalStateException("Cannot load " + screen.fxml(), e);
        }
    }

    private Object createController(Class<?> type) {
        try {
            try {
                return type.getConstructor(NavigationManager.class).newInstance(this);
            } catch (NoSuchMethodException e) {
                return type.getConstructor().newInstance();
            }
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException("Cannot create controller " + type.getName(), e);
        }
    }

    private void makeDraggable(Scene scene, Stage stage) {
        double[] offset = new double[2]; // где внутри окна нажали мышью

        scene.getRoot().addEventHandler(MouseEvent.MOUSE_PRESSED, e -> {
            offset[0] = e.getSceneX();
            offset[1] = e.getSceneY();
        });

        scene.getRoot().addEventHandler(MouseEvent.MOUSE_DRAGGED, e -> {
            stage.setX(e.getScreenX() - offset[0]);
            stage.setY(e.getScreenY() - offset[1]);
        });
    }

    private URL resource(String path) {
        URL url = getClass().getResource(path);
        if (url == null) throw new IllegalStateException("Resource not found: " + path);
        return url;
    }
}