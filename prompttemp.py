#import streamlit as st

defect_prompt="""What is the defect category of a given defect details {defect_detail}?
            -Cut
            -Dent
            -Leak
            -Wiring
            -Scratch
            -Fastene
            -Alignment

            Please only print the category name without anything else.

            defect_description: Deep scratch across the driver's side door, approximately 10 cm long.
            defect_category: Scratch

            defect_description: Large dent on the passenger side fender, appears pushed in from the outside.
            defect_category: Dent

            defect_description: Oil leak originating from underneath the engine, visible staining on the undercarriage.
            defect_category: Leak

            defect_description: Inoperative turn signal on the driver's side mirror, likely a wiring issue.
            defect_category: Wiring

            defect_description: Network of fine scratches on the hood, consistent with car wash brush marks.
            defect_category: Scratch

            defect_description: Missing bolt on the front bumper, slight misalignment visible.
            defect_category: Fastener

            defect_description: Headlight misaligned, beam pointing slightly upwards.
            defect_category: Alignment

            defect_description: Water leak from the sunroof, pooling evident on the headliner.
            defect_category: Leak

            defect_description: Paint chipping along the edge of the driver's side door, possible rust underneath.
            defect_category: Scratch

            defect_description: Loose trim panel on the passenger side dashboard, rattling sound when driving.
            defect_category: Fastener

            defect_description: Faulty sensor on the front bumper, causing parking assist malfunction.
            defect_category: Wiring

            defect_description: Scratches on the alloy wheels from curb rash, multiple locations.
            defect_category: Scratch

            defect_description: Dented rim on the passenger side rear wheel, likely requires replacement.
            defect_category: Dent
            
            defect_description: {defect_detail}
            defect_category:
            """
            
## Todo change project name
json_data = {"dataset_id": "<GCP project name>",
  "description": "A dataset containing information related company vendors, likely including purchase orders, capa logs, vendor details, parts and alternative parts and other relevant data.",
  "tables": [
    {
      "table_id": "vendor_purchase_orders",
      "description": "This table contains Vendor Purchase Orders details",
      "schema": {
        "fields": [
          {
            "name": "date",
            "type": "DATE",
            "description": "Date of purchase"
          },
          {
            "name": "shift_id",
            "type": "INTEGER",
            "description": "Identifier for the work shift during which the purchase order was created or processed."
          },
          {
            "name": "purchase_order",
            "type": "INTEGER",
            "description": "Unique identifier for the purchase order."
          },
          {
            "mode": "NULLABLE",
            "name": "vendor_name",
            "type": "STRING",
            "description": "Name of the vendor from whom the purchase was made."
          },
          {
            "name": "receipt_number",
            "type": "INTEGER",
            "description": "Unique identifier for the receipt associated with the purchase order."
          },
          {
            "name": "part_number",
            "type": "STRING",
            "description": "Identifier for the specific part or item ordered."
          },
          {
            "name": "quantity_ordered",
            "type": "INTEGER",
            "description": "Total number of units ordered for the specific part."
          },
          {
            "name": "quantity_good",
            "type": "INTEGER",
            "description": "Number of units received in good condition."
          },
          {
            "name": "quantity_defective",
            "type": "INTEGER",
            "description": "Number of units received with defects."
          },
          {
            "name": "defect_reason_1",
            "type": "STRING",
            "description": "Primary reason for the defect in the received units."
          },
          {
            "name": "defect_category",
            "type": "STRING",
            "description": "Category or type of the defect"
          },
          {
            "name": "defect_reason_2",
            "type": "STRING",
            "description": "Secondary reason for the defect, if applicable."
          },
          {
            "name": "defect_reason_3",
            "type": "STRING",
            "description": "Tertiary reason for the defect, if applicable."
          },
          {
            "name": "part_image",
            "type": "STRING",
            "description": "Image url of the part"
          }
          

        ]
      }
    },
    {
      "table_id": "capa_log",
      "description": "This table contains CAPA logs details",
      "schema": {
        "fields": [
          {
            "name": "date",
            "type": "DATE",
            "description": "Date of the record"
          },
          {
            "name": "shift_id",
            "type": "INTEGER",
            "description": "Shift identifier"
          },
          {
            "name": "capa_id",
            "type": "STRING",
            "description": "Unique identifier for the corrective action"
          },
          {
            "name": "incident_title",
            "type": "STRING",
            "description": "Title of the incident"
          },
          {
            "name": "description",
            "type": "STRING",
            "description": "Detailed description of the incident"
          },
          {
            "name": "vendor_name",
            "type": "STRING",
            "description": "Name of the vendor involved"
          },
          {
            "name": "work_order_number",
            "type": "INTEGER",
            "description": "Work order number associated with the incident"
          },
          {
            "name": "part_number",
            "type": "STRING",
            "description": "Part number involved in the incident"
          },
          {
            "name": "disposition",
            "type": "STRING",
            "description": "Outcome or resolution of the incident"
          },
          {
            "name": "root_cause",
            "type": "STRING",
            "description": "Identified root cause of the incident"
          },
          {
            "name": "defect_category",
            "type": "STRING",
            "description": "Category or type of the defect"
          }
        ]
      }
    },
    {
      "table_id": "vendor_parts",
      "description": "This table contains vendor names and the part numbers the sell",
      "schema": {
        "fields": [
          {
            "name": "vendor_name",
            "type": "STRING",
            "description": "Name of the vendor "
          },
          {
            "name": "part_number",
            "type": "STRING",
            "description": "part number the vendor sells"
          },
         
        ]
      }
    },
     {
      "table_id": "part_alternatives",
      "description": "This table contains part numbers and the alternative to the part numbers",
      "schema": {
        "fields": [
         
          {
            "name": "part_number",
            "type": "STRING",
            "description": "part number use this column to compare part number from vendor parts table"
          },
           {
            "name": "part_number_alternative",
            "type": "STRING",
            "description": "Alternative part number "
          }
         
        ]
      }
    },
    {
      "table_id": "vendor_location",
      "description": "This table contains CAPA logs details",
      "schema": {
        "fields": [
          {
            "name": "vendor_name",
            "type": "STRING",
            "description": "Name of the vendor"
          },
          {
            "name": "lat",
            "type": "FLOAT",
            "description": "Latitude coordinate of the vendor location"
          },
          {
            "name": "long",
            "type": "FLOAT",
            "description": "Longitude coordinate of the vendor location"
          }
        ]
      }
    }
  ]
}

