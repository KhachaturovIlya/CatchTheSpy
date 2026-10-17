package app.domain.model.loyaltycard;

import app.domain.exception.InitException;
import app.domain.model.passenger.PassengerId;

public record LoyaltyCard(LoyaltyCardId id, String programName, PassengerId passengerId) {

    public LoyaltyCard {
        if (id == null) throw new InitException("Loyalty card id is null");

        if (programName == null || programName.isBlank())
            throw new InitException("Loyalty card programName is null");

        programName = programName.strip();

        // passengerId could be null, at my thoughts...
    }

}
