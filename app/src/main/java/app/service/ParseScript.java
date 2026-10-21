package app.service;

import app.domain.SourceType;

import java.util.List;

import static app.domain.SourceType.*;


public enum ParseScript implements PipelineScript {
    BOARDING_PASSENGERS("boarding_passengers.py", "passengers.csv",
            List.of(CSV, TAB), List.of()),
    BOARDING_FLIGHTS("boarding_flights.py", "flights.csv",
            List.of(EXCEL_DIR, TAB, XML, YAML, JSON), List.of()),
    BOARDING_TICKETS("boarding_tickets.py", "tickets.csv",
            List.of(CSV, TAB), List.of("flights.csv")),
    LOYALTY_CARDS("loyalty_cards.py", "loyalty.csv",
            List.of(EXCEL_DIR, CSV, TAB), List.of());

    private static final String DIR = "/scripts/parse/";

    private final String resource;
    private final String output;
    private final List<SourceType> sources;
    private final List<String> uses;

    ParseScript(String fileName, String output,
                List<SourceType> sources, List<String> uses) {
        this.resource = DIR + fileName;
        this.output = output;
        this.sources = sources;
        this.uses = uses;
    }

    public String resource() { return resource; }
    public String output() { return output; }
    public List<SourceType> sources() { return sources; }
    public List<String> uses() { return uses; }
}