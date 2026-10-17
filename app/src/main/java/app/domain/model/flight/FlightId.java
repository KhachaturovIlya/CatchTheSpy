package app.domain.model.flight;

import app.domain.exception.InitException;

public record FlightId(String name) {
    public FlightId {
        if (name == null || name.isBlank()) throw new InitException("flight name must not be empty");

        name = name.strip();
    }
}
