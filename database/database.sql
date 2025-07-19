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
------------------------------------
-- MOCK DATA
-- 1. Parts
INSERT INTO Parts (part_number, description)
VALUES ('200-00001', 'Car Door'),
  ('200-00002', 'Car Window'),
  ('200-00003', 'Wheel'),
  ('200-00004', 'Engine'),
  ('200-00005', 'Battery Pack');
-- 2. Products
INSERT INTO Products (product_number, description)
VALUES ('100-00001', 'Compact Car'),
  ('100-00002', 'Electric SUV');
-- 3. BOM (Bill of Materials)
INSERT INTO BOM (product_number, part_number, quantity)
VALUES -- Compact Car
  ('100-00001', '200-00001', 4),
  -- Doors
  ('100-00001', '200-00002', 6),
  -- Windows
  ('100-00001', '200-00003', 4),
  -- Wheels
  ('100-00001', '200-00004', 1),
  -- Engine
  -- Electric SUV
  ('100-00002', '200-00001', 4),
  -- Doors
  ('100-00002', '200-00002', 8),
  -- Windows
  ('100-00002', '200-00003', 4),
  -- Wheels
  ('100-00002', '200-00005', 1);
-- Battery Pack
-- 4. Stations
INSERT INTO Stations (station_number, description)
VALUES ('1', 'Door Assembly'),
  ('2', 'Window Fitting'),
  ('3', 'Wheel Mounting'),
  ('4', 'Engine Assembly'),
  ('5', 'Battery Install'),
  ('6', 'Reserved'),
  ('7', 'Reserved'),
  ('8', 'Reserved'),
  ('9', 'Reserved'),
  ('10', 'Reserved'),
  ('11', 'Reserved'),
  ('12', 'Reserved'),
  ('13', 'Reserved');
-- 5. StationParts
INSERT INTO StationParts (station_number, part_number, quantity_required)
VALUES ('1', '200-00001', 2),
  ('2', '200-00002', 3),
  ('3', '200-00003', 4),
  ('4', '200-00004', 1),
  ('5', '200-00005', 1);
-- 6. WorkOrders
INSERT INTO WorkOrders (product_number, quantity_to_produce)
VALUES ('100-00001', 10),
  -- Compact Car
  ('100-00002', 5);
-- Electric SUV
-- Get work_order_ids (assuming SERIALs start from 1)
-- We'll manually use 1 and 2 below
-- 7. WorkOrderParts
INSERT INTO WorkOrderParts (
    work_order_id,
    part_number,
    quantity_needed,
    quantity_supplied
  )
VALUES -- WO1: 10 Compact Cars
  (1, '200-00001', 40, 0),
  (1, '200-00002', 60, 0),
  (1, '200-00003', 40, 0),
  (1, '200-00004', 10, 0),
  -- WO2: 5 Electric SUVs
  (2, '200-00001', 20, 0),
  (2, '200-00002', 40, 0),
  (2, '200-00003', 20, 0),
  (2, '200-00005', 5, 0);
-- 8. StationWorkOrderParts
INSERT INTO StationWorkOrderParts (
    work_order_id,
    station_number,
    part_number,
    quantity_needed,
    quantity_supplied
  )
VALUES -- WO1
  (1, '1', '200-00001', 40, 0),
  (1, '2', '200-00002', 60, 0),
  (1, '3', '200-00003', 40, 0),
  (1, '4', '200-00004', 10, 0),
  -- WO2
  (2, '1', '200-00001', 20, 0),
  (2, '2', '200-00002', 40, 0),
  (2, '3', '200-00003', 20, 0),
  (2, '5', '200-00005', 5, 0);
-- 9. Optional: PartSupplyLog
-- Let’s say station 1 already supplied 16 doors for WO1
INSERT INTO PartSupplyLog (
    work_order_id,
    station_number,
    part_number,
    quantity_supplied
  )
VALUES (1, '1', '200-00001', 16);