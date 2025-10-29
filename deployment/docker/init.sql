-- Initialisation de la base de données TwisterLab Production
-- Ce script est exécuté automatiquement lors du premier démarrage du conteneur PostgreSQL

-- Activer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Créer la table de statut pour vérifier l'initialisation
CREATE TABLE IF NOT EXISTS db_status (
    id SERIAL PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'initialized',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insérer un enregistrement de statut
INSERT INTO db_status (status) VALUES ('database_initialized')
ON CONFLICT DO NOTHING;

-- Note: Les tables principales sont créées par les migrations Alembic
-- exécutées après le démarrage de l'application