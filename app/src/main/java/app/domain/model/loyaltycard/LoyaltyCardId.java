package app.domain.model.loyaltycard;

import app.domain.exception.InitException;

public record LoyaltyCardId(long id) {
    public LoyaltyCardId {
        if (id <= 0) throw new InitException("Loyalty card id cannot be negative");
    }
}
