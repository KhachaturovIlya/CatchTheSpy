package app.domain.model.flight;

import app.domain.exception.InitException;

import java.time.LocalDate;
import java.time.LocalTime;

public record Flight(FlightId id, LocalDate depDate, LocalTime depTime, String from, String to) {
    public Flight {
        if (id == null) throw new InitException("id is null");

        if (from == null || from.isBlank()) throw new InitException("from is null");
        if (to == null || to.isBlank()) throw new InitException("to is null");

        from = from.strip();
        to = to.strip();
    }
}
