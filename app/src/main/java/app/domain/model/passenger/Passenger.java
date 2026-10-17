package app.domain.model.passenger;

import app.domain.exception.InitException;

import java.time.LocalDate;

public record Passenger(PassengerId id, String name, LocalDate date, Gender gender) {
    public Passenger {
        if (id == null) throw new InitException("id must not be null");
        if (name == null || name.isBlank()) throw new InitException("name is empty");

        name = name.strip();
    }
}
