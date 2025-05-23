import streamlit as st
import pandas as pd
import time
from datetime import datetime
from PIL import Image
# Import custom components
from components import create_landing_animation, create_card_layout

from data.test_data_manager import GoogleSheetsManager

# Page configuration with friendly title and wide layout
st.set_page_config(
    page_title="Exhibitor Portal - Expo Convention Contractors",
    page_icon="🎪",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Apply custom CSS for light mode and styling
st.markdown("""
<style>
    # /* Force light mode regardless of browser settings */
    # :root {
    #     --background-color: #f8f9fa !important;
    #     --secondary-background-color: #ffffff !important;
    #     --text-color: #2c3e50 !important;
    #     --font: "Source Sans Pro", sans-serif !important;
    # }
    
    # /* Override Streamlit's auto dark mode detection */
    # [data-testid="stAppViewContainer"], 
    # [data-testid="stHeader"],
    # [data-testid="stToolbar"],
    # [data-testid="stSidebar"],
    # .stApp {
    #     background-color: #f8f9fa !important;
    #     color: #2c3e50 !important;
    # }
    
    # /* Make sure text remains dark */
    # p, h1, h2, h3, span, label, .stTextInput > label, .stSelectbox > label {
    #     color: #2c3e50 !important;
    # }
    
    # /* Ensure input fields have proper contrast */
    # .stTextInput > div > div > input, .stSelectbox > div > div > div {
    #     background-color: white !important;
    #     color: #2c3e50 !important;
    #     border: 1px solid #e0e0e0 !important;
    # }
    
    /* Button styling */
    .stButton button {
        background-color: #3498db !important;
        color: white !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }
    .stButton button:hover {
        background-color: #2980b9 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    /* Card styling */
    .card {
        border-radius: 15px !important;
        padding: 1.5rem !important;
        background: white !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease !important;
    }
    .card:hover {
        box-shadow: 0 6px 14px rgba(0,0,0,0.1) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Status indicators */
    .status-delivered {
        color: #27ae60 !important;
        font-weight: bold !important;
    }
    .status-in-progress {
        color: #f39c12 !important;
        font-weight: bold !important;
    }
    .status-not-started {
        color: #e74c3c !important;
        font-weight: bold !important;
    }
    
    # /* Sidebar styling */
    # [data-testid="stSidebar"] {
    #     background-color: #ffffff !important;
    #     border-right: 1px solid #e0e0e0 !important;
    # }
    
    # /* Make sure dropdown menus are visible */
    # .stSelectbox > div > div > ul {
    #     background-color: white !important;
    #     color: #2c3e50 !important;
    # }
    
    # /* Tab styling for visibility */
    # div[role="tablist"] {
    #     background-color: #f1f3f4 !important;
    #     border-radius: 4px !important;
    # }
    
    # /* Style for ALL tab buttons to ensure they're visible */
    # div[role="tablist"] button {
    #     opacity: 1 !important;
    #     background-color: transparent !important;
    #     color: #2c3e50 !important;
    #     font-weight: 500 !important;
    #     padding: 10px 15px !important;
    #     transition: all 0.2s ease !important;
    # }
    
    # /* Style for active tab */
    # div[role="tablist"] button[aria-selected="true"] {
    #     background-color: #3498db !important;
    #     color: white !important;
    #     border-radius: 4px !important;
    # }
    
    # /* Style for tab text in both selected and unselected state */
    # div[role="tablist"] button p {
    #     color: inherit !important;
    #     font-weight: inherit !important;
    # }
    
    # /* Style for tab content area */
    # div[data-baseweb="tab-panel"] {
    #     background-color: white !important;
    #     border-radius: 0 4px 4px 4px !important;
    #     border: 1px solid #e0e0e0 !important;
    #     padding: 15px !important;
    #     margin-top: -1px !important;
    # }
</style>

""", unsafe_allow_html=True)


# Initialize the Google Sheets manager
gs_manager = GoogleSheetsManager()

# Function to load available shows
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_shows():
    try:
        # Replace with actual sheet ID from your secrets when deploying
        sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE"
        shows_df = gs_manager.get_data(sheet_id, "Shows")
        
        # Process the data: assume first row contains headers
        shows_df.columns = shows_df.iloc[0].str.strip()
        shows_df = shows_df[1:].reset_index(drop=True)
        
        # Extract show names from the data
        show_list = shows_df["Show Name"].dropna().tolist() if "Show Name" in shows_df.columns else []
        
        # If no shows are found, provide some sample data
        if not show_list:
            show_list = ["Miami Home Design and Remodeling Show", "Florida International Boat Show", "South Florida Business Expo"]
            
        return show_list
    except Exception as e:
        # st.error(f"Error loading shows: {e}")
        return ["Miami Home Design and Remodeling Show", "Florida International Boat Show", "South Florida Business Expo"]

# Initialize session state for storing booth and show information
if "booth_number" not in st.session_state:
    st.session_state.booth_number = None

if "selected_show" not in st.session_state:
    st.session_state.selected_show = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "reload_data" not in st.session_state:
    st.session_state.reload_data = False

# Landing page for selecting show and booth
def show_landing_page():
    # Create columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Add logo or welcome animation
        create_landing_animation()
        
        # Show selection
        shows = load_shows()
        selected_show = st.selectbox("Select Your Show:", shows)
        
        # Booth number input
        booth_number = st.text_input("Enter Your Booth Number:", 
                                    placeholder="e.g., 108",
                                    help="Please enter your assigned booth number")
        
        # Login button
        login_col1, login_col2 = st.columns([3, 1])
        with login_col2:
            if st.button("Continue →", use_container_width=True):
                if booth_number and selected_show:
                    # Store in session state
                    st.session_state.booth_number = booth_number
                    st.session_state.selected_show = selected_show
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Please enter both your show and booth number to continue.")
        
        # Add some friendly help text
        st.caption("Need help? Contact our support team at support@expocontractors.com")

# Function to load orders for a specific booth
@st.cache_data(ttl=120)  # Cache for 2 minutes to simulate real-time updates
def load_booth_orders(booth_number, show_name):
    try:
        # Replace with actual sheet ID from your secrets when deploying
        sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE" 
        
        # Load orders data
        orders_df = gs_manager.get_data(sheet_id, "Orders")
        
        # Process the dataframe: assume first row contains headers
        if not orders_df.empty:
            orders_df.columns = orders_df.iloc[0].str.strip()
            orders_df = orders_df[1:].reset_index(drop=True)
            
            # Filter for the booth number
            if "Booth #" in orders_df.columns:
                # Convert booth numbers to string for comparison
                orders_df["Booth #"] = orders_df["Booth #"].astype(str)
                booth_orders = orders_df[orders_df["Booth #"] == str(booth_number)]
                return booth_orders
            else:
                st.warning("Data format issue: 'Booth #' column not found")
                return pd.DataFrame()
        else:
            st.warning("No orders data found")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading orders: {e}")
        return pd.DataFrame()

# Function to load available items for ordering
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_inventory():
    try:
        # Replace with actual sheet ID from your secrets when deploying
        sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE"
        
        # Load inventory data
        inventory_df = gs_manager.get_data(sheet_id, "Show Inventory")
        
        # Process the dataframe: assume first row contains headers
        if not inventory_df.empty:
            inventory_df.columns = inventory_df.iloc[0].str.strip()
            inventory_df = inventory_df[1:].reset_index(drop=True)
            
            # Extract available items
            available_items = inventory_df["Items"].dropna().tolist() if "Items" in inventory_df.columns else []
            return available_items
        else:
            # Return sample items if no data found
            return ["Chair", "Table", "Booth Carpet", "Lighting", "Display Shelf", "Counter"]
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        # Return sample items in case of error
        return ["Chair", "Table", "Booth Carpet", "Lighting", "Display Shelf", "Counter"]

# def get_exhibitor_name(booth_number):
#     try:
#         # Replace with actual sheet ID from your secrets when deploying
#         sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE" 
        
#         # Load exhibitors data - assuming data is in a sheet named "Exhibitors"
#         exhibitors_df = gs_manager.get_data(sheet_id, "Exhibitor Name ")
        
#         # Process the dataframe: assume first row contains headers
#         if not exhibitors_df.empty:
#             exhibitors_df.columns = exhibitors_df.iloc[0].str.strip()
#             exhibitors_df = exhibitors_df[1:].reset_index(drop=True)
            
#             # Filter for the booth number
#             if "Booth #" in exhibitors_df.columns and "Exhibitor Name" in exhibitors_df.columns:
#                 exhibitors_df["Booth #"] = exhibitors_df["Booth #"].astype(str)
#                 exhibitor_match = exhibitors_df[exhibitors_df["Booth #"] == str(booth_number)]
                
#                 if not exhibitor_match.empty:
#                     return exhibitor_match["Exhibitor Name "].iloc[0]
        
#         # return f"Booth #{booth_number}"  # Default fallback
#         return f"Exhibitor {booth_number}"  # Default fallback
#     except Exception as e:
#         return f"Exhibitor {booth_number}"  # Return booth number on error






# def get_exhibitor_name(booth_number):
#     try:
#         sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE"
        
#         # Load full sheet and start from row 6 (index 5 in 0-based indexing)
#         raw_df = gs_manager.get_data(sheet_id, "Orders")
#         exhibitors_df = raw_df.iloc[5:].reset_index(drop=True)

#         # Use the first row of this slice as header
#         exhibitors_df.columns = exhibitors_df.iloc[0].astype(str).str.strip()
#         exhibitors_df = exhibitors_df[1:].reset_index(drop=True)

#         # Clean strings
#         exhibitors_df = exhibitors_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

#         # Safe access
#         if "Booth #" in exhibitors_df.columns and "Exhibitor Name " in exhibitors_df.columns:
#             booth_number = str(booth_number).strip()
#             exhibitors_df["Booth #"] = exhibitors_df["Booth #"].astype(str).str.strip()

#             match = exhibitors_df[exhibitors_df["Booth #"] == booth_number]
#             if not match.empty:
#                 return match["Exhibitor Name "].iloc[0]

#         return f"Exhibitor {booth_number}"  # fallback
#     except Exception as e:
#         return f"Exhibitor {booth_number}"  # on error

def get_exhibitor_name(booth_number):
    try:
        sheet_id = "1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE"
        
        # Load Orders sheet
        orders_df = gs_manager.get_data(sheet_id, "Orders")
        
        # Convert booth_number to string for comparison
        booth_number = str(booth_number).strip()
        
        # Based on your sample data, we need to find rows where:
        # - Column 1 (index 0) contains the booth number
        # - Column 3 (index 2) contains the exhibitor name
        
        # First, find the row index where the exhibitor name header is located
        header_row = -1
        for i, row in orders_df.iterrows():
            if "Exhibitor Name" in str(row):
                header_row = i
                break
        
        if header_row >= 0:
            # Start searching from the row after the header
            for i in range(header_row + 1, len(orders_df)):
                current_booth = str(orders_df.iloc[i, 0]).strip() if pd.notna(orders_df.iloc[i, 0]) else ""
                if current_booth == booth_number and pd.notna(orders_df.iloc[i, 2]):
                    return str(orders_df.iloc[i, 2]).strip()
        
        # If no match found, return default
        return f"Exhibitor {booth_number}"
        
    except Exception as e:
        # On error, return the default
        return f"Exhibitor {booth_number}"


# 2. Then modify just the welcome header in show_dashboard function
def show_dashboard():
    # Get exhibitor name
    exhibitor_name = get_exhibitor_name(st.session_state.booth_number)
    
    # Add a welcome header with exhibitor name instead of booth number
    st.title(f"Welcome {exhibitor_name}! 🎪")
    st.caption(f"Booth #{st.session_state.booth_number} | Show: {st.session_state.selected_show}")
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Your Orders", "Place New Order"])
    # (tab1,) = st.tabs(["Your Orders"])
    
    # Check if we need to reload data
    if st.session_state.get('reload_data', False):
        load_booth_orders.clear()
        st.session_state.reload_data = False
    
    # Tab 1: Orders Overview
    with tab1:
        # Get booth's orders
        booth_orders = load_booth_orders(st.session_state.booth_number, st.session_state.selected_show)
        
        if not booth_orders.empty:
            st.subheader(f"Your Current Orders ({len(booth_orders)})")
            
            # Display all orders in a single column list layout
            for _, order in booth_orders.iterrows():
                create_card_layout(order)
        else:
            # st.info("You don't have any orders yet. Use the 'Place New Order' tab to get started!")
            st.info("You don't have any orders yet.")
            
            # Add a hint for first-time users
            with st.expander("How to place your first order"):
                st.write("""
                1. Click on the 'Place New Order' tab above
                2. Select the item you need from the dropdown
                3. Enter the quantity
                4. Add any special requests in the comments
                5. Click 'Place Order' to submit your request
                
                Our team will process your order as soon as possible!
                """)
    
    # Tab 2: New Order
    with tab2:
        # Get available items
        available_items = load_inventory()
        
        st.subheader("Place a New Order")
        
        with st.form("new_order_form"):
            # Create a cleaner layout with columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Item selection with a friendly dropdown
                item = st.selectbox(
                    "What item do you need?",
                    options=[""] + available_items,
                    format_func=lambda x: f"🔹 {x}" if x else "Select an item...",
                    help="Select the item you wish to order"
                )
                
                # Quantity selection
                quantity = st.number_input(
                    "How many do you need?",
                    min_value=1,
                    max_value=100,
                    value=1,
                    help="Enter the quantity needed"
                )
            
            with col2:
                # Add color selection if applicable
                color_options = ["White ", "Black ", "Blue", "Red ", "Gray" "Green ", "Burgundy ", "Teal", "Other"]
                color = st.selectbox("Color (if applicable):", color_options)
                
                # Comments or special requests
                comments = st.text_area(
                    "Any special requests?",
                    max_chars=500,
                    placeholder="Enter any special requirements or requests here...",
                    help="Add any additional information about your order"
                )
            
            # Submit button with better styling
            submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
            with submit_col2:
                submitted = st.form_submit_button("Place Order", use_container_width=True)
            
            if submitted:
                if not item:
                    st.error("Please select an item to order.")
                else:
                    # Prepare the order data
                    order_data = {
                        'Booth #': st.session_state.booth_number,
                        'Exhibitor Name': f"Booth {st.session_state.booth_number}",  # Can be updated if we collect exhibitor name
                        'Section': "Main Floor",  # Default section
                        'Item': item,
                        'Color': color,
                        'Quantity': quantity,
                        'Status': "In Process",  # Default status for new orders
                        'Type': "New Order",
                        'Comments': comments,
                        'User': f"Exhibitor-{st.session_state.booth_number}"  # Track that this came from an exhibitor
                    }
                    
                    # Add new order to Google Sheets
                    try:
                        from data.direct_sheets_operations import direct_add_order
                        success = direct_add_order("1dYeok-Dy_7a03AhPDLV2NNmGbRNoCD3q0zaAHPwxxCE", order_data)
                        
                        if success:
                            # Store the order data in session state for confirmation screen
                            st.session_state.last_order = order_data
                            st.session_state.show_confirmation = True
                            st.session_state.reload_data = True
                            
                            # Redirect to confirmation screen
                            st.rerun()
                        else:
                            st.error("There was an error submitting your order. Please try again.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.info("For testing purposes, we'll simulate a successful order.")
                        
                        # For demo without actual Google Sheets
                        st.session_state.last_order = order_data
                        st.session_state.show_confirmation = True
                        st.rerun()

# Confirmation screen with animation
def show_confirmation():
     # Force scroll to top when the page loads
    st.components.v1.html("""
        <script>
            window.scrollTo(0, 0);
        </script>
    """, height=0)
    
    # Rest of your confirmation function
    # add_scroll_to_top_script()
    st.title("🎉 Order Confirmed!")


    from streamlit.components.v1 import html
    from datetime import datetime

    component_key = f"confirmation_{datetime.now().timestamp()}"


    # Get the last order details
    order = st.session_state.last_order

    # Create a nice confirmation box
    with st.container():
        st.markdown("""
        <div style="padding: 2rem; background-color: #f0f9ff; border-radius: 15px; 
                    border-left: 5px solid #3498db; margin-bottom: 1rem;">
            <h2 style="color: #2980b9;">Order Summary</h2>
            <p style="font-size: 1.1rem;">
                <strong>Item:</strong> {item}<br>
                <strong>Quantity:</strong> {quantity}<br>
                <strong>Color:</strong> {color}<br>
                <strong>Comments:</strong> {comments}
            </p>
        </div>
        """.format(
            item=order.get('Item', 'N/A'),
            quantity=order.get('Quantity', 'N/A'),
            color=order.get('Color', 'N/A'),
            comments=order.get('Comments', 'None')
        ), unsafe_allow_html=True)

    
    html("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/17.0.2/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/17.0.2/umd/react-dom.production.min.js"></script>

    <div id="confirmation-animation-root" style="margin: 2rem 0;"></div>

         
<div id="confirmation-animation-root" class="relative z-10"></div>
<canvas id="fireworks-canvas" class="fixed top-0 left-0 w-full h-full z-0 pointer-events-none"></canvas>

<script>
// Confirmation Animation (unchanged)
function ConfirmationAnimation() {
    const [currentMessage, setCurrentMessage] = React.useState(0);
    const [fade, setFade] = React.useState(true);

    const messages = [
        "We've got everything covered ✅",
        "Your order is on its way to you 🚚",
        "Your order is excited to meet you 😊"
    ];

    React.useEffect(() => {
        const fadeOutTimer = setTimeout(() => setFade(false), 3500);
        const changeMessageTimer = setTimeout(() => {
            setCurrentMessage((prev) => (prev + 1) % messages.length);
            setFade(true);
        }, 4000);
        return () => {
            clearTimeout(fadeOutTimer);
            clearTimeout(changeMessageTimer);
        };
    }, [currentMessage]);

    return React.createElement(
        'div',
        { className: 'flex flex-col items-center justify-center w-full py-8' },
        React.createElement(
            'div',
            {
                className: `font-bold transition-opacity duration-1000 ${fade ? 'opacity-100' : 'opacity-0'}`,
                style: {
                    color: '#2980b9',
                    fontSize: '1.200rem',
                    transition: 'opacity 1s ease'
                }
            },
            messages[currentMessage]
        )
    );
}

const domContainer = document.querySelector('#confirmation-animation-root');
ReactDOM.render(React.createElement(ConfirmationAnimation), domContainer);
</script>

<script>
// Light-style multicolored fireworks
const canvas = document.getElementById('fireworks-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

function random(min, max) {
    return Math.random() * (max - min) + min;
}

class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.angle = random(0, Math.PI * 2);
            this.speed = random(1, 4);
            this.radius = random(1, 2.5);
            this.alpha = 1;
            this.gravity = 0.05;

            const hue = Math.floor(random(0, 360));
            this.color = `hsla(${hue}, 90%, 75%, ${this.alpha})`; // pastel tones
        }

        update() {
            this.x += Math.cos(this.angle) * this.speed;
            this.y += Math.sin(this.angle) * this.speed + this.gravity;
            this.alpha -= 0.015;
            const hueMatch = this.color.match(/hsla\((\d+),/);
            const hue = hueMatch ? hueMatch[1] : 0;
            this.color = `hsla(${hue}, 90%, 75%, ${this.alpha})`;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    }

    let particles = [];
    let startTime = Date.now(); // Track when the animation starts
    const duration = 10000; // 7 seconds in milliseconds

    function spawnFirework() {
        if (Date.now() - startTime > duration) {
            return; // Stop spawning particles after 7 seconds
        }
        const x = random(canvas.width * 0.2, canvas.width * 0.8);
        const y = random(canvas.height * 0.1, canvas.height * 0.5);
        for (let i = 0; i < 3; i++) {
            particles.push(new Particle(x, y));
        }
    }

    function animate() {
        requestAnimationFrame(animate);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        spawnFirework();
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        particles = particles.filter(p => p.alpha > 0);

        // Stop the animation after 7 seconds
        if (Date.now() - startTime > duration) {
            cancelAnimationFrame(animate); // Stop the animation
        }
    }

    animate();
    </script>
    """, height=150)
    
    

    
    # Navigation buttons
    col1, col2 = st.columns(2)
    # (col1,) = st.columns(1)

    
    with col1:
        if st.button("View Your Orders", use_container_width=True):
            st.session_state.show_confirmation = False
            st.rerun()
    
    with col2:
        if st.button("Place Another Order", use_container_width=True):
            st.session_state.show_confirmation = False
            st.rerun()

# Sidebar with helpful information
with st.sidebar:
    # Show booth information if logged in
    if st.session_state.get("logged_in", False):
        st.header(f"Booth #{st.session_state.booth_number}")
        st.subheader(st.session_state.selected_show)
        
        # Add a divider
        st.divider()
        
        # Refresh data button
        if st.button("🔄 Refresh Data", use_container_width=True):
            load_booth_orders.clear()
            load_inventory.clear()
            st.session_state.reload_data = True
            st.rerun()
        
        # Logout button
        if st.button("📤 Log Out", use_container_width=True):
            # Reset session state
            st.session_state.logged_in = False
            st.session_state.booth_number = None
            st.session_state.selected_show = None
            st.session_state.show_confirmation = False
            # Reload the page
            st.rerun()
    
    # Always show contact information
    st.divider()
    st.subheader("Need Assistance?")
    st.markdown("""
    📞 Call: (305) 555-1234  
    📱 Text: (305) 555-5678  
    📧 Email: support@expocontractors.com
    """)
    
    st.caption("On-site support is available at the Exhibitor Service Desk")

# Main app flow
if not st.session_state.get("logged_in", False):
    # Show landing page for non-logged in users
    show_landing_page()
elif st.session_state.get("show_confirmation", False):
    # Show confirmation screen after order is placed
    show_confirmation()
else:
    # Show main dashboard for logged-in users
    show_dashboard()
