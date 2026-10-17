package app.domain.model.ticket;

import app.domain.exception.InitException;
import app.domain.model.flight.FlightId;
import app.domain.model.passenger.PassengerId;

public record Ticket(TicketId id, PassengerId passengerId, FlightId flightId) {

    public Ticket {
        if (id == null || passengerId == null || flightId == null) {
            throw new InitException("ticket info is not full");
        }
    }

}
