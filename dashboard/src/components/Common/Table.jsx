import { ChevronUp, ChevronDown } from 'lucide-react';
import './Table.css';

const Table = ({ columns, data, loading, onRowClick, onSort, sortConfig }) => {
    if (loading) {
        return <div className="table-loading">Loading data...</div>;
    }

    if (!data || data.length === 0) {
        return <div className="table-empty">No data found.</div>;
    }

    const renderSortIcon = (columnKey) => {
        if (!sortConfig || sortConfig.key !== columnKey) {
            return <ChevronUp size={14} className="sort-icon placeholder" />;
        }
        return sortConfig.direction === 'asc'
            ? <ChevronUp size={14} className="sort-icon active" />
            : <ChevronDown size={14} className="sort-icon active" />;
    };

    return (
        <div className="table-container">
            <table className="custom-table">
                <thead>
                    <tr>
                        {columns.map((col, index) => (
                            <th
                                key={index}
                                style={{ width: col.width, cursor: (onSort && col.key && col.sortable !== false) ? 'pointer' : 'default' }}
                                onClick={() => (onSort && col.key && col.sortable !== false) && onSort(col.key)}
                                className={sortConfig?.key === col.key ? 'active-sort' : ''}
                            >
                                <div className="th-content">
                                    {col.title}
                                    {(onSort && col.key && col.sortable !== false) && renderSortIcon(col.key)}
                                </div>
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, rowIndex) => (
                        <tr
                            key={rowIndex}
                            onClick={() => {
                                console.log('Table tr clicked for row:', row);
                                if (onRowClick) onRowClick(row);
                            }}
                            className={onRowClick ? 'clickable' : ''}
                        >
                            {columns.map((col, colIndex) => (
                                <td key={colIndex}>
                                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Table;
