package app.core.navigation;

public enum Screen {
    START("/app/ui/main/start.fxml"),
    HELP("/app/ui/help/help.fxml"),
    SCAN("/app/ui/scan/scan.fxml"),
    PARSE("/app/ui/parse/parse.fxml"),
    CHECK("/app/ui/check/check.fxml"),
    RESULTS("/app/ui/results/results.fxml"),
    ;


    private final String fxml;

    Screen(String fxml) { this.fxml = fxml; }

    public String fxml() { return fxml; }
}