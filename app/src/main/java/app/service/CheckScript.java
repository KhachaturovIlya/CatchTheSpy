package app.service;

import app.domain.SourceType;

import java.util.List;

import static app.domain.SourceType.*;

public enum CheckScript implements PipelineScript {
    DUPLICATE_PASSPORTS("duplicate_passports.py", "duplicate_passports.csv",
            List.of(), List.of("passengers.csv")),
    SHARED_CARDS("shared_cards.py", "shared_cards.csv",
            List.of(XML), List.of("loyalty.csv", "passengers.csv"));

    private static final String DIR = "/scripts/check/";

    private final String resource;
    private final String output;
    private final List<SourceType> sources;
    private final List<String> uses;

    CheckScript(String fileName, String output,
                List<SourceType> sources, List<String> uses) {
        this.resource = DIR + fileName;
        this.output = output;
        this.sources = sources;
        this.uses = uses;
    }

    @Override public String resource() { return resource; }
    @Override public String output() { return output; }
    @Override public List<SourceType> sources() { return sources; }
    @Override public List<String> uses() { return uses; }
}