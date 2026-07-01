import React from 'react';
import './ui.css';

const DataTable = ({ 
  headers = [], 
  data = [], 
  renderRow 
}) => {
  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length > 0 ? (
            data.map((row, index) => renderRow(row, index))
          ) : (
            <tr>
              <td colSpan={headers.length} style={{ textAlign: 'center', padding: '24px' }}>
                No records available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
