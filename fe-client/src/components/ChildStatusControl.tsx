import { useState } from 'react';
import { getStatusColor } from '../utils/StatusColors.ts';
import { ChildType, getNextStatuses } from '../config/childStatusTransitions.ts';

interface ChildStatusControlProps {
    childType: ChildType;
    status: string;
    editable?: boolean;
    onSelect: (newStatus: string) => void | Promise<void>;
}

/**
 * PRD-07 FR-7/FR-8: a status badge that, for an editable child, opens a small
 * dropdown of valid next states. Purely presentational — the parent performs
 * the actual update (optimistic apply + revert + toast).
 */
const ChildStatusControl = ({ childType, status, editable = true, onSelect }: ChildStatusControlProps) => {
    const [open, setOpen] = useState(false);
    const [busy, setBusy] = useState(false);

    const nextStatuses = getNextStatuses(childType, status);
    const canEdit = editable && nextStatuses.length > 0 && !busy;

    const badgeClass = `px-3 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(status)}`;

    if (!canEdit) {
        return <span className={badgeClass}>{status}</span>;
    }

    const handleSelect = async (newStatus: string) => {
        setOpen(false);
        setBusy(true);
        try {
            await onSelect(newStatus);
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="relative inline-block text-left">
            <button
                type="button"
                onClick={() => setOpen(o => !o)}
                className={`${badgeClass} cursor-pointer hover:ring-2 hover:ring-blue-200 focus:outline-none`}
                aria-haspopup="true"
                aria-expanded={open}
                title="Change status"
            >
                {status} ▾
            </button>
            {open && (
                <div className="absolute right-0 z-10 mt-1 w-36 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5">
                    <ul className="py-1">
                        {nextStatuses.map(next => (
                            <li key={next}>
                                <button
                                    type="button"
                                    onClick={() => handleSelect(next)}
                                    className="block w-full px-4 py-2 text-left text-sm capitalize text-gray-700 hover:bg-gray-100"
                                >
                                    {next}
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default ChildStatusControl;
