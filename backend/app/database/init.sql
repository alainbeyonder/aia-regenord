-- Script d'initialisation de la base de données AIA Regenord
-- PostgreSQL 15+

-- Créer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Pour la recherche textuelle

-- Table des entreprises (optionnel si multi-tenant)
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    qbo_realm_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des données QuickBooks cachées
CREATE TABLE IF NOT EXISTS qbo_data_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL, -- 'income_statement', 'balance_sheet', etc.
    fiscal_year INTEGER NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, data_type, fiscal_year)
);

-- Table des projections financières générées
CREATE TABLE IF NOT EXISTS financial_projections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    projection_year INTEGER NOT NULL,
    revenue_projection DECIMAL(15, 2),
    expense_projection DECIMAL(15, 2),
    profit_projection DECIMAL(15, 2),
    assumptions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, projection_year)
);

-- Table des tokens OAuth pour QBO
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des logs d'audit
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    user_email VARCHAR(255),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_qbo_data_cache_company ON qbo_data_cache(company_id);
CREATE INDEX IF NOT EXISTS idx_qbo_data_cache_type ON qbo_data_cache(data_type);
CREATE INDEX IF NOT EXISTS idx_financial_projections_company ON financial_projections(company_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_company ON audit_logs(company_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at DESC);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers pour updated_at
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qbo_data_cache_updated_at
    BEFORE UPDATE ON qbo_data_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_projections_updated_at
    BEFORE UPDATE ON financial_projections
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_oauth_tokens_updated_at
    BEFORE UPDATE ON oauth_tokens
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insérer des données de test (optionnel, commentez en production)
-- INSERT INTO companies (name, qbo_realm_id) VALUES ('Groupe Regenord', 'test-realm-id');

COMMIT;
