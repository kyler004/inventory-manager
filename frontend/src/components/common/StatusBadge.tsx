import type { StockStatus } from "@/types/stock.types";

interface Props {
    status: StockStatus
}

const config = {
    OK: { label: 'OK', classes: 'bg-green-100 text-green-700'},
    LOW: { label: 'Low', classes: 'bg-yellow-100 text-yellow-700'},
    OUT: { label: 'Out', classes: 'bg-red-100 text-red-700'},
}

export const StatusBadge = ({status} : Props) => {
    const { label, classes } = config[status]
    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${classes}`}>
            {label}
        </span>
    )
}