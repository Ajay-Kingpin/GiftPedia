-- Products table for storing product metadata (fallback from vector database)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(255) UNIQUE NOT NULL, -- External product ID (e.g., Amazon ASIN)
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price_inr DECIMAL(10,2),
    brand VARCHAR(100),
    description TEXT,
    image_url TEXT,
    affiliate_link TEXT,
    occasion_tags TEXT[] DEFAULT '{}',
    relationship_tags TEXT[] DEFAULT '{}',
    interest_tags TEXT[] DEFAULT '{}',
    embedding_id VARCHAR(255), -- Reference to vector database entry
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_products_product_id (product_id),
    INDEX idx_products_category (category),
    INDEX idx_products_price (price_inr),
    INDEX idx_products_brand (brand),
    INDEX idx_products_is_active (is_active),
    INDEX idx_products_created_at (created_at),
    
    -- GIN indexes for array fields
    INDEX idx_products_occasion_tags USING GIN (occasion_tags),
    INDEX idx_products_relationship_tags USING GIN (relationship_tags),
    INDEX idx_products_interest_tags USING GIN (interest_tags)
);

-- Product embeddings table for tracking vector database entries
CREATE TABLE product_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id VARCHAR(255) UNIQUE NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    vector_id VARCHAR(255) NOT NULL, -- Pinecone vector ID
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-004',
    dimensions INTEGER DEFAULT 1536,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_product_embeddings_product_id (product_id),
    INDEX idx_product_embeddings_vector_id (vector_id)
);

-- Product sync status for tracking data synchronization
CREATE TABLE product_sync_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(100) NOT NULL, -- e.g., 'amazon', 'etsy', 'manual'
    sync_type VARCHAR(50) NOT NULL, -- e.g., 'full', 'incremental'
    status VARCHAR(50) NOT NULL, -- e.g., 'pending', 'running', 'completed', 'failed'
    products_processed INTEGER DEFAULT 0,
    products_created INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_product_sync_status_source (source),
    INDEX idx_product_sync_status_status (status),
    INDEX idx_product_sync_status_started_at (started_at)
);

-- Trigger to update updated_at columns
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing
INSERT INTO products (
    product_id, name, category, subcategory, price_inr, brand, 
    image_url, affiliate_link, occasion_tags, relationship_tags, interest_tags
) VALUES 
(
    'amz_B08N5WRWSN',
    'Fender Custom Guitar Strap',
    'Music & Instruments',
    'Guitar Straps',
    1899.00,
    'Fender',
    'https://example.com/fender-strap.jpg',
    'https://amazon.in/dp/B08N5WRWSN',
    ARRAY['birthday', 'anniversary'],
    ARRAY['friend', 'family'],
    ARRAY['music', 'guitar', 'accessory']
),
(
    'amz_B07XJ8C8F5',
    'Professional Studio Headphones',
    'Music & Instruments',
    'Headphones',
    2499.00,
    'Audio-Technica',
    'https://example.com/headphones.jpg',
    'https://amazon.in/dp/B07XJ8C8F5',
    ARRAY['birthday', 'just_because'],
    ARRAY['friend', 'family', 'colleague'],
    ARRAY['music', 'audio', 'studio']
),
(
    'amz_B08N5WRWQ9',
    'Coffee Brewing Kit',
    'Kitchen & Dining',
    'Coffee Makers',
    1599.00,
    'BrewMaster',
    'https://example.com/coffee-kit.jpg',
    'https://amazon.in/dp/B08N5WRWQ9',
    ARRAY['birthday', 'housewarming'],
    ARRAY['friend', 'family', 'colleague'],
    ARRAY['coffee', 'brewing', 'kitchen']
);
