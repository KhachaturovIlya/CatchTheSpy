package app.core.navigation;

public enum Screen {
    START("/app/ui/main/start.fxml"),
    HELP("/app/ui/help/help.fxml"),;

    private final String fxml;

    Screen(String fxml) { this.fxml = fxml; }

    public String fxml() { return fxml; }
}