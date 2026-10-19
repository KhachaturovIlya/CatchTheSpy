package app.service;

import app.domain.SourceType;

import java.util.List;

public interface PipelineScript {
    String name();
    String resource();
    String output();
    List<SourceType> sources();
    List<String> uses();
}