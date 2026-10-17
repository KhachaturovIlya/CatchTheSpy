package app.domain.model.ticket;

import app.domain.exception.InitException;

public record TicketId(long value) {
    public TicketId {
        if (value <= 0) throw new InitException("ticket id is negative");
    }
}
