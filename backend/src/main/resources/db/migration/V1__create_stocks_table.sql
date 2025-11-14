-- Create stocks table
CREATE TABLE stocks (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_stocks_ticker ON stocks(ticker);
CREATE INDEX idx_stocks_is_active ON stocks(is_active);
CREATE INDEX idx_stocks_sector ON stocks(sector);
CREATE INDEX idx_stocks_industry ON stocks(industry);

-- Comments
COMMENT ON TABLE stocks IS 'Stores stock/ticker information';
COMMENT ON COLUMN stocks.ticker IS 'Stock ticker symbol (e.g., AAPL, TSLA)';
COMMENT ON COLUMN stocks.company_name IS 'Full company name';
COMMENT ON COLUMN stocks.market_cap IS 'Market capitalization in dollars';
