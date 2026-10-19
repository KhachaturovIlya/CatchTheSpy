package app.domain;

public enum SourceType {
    JSON("json", "*.json"),
    YAML("yaml", "*.yaml", "*.yml"),
    PDF("pdf", "*.pdf"),
    TAB("tab", "*.tab"),
    CSV("csv", "*.csv"),
    XML("xml", "*.xml"),
    EXCEL_DIR("excel (dir)");

    private final String title;
    private final String[] patterns;

    SourceType(String title, String... patterns) {
        this.title = title;
        this.patterns = patterns;
    }

    public String title() { return title; }
    public String[] patterns() { return patterns; }
    public boolean isDirectory() { return patterns.length == 0; }
}