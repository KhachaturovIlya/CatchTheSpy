package app.domain.model.passenger;

import app.domain.exception.InitException;

public record PassengerId(String passport) {
    public PassengerId {
        if (passport == null || passport.isBlank()) throw new InitException("passport must not be empty");

        passport = passport.strip();
    }
}