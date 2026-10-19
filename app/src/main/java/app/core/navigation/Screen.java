package app.core.navigation;

public enum Screen {
    START("/app/ui/start.fxml"),
    HELP("/app/ui/help.fxml"),
    SCAN("/app/ui/scan.fxml"),
    PARSE("/app/ui/parse.fxml"),
    CHECK("/app/ui/check.fxml"),
    RESULTS("/app/ui/results.fxml"),
    ;


    private final String fxml;

    Screen(String fxml) { this.fxml = fxml; }

    public String fxml() { return fxml; }
}