import pandas as pd

# Load data
tourist = pd.read_csv("tourist_place.csv.txt")
district = pd.read_csv("district.csv.txt")
guides = pd.read_csv("guides.csv.txt")
tour_guide = pd.read_csv("tour_guide.csv.txt")
accomm = pd.read_csv("accommodation.csv (2).txt")
restaurant = pd.read_csv("restaurant.csv (2).txt")
reaches = pd.read_csv("reaches.csv.txt")
transport = pd.read_csv("transport_route.csv.txt")

# Merge tourist place with district
df = tourist.merge(district, on="district_id", how="left")

# Merge guides (by place_id and district_id)
guides_merged = guides.merge(tour_guide, on="guide_id", how="left")
df = df.merge(guides_merged, on=["place_id", "district_id"], how="left")

# Merge accommodations
df = df.merge(accomm, on=["place_id", "district_id"], how="left")

# Merge restaurants
df = df.merge(restaurant, on=["place_id", "district_id"], how="left")

# Merge routes (reaches links route_id to place_id)
reaches_transport = reaches.merge(transport, on="route_id", how="left")
df = df.merge(reaches_transport, on=["place_id", "route_id"], how="left")

# Select and rename columns per ER diagram
df_out = df[[
    "place_id", "name_x", "type", "district_id", "district_name", "division",
    "guide_id", "name_y", "contact", "language_speciality",
    "accommodation_id", "accommodation_name", "category", "room_count", "contact_no",
    "restaurant_id", "restaurant_name", "address", "seat_capacity", "mobile_no",
    "route_id", "route_description", "transport_type", "stop_order"
]].copy()

df_out.columns = [
    "place_id", "place_name", "place_type", "district_id", "district_name", "division",
    "guide_id", "guide_name", "guide_contact", "guide_languages",
    "accommodation_id", "accommodation_name", "accommodation_category",
    "accommodation_room_count", "accommodation_contact",
    "restaurant_id", "restaurant_name", "restaurant_address",
    "restaurant_seat_capacity", "restaurant_mobile",
    "route_id", "route_description", "transport_type", "stop_order"
]

# Add missing sea_foods column with empty values
df_out["restaurant_sea_foods"] = ""

# Remove rows where place_id is missing (should not happen)
df_out = df_out.dropna(subset=["place_id"])

# Save to CSV
df_out.to_csv("merged_tourist_data.csv", index=False)
print("Merged CSV saved as 'merged_tourist_data.csv'")
