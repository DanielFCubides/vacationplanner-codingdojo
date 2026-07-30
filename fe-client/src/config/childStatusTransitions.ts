// PRD-07: per-child-type status transition maps.
// These MUST mirror the backend domain validators
// (vacation_stay_scrapper/src/trips/domain/services/child_status_transition.py).
// The backend is authoritative; this map only drives which options the UI offers.

export type ChildType = 'flight' | 'accommodation' | 'activity';

type TransitionMap = Record<string, string[]>;

const FLIGHT_TRANSITIONS: TransitionMap = {
    pending: ['confirmed', 'cancelled'],
    confirmed: ['cancelled'],
    cancelled: ['pending'],
};

const ACCOMMODATION_TRANSITIONS: TransitionMap = {
    pending: ['confirmed', 'cancelled'],
    confirmed: ['cancelled'],
    cancelled: ['pending'],
};

const ACTIVITY_TRANSITIONS: TransitionMap = {
    pending: ['booked', 'cancelled'],
    booked: ['cancelled'],
    cancelled: ['pending'],
};

const TRANSITIONS_BY_TYPE: Record<ChildType, TransitionMap> = {
    flight: FLIGHT_TRANSITIONS,
    accommodation: ACCOMMODATION_TRANSITIONS,
    activity: ACTIVITY_TRANSITIONS,
};

/**
 * Return the list of statuses a child of the given type may transition to from
 * its current status. Empty if the status is terminal / unknown.
 */
export const getNextStatuses = (childType: ChildType, current: string): string[] => {
    return TRANSITIONS_BY_TYPE[childType][current.toLowerCase()] ?? [];
};
