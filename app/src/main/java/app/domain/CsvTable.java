package app.domain;

import java.util.List;

public record CsvTable(List<String> headers, List<List<String>> rows) {}