package app.ui.check;

import app.core.config.AppPaths;
import app.core.navigation.NavigationManager;
import app.core.navigation.Screen;
import app.core.navigation.ScreenParameter;
import app.domain.ParseRequest;
import app.service.CheckScript;
import app.service.PipelineService;
import app.service.ScriptRunner;
import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressIndicator;
import javafx.scene.control.TextArea;

import java.awt.Desktop;
import java.io.IOException;

public class CheckController implements ScreenParameter<ParseRequest> {
    private final NavigationManager navigation;
    private final PipelineService pipeline =
            new PipelineService(new ScriptRunner(), AppPaths.OUT);

    @FXML private ProgressIndicator progress;
    @FXML private Label statusLabel;
    @FXML private TextArea logArea;
    @FXML private Button backButton;
    @FXML private Button openFolderButton;
    @FXML private Button resultsButton;

    public CheckController(NavigationManager navigation) {
        this.navigation = navigation;
    }

    @Override
    public void onShow(ParseRequest request) {
        Task<Void> task = new Task<>() {
            @Override
            protected Void call() throws Exception {
                pipeline.run(CheckScript.values(), request,
                        line -> Platform.runLater(() -> logArea.appendText(line + "\n")));
                return null;
            }
        };
        task.setOnSucceeded(e -> showSuccess());
        task.setOnFailed(e -> showError(task.getException()));

        Thread thread = new Thread(task, "check-task");
        thread.setDaemon(true);
        thread.start();
    }

    private void showSuccess() {
        setShown(progress, false);
        statusLabel.setText("Scanning completed successfully");
        statusLabel.getStyleClass().add("success");
        logArea.appendText("\nResults saved to: " + AppPaths.OUT + "\n");
        setShown(openFolderButton, true);
        setShown(resultsButton, true);
    }

    private void showError(Throwable error) {
        setShown(progress, false);
        statusLabel.setText("Scanning failed");
        statusLabel.getStyleClass().add("error");
        logArea.appendText("ERROR: " + error.getMessage() + "\n");
        setShown(backButton, true);
    }

    @FXML
    private void onOpenFolder() {
        try {
            if (!Desktop.isDesktopSupported()) {
                logArea.appendText("Cannot open folder automatically: " + AppPaths.OUT + "\n");
                return;
            }
            Desktop.getDesktop().open(AppPaths.OUT.toFile());
        } catch (IOException e) {
            logArea.appendText("Cannot open folder: " + e.getMessage() + "\n");
        }
    }

    @FXML
    private void onBack() {
        navigation.showInPrimary(Screen.SCAN);
    }

    private static void setShown(Node node, boolean shown) {
        node.setVisible(shown);
        node.setManaged(shown);
    }

    @FXML
    private void onViewResults() {
        navigation.showInPrimary(Screen.RESULTS);
    }
}