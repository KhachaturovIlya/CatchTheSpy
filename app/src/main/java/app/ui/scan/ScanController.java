package app.ui.scan;

import app.core.navigation.NavigationManager;
import app.core.navigation.Screen;
import javafx.fxml.FXML;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.DirectoryChooser;
import javafx.stage.FileChooser;
import javafx.stage.Window;

import java.io.File;
import java.nio.file.Path;
import java.util.EnumMap;
import java.util.Map;

public class ScanController {
    private static final String NOT_SELECTED = "not selected";

    private final NavigationManager navigation;
    private final Map<SourceType, Path> selected = new EnumMap<>(SourceType.class);
    private final Map<SourceType, Label> pathLabels = new EnumMap<>(SourceType.class);

    @FXML private VBox sourcesBox;
    @FXML private Button parseButton;

    public ScanController(NavigationManager navigation) {
        this.navigation = navigation;
    }

    @FXML
    private void initialize() {
        for (SourceType type : SourceType.values()) {
            sourcesBox.getChildren().add(createRow(type));
        }
        updateParseButton();
    }

    private HBox createRow(SourceType type) {
        Button button = new Button(type.title());
        button.getStyleClass().addAll("secondary", "source-button");
        button.setOnAction(e -> pick(type, button));

        Label path = new Label(NOT_SELECTED);
        path.getStyleClass().add("path-label");
        pathLabels.put(type, path);

        HBox row = new HBox(20, button, path);
        row.setAlignment(Pos.CENTER_LEFT);
        return row;
    }

    private void pick(SourceType type, Node owner) {
        Window window = owner.getScene().getWindow();
        File file;

        if (type.isDirectory()) {
            DirectoryChooser chooser = new DirectoryChooser();
            chooser.setTitle("Select folder: " + type.title());
            file = chooser.showDialog(window);
        } else {
            FileChooser chooser = new FileChooser();
            chooser.setTitle("Select " + type.title() + " file");
            chooser.getExtensionFilters().add(
                    new FileChooser.ExtensionFilter(type.title() + " files", type.patterns()));
            file = chooser.showOpenDialog(window);
        }

        if (file == null) return;

        selected.put(type, file.toPath());
        Label label = pathLabels.get(type);
        label.setText(file.getAbsolutePath());
        if (!label.getStyleClass().contains("selected")) {
            label.getStyleClass().add("selected");
        }
        updateParseButton();
    }

    @FXML
    private void onParse() {
        // позже: передать selected в сервис парсинга
    }

    @FXML
    private void onSkip() {
        // позже: сразу перейти к готовой БД.
    }

    @FXML
    private void onBack() {
        navigation.showInPrimary(Screen.START);
    }

    private void updateParseButton() {
        parseButton.setDisable(selected.size() < SourceType.values().length);
    }
}