package app.ui;

import app.core.config.AppPaths;
import app.core.navigation.NavigationManager;
import app.core.navigation.Screen;
import app.domain.CsvTable;
import app.service.CsvTableReader;
import javafx.animation.PauseTransition;
import javafx.beans.property.ReadOnlyStringWrapper;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.collections.transformation.FilteredList;
import javafx.collections.transformation.SortedList;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import javafx.scene.control.ToggleButton;
import javafx.scene.control.ToggleGroup;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.VBox;
import javafx.util.Duration;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import java.util.stream.Stream;

public class ResultsController {
    private static final String ALL_COLUMNS = "All columns";

    private static final List<String> TAB_ORDER = List.of(
            "passengers.csv", "flights.csv", "tickets.csv", "loyalty.csv",
            "duplicate_passports.csv", "shared_cards.csv");

    private final NavigationManager navigation;
    private final Map<Path, CsvTable> cache = new HashMap<>();
    private final ToggleGroup tabsGroup = new ToggleGroup();
    private final PauseTransition debounce = new PauseTransition(Duration.millis(100));
    private final List<FilterRow> filterRows = new ArrayList<>();

    private Path currentFile;
    private List<String> currentHeaders = List.of();
    private FilteredList<List<String>> filtered;
    private int totalRows;

    @FXML private VBox tabsBox;
    @FXML private VBox filtersBox;
    @FXML private TableView<List<String>> table;
    @FXML private Label countLabel;

    public ResultsController(NavigationManager navigation) {
        this.navigation = navigation;
    }

    @FXML
    private void initialize() {
        debounce.setOnFinished(e -> applyFilter());

        tabsGroup.selectedToggleProperty().addListener((obs, old, now) -> {
            if (now == null) {
                old.setSelected(true);
            } else {
                show((Path) now.getUserData());
            }
        });

        List<Path> files = findCsvFiles();
        if (files.isEmpty()) {
            table.setPlaceholder(new Label("No CSV files in " + AppPaths.OUT));
            return;
        }
        for (Path file : files) {
            tabsBox.getChildren().add(createTab(file));
        }
        tabsGroup.selectToggle(tabsGroup.getToggles().getFirst());
    }

    private static String tabTitle(Path file) {
        String name = file.getFileName().toString()
                .replaceFirst("\\.csv$", "")
                .replace('_', ' ');
        if (name.isEmpty()) return file.getFileName().toString();
        return Character.toUpperCase(name.charAt(0)) + name.substring(1);
    }

    private ToggleButton createTab(Path file) {
        String name = tabTitle(file);
        ToggleButton tab = new ToggleButton(name);
        tab.setUserData(file);
        tab.setToggleGroup(tabsGroup);
        tab.getStyleClass().add("tab-button");
        return tab;
    }

    private List<Path> findCsvFiles() {
        if (!Files.isDirectory(AppPaths.OUT)) return List.of();
        try (Stream<Path> stream = Files.list(AppPaths.OUT)) {
            return stream
                    .filter(p -> p.getFileName().toString().endsWith(".csv"))
                    .sorted(Comparator.comparingInt(ResultsController::orderOf)
                            .thenComparing(p -> p.getFileName().toString()))
                    .toList();
        } catch (IOException e) {
            return List.of();
        }
    }

    private static int orderOf(Path path) {
        int index = TAB_ORDER.indexOf(path.getFileName().toString());
        return index < 0 ? TAB_ORDER.size() : index;
    }

    private void show(Path file) {
        if (file.equals(currentFile)) return;
        currentFile = file;
        resetFilters();

        CsvTable cached = cache.get(file);
        if (cached != null) {
            display(cached);
            return;
        }

        table.getColumns().clear();
        table.setItems(FXCollections.emptyObservableList());
        table.setPlaceholder(new Label("Loading..."));
        countLabel.setText("");

        Thread thread = getThread(file);
        thread.setDaemon(true);
        thread.start();
    }

    private Thread getThread(Path file) {
        Task<CsvTable> task = new Task<>() {
            @Override
            protected CsvTable call() throws Exception {
                return CsvTableReader.read(file);
            }
        };
        task.setOnSucceeded(e -> {
            cache.put(file, task.getValue());
            if (file.equals(currentFile)) display(task.getValue());
        });
        task.setOnFailed(e -> {
            if (file.equals(currentFile)) {
                table.setPlaceholder(new Label("Cannot read "
                        + file.getFileName() + ": " + task.getException().getMessage()));
            }
        });

        return new Thread(task, "csv-loader");
    }

    private void display(CsvTable data) {
        currentHeaders = data.headers();

        table.getColumns().clear();
        for (int i = 0; i < currentHeaders.size(); i++) {
            final int index = i;
            TableColumn<List<String>, String> column = new TableColumn<>(currentHeaders.get(i));
            column.setCellValueFactory(cell -> {
                List<String> row = cell.getValue();
                return new ReadOnlyStringWrapper(index < row.size() ? row.get(index) : "");
            });
            column.setPrefWidth(180);
            table.getColumns().add(column);
        }

        ObservableList<List<String>> items = FXCollections.observableArrayList(data.rows());
        totalRows = items.size();
        filtered = new FilteredList<>(items, row -> true);

        SortedList<List<String>> sorted = new SortedList<>(filtered);
        sorted.comparatorProperty().bind(table.comparatorProperty());

        table.setPlaceholder(new Label("No rows"));
        table.setItems(sorted);

        debounce.setDuration(Duration.millis(totalRows > 20_000 ? 120 : 30));

        addFilterRow();
        updateCount();
    }

    @FXML
    private void onAddFilter() {
        if (filtered != null) addFilterRow();
    }

    @FXML
    private void onResetFilters() {
        if (filtered == null) return;
        filterRows.clear();
        filtersBox.getChildren().clear();
        addFilterRow();
        applyFilter();
    }

    private void addFilterRow() {
        FilterRow row = new FilterRow();
        filterRows.add(row);
        filtersBox.getChildren().add(row.root);
    }

    private void removeFilterRow(FilterRow row) {
        filterRows.remove(row);
        filtersBox.getChildren().remove(row.root);
        applyFilter();
    }

    private void resetFilters() {
        debounce.stop();
        filterRows.clear();
        filtersBox.getChildren().clear();
        filtered = null;
    }

    private void applyFilter() {
        if (filtered == null) return;

        List<Predicate<List<String>>> conditions = new ArrayList<>();
        for (FilterRow filterRow : filterRows) {
            String query = filterRow.text.getText().strip();
            if (query.isEmpty()) continue;

            int index = currentHeaders.indexOf(filterRow.column.getValue());
            if (index < 0) {
                conditions.add(row -> row.stream().anyMatch(cell -> containsIgnoreCase(cell, query)));
            } else {
                conditions.add(row -> index < row.size() && containsIgnoreCase(row.get(index), query));
            }
        }

        filtered.setPredicate(row -> {
            for (Predicate<List<String>> condition : conditions) {
                if (!condition.test(row)) return false;
            }
            return true;
        });
        updateCount();
    }

    private void updateCount() {
        countLabel.setText(filtered.size() + " of " + totalRows + " rows");
    }

    private static boolean containsIgnoreCase(String text, String query) {
        for (int i = 0, last = text.length() - query.length(); i <= last; i++) {
            if (text.regionMatches(true, i, query, 0, query.length())) return true;
        }
        return false;
    }

    private final class FilterRow {
        final ComboBox<String> column = new ComboBox<>();
        final TextField text = new TextField();
        final HBox root;

        FilterRow() {
            column.getItems().add(ALL_COLUMNS);
            column.getItems().addAll(currentHeaders);
            column.setValue(ALL_COLUMNS);
            column.getStyleClass().add("filter-combo");

            text.setPromptText("contains...");
            text.getStyleClass().add("filter-field");
            HBox.setHgrow(text, Priority.ALWAYS);

            Button remove = new Button("✕");
            remove.getStyleClass().add("filter-remove");
            remove.setOnAction(e -> removeFilterRow(this));

            root = new HBox(12, column, text, remove);
            root.setAlignment(Pos.CENTER_LEFT);

            text.textProperty().addListener((obs, old, now) -> debounce.playFromStart());
            column.valueProperty().addListener((obs, old, now) -> debounce.playFromStart());
        }
    }

    @FXML
    private void onMenu() {
        navigation.showInPrimary(Screen.START);
    }
}