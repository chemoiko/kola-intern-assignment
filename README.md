# Procurement Workflow: From Request to Purchase Order

✅ Install the Purchases application in Odoo 18.0.  
✅ Add the ability to assign an RFQ to several vendors  
✅ Add process for receiving bids from suppliers against the RFQ  
✅ Add process for selecting the winning bidder and assigning them a Purchase Order  
✅ Implement a Purchase Request module for employees  

## Project Overview

An employee initiates a purchase request by specifying products, quantities, and estimated costs, creating records in the purchase_request and purchase_request_line tables in a "draft" state. Procurement can then log in and review on their end to approve the request, updating its state to "approved". Using a frontend wizard, the procurement clicks create RFQ converting the PR into a draft RFQ (purchase_order) with all the products that were in the PR getting moved as well. Multiple vendors are assigned to the RFQ if need be. An email is sent out to the vendors and bids page is then made visible. bids are then input by the responsible personnel into the bids form rows. Once competitive bids are evaluated, the winning vendor is selected, updating bid states of it to winner and setting winner as the main vendor. Finally, the RFQ is confirmed as a Purchase Order (purchase_order.state = "purchase") with that winning vendor selected, maintaining full traceability from the initial request to the final order.

## 1. Employee Creates Purchase Request

An employee creates a purchase request with the purchase request module in the database, specifying product details, quantities, and estimated costs. The system creates records in the `purchase_request` and `purchase_request_line` tables, with the request initially in "draft" state. It is linked to the users and company tables.

![Purchase Request Creation](https://i.imgur.com/r6KURgA.png)

![Purchase Request Gallery](https://imgur.com/gallery/0-xAPQhy7)

**Database Tables**:
- `purchase_request`: Stores request header information
- `purchase_request_line`: Stores individual product line items

```sql
-- Purchase Request Table
 purchase_request (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,                    -- Request number (sequence)
  requested_by INT NOT NULL REFERENCES res_users(id),
  date_start DATE NOT NULL,
  company_id INT REFERENCES res_company(id),
  description TEXT,
  state VARCHAR DEFAULT 'draft'             -- draft/to_approve/approved/done
);

-- Purchase Request Lines Table
 purchase_request_line (
  id SERIAL PRIMARY KEY,
  request_id INT NOT NULL REFERENCES purchase_request(id) ON DELETE CASCADE,
  product_id INT REFERENCES product_product(id),
  name VARCHAR,
  product_qty NUMERIC,
  estimated_cost NUMERIC,
  currency_id INT REFERENCES res_currency(id)
);
```

## 2. Manager Approval Process

The admin receives, reviews approves the purchase request on his end, updating the `state` field to "approved" in the `purchase_request` table. 

![Manager Approval](https://i.imgur.com/crFMQBd.png)
![Create RFQ](https://i.imgur.com/jL0Fkr2.png)

## 3. Procurement Creates RFQ

The admin uses the interface to convert the approved purchase request into a Request for Quotation (RFQ). A new `RFQ`.
![Create RFQ](https://i.imgur.com/pgCn6NW.png)


## 4. Multi-Vendor Assignment

The admin assigns multiple vendors to the RFQ through the Vendors tab. Records are created in the `purchase_rfq_vendor` table, establishing the one-to-many relationship between the RFQ and vendors.

![Multi-Vendor Assignment](https://i.imgur.com/MOlfZu8.png)

The RFQ to vendors relationship operates through a one-to-many connection that allows a single Request for Quotation to be assigned to multiple vendors simultaneously. This relationship is implemented using a junction table called purchase_rfq_vendor that acts as an intermediary between the main RFQ record and the vendor records. A vendor can also be assigned to multiple different RFQs over time, and each RFQ can have multiple vendors assigned to it.

**Database Table**:

+-------------------+           +----------------------+
|   purchase_order  |           |   purchase_rfq_bid   |
|-------------------|           |----------------------|
| id (PK)           |<--+    +--| id (PK)              |
| name              |   |    |  | rfq_id (FK)          |
| ...               |   |    |  | vendor_id (FK)       |
+-------------------+   |    |  | product_qty          |
                        |    |  | price_total          |
                        |    |  | currency_id (FK)     |
                        |    |  | date_expected        |
                        |    |  | note                 |
                        |    |  | state                |
                        |    |  +----------------------+
                        |    |
                        |    |  +----------------------+
                        |    +--| res_partner          |
                        |       |----------------------|
                        +-------| id (PK)              |
                                | name                 |
                                | ...                  |
                                +----------------------+
- `purchase_rfq_vendor`: Links RFQ to multiple vendors with sequence ordering

```sql
 purchase_rfq_vendor (
  id SERIAL PRIMARY KEY,
  rfq_id INT NOT NULL REFERENCES purchase_order(id) ON DELETE CASCADE,
  partner_id INT NOT NULL REFERENCES res_partner(id),
  sequence INT DEFAULT 10,
  UNIQUE (rfq_id, partner_id)
);
```

## 5. Bidding Process

After sending the emails to multiple vendors, the bids tab then becomes visible and the vendors bids are input via the Bids tab. Each bid creates a record in the `purchase_rfq_bid` table with pricing and delivery terms.
The bidding process operates through a one-to-many relationship where a single RFQ can receive multiple bids from different vendors, creating a competitive procurement environment. This relationship is implemented using the purchase_rfq_bid table that acts as a junction between the RFQ and the vendor responses.

![Competitive Bidding](https://i.imgur.com/3QxUvGc.png)


```sql
-- RFQ Bids Table
 purchase_rfq_bid (
  id SERIAL PRIMARY KEY,
  rfq_id INT NOT NULL REFERENCES purchase_order(id) ON DELETE CASCADE,
  vendor_id INT NOT NULL REFERENCES res_partner(id),
  price_total NUMERIC,                      -- Total bid amount
  currency_id INT REFERENCES res_currency(id), -- Currency for pricing
  date_expected DATE,                       -- Expected delivery date
  note TEXT,                                -- Additional notes/comments
  state VARCHAR DEFAULT 'draft',            -- Bid status: draft/submitted/won/lost
  
  CONSTRAINT uniq_rfq_vendor UNIQUE (rfq_id, vendor_id)
);
```

**Database Table**:
- `purchase_rfq_bid`: Stores vendor bids with state management (draft/submitted/won/lost)

## 6. Winner Selection

The admin  selects the winning bid by clicking the Accept button. The system automatically updates the bid states, marks the selected vendor as "won" and others as "lost", and sets the RFQ's main vendor to the winning vendor.

![Winner Selection](https://i.imgur.com/3QxUvGc.png)

**Database Updates**:
- `purchase_rfq_bid.state`: Winner set to "won", others to "lost"
- `purchase_order.partner_id`: Set to winning vendor

## 7. Purchase Order Confirmation

The RFQ is confirmed, converting it to a Purchase Order with state "purchase". The Vendors and bids tab becomes hidden as only the winning vendor remains relevant and the rest of the steps can be continued normally.

![Purchase Order Confirmation](https://i.imgur.com/pwNKwAC.png)

**Final State**:
- `purchase_order.state`: "purchase"
- Complete traceability maintained from request to final order

This workflow demonstrates the complete procurement process from initial employee request through competitive bidding to final vendor selection, with all data relationships properly maintained in the database.
