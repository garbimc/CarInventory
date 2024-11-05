import streamlit as st
import db2 as db
import pandas as pd
import plotly.express as px

# Initialize the database
db.init_db()

# Set up page configuration
st.set_page_config(page_title="Car Inventory Management", page_icon="🚗")

# Check if 'authentication' is already set in session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Show login or registration based on tab selection
def login_tab():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        if db.verify_user(username, password):
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.success("Login successful!")
            st.button("Start")
        else:
            st.error("Invalid username or password")

def register_tab():
    st.subheader("Register")
    username = st.text_input("New Username", key="register_username")
    password = st.text_input("New Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
    
    if st.button("Register", key="register_button"):
        if password == confirm_password:
            if db.register_user(username, password):
                st.success("Registration successful! Please log in.")
            else:
                st.error("Username already exists. Please choose another.")
        else:
            st.error("Passwords do not match.")

def main_app():
    

    # Sidebar Navigation
    st.sidebar.header("📋 Navigation")
    options = [ "View Inventory","Add New Car", "Update Car Info", "Delete Car", "Add Spare Parts", "Sell Car", "Sales Dashboard","Logout"]
    choice = st.sidebar.selectbox("Choose an option", options)

    # Header and container layout for main content
    st.title("🚗 Car Inventory Management")

    with st.container():
        st.write(f"Hello, **{st.session_state.get('username', 'User')}**!")

        # Handle logout
        if choice == "Logout":
                st.session_state['authenticated'] = False
                st.session_state['username'] = ""

        # Add New Car
        if choice == "Add New Car":
            st.header("Add a New Car to Inventory")
            
            with st.form("new_car_form"):
                manufacture = st.text_input("Manufacture")
                model = st.text_input("Model")
                specification = st.text_input("Specification")
                kilometers = st.number_input("Kilometers", min_value=0)
                gear_type = st.selectbox("Gear Type", ["Manual", "Automatic"])
                fuel = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Electric"])
                license_plate = st.text_input("License Plate")
                price = st.number_input("Price", min_value=0.0)
                color = st.text_input("Color")
                extra_items = st.text_area("Extra Items")
                
                submitted = st.form_submit_button("Add Car")
                
                if submitted:
                    db.add_car(manufacture, model, specification, kilometers, gear_type, fuel, license_plate, price, color, extra_items)
                    st.success("Car added to inventory successfully!")

        # Update Car Info
        elif choice == "Update Car Info":
            st.header("Update Car Information")
            cars = db.get_all_cars()
            
            if not cars:
                st.info("No cars available in the inventory to update.")
            else:
                car_dict = {f"{car[1]} {car[2]} ({car[7]})": car[0] for car in cars}
                selected_car = st.selectbox("Select a Car", list(car_dict.keys()))
                car_id = car_dict.get(selected_car)

                car = next(car for car in cars if car[0] == car_id)
                    
                # Display fields for updating
                manufacture = st.text_input("Manufacture", value=car[1])
                model = st.text_input("Model", value=car[2])
                specification = st.text_input("Specification", value=car[3])
                kilometers = st.number_input("Kilometers", min_value=0, value=car[4])
                gear_type = st.selectbox("Gear Type", ["Manual", "Automatic"], index=["Manual", "Automatic"].index(car[5]))
                fuel = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Electric"], index=["Petrol", "Diesel", "Electric"].index(car[6]))
                price = st.number_input("Price", min_value=0.0, value=car[8])
                color = st.text_input("Color", value=car[9])
                extra_items = st.text_area("Extra Items", value=car[10])

                    
                if st.button("Update Car"):
                        db.update_car(car_id, manufacture=manufacture, model=model, specification=specification,
                                    kilometers=kilometers, gear_type=gear_type, fuel=fuel,
                                    price=price, color=color, extra_items=extra_items)
                        st.success("Car updated successfully!")

        # Delete Car
        elif choice == "Delete Car":
            st.header("Delete a Car from Inventory")
            cars = db.get_all_cars()

            if not cars:
                st.info("No cars available in the inventory to delete.")
            else:
                car_dict = {f"{car[1]} {car[2]} ({car[7]})": car[0] for car in cars}
                selected_car = st.selectbox("Select a Car to Delete", list(car_dict.keys()))
                car_id = car_dict.get(selected_car)

                if st.button("Delete Car") and car_id:
                    db.delete_car(car_id)
                    db.delete_spare_part(car_id)
                    st.success("Car deleted from inventory!")

        # Add Spare Parts
        elif choice == "Add Spare Parts":
            st.header("Add Spare Parts Cost for a Car")
            cars = db.get_all_cars()
            if not cars:
                st.info("No cars available in the inventory to add Spare Parts.")
            else:
                car_dict = {f"{car[1]} {car[2]} ({car[7]})": car[0] for car in cars}
                selected_car = st.selectbox("Select a Car", list(car_dict.keys()))
                car_id = car_dict[selected_car]
            
                with st.form("spare_part_form"):
                    part_name = st.text_input("Part Name")
                    cost = st.number_input("Cost", min_value=0.0)
                    submitted = st.form_submit_button("Add Spare Part")
                
                    if submitted:
                        db.add_spare_part(car_id, part_name, cost)
                        st.success("Spare part added successfully!")

        # Sell Car Section
        if choice == "Sell Car":
            # Improved Sell Car Page
            st.title("Sell a Car")
            # Retrieve available cars
            cars = db.get_all_cars()
            if not cars:
                st.info("No cars available in the inventory to sell.")
            else:
                car_dict = {f"{car[1]} {car[2]} ({car[7]})": car[0] for car in cars}
                selected_car = st.selectbox("Select a Car", list(car_dict.keys()))
                car_id = car_dict[selected_car]
                
                if cars:
                    for car in cars:
                        car = next(car for car in cars if car[0] == car_id)
                        car_id, manufacture, model, specification, kilometers, gear_type, fuel, license_plate, price, color, extra_items = car
                        spare_parts_cost = db.get_spare_parts_cost(car_id) or 0.0
                        total_cost = float(price) + float(spare_parts_cost)  # Calculate total cost

                    # Car Display Card
                    with st.container():
                        st.subheader(f"{manufacture} {model} ({license_plate})")
                        st.write(f"Specification: {specification}")
                        st.write(f"Kilometers: {kilometers} km")
                        st.write(f"Gear Type: {gear_type}, Fuel Type: {fuel}")
                        st.write(f"Color: {color}")
                        st.write(f"Extra Items: {extra_items}")
                        st.write(f"Base Price: ${price:,.2f}")
                        st.write(f"Spare Parts Cost: ${spare_parts_cost:,.2f}")
                        st.write(f"**Total Cost: ${total_cost:,.2f}**")

                        # Sale Price Input and Confirm Sale Button
                        sale_price = st.number_input(f"Enter Sale Price for {manufacture} {model} ({license_plate})", min_value=0.0, value=total_cost, key=f"sale_price_{car_id}")
                        confirm_button = st.button(f"Confirm Sale for {manufacture} {model} ({license_plate})", key=f"confirm_{car_id}")

                        # Handle Sale Confirmation
                        if confirm_button:
                            if sale_price <= 0:
                                st.warning("Please enter a valid sale price.")
                            else:
                                # Confirm Sale Modal
                                with st.expander("Confirm Sale Details",True):
                                    st.write(f"**Manufacture**: {manufacture}")
                                    st.write(f"**Model**: {model}")
                                    st.write(f"**License Plate**: {license_plate}")
                                    st.write(f"**Total Sale Price**: ${sale_price:,.2f}")
                                    st.write(f"**Profit**: ${sale_price - total_cost:,.2f}")

                                    # Show Sale Summary for Confirmation
                                    st.write(f"**Confirming Sale Details** for {manufacture} {model}")
                                    st.write(f"**Total Sale Price**: ${sale_price:,.2f}")
                                    st.write(f"**Profit**: ${sale_price - total_cost:,.2f}")

                                    # Finalize Sale and Remove Car from Inventory
                                    db.add_sale(car_id, manufacture, model, specification, license_plate, sale_price, total_cost)
                                    db.delete_car(car_id)
                                    st.success(f"Sale completed for {manufacture} {model} ({license_plate}) and car removed from inventory.")
                else:
                    st.warning("No cars available in inventory.")

        # View Inventory
        elif choice == "View Inventory":
            st.header("Current Inventory Overview")
            
            cars = db.get_car_with_spare_parts()
            total_inventory_cost = 0

            if cars:
                for car in cars:
                    car_id, manufacture, model, specification, kilometers, gear_type, fuel, license_plate, price, color, extra_items, spare_parts_cost = car
                    total_car_cost = price + spare_parts_cost
                    total_inventory_cost += total_car_cost

                    with st.expander(f"{manufacture} {model} ({license_plate}) - ${total_car_cost:.2f}", expanded=False):
                        st.markdown(f"**Specification**: {specification}")
                        st.markdown(f"**Kilometers**: {kilometers} km")
                        st.markdown(f"**Gear Type**: {gear_type}")
                        st.markdown(f"**Fuel Type**: {fuel}")
                        st.markdown(f"**Color**: {color}")
                        st.markdown(f"**Extra Items**: {extra_items}")
                        st.markdown(f"**Base Price**: ${price:.2f}")
                        st.markdown(f"**Spare Parts Cost**: ${spare_parts_cost:.2f}")
                        st.markdown(f"**Total Cost for Car**: ${total_car_cost:.2f}")
                        
                        st.markdown("---")

                st.subheader("💰 Total Inventory Cost")
                st.markdown(f"**${total_inventory_cost:.2f}**")
            else:
                st.info("No cars available in the inventory.")

        elif choice == "Sales Dashboard":
            st.header("Sales Dashboard")

            # Retrieve sales and car data from the database
            sales = db.get_all_sales()
            cars = db.get_all_cars()  # Used for additional car details if needed

            # Check if sales data exists
            if not sales:
                st.info("No sales data available. Please complete a sale first.")
            else:
                # Convert sales data to a DataFrame
                sales_df = pd.DataFrame(sales, columns=["Sale ID", "Car ID", "Manufacture", "Model", "Specification", 
                                                        "License Plate", "Sale Price", "Sale Cost", "Sale Date"])
                
                # Calculate profit for each sale and add it as a new column
                sales_df['Profit'] = sales_df['Sale Price'] - sales_df['Sale Cost']

                # Display historical sales data in a table
                st.subheader("Sales Data History")
                st.dataframe(sales_df)

                # Graph 1: Profit per Sale
                st.subheader("Profit per Sale")
                fig_profit = px.bar(sales_df, x="Sale Date", y="Profit", color="Profit",
                                    title="Profit per Sale Over Time", labels={"Profit": "Profit ($)"})
                st.plotly_chart(fig_profit)

                # Graph 2: Sales Trends Over Time
                st.subheader("Total Sales and Profit Trends")
                trend_df = sales_df.groupby("Sale Date").agg(
                    Total_Sales=('Sale Price', 'sum'),
                    Total_Profit=('Profit', 'sum')
                ).reset_index()
                fig_trends = px.line(trend_df, x="Sale Date", y=["Total_Sales", "Total_Profit"],
                                    title="Total Sales and Profit Trends Over Time",
                                    labels={"value": "Amount ($)", "variable": "Metric"})
                fig_trends.update_layout(yaxis_title="Amount ($)")
                st.plotly_chart(fig_trends)

                # Graph 3: Top-Selling Models
                st.subheader("Top-Selling Car Models")
                model_counts = sales_df['Model'].value_counts().reset_index()
                model_counts.columns = ["Model", "Sales Count"]
                fig_models = px.bar(model_counts, x="Model", y="Sales Count", color="Sales Count",
                                    title="Top-Selling Car Models", labels={"Sales Count": "Number of Sales"})
                st.plotly_chart(fig_models)

                # Graph 4: Average Sale Price by Manufacturer
                st.subheader("Average Sale Price by Manufacturer")
                avg_price_df = sales_df.groupby("Manufacture")['Sale Price'].mean().reset_index()
                fig_avg_price = px.bar(avg_price_df, x="Manufacture", y="Sale Price", 
                                    title="Average Sale Price by Manufacturer", 
                                    labels={"Sale Price": "Average Sale Price ($)"})
                st.plotly_chart(fig_avg_price)

                # Summary Statistics
                st.subheader("Sales Summary Statistics")
                total_sales = sales_df['Sale Price'].sum()
                total_profit = sales_df['Profit'].sum()
                avg_profit = sales_df['Profit'].mean()
                st.write(f"**Total Sales:** ${total_sales:,.2f}")
                st.write(f"**Total Profit:** ${total_profit:,.2f}")
                st.write(f"**Average Profit per Sale:** ${avg_profit:,.2f}")

# Display login and registration in tabs if not authenticated
if not st.session_state.get('authenticated', False):
    login_register_tabs = st.tabs(["Login", "Register"])
    
    with login_register_tabs[0]:
        login_tab()
        
    with login_register_tabs[1]:
        register_tab()
else:
    main_app()  # Show the main app if authenticated