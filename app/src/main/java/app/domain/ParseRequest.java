package app.domain;

import app.domain.SourceType;
import app.domain.exception.InitException;

import java.nio.file.Path;
import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;

public record ParseRequest(Map<SourceType, Path> sources) {
    public ParseRequest {
        if (sources == null || sources.isEmpty())
            throw new InitException("no sources selected");
        sources = Collections.unmodifiableMap(new EnumMap<>(sources));
    }
}