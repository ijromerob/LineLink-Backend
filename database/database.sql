-- 1. ENUM type for user roles
CREATE TYPE public.account_type AS ENUM (
  'production_employee',
  'warehouse_employee',
  'admin',
  'manager'
);
-- 2. Parts Table
CREATE TABLE Parts (
  part_number TEXT PRIMARY KEY,
  description TEXT NOT NULL
);
-- 3. Products Table
CREATE TABLE Products (
  product_number TEXT PRIMARY KEY,
  description TEXT NOT NULL
);
-- 4. BOM (Bill of Materials)
CREATE TABLE BOM (
  product_number TEXT REFERENCES Products(product_number) ON DELETE CASCADE,
  part_number TEXT REFERENCES Parts(part_number) ON DELETE CASCADE,
  quantity NUMERIC NOT NULL CHECK (quantity > 0),
  PRIMARY KEY (product_number, part_number)
);
-- 5. Stations Table
CREATE TABLE Stations (
  station_number TEXT PRIMARY KEY,
  description TEXT NOT NULL
);
-- 6. StationParts Table
CREATE TABLE StationParts (
  station_number TEXT REFERENCES Stations(station_number) ON DELETE CASCADE,
  part_number TEXT REFERENCES Parts(part_number) ON DELETE CASCADE,
  quantity_required NUMERIC NOT NULL CHECK (quantity_required > 0),
  PRIMARY KEY (station_number, part_number)
);
-- 7. WorkOrders Table
CREATE TABLE WorkOrders (
  work_order_id SERIAL PRIMARY KEY,
  product_number TEXT REFERENCES Products(product_number) ON DELETE RESTRICT,
  quantity_to_produce INT NOT NULL CHECK (quantity_to_produce > 0),
  created_at TIMESTAMP DEFAULT now()
);
-- 8. WorkOrderParts Table
CREATE TABLE WorkOrderParts (
  work_order_id INT REFERENCES WorkOrders(work_order_id) ON DELETE CASCADE,
  part_number TEXT REFERENCES Parts(part_number) ON DELETE CASCADE,
  quantity_needed NUMERIC NOT NULL CHECK (quantity_needed >= 0),
  quantity_supplied NUMERIC DEFAULT 0 CHECK (quantity_supplied >= 0),
  PRIMARY KEY (work_order_id, part_number)
);
-- 9. StationWorkOrderParts Table
CREATE TABLE StationWorkOrderParts (
  work_order_id INT REFERENCES WorkOrders(work_order_id) ON DELETE CASCADE,
  station_number TEXT REFERENCES Stations(station_number) ON DELETE CASCADE,
  part_number TEXT REFERENCES Parts(part_number) ON DELETE CASCADE,
  quantity_needed NUMERIC NOT NULL CHECK (quantity_needed >= 0),
  quantity_supplied NUMERIC DEFAULT 0 CHECK (quantity_supplied >= 0),
  PRIMARY KEY (work_order_id, station_number, part_number)
);
-- 10. PartSupplyLog Table
CREATE TABLE PartSupplyLog (
  supply_id SERIAL PRIMARY KEY,
  work_order_id INT REFERENCES WorkOrders(work_order_id) ON DELETE CASCADE,
  station_number TEXT REFERENCES Stations(station_number) ON DELETE CASCADE,
  part_number TEXT REFERENCES Parts(part_number) ON DELETE CASCADE,
  quantity_supplied NUMERIC NOT NULL CHECK (quantity_supplied > 0),
  supplied_at TIMESTAMP DEFAULT now()
);
-- 11. Trigger Function to update StationWorkOrderParts
CREATE OR REPLACE FUNCTION update_station_work_order_parts_supply() RETURNS TRIGGER AS $$ BEGIN
UPDATE StationWorkOrderParts
SET quantity_supplied = quantity_supplied + NEW.quantity_supplied
WHERE work_order_id = NEW.work_order_id
  AND station_number = NEW.station_number
  AND part_number = NEW.part_number;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- 12. Trigger on PartSupplyLog
CREATE TRIGGER trg_update_station_work_order_parts_supply
AFTER
INSERT ON PartSupplyLog FOR EACH ROW EXECUTE FUNCTION update_station_work_order_parts_supply();
-- 13. Users Table
CREATE TABLE Users (
  user_id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  account_type public.account_type NOT NULL,
  first_name TEXT,
  last_name TEXT,
  company TEXT
);
-- 14. View for Parts Requested per Work Order
CREATE VIEW PartsRequestLog AS
SELECT wo.work_order_id,
  wo.product_number,
  b.part_number,
  p.description AS part_description,
  b.quantity * wo.quantity_to_produce AS quantity_needed
FROM WorkOrders wo
  JOIN BOM b ON wo.product_number = b.product_number
  JOIN Parts p ON b.part_number = p.part_number
ORDER BY wo.work_order_id,
  b.part_number;