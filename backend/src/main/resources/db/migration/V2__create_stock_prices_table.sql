-- Create stock_prices table for OHLCV data
CREATE TABLE stock_prices (
    id BIGSERIAL,
    stock_id BIGINT NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    date TIMESTAMP NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    adj_close DECIMAL(12, 4),

    PRIMARY KEY (stock_id, date)
);

-- Create indexes for efficient time-series queries
CREATE INDEX idx_stock_prices_stock_id ON stock_prices(stock_id);
CREATE INDEX idx_stock_prices_date ON stock_prices(date DESC);
CREATE INDEX idx_stock_prices_stock_date ON stock_prices(stock_id, date DESC);

-- Comments
COMMENT ON TABLE stock_prices IS 'Historical OHLCV price data for stocks';
COMMENT ON COLUMN stock_prices.date IS 'Trading day timestamp';
COMMENT ON COLUMN stock_prices.open IS 'Opening price';
COMMENT ON COLUMN stock_prices.high IS 'Highest price during the day';
COMMENT ON COLUMN stock_prices.low IS 'Lowest price during the day';
COMMENT ON COLUMN stock_prices.close IS 'Closing price';
COMMENT ON COLUMN stock_prices.volume IS 'Trading volume';
COMMENT ON COLUMN stock_prices.adj_close IS 'Adjusted closing price (splits/dividends)';

-- Note: TimescaleDB hypertable conversion can be done manually if TimescaleDB extension is available:
-- SELECT create_hypertable('stock_prices', 'date');
