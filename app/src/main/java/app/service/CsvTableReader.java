package app.service;

import app.domain.CsvTable;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class CsvTableReader {
    private CsvTableReader() {}

    public static CsvTable read(Path file) throws IOException {
        CSVFormat format = CSVFormat.DEFAULT.builder()
                .setHeader()
                .setSkipHeaderRecord(true)
                .build();

        try (Reader reader = Files.newBufferedReader(file, StandardCharsets.UTF_8);
             CSVParser parser = format.parse(reader)) {

            List<String> headers = parser.getHeaderNames();
            List<List<String>> rows = new ArrayList<>();
            for (CSVRecord record : parser) {
                rows.add(record.toList());
            }
            return new CsvTable(headers, rows);
        }
    }
}