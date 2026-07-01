import React, { useEffect, useState } from 'react';
import { getInventoryItems, getInventoryOverview, getReorderAlerts, restockItem, getItemForecast } from '../api/inventory';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import StatCard from '../components/ui/StatCard';
import DataTable from '../components/ui/DataTable';
import AreaChart from '../components/charts/AreaChart';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import { formatCurrency } from '../utils/formatters';
import { 
  Package, 
  ShoppingCart, 
  AlertOctagon, 
  TrendingUp, 
  Plus, 
  RotateCcw 
} from 'lucide-react';
import './InventoryForecasting.css';

const InventoryForecasting = () => {
  const [items, setItems] = useState([]);
  const [overview, setOverview] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Forecast Modal State
  const [selectedItem, setSelectedItem] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [itemForecast, setItemForecast] = useState(null);
  const [horizon, setHorizon] = useState(30);

  const fetchData = async () => {
    try {
      const [itemList, overviewData, alertList] = await Promise.all([
        getInventoryItems(),
        getInventoryOverview(),
        getReorderAlerts()
      ]);
      setItems(itemList);
      setOverview(overviewData);
      setAlerts(alertList);
    } catch (err) {
      console.error('Failed to fetch inventory details:', err);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchData().finally(() => setLoading(false));
  }, []);

  const handleOpenForecast = async (id) => {
    setSelectedItem(id);
    setForecastLoading(true);
    try {
      const data = await getItemForecast(id, horizon);
      setItemForecast(data);
    } catch (err) {
      console.error(err);
    } finally {
      setForecastLoading(false);
    }
  };

  // Re-fetch forecast when horizon updates
  useEffect(() => {
    if (selectedItem) {
      setForecastLoading(true);
      getItemForecast(selectedItem, horizon)
        .then(setItemForecast)
        .catch(console.error)
        .finally(() => setForecastLoading(false));
    }
  }, [horizon]);

  const handleCloseForecast = () => {
    setSelectedItem(null);
    setItemForecast(null);
  };

  const handleRestock = async (id, qty) => {
    try {
      await restockItem(id, qty);
      await fetchData();
      if (selectedItem === id) {
        handleOpenForecast(id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <Loader type="shimmer" count={5} height="90px" />;
  }

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700 }}>
          Inventory <span style={{ backgroundColor: 'var(--color-accent-lime)', color: 'var(--color-ink-deep)', borderRadius: 'var(--rounded-xs)', padding: '2px 12px' }}>Forecasting</span>
        </h2>
        <p style={{ color: 'var(--color-on-dark-muted)', marginTop: '8px' }}>
          Time-series inventory demand forecasting, safety stock thresholds, and auto-reorder points.
        </p>
      </div>

      {/* KPI Cards Row */}
      {overview && (
        <div className="stat-card-grid">
          <StatCard 
            title="Total Inventory Items" 
            value={overview.total_items} 
            icon={Package}
            desc="Catalog of spares, raw materials, & supplies"
          />
          <StatCard 
            title="Total Stock Value" 
            value={formatCurrency(overview.total_value)} 
            icon={ShoppingCart}
            desc="Estimated value of current materials in warehouse"
          />
          <StatCard 
            title="Low Stock Alerts" 
            value={overview.low_stock_count} 
            icon={AlertOctagon}
            desc="Items below the safety reorder point"
          />
          <StatCard 
            title="Critical Shortages" 
            value={overview.critical_stock_count} 
            icon={AlertOctagon}
            desc="Items below absolute minimum stock level"
          />
        </div>
      )}

      <div className="inventory-dashboard">
        {/* Main Inventory Catalog */}
        <div>
          <Card>
            <h3 className="dashboard-card-title">Inventory & Forecasting Catalog</h3>
            <DataTable
              headers={['SKU', 'Name', 'Category', 'Stock Status', 'Current Stock', 'Forecast Tools']}
              data={items}
              renderRow={(item) => (
                <tr key={item.id}>
                  <td style={{ fontFamily: 'var(--font-code)', fontSize: '0.85rem' }}>{item.sku}</td>
                  <td style={{ fontWeight: 600 }}>{item.name}</td>
                  <td style={{ textTransform: 'capitalize' }}>{item.category.replace('_', ' ')}</td>
                  <td>
                    <Badge status={item.stock_status}>{item.stock_status}</Badge>
                  </td>
                  <td>
                    <strong>{item.current_stock}</strong> / {item.max_stock}
                  </td>
                  <td>
                    <Button variant="ghost" onClick={() => handleOpenForecast(item.id)} style={{ padding: '6px 12px' }}>
                      <TrendingUp size={14} /> Forecast Demand
                    </Button>
                  </td>
                </tr>
              )}
            />
          </Card>
        </div>

        {/* Low Stock Reorder Assistant */}
        <div>
          <Card>
            <h3 className="dashboard-card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShoppingCart size={18} style={{ color: 'var(--color-accent-lime)' }} />
              Reorder Assistant
            </h3>
            <div className="low-stock-panel">
              {alerts.length > 0 ? (
                alerts.map((alert) => (
                  <div key={alert.id} className="reorder-item">
                    <div className="reorder-item-details">
                      <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{alert.name}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-muted)' }}>Supplier: {alert.supplier || 'N/A'}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-on-dark-muted)' }}>Lead Time: {alert.lead_time_days} days</span>
                    </div>

                    <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <span style={{ fontSize: '0.8rem', color: 'var(--color-accent-pink)', fontWeight: 600 }}>Order: +{alert.recommended_qty} units</span>
                      <Button variant="ghost" onClick={() => handleRestock(alert.id, alert.recommended_qty)} style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                        <Plus size={12} /> Restock
                      </Button>
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '24px', color: 'var(--color-on-dark-muted)' }}>
                  All inventory stock counts inside healthy margins.
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Demand Forecast Modal */}
      <Modal isOpen={selectedItem !== null} onClose={handleCloseForecast} title="Demand Forecast Detail">
        {forecastLoading ? (
          <Loader type="spinner" />
        ) : itemForecast ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3>{itemForecast.item_name}</h3>
                <p style={{ color: 'var(--color-on-dark-muted)' }}>Current stock level: <strong>{itemForecast.current_stock} units</strong></p>
              </div>

              {/* Horizon Selector */}
              <div style={{ display: 'flex', gap: '6px' }}>
                {[7, 14, 30, 90].map((h) => (
                  <Button 
                    key={h} 
                    variant={horizon === h ? 'primary' : 'ghost'} 
                    onClick={() => setHorizon(h)}
                    style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                  >
                    {h} Days
                  </Button>
                ))}
              </div>
            </div>

            {/* Forecast AreaChart */}
            <AreaChart data={itemForecast.forecasts} height={220} />

            {/* Reorder Recommendation Box */}
            <Card style={{ backgroundColor: 'var(--color-ink-deep)' }}>
              <h4 style={{ marginBottom: '12px', textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '0.5px' }}>ML Demand Recommendations</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.9rem' }}>
                <div>Avg daily demand: <strong>{itemForecast.reorder_info.avg_daily_demand} units</strong></div>
                <div>Reorder Point: <strong>{itemForecast.reorder_info.reorder_point} units</strong></div>
                <div>Days until stockout: <strong>{itemForecast.reorder_info.days_until_stockout || 'N/A'}</strong></div>
                <div>Reorder needed: <strong style={{ color: itemForecast.reorder_info.reorder_needed ? 'var(--color-accent-pink)' : 'var(--color-accent-lime)' }}>{itemForecast.reorder_info.reorder_needed ? 'YES' : 'NO'}</strong></div>
              </div>

              {itemForecast.reorder_info.reorder_needed && (
                <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-accent-pink)', fontWeight: 600 }}>
                    Recommended Quantity: {itemForecast.reorder_info.recommended_qty} units
                  </span>
                  <Button variant="inverted" onClick={() => handleRestock(itemForecast.item_id, itemForecast.reorder_info.recommended_qty)}>
                    <ShoppingCart size={14} /> Place Reorder
                  </Button>
                </div>
              )}
            </Card>
          </div>
        ) : (
          <div>Failed to retrieve demand details.</div>
        )}
      </Modal>
    </div>
  );
};

export default InventoryForecasting;
