import base64
import io
import json
import os
import re
from datetime import date, datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from deep_translator import GoogleTranslator
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, MetaData,
    String, Table, Text, UniqueConstraint, create_engine, delete,
    insert, select, update,
)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

# ============================================================
# SHIVPRUBA BILLING - COMPLETE SINGLE FILE APP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_FILE = BASE_DIR / "gst_sathi.db"

# ============================================================
# APP ICON
# ============================================================

def make_icon_bytes():
    img = Image.new("RGB", (512, 512), "white")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((32, 32, 480, 480), radius=92, fill=(15, 88, 190))
    d.rounded_rectangle((78, 78, 434, 434), radius=62, fill="white")
    d.text((160, 165), "GST", fill=(15, 88, 190))
    d.text((155, 260), "SATHI", fill=(15, 88, 190))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

ICON_BYTES = make_icon_bytes()
ICON_FILE = BASE_DIR / "shivpruba_billing_icon_final.png"
ICON_BYTES = ICON_FILE.read_bytes()
APP_ICON = Image.open(io.BytesIO(ICON_BYTES))

st.set_page_config(
    page_title="SHIVPRUBA BILLING",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# MOBILE / HOME SCREEN ICON
# ============================================================

def inject_mobile_icon():
    try:
        icon_b64 = base64.b64encode(ICON_BYTES).decode("ascii")
        components.html(
            f"""
            <script>
            const head = window.parent.document.head;
            const icon = 'data:image/png;base64,{icon_b64}';

            function ensure(rel) {{
                let el = head.querySelector(`link[rel='${{rel}}']`);
                if (!el) {{
                    el = window.parent.document.createElement('link');
                    el.rel = rel;
                    head.appendChild(el);
                }}
                el.href = icon;
            }}

            ensure('icon');
            ensure('apple-touch-icon');
            window.parent.document.title = 'SHIVPRUBA BILLING';
            </script>
            """,
            height=0,
            width=0,
        )
    except Exception:
        pass

inject_mobile_icon()

# ============================================================
# GLOBAL DESIGN
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(120,140,170,.25);
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #17345f 0%, #245a9f 100%) !important;
        border: 1px solid rgba(255,255,255,.14) !important;
        border-radius: 18px !important;
        padding: 16px 18px !important;
        min-height: 112px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,.16) !important;
    }

    [data-testid="stMetric"] * {
        color: #ffffff !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: .95rem !important;
        font-weight: 700 !important;
        opacity: .92 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(1)
    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            #123c74 0%,
            #1976d2 100%
        ) !important;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(2)
    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            #145a46 0%,
            #16a085 100%
        ) !important;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(3)
    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            #8a4b08 0%,
            #f39c12 100%
        ) !important;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(4)
    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            #56348c 0%,
            #8e44ad 100%
        ) !important;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        min-height: 3rem;
        border-radius: 12px;
        font-weight: 700;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: .45rem;
            padding-right: .45rem;
            padding-top: .4rem;
        }

        h1 {
            font-size: 1.55rem !important;
            line-height: 1.15 !important;
        }

        h2 {
            font-size: 1.25rem !important;
            line-height: 1.15 !important;
        }

        h3 {
            font-size: 1.05rem !important;
            line-height: 1.2 !important;
        }

        [data-testid="stHorizontalBlock"] {
            gap: .45rem !important;
        }

        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: .45rem !important;
            align-items: stretch !important;
        }

        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > * {
            min-width: 0 !important;
            width: auto !important;
            flex: none !important;
        }

        [data-testid="stMetric"] {
            min-height: 68px !important;
            height: auto !important;
            padding: 8px 10px !important;
            border-radius: 12px !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: .70rem !important;
            line-height: 1.05 !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.02rem !important;
            line-height: 1.08 !important;
        }

        [data-testid="stHeadingWithActionElements"] h3,
        [data-testid="stHeading"] h3 {
            font-size: 1.05rem !important;
            line-height: 1.2 !important;
        }

        div.stButton > button,
        div.stDownloadButton > button {
            width: 100%;
            min-height: 2.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# LANGUAGES
# ============================================================

LANGUAGES = {
    "English": ["english"],
    "অসমীয়া - Assamese": ["assamese"],
    "বাংলা - Bengali": ["bengali"],
    "बड़ो - Bodo": ["bodo"],
    "डोगरी - Dogri": ["dogri"],
    "ગુજરાતી - Gujarati": ["gujarati"],
    "हिन्दी - Hindi": ["hindi"],
    "ಕನ್ನಡ - Kannada": ["kannada"],
    "کٲشُر - Kashmiri": ["kashmiri"],
    "कोंकणी - Konkani": ["konkani"],
    "मैथिली - Maithili": ["maithili"],
    "മലയാളം - Malayalam": ["malayalam"],
    "Manipuri / Meitei": [
        "manipuri",
        "meitei",
        "meiteilon",
    ],
    "मराठी - Marathi": ["marathi"],
    "नेपाली - Nepali": ["nepali"],
    "ଓଡ଼ିଆ - Odia": ["odia", "oriya"],
    "ਪੰਜਾਬੀ - Punjabi": ["punjabi"],
    "संस्कृत - Sanskrit": ["sanskrit"],
    "ᱥᱟᱱᱛᱟᱲᱤ - Santali": ["santali"],
    "سنڌي - Sindhi": ["sindhi"],
    "தமிழ் - Tamil": ["tamil"],
    "తెలుగు - Telugu": ["telugu"],
    "اردو - Urdu": ["urdu"],
}

EN = {
    "menu": "Menu",
    "login": "Login",
    "signup": "Create Account",
    "logout": "Logout",
    "username": "Mobile / Email / Username",
    "password": "Password",
    "confirm_password": "Confirm Password",
    "invalid_login": "Incorrect username or password.",
    "account_exists": "This username already exists.",
    "password_short": "Password must be at least 6 characters.",
    "password_mismatch": "Passwords do not match.",
    "account_created": "Account created successfully.",
    "welcome": "Welcome to SHIVPRUBA BILLING",
    "business_setup": "Business Setup",
    "business_setup_help":
        "Enter your business details once. "
        "You can change them later in Settings.",
    "get_started": "Save & Get Started",

    "dashboard": "Dashboard",
    "new_invoice": "New Invoice",
    "customers": "Customers",
    "products": "Products",
    "invoice_history": "Invoice History",
    "reports": "Reports",
    "settings": "Settings",
    "backup": "Backup",

    "total_invoices": "Total Invoices",
    "total_sales": "Total Sales",
    "today_invoices": "Today's Invoices",
    "total_gst": "Total GST",
    "recent_invoices": "Recent Invoices",
    "no_invoices": "No invoices yet.",

    "create_invoice": "Create Tax Invoice",
    "customer_info": "Customer Information",
    "saved_customer": "Saved Customer",
    "manual_customer": "New / Manual Customer",
    "saved_supplier": "Saved Supplier",
    "manual_supplier": "New / Manual Supplier",

    "customer_name": "Customer Name",
    "customer_address": "Customer Address",
    "customer_gstin": "Customer GSTIN (Optional)",
    "customer_state": "Customer State",

    "invoice_details": "Invoice Details",
    "invoice_number": "Invoice Number",
    "invoice_date": "Invoice Date",
    "place_of_supply": "Place of Supply",

    "items": "Goods / Services",
    "number_of_items": "Number of items",
    "item": "Item",
    "saved_product": "Saved Product",
    "custom_item": "Custom Item",
    "description": "Description",
    "hsn": "HSN / SAC",
    "quantity": "Quantity",
    "rate": "Rate",
    "gst_rate": "GST %",

    "save_invoice": "Calculate & Save Invoice",
    "customer_required": "Please enter the customer name.",
    "invoice_saved": "Invoice saved successfully.",
    "invoice_duplicate": "This invoice number already exists.",

    "taxable_value": "Taxable Value",
    "grand_total": "Grand Total",
    "download_pdf": "Download PDF",
    "search": "Search invoice number or customer name",
    "found": "invoices found",
    "date": "Date",
    "amount": "Amount",
    "address": "Address",

    "add_customer": "Add Customer",
    "save_customer": "Save Customer",
    "customer_saved": "Customer saved.",
    "no_customers": "No saved customers yet.",
    "delete": "Delete",

    "add_product": "Add Product / Service",
    "product_name": "Product / Service Name",
    "save_product": "Save Product",
    "product_saved": "Product saved.",
    "no_products": "No saved products yet.",

    "company_profile": "Company Profile",
    "company_name": "Company Name",
    "gstin": "GSTIN",
    "phone": "Phone",
    "email": "Email",
    "state": "State",
    "save_settings": "Save Settings",
    "settings_saved": "Settings saved.",

    "sales_summary": "Sales Summary",
    "taxable_sales": "Taxable Sales",
    "cgst": "CGST",
    "sgst": "SGST",
    "igst": "IGST",

    "phone_install": "Use on Phone",
    "phone_install_help":
        "Open the public SHIVPRUBA BILLING link in Chrome or Safari, "
        "then choose Add to Home Screen.",

    "download_backup": "Download My Backup",
    "backup_help":
        "Download a copy of your business profile, customers, "
        "suppliers, products, purchases, stock, invoices and payments.",

    "translation_note":
        "This language could not be translated right now, "
        "so English is being shown.",

    "purchases": "Purchases / Stock In",
    "suppliers": "Suppliers",
    "stock": "Stock",
    "purchase_history": "Purchase History",
    "total_purchases": "Total Purchases",
    "today_purchases": "Today's Purchases",
    "stock_value": "Stock Value",
    "low_stock": "Low Stock",
    "recent_purchases": "Recent Purchases",
    "no_purchases": "No purchases yet.",

    "add_supplier": "Add Supplier",
    "supplier_name": "Supplier Name",
    "supplier_address": "Supplier Address",
    "supplier_gstin": "Supplier GSTIN (Optional)",
    "supplier_state": "Supplier State",
    "save_supplier": "Save Supplier",
    "supplier_saved": "Supplier saved.",
    "no_suppliers": "No saved suppliers yet.",

    "purchase_bill_number": "Supplier Bill Number",
    "purchase_date": "Purchase Date",
    "create_purchase": "Record Purchase / Stock In",
    "save_purchase": "Calculate & Save Purchase",
    "purchase_saved": "Purchase saved and stock updated.",
    "purchase_duplicate": "This supplier bill number already exists.",
    "purchase_rate": "Purchase Rate",
    "selling_rate": "Selling Rate",
    "sku": "SKU / Product Code",
    "unit": "Unit",
    "opening_stock": "Opening Stock",
    "current_stock": "Current Stock",
    "low_stock_limit": "Low Stock Limit",
    "stock_in": "Stock In",
    "stock_out": "Stock Out",
    "stock_ledger": "Stock Ledger",
    "stock_adjustment": "Stock Adjustment",
    "adjustment_qty": "Adjustment Quantity (+/-)",
    "adjustment_reason": "Reason",
    "apply_adjustment": "Apply Stock Adjustment",
    "insufficient_stock":
        "Insufficient stock for one or more products.",
    "stock_updated": "Stock updated.",

    "purchase_summary": "Purchase Summary",
    "purchase_taxable": "Taxable Purchases",
    "purchase_gst": "Purchase GST",

    "invoice_prefix": "Invoice Prefix",
    "default_low_stock": "Default Low Stock Limit",
    "save_product_changes": "Update Product",
    "product_updated": "Product updated.",

    "date_from": "From Date",
    "date_to": "To Date",
    "product_sales": "Product-wise Taxable Sales",
    "supplier_purchases": "Supplier-wise Purchases (Incl. GST)",
    "customer_sales": "Customer-wise Sales (Incl. GST)",

    "customer_ledger": "Customer Ledger",
    "record_payment": "Record Payment",
    "payment_amount": "Payment Amount",
    "payment_date": "Payment Date",
    "payment_note": "Payment Note",
    "payment_status": "Payment Status",
    "paid": "Paid",
    "unpaid": "Unpaid",
    "partly_paid": "Partly Paid",
    "paid_amount": "Paid Amount",
    "balance_amount": "Balance Amount",
    "total_paid": "Total Paid",
    "total_outstanding": "Total Outstanding",
    "payment_saved": "Payment saved.",
    "payment_too_high":
        "Payment amount cannot be more than the balance amount.",
    "payment_duplicate":
        "This payment was already recorded. "
        "Please wait before submitting again.",
    "no_payments": "No payments recorded yet.",
    "payment_history": "Payment History",
    "delete_payment": "Delete Payment",
    "payment_deleted": "Payment deleted successfully.",

    "version": "Version 4.3 | SHIVPRUBA BILLING",
}

STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
    "Other",
]

# ============================================================
# TRANSLATION
# ============================================================

@st.cache_data(show_spinner=False)
def build_language_pack(language_name):
    if language_name == "English":
        return EN.copy(), {s: s for s in STATES}, True

    try:
        probe = GoogleTranslator(
            source="en",
            target="hi",
        )

        supported = probe.get_supported_languages(
            as_dict=True
        )

        target_code = None

        for alias in [
            a.lower()
            for a in LANGUAGES.get(
                language_name,
                [],
            )
        ]:
            for supported_name, code in supported.items():
                name = supported_name.lower()

                if name == alias or alias in name:
                    target_code = code
                    break

            if target_code:
                break

        if not target_code:
            return (
                EN.copy(),
                {s: s for s in STATES},
                False,
            )

        all_text = list(EN.values()) + STATES

        translator = GoogleTranslator(
            source="en",
            target=target_code,
        )

        out = []

        for i in range(
            0,
            len(all_text),
            25,
        ):
            batch = all_text[i:i + 25]

            translated = translator.translate_batch(
                batch
            )

            if (
                not translated
                or len(translated) != len(batch)
            ):
                raise ValueError(
                    "Translation failed"
                )

            out.extend(
                translated
            )

        ui_n = len(EN)

        return (
            dict(
                zip(
                    EN.keys(),
                    out[:ui_n],
                )
            ),
            dict(
                zip(
                    STATES,
                    out[ui_n:],
                )
            ),
            True,
        )

    except Exception:
        return (
            EN.copy(),
            {s: s for s in STATES},
            False,
        )

# ============================================================
# DATABASE TABLES
# ============================================================

metadata = MetaData()

users = Table(
    "users",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "username",
        String(255),
        nullable=False,
        unique=True,
    ),

    Column(
        "password_hash",
        String(500),
        nullable=False,
    ),

    Column(
        "preferred_language",
        String(120),
        nullable=False,
        default="English",
    ),

    Column(
        "setup_complete",
        Boolean,
        nullable=False,
        default=False,
    ),

    Column(
        "company_name",
        String(300),
        default="",
    ),

    Column(
        "company_address",
        Text,
        default="",
    ),

    Column(
        "company_gstin",
        String(40),
        default="",
    ),

    Column(
        "company_phone",
        String(80),
        default="",
    ),

    Column(
        "company_email",
        String(255),
        default="",
    ),

    Column(
        "company_state",
        String(120),
        default="Maharashtra",
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),
)

customers_table = Table(
    "customers",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "name",
        String(300),
        nullable=False,
    ),

    Column(
        "address",
        Text,
        default="",
    ),

    Column(
        "gstin",
        String(40),
        default="",
    ),

    Column(
        "state",
        String(120),
        default="Maharashtra",
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),
)

products_table = Table(
    "products",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "name",
        String(300),
        nullable=False,
    ),

    Column(
        "hsn",
        String(80),
        default="",
    ),

    Column(
        "rate",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "gst_rate",
        Float,
        nullable=False,
        default=18.0,
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),
)

invoices_table = Table(
    "invoices",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "invoice_number",
        String(120),
        nullable=False,
    ),

    Column(
        "invoice_date",
        String(20),
        nullable=False,
    ),

    Column(
        "customer_name",
        String(300),
        nullable=False,
    ),

    Column(
        "customer_address",
        Text,
        default="",
    ),

    Column(
        "customer_gstin",
        String(40),
        default="",
    ),

    Column(
        "customer_state",
        String(120),
        default="",
    ),

    Column(
        "place_of_supply",
        String(120),
        default="",
    ),

    Column(
        "items_json",
        Text,
        nullable=False,
    ),

    Column(
        "taxable_value",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "cgst",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "sgst",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "igst",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "grand_total",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "is_intra_state",
        Boolean,
        nullable=False,
        default=True,
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),

    UniqueConstraint(
        "user_id",
        "invoice_number",
        name="uq_invoice_user_number",
    ),
)

suppliers_table = Table(
    "suppliers",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "name",
        String(300),
        nullable=False,
    ),

    Column(
        "address",
        Text,
        default="",
    ),

    Column(
        "gstin",
        String(40),
        default="",
    ),

    Column(
        "phone",
        String(80),
        default="",
    ),

    Column(
        "email",
        String(255),
        default="",
    ),

    Column(
        "state",
        String(120),
        default="Maharashtra",
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),
)

product_inventory_table = Table(
    "product_inventory",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "product_id",
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "sku",
        String(120),
        default="",
    ),

    Column(
        "unit",
        String(50),
        default="Pcs",
    ),

    Column(
        "purchase_rate",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "opening_stock",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "low_stock_limit",
        Float,
        nullable=False,
        default=5.0,
    ),

    Column(
        "current_stock",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "updated_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),

    UniqueConstraint(
        "user_id",
        "product_id",
        name="uq_inventory_user_product",
    ),
)

purchases_table = Table(
    "purchases",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "bill_number",
        String(120),
        nullable=False,
    ),

    Column(
        "purchase_date",
        String(20),
        nullable=False,
    ),

    Column(
        "supplier_name",
        String(300),
        nullable=False,
    ),

    Column(
        "supplier_address",
        Text,
        default="",
    ),

    Column(
        "supplier_gstin",
        String(40),
        default="",
    ),

    Column(
        "supplier_state",
        String(120),
        default="",
    ),

    Column(
        "items_json",
        Text,
        nullable=False,
    ),

    Column(
        "taxable_value",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "cgst",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "sgst",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "igst",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "grand_total",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "is_intra_state",
        Boolean,
        nullable=False,
        default=True,
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),

    UniqueConstraint(
        "user_id",
        "bill_number",
        name="uq_purchase_user_bill",
    ),
)

stock_ledger_table = Table(
    "stock_ledger",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "product_id",
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "movement_type",
        String(40),
        nullable=False,
    ),

    Column(
        "qty_change",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "balance_after",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "reference_type",
        String(40),
        default="",
    ),

    Column(
        "reference_id",
        Integer,
        default=0,
    ),

    Column(
        "reference_number",
        String(120),
        default="",
    ),

    Column(
        "note",
        Text,
        default="",
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),
)

user_settings_table = Table(
    "user_settings",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    ),

    Column(
        "invoice_prefix",
        String(30),
        nullable=False,
        default="INV",
    ),

    Column(
        "default_low_stock",
        Float,
        nullable=False,
        default=5.0,
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),

    Column(
        "updated_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),
)

payments_table = Table(
    "payments",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "invoice_id",
        Integer,
        ForeignKey("invoices.id"),
        nullable=False,
        index=True,
    ),

    Column(
        "amount",
        Float,
        nullable=False,
        default=0.0,
    ),

    Column(
        "payment_date",
        String(20),
        nullable=False,
    ),

    Column(
        "note",
        Text,
        default="",
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    ),
)

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_secret(name, default=""):
    try:
        return st.secrets.get(
            name,
            default,
        )
    except Exception:
        return default


@st.cache_resource
def get_engine():
    db_url = (
        get_secret(
            "DATABASE_URL",
            "",
        )
        or os.environ.get(
            "DATABASE_URL",
            "",
        )
    )

    if not db_url:
        db_url = (
            f"sqlite:///"
            f"{LOCAL_DB_FILE.as_posix()}"
        )

    if db_url.startswith(
        "postgres://"
    ):
        db_url = (
            "postgresql+psycopg2://"
            + db_url[len("postgres://"):]
        )

    elif db_url.startswith(
        "postgresql://"
    ):
        db_url = (
            "postgresql+psycopg2://"
            + db_url[len("postgresql://"):]
        )

    kwargs = {
        "pool_pre_ping": True
    }

    if db_url.startswith(
        "sqlite:"
    ):
        kwargs["connect_args"] = {
            "check_same_thread": False
        }

    eng = create_engine(
        db_url,
        **kwargs,
    )

    metadata.create_all(
        eng
    )

    return eng


engine = get_engine()

# ============================================================
# DATABASE HELPERS
# ============================================================

def row_dict(row):
    return (
        dict(row._mapping)
        if row is not None
        else None
    )


def get_user(user_id):
    with engine.connect() as con:
        return row_dict(
            con.execute(
                select(users).where(
                    users.c.id == user_id
                )
            ).first()
        )


def get_user_by_username(username):
    username = username.strip().lower()

    with engine.connect() as con:
        return row_dict(
            con.execute(
                select(users).where(
                    users.c.username == username
                )
            ).first()
        )


def get_customers(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                customers_table
            )
            .where(
                customers_table.c.user_id
                == user_id
            )
            .order_by(
                customers_table.c.name
            )
        ).all()

    return [
        row_dict(r)
        for r in rows
    ]


def get_products(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                products_table
            )
            .where(
                products_table.c.user_id
                == user_id
            )
            .order_by(
                products_table.c.name
            )
        ).all()

    return [
        row_dict(r)
        for r in rows
    ]


def get_invoices(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                invoices_table
            )
            .where(
                invoices_table.c.user_id
                == user_id
            )
            .order_by(
                invoices_table.c.id
            )
        ).all()

    out = []

    for r in rows:
        d = row_dict(r)

        try:
            d["items"] = json.loads(
                d.pop(
                    "items_json"
                )
            )
        except Exception:
            d["items"] = []

        out.append(d)

    return out


def get_suppliers(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                suppliers_table
            )
            .where(
                suppliers_table.c.user_id
                == user_id
            )
            .order_by(
                suppliers_table.c.name
            )
        ).all()

    return [
        row_dict(r)
        for r in rows
    ]


def get_purchases(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                purchases_table
            )
            .where(
                purchases_table.c.user_id
                == user_id
            )
            .order_by(
                purchases_table.c.id
            )
        ).all()

    out = []

    for r in rows:
        d = row_dict(r)

        try:
            d["items"] = json.loads(
                d.pop(
                    "items_json"
                )
            )
        except Exception:
            d["items"] = []

        out.append(d)

    return out


def get_inventory(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                product_inventory_table
            )
            .where(
                product_inventory_table.c.user_id
                == user_id
            )
            .order_by(
                product_inventory_table.c.product_id
            )
        ).all()

    return [
        row_dict(r)
        for r in rows
    ]


def get_stock_ledger(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                stock_ledger_table
            )
            .where(
                stock_ledger_table.c.user_id
                == user_id
            )
            .order_by(
                stock_ledger_table.c.id.desc()
            )
        ).all()

    return [
        row_dict(r)
        for r in rows
    ]


def get_payments(user_id):
    with engine.connect() as con:
        rows = con.execute(
            select(
                payments_table
            )
            .where(
                payments_table.c.user_id
                == user_id
            )
            .order_by(
                payments_table.c.id
            )
        ).all()

    return [
        row_dict(r)
        for r in rows
    ]


def make_paid_map(payment_rows):
    out = {}

    for payment in payment_rows:
        invoice_id = int(
            payment.get(
                "invoice_id",
                0,
            )
            or 0
        )

        out[invoice_id] = (
            out.get(
                invoice_id,
                0.0,
            )
            + float(
                payment.get(
                    "amount",
                    0,
                )
                or 0
            )
        )

    return out


def payment_status_for_invoice(
    inv,
    paid_map,
):
    total = float(
        inv.get(
            "grand_total",
            0,
        )
        or 0
    )

    paid_amount = float(
        paid_map.get(
            int(
                inv.get(
                    "id",
                    0,
                )
                or 0
            ),
            0.0,
        )
        or 0.0
    )

    balance = max(
        0.0,
        total - paid_amount,
    )

    if (
        total <= 0.005
        or balance <= 0.005
    ):
        status_key = "paid"

    elif paid_amount > 0.005:
        status_key = "partly_paid"

    else:
        status_key = "unpaid"

    return (
        paid_amount,
        balance,
        status_key,
    )


def ensure_user_settings(user_id):
    with engine.begin() as con:
        row = con.execute(
            select(
                user_settings_table
            ).where(
                user_settings_table.c.user_id
                == user_id
            )
        ).first()

        if not row:
            con.execute(
                insert(
                    user_settings_table
                ).values(
                    user_id=user_id,
                    invoice_prefix="INV",
                    default_low_stock=5.0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )

    with engine.connect() as con:
        return row_dict(
            con.execute(
                select(
                    user_settings_table
                ).where(
                    user_settings_table.c.user_id
                    == user_id
                )
            ).first()
        )


def ensure_inventory_rows(
    user_id,
    products,
):
    settings = ensure_user_settings(
        user_id
    )

    default_low = float(
        settings.get(
            "default_low_stock",
            5.0,
        )
        or 5.0
    )

    with engine.begin() as con:
        existing = {
            int(r.product_id)

            for r in con.execute(
                select(
                    product_inventory_table.c.product_id
                )
                .where(
                    product_inventory_table.c.user_id
                    == user_id
                )
            ).all()
        }

        for p in products:
            if int(p["id"]) not in existing:
                con.execute(
                    insert(
                        product_inventory_table
                    ).values(
                        user_id=user_id,
                        product_id=int(p["id"]),
                        sku="",
                        unit="Pcs",
                        purchase_rate=0.0,
                        opening_stock=0.0,
                        low_stock_limit=default_low,
                        current_stock=0.0,
                        updated_at=datetime.utcnow(),
                    )
                )


def inventory_map(user_id):
    return {
        int(x["product_id"]): x

        for x in get_inventory(
            user_id
        )
    }


def lock_inventory(
    con,
    user_id,
    product_id,
):
    stmt = (
        select(
            product_inventory_table
        )
        .where(
            product_inventory_table.c.user_id
            == user_id,

            product_inventory_table.c.product_id
            == product_id,
        )
        .with_for_update()
    )

    return row_dict(
        con.execute(
            stmt
        ).first()
    )


def change_stock(
    con,
    user_id,
    product_id,
    qty_change,
    movement_type,
    reference_type="",
    reference_id=0,
    reference_number="",
    note="",
):
    inv = lock_inventory(
        con,
        user_id,
        product_id,
    )

    if not inv:
        con.execute(
            insert(
                product_inventory_table
            ).values(
                user_id=user_id,
                product_id=product_id,
                sku="",
                unit="Pcs",
                purchase_rate=0.0,
                opening_stock=0.0,
                low_stock_limit=5.0,
                current_stock=0.0,
                updated_at=datetime.utcnow(),
            )
        )

        inv = lock_inventory(
            con,
            user_id,
            product_id,
        )

    new_balance = (
        float(
            inv.get(
                "current_stock",
                0.0,
            )
            or 0.0
        )
        + float(
            qty_change
        )
    )

    if new_balance < -1e-9:
        raise ValueError(
            "INSUFFICIENT_STOCK"
        )

    con.execute(
        update(
            product_inventory_table
        )
        .where(
            product_inventory_table.c.id
            == inv["id"]
        )
        .values(
            current_stock=max(
                0.0,
                new_balance,
            ),
            updated_at=datetime.utcnow(),
        )
    )

    con.execute(
        insert(
            stock_ledger_table
        ).values(
            user_id=user_id,
            product_id=product_id,
            movement_type=movement_type,
            qty_change=float(qty_change),
            balance_after=max(
                0.0,
                new_balance,
            ),
            reference_type=reference_type,
            reference_id=int(
                reference_id
                or 0
            ),
            reference_number=(
                reference_number
                or ""
            ),
            note=(
                note
                or ""
            ),
            created_at=datetime.utcnow(),
        )
    )

    return max(
        0.0,
        new_balance,
    )


def parse_app_date(value):
    try:
        return datetime.strptime(
            str(value),
            "%d-%m-%Y",
        ).date()

    except Exception:
        return None


def money(value):
    return (
        f"₹ "
        f"{float(value or 0):,.2f}"
    )


def clean_filename(value):
    return (
        re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            str(value),
        ).strip("_")
        or "invoice"
    )

# ============================================================
# SESSION + LANGUAGE
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = None

current_user = (
    get_user(
        st.session_state.user_id
    )
    if st.session_state.user_id
    else None
)

saved_lang = (
    current_user.get(
        "preferred_language",
        "English",
    )
    if current_user
    else "English"
)

if saved_lang not in LANGUAGES:
    saved_lang = "English"

selected_language = st.sidebar.selectbox(
    "🌐 भाषा / Language",
    list(
        LANGUAGES.keys()
    ),
    index=list(
        LANGUAGES.keys()
    ).index(
        saved_lang
    ),
)

TEXT, STATE_LABELS, TRANSLATION_OK = build_language_pack(
    selected_language
)


def t(key):
    return TEXT.get(
        key,
        EN.get(
            key,
            key,
        ),
    )


if (
    selected_language != "English"
    and not TRANSLATION_OK
):
    st.sidebar.warning(
        EN["translation_note"]
    )

st.sidebar.title(
    "🧾 SHIVPRUBA BILLING"
)

# ============================================================
# LOGIN / SIGNUP
# ============================================================

if not current_user:
    st.title(
        f"🧾 {t('welcome')}"
    )

    tab1, tab2 = st.tabs(
        [
            t("login"),
            t("signup"),
        ]
    )

    with tab1:
        with st.form(
            "login_form"
        ):
            login_username = st.text_input(
                t("username")
            )

            login_password = st.text_input(
                t("password"),
                type="password",
            )

            login_submit = st.form_submit_button(
                t("login"),
                use_container_width=True,
                type="primary",
            )

        if login_submit:
            found = get_user_by_username(
                login_username
            )

            if (
                found
                and check_password_hash(
                    found["password_hash"],
                    login_password,
                )
            ):
                st.session_state.user_id = found["id"]
                st.rerun()

            else:
                st.error(
                    t("invalid_login")
                )

    with tab2:
        with st.form(
            "signup_form"
        ):
            new_username = st.text_input(
                t("username"),
                key="signup_username",
            )

            new_password = st.text_input(
                t("password"),
                type="password",
                key="signup_password",
            )

            confirm_password = st.text_input(
                t("confirm_password"),
                type="password",
            )

            signup_submit = st.form_submit_button(
                t("signup"),
                use_container_width=True,
                type="primary",
            )

        if signup_submit:
            uname = (
                new_username
                .strip()
                .lower()
            )

            if len(uname) < 3:
                st.error(
                    "Username is required."
                )

            elif len(new_password) < 6:
                st.error(
                    t("password_short")
                )

            elif (
                new_password
                != confirm_password
            ):
                st.error(
                    t("password_mismatch")
                )

            else:
                try:
                    with engine.begin() as con:
                        result = con.execute(
                            insert(
                                users
                            ).values(
                                username=uname,
                                password_hash=(
                                    generate_password_hash(
                                        new_password
                                    )
                                ),
                                preferred_language=selected_language,
                                setup_complete=False,
                                company_state="Maharashtra",
                                created_at=datetime.utcnow(),
                            )
                        )

                        new_id = (
                            result
                            .inserted_primary_key[0]
                        )

                    st.session_state.user_id = int(
                        new_id
                    )

                    st.success(
                        t("account_created")
                    )

                    st.rerun()

                except IntegrityError:
                    st.error(
                        t("account_exists")
                    )

    st.stop()

# ============================================================
# LOGGED USER + LANGUAGE SAVE
# ============================================================

current_user = get_user(
    st.session_state.user_id
)

USER_ID = current_user["id"]

if (
    selected_language
    != current_user.get(
        "preferred_language"
    )
):
    with engine.begin() as con:
        con.execute(
            update(
                users
            )
            .where(
                users.c.id
                == USER_ID
            )
            .values(
                preferred_language=selected_language
            )
        )

# ============================================================
# FIRST BUSINESS SETUP
# ============================================================

if not current_user.get(
    "setup_complete",
    False,
):
    st.title(
        f"🏪 {t('business_setup')}"
    )

    st.caption(
        t("business_setup_help")
    )

    with st.form(
        "business_setup_form"
    ):
        company_name = st.text_input(
            t("company_name"),
            value=(
                current_user.get(
                    "company_name"
                )
                or ""
            ),
        )

        company_address = st.text_area(
            t("address"),
            value=(
                current_user.get(
                    "company_address"
                )
                or ""
            ),
        )

        company_gstin = st.text_input(
            t("gstin"),
            value=(
                current_user.get(
                    "company_gstin"
                )
                or ""
            ),
        )

        company_phone = st.text_input(
            t("phone"),
            value=(
                current_user.get(
                    "company_phone"
                )
                or ""
            ),
        )

        company_email = st.text_input(
            t("email"),
            value=(
                current_user.get(
                    "company_email"
                )
                or ""
            ),
        )

        state0 = (
            current_user.get(
                "company_state"
            )
            if current_user.get(
                "company_state"
            ) in STATES
            else "Maharashtra"
        )

        company_state = st.selectbox(
            t("state"),
            STATES,
            index=STATES.index(
                state0
            ),
            format_func=lambda s:
                STATE_LABELS.get(
                    s,
                    s,
                ),
        )

        setup_submit = st.form_submit_button(
            t("get_started"),
            use_container_width=True,
            type="primary",
        )

    if setup_submit:
        if not company_name.strip():
            st.error(
                "Company name is required."
            )

        else:
            with engine.begin() as con:
                con.execute(
                    update(
                        users
                    )
                    .where(
                        users.c.id
                        == USER_ID
                    )
                    .values(
                        setup_complete=True,
                        company_name=company_name.strip(),
                        company_address=company_address.strip(),
                        company_gstin=company_gstin.strip(),
                        company_phone=company_phone.strip(),
                        company_email=company_email.strip(),
                        company_state=company_state,
                    )
                )

            st.rerun()

    st.stop()

# ============================================================
# PDF HELPERS
# ============================================================

def register_pdf_font():
    candidates = [
        "C:/Windows/Fonts/Nirmala.ttf",
        "C:/Windows/Fonts/mangal.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]

    for path in candidates:
        if os.path.exists(
            path
        ):
            try:
                pdfmetrics.registerFont(
                    TTFont(
                        "GSTFont",
                        path,
                    )
                )

                return "GSTFont"

            except Exception:
                pass

    return "Helvetica"


PDF_FONT = register_pdf_font()


def pdf_text(
    pdf,
    x,
    y,
    text,
    size=9,
    bold=False,
):
    font = PDF_FONT

    if (
        PDF_FONT == "Helvetica"
        and bold
    ):
        font = "Helvetica-Bold"

    pdf.setFont(
        font,
        size,
    )

    pdf.drawString(
        x,
        y,
        str(
            text
            or ""
        ),
    )

# ============================================================
# CREATE PDF
# ============================================================

def make_invoice_pdf(
    inv,
    business,
):
    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    width, height = A4

    pdf.setTitle(
        f"SHIVPRUBA BILLING - "
        f"{inv['invoice_number']}"
    )

    pdf_text(
        pdf,
        18 * mm,
        height - 18 * mm,
        "TAX INVOICE",
        16,
        True,
    )

    pdf_text(
        pdf,
        18 * mm,
        height - 29 * mm,
        business.get(
            "company_name",
            "",
        ),
        13,
        True,
    )

    pdf_text(
        pdf,
        18 * mm,
        height - 36 * mm,
        business.get(
            "company_address",
            "",
        ),
        9,
    )

    pdf_text(
        pdf,
        18 * mm,
        height - 43 * mm,
        f"GSTIN: "
        f"{business.get('company_gstin','')}",
        9,
    )

    pdf_text(
        pdf,
        18 * mm,
        height - 50 * mm,
        f"Phone: "
        f"{business.get('company_phone','')}",
        9,
    )

    pdf_text(
        pdf,
        18 * mm,
        height - 57 * mm,
        f"Email: "
        f"{business.get('company_email','')}",
        9,
    )

    pdf_text(
        pdf,
        118 * mm,
        height - 29 * mm,
        f"Invoice No: "
        f"{inv['invoice_number']}",
        9,
        True,
    )

    pdf_text(
        pdf,
        118 * mm,
        height - 37 * mm,
        f"Date: "
        f"{inv['invoice_date']}",
        9,
    )

    pdf_text(
        pdf,
        118 * mm,
        height - 45 * mm,
        f"Place of Supply: "
        f"{inv.get('place_of_supply','')}",
        9,
    )

    y = height - 75 * mm

    pdf.line(
        18 * mm,
        y,
        192 * mm,
        y,
    )

    y -= 8 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        "Bill To:",
        10,
        True,
    )

    y -= 7 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        inv.get(
            "customer_name",
            "",
        ),
        10,
        True,
    )

    y -= 6 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        inv.get(
            "customer_address",
            "",
        ),
        9,
    )

    y -= 6 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        f"GSTIN: "
        f"{inv.get('customer_gstin','')}",
        9,
    )

    y -= 6 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        f"State: "
        f"{inv.get('customer_state','')}",
        9,
    )

    y -= 10 * mm

    pdf.line(
        18 * mm,
        y,
        192 * mm,
        y,
    )

    y -= 7 * mm

    headers = [
        "#",
        "Description",
        "HSN",
        "Qty",
        "Rate",
        "GST%",
        "Amount",
    ]

    xs = [
        18,
        28,
        92,
        116,
        132,
        157,
        174,
    ]

    for x, header in zip(
        xs,
        headers,
    ):
        pdf_text(
            pdf,
            x * mm,
            y,
            header,
            8,
            True,
        )

    y -= 6 * mm

    pdf.line(
        18 * mm,
        y,
        192 * mm,
        y,
    )

    y -= 6 * mm

    for index, item in enumerate(
        inv.get(
            "items",
            [],
        ),
        1,
    ):
        if y < 45 * mm:
            pdf.showPage()
            y = height - 25 * mm

        pdf_text(
            pdf,
            18 * mm,
            y,
            index,
            8,
        )

        pdf_text(
            pdf,
            28 * mm,
            y,
            str(
                item.get(
                    "desc",
                    "",
                )
            )[:30],
            8,
        )

        pdf_text(
            pdf,
            92 * mm,
            y,
            item.get(
                "hsn",
                "",
            ),
            8,
        )

        pdf_text(
            pdf,
            116 * mm,
            y,
            f"{float(item.get('qty',0)):g}",
            8,
        )

        pdf_text(
            pdf,
            132 * mm,
            y,
            f"{float(item.get('rate',0)):,.2f}",
            8,
        )

        pdf_text(
            pdf,
            157 * mm,
            y,
            f"{float(item.get('gst_rate',0)):g}",
            8,
        )

        pdf_text(
            pdf,
            174 * mm,
            y,
            f"{float(item.get('amount',0)):,.2f}",
            8,
        )

        y -= 7 * mm

    y -= 4 * mm

    pdf.line(
        112 * mm,
        y,
        192 * mm,
        y,
    )

    y -= 7 * mm

    pdf_text(
        pdf,
        120 * mm,
        y,
        "Taxable Value",
        9,
    )

    pdf_text(
        pdf,
        170 * mm,
        y,
        f"{inv.get('taxable_value',0):,.2f}",
        9,
    )

    y -= 6 * mm

    if inv.get(
        "is_intra_state"
    ):
        pdf_text(
            pdf,
            120 * mm,
            y,
            "CGST",
            9,
        )

        pdf_text(
            pdf,
            170 * mm,
            y,
            f"{inv.get('cgst',0):,.2f}",
            9,
        )

        y -= 6 * mm

        pdf_text(
            pdf,
            120 * mm,
            y,
            "SGST",
            9,
        )

        pdf_text(
            pdf,
            170 * mm,
            y,
            f"{inv.get('sgst',0):,.2f}",
            9,
        )

    else:
        pdf_text(
            pdf,
            120 * mm,
            y,
            "IGST",
            9,
        )

        pdf_text(
            pdf,
            170 * mm,
            y,
            f"{inv.get('igst',0):,.2f}",
            9,
        )

    y -= 8 * mm

    pdf.line(
        112 * mm,
        y,
        192 * mm,
        y,
    )

    y -= 8 * mm

    pdf_text(
        pdf,
        120 * mm,
        y,
        "GRAND TOTAL",
        11,
        True,
    )

    pdf_text(
        pdf,
        166 * mm,
        y,
        f"Rs. "
        f"{inv.get('grand_total',0):,.2f}",
        11,
        True,
    )

    pdf_text(
        pdf,
        18 * mm,
        18 * mm,
        "Generated with SHIVPRUBA BILLING",
        8,
    )

    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()

# ============================================================
# LOAD USER DATA
# ============================================================

current_user = get_user(
    USER_ID
)

customers = get_customers(
    USER_ID
)

products = get_products(
    USER_ID
)

ensure_inventory_rows(
    USER_ID,
    products,
)

suppliers = get_suppliers(
    USER_ID
)

purchases = get_purchases(
    USER_ID
)

invoices = get_invoices(
    USER_ID
)

payments = get_payments(
    USER_ID
)

inventory = get_inventory(
    USER_ID
)

stock_ledger = get_stock_ledger(
    USER_ID
)

app_settings = ensure_user_settings(
    USER_ID
)

INV_MAP = {
    int(x["product_id"]): x
    for x in inventory
}

PAID_MAP = make_paid_map(
    payments
)

# ============================================================
# MENU
# ============================================================

MENU_ICONS = {
    "dashboard": "🏠",
    "new_invoice": "🧾",
    "purchases": "📥",
    "customers": "👥",
    "customer_ledger": "📒",
    "suppliers": "🏭",
    "products": "📦",
    "stock": "📊",
    "invoice_history": "🕘",
    "purchase_history": "📚",
    "reports": "📈",
    "settings": "⚙️",
}

menu = st.sidebar.radio(
    t("menu"),
    list(
        MENU_ICONS.keys()
    ),
    format_func=lambda x:
        f"{MENU_ICONS[x]} "
        f"{t(x)}",
)

st.sidebar.markdown(
    "---"
)

st.sidebar.caption(
    current_user.get(
        "company_name",
        "",
    )
)

st.sidebar.caption(
    t("version")
)

if st.sidebar.button(
    f"🚪 {t('logout')}",
    use_container_width=True,
):
    st.session_state.user_id = None
    st.rerun()

# ============================================================
# DASHBOARD
# ============================================================

if menu == "dashboard":
    st.title(
        f"🏠 {t('dashboard')}"
    )

    total_sales = sum(
        float(
            i.get(
                "grand_total",
                0,
            )
        )
        for i in invoices
    )

    total_tax = sum(
        float(
            i.get(
                "cgst",
                0,
            )
        )
        + float(
            i.get(
                "sgst",
                0,
            )
        )
        + float(
            i.get(
                "igst",
                0,
            )
        )
        for i in invoices
    )

    total_purchases = sum(
        float(
            p.get(
                "grand_total",
                0,
            )
        )
        for p in purchases
    )

    stock_value = sum(
        float(
            x.get(
                "current_stock",
                0,
            )
            or 0
        )
        * float(
            x.get(
                "purchase_rate",
                0,
            )
            or 0
        )
        for x in inventory
    )

    today_str = date.today().strftime(
        "%d-%m-%Y"
    )

    today_count = sum(
        1
        for i in invoices
        if i.get(
            "invoice_date"
        ) == today_str
    )

    today_purchase_count = sum(
        1
        for p in purchases
        if p.get(
            "purchase_date"
        ) == today_str
    )

    low_items = [
        x
        for x in inventory
        if (
            x.get(
                "unit"
            )
            != "Service"
        )
        and (
            float(
                x.get(
                    "low_stock_limit",
                    0,
                )
                or 0
            )
            > 0
        )
        and (
            float(
                x.get(
                    "current_stock",
                    0,
                )
                or 0
            )
            <= float(
                x.get(
                    "low_stock_limit",
                    0,
                )
                or 0
            )
        )
    ]

    c1, c2, c3, c4 = st.columns(
        4
    )

    c1.metric(
        t("total_invoices"),
        len(invoices),
    )

    c2.metric(
        t("total_sales"),
        money(
            total_sales
        ),
    )

    c3.metric(
        t("today_invoices"),
        today_count,
    )

    c4.metric(
        t("total_gst"),
        money(
            total_tax
        ),
    )

    c5, c6, c7, c8 = st.columns(
        4
    )

    c5.metric(
        t("total_purchases"),
        money(
            total_purchases
        ),
    )

    c6.metric(
        t("today_purchases"),
        today_purchase_count,
    )

    c7.metric(
        t("stock_value"),
        money(
            stock_value
        ),
    )

    c8.metric(
        t("low_stock"),
        len(
            low_items
        ),
    )

    if low_items:
        product_by_id = {
            int(p["id"]): p
            for p in products
        }

        names = []

        for x in low_items[:8]:
            p = product_by_id.get(
                int(
                    x["product_id"]
                ),
                {},
            )

            names.append(
                f"{p.get('name','Product')}: "
                f"{float(x.get('current_stock',0)):g} "
                f"{x.get('unit','')}"
            )

        st.warning(
            "⚠️ "
            + t("low_stock")
            + ": "
            + " | ".join(
                names
            )
        )

    st.markdown(
        "---"
    )

    a, b = st.columns(
        2
    )

    with a:
        st.subheader(
            t("recent_invoices")
        )

        if not invoices:
            st.info(
                t("no_invoices")
            )

        for inv in invoices[-5:][::-1]:
            with st.expander(
                f"{inv['invoice_number']} | "
                f"{inv['customer_name']} | "
                f"{money(inv['grand_total'])}"
            ):
                st.write(
                    f"**{t('date')}:** "
                    f"{inv['invoice_date']}"
                )

                st.write(
                    f"**{t('grand_total')}:** "
                    f"{money(inv['grand_total'])}"
                )

                st.download_button(
                    t("download_pdf"),
                    make_invoice_pdf(
                        inv,
                        current_user,
                    ),
                    f"{clean_filename(inv['invoice_number'])}.pdf",
                    "application/pdf",
                    key=f"dash_pdf_{inv['id']}",
                )

    with b:
        st.subheader(
            t("recent_purchases")
        )

        if not purchases:
            st.info(
                t("no_purchases")
            )

        for pur in purchases[-5:][::-1]:
            with st.expander(
                f"{pur['bill_number']} | "
                f"{pur['supplier_name']} | "
                f"{money(pur['grand_total'])}"
            ):
                st.write(
                    f"**{t('date')}:** "
                    f"{pur['purchase_date']}"
                )

                st.write(
                    f"**{t('grand_total')}:** "
                    f"{money(pur['grand_total'])}"
                )

# ============================================================
# NEW INVOICE
# ============================================================

elif menu == "new_invoice":
    st.title(
        f"🧾 {t('create_invoice')}"
    )

    left, right = st.columns(
        2
    )

    customer_map = {
        c["name"]: c
        for c in customers
    }

    with left:
        st.subheader(
            t("customer_info")
        )

        choice = st.selectbox(
            t("saved_customer"),
            [
                t("manual_customer")
            ]
            + list(
                customer_map.keys()
            ),
        )

        cdata = customer_map.get(
            choice,
            {},
        )

        customer_name = st.text_input(
            t("customer_name"),
            value=cdata.get(
                "name",
                "",
            ),
            key=f"cn_{choice}",
        )

        customer_address = st.text_area(
            t("customer_address"),
            value=cdata.get(
                "address",
                "",
            ),
            key=f"ca_{choice}",
        )

        customer_gstin = st.text_input(
            t("customer_gstin"),
            value=cdata.get(
                "gstin",
                "",
            ),
            key=f"cg_{choice}",
        )

        cstate = (
            cdata.get(
                "state",
                "Maharashtra",
            )
            if cdata.get(
                "state",
                "Maharashtra",
            ) in STATES
            else "Maharashtra"
        )

        customer_state = st.selectbox(
            t("customer_state"),
            STATES,
            index=STATES.index(
                cstate
            ),
            format_func=lambda s:
                STATE_LABELS.get(
                    s,
                    s,
                ),
            key=f"cs_{choice}",
        )

    with right:
        st.subheader(
            t("invoice_details")
        )

        prefix = (
            app_settings.get(
                "invoice_prefix"
            )
            or "INV"
        ).strip() or "INV"

        suggested = (
            f"{prefix}-"
            f"{datetime.now().strftime('%Y%m%d')}-"
            f"{len(invoices)+1:03d}"
        )

        invoice_number = st.text_input(
            t("invoice_number"),
            value=suggested,
        )

        inv_date = st.date_input(
            t("invoice_date"),
            value=date.today(),
        )

        place_supply = st.selectbox(
            t("place_of_supply"),
            STATES,
            index=STATES.index(
                customer_state
            ),
            format_func=lambda s:
                STATE_LABELS.get(
                    s,
                    s,
                ),
        )

    st.markdown(
        "---"
    )

    st.subheader(
        f"📦 {t('items')}"
    )

    nitems = int(
        st.number_input(
            t("number_of_items"),
            min_value=1,
            max_value=20,
            value=1,
            step=1,
        )
    )

    pmap = {
        p["name"]: p
        for p in products
    }

    invoice_items = []

    for i in range(
        nitems
    ):
        st.markdown(
            f"**{t('item')} "
            f"{i+1}**"
        )

        pchoice = st.selectbox(
            t("saved_product"),
            [
                t("custom_item")
            ]
            + list(
                pmap.keys()
            ),
            key=f"pc_{i}",
        )

        pdata = pmap.get(
            pchoice,
            {},
        )

        product_id = (
            int(
                pdata["id"]
            )
            if pdata
            else None
        )

        invdata = (
            INV_MAP.get(
                product_id,
                {},
            )
            if product_id
            else {}
        )

        if product_id:
            st.caption(
                f"{t('current_stock')}: "
                f"{float(invdata.get('current_stock',0) or 0):g} "
                f"{invdata.get('unit','Pcs')}"
            )

        a, b, c, d, e = st.columns(
            [
                3,
                1.2,
                1,
                1.3,
                1.1,
            ]
        )

        with a:
            desc = st.text_input(
                t("description"),
                value=pdata.get(
                    "name",
                    "",
                ),
                key=(
                    f"desc_"
                    f"{i}_"
                    f"{pchoice}"
                ),
            )

        with b:
            hsn = st.text_input(
                t("hsn"),
                value=pdata.get(
                    "hsn",
                    "",
                ),
                key=(
                    f"hsn_"
                    f"{i}_"
                    f"{pchoice}"
                ),
            )

        with c:
            qty = st.number_input(
                t("quantity"),
                min_value=0.01,
                value=1.0,
                step=1.0,
                key=f"qty_{i}",
            )

        with d:
            rate = st.number_input(
                t("rate"),
                min_value=0.0,
                value=float(
                    pdata.get(
                        "rate",
                        0.0,
                    )
                ),
                step=10.0,
                key=(
                    f"rate_"
                    f"{i}_"
                    f"{pchoice}"
                ),
            )

        with e:
            opts = [
                0,
                5,
                12,
                18,
                28,
            ]

            default_gst = int(
                pdata.get(
                    "gst_rate",
                    18,
                )
            )

            if default_gst not in opts:
                default_gst = 18

            gst = st.selectbox(
                t("gst_rate"),
                opts,
                index=opts.index(
                    default_gst
                ),
                key=(
                    f"gst_"
                    f"{i}_"
                    f"{pchoice}"
                ),
            )

        track_stock = bool(
            product_id
            and invdata.get(
                "unit"
            ) != "Service"
        )

        if (
            track_stock
            and float(qty)
            > float(
                invdata.get(
                    "current_stock",
                    0,
                )
                or 0
            )
        ):
            st.warning(
                t("insufficient_stock")
            )

        invoice_items.append(
            {
                "product_id": product_id,
                "track_stock": track_stock,
                "desc": desc,
                "hsn": hsn,
                "qty": float(qty),
                "rate": float(rate),
                "gst_rate": float(gst),
                "amount": (
                    float(qty)
                    * float(rate)
                ),
            }
        )

        st.markdown(
            "---"
        )

    if st.button(
        t("save_invoice"),
        use_container_width=True,
        type="primary",
    ):
        if not customer_name.strip():
            st.error(
                t("customer_required")
            )

        elif any(
            i["invoice_number"]
            == invoice_number.strip()

            for i in invoices
        ):
            st.error(
                t("invoice_duplicate")
            )

        elif any(
            x.get(
                "track_stock"
            )
            and x.get(
                "product_id"
            )
            and (
                float(
                    x.get(
                        "qty",
                        0,
                    )
                )
                > float(
                    INV_MAP.get(
                        int(
                            x["product_id"]
                        ),
                        {},
                    ).get(
                        "current_stock",
                        0,
                    )
                    or 0
                )
            )

            for x in invoice_items
        ):
            st.error(
                t("insufficient_stock")
            )

        else:
            taxable = sum(
                x["amount"]
                for x in invoice_items
            )

            intra = (
                current_user.get(
                    "company_state"
                )
                == place_supply
            )

            cgst = 0.0
            sgst = 0.0
            igst = 0.0

            for x in invoice_items:
                tax = (
                    x["amount"]
                    * x["gst_rate"]
                    / 100
                )

                if intra:
                    cgst += tax / 2
                    sgst += tax / 2

                else:
                    igst += tax

            grand = (
                taxable
                + cgst
                + sgst
                + igst
            )

            try:
                with engine.begin() as con:
                    result = con.execute(
                        insert(
                            invoices_table
                        ).values(
                            user_id=USER_ID,
                            invoice_number=invoice_number.strip(),
                            invoice_date=inv_date.strftime("%d-%m-%Y"),
                            customer_name=customer_name.strip(),
                            customer_address=customer_address.strip(),
                            customer_gstin=customer_gstin.strip(),
                            customer_state=customer_state,
                            place_of_supply=place_supply,
                            items_json=json.dumps(
                                invoice_items,
                                ensure_ascii=False,
                            ),
                            taxable_value=taxable,
                            cgst=cgst,
                            sgst=sgst,
                            igst=igst,
                            grand_total=grand,
                            is_intra_state=intra,
                            created_at=datetime.utcnow(),
                        )
                    )

                    inv_id = (
                        result
                        .inserted_primary_key[0]
                    )

                    for item in invoice_items:
                        if (
                            item.get(
                                "product_id"
                            )
                            and item.get(
                                "track_stock"
                            )
                        ):
                            change_stock(
                                con,
                                USER_ID,
                                int(
                                    item["product_id"]
                                ),
                                -float(
                                    item["qty"]
                                ),
                                "SALE",
                                "INVOICE",
                                inv_id,
                                invoice_number.strip(),
                                f"Sold: "
                                f"{item.get('desc','')}",
                            )

            except IntegrityError:
                st.error(
                    t("invoice_duplicate")
                )
                st.stop()

            except ValueError as exc:
                if str(exc) == "INSUFFICIENT_STOCK":
                    st.error(
                        t("insufficient_stock")
                    )
                    st.stop()

                raise

            if (
                customer_name.strip()
                and not any(
                    c["name"]
                    .strip()
                    .lower()
                    == customer_name
                    .strip()
                    .lower()

                    for c in customers
                )
            ):
                with engine.begin() as con:
                    con.execute(
                        insert(
                            customers_table
                        ).values(
                            user_id=USER_ID,
                            name=customer_name.strip(),
                            address=customer_address.strip(),
                            gstin=customer_gstin.strip(),
                            state=customer_state,
                            created_at=datetime.utcnow(),
                        )
                    )

            new_inv = {
                "id": inv_id,
                "invoice_number":
                    invoice_number.strip(),
                "invoice_date":
                    inv_date.strftime(
                        "%d-%m-%Y"
                    ),
                "customer_name":
                    customer_name.strip(),
                "customer_address":
                    customer_address.strip(),
                "customer_gstin":
                    customer_gstin.strip(),
                "customer_state":
                    customer_state,
                "place_of_supply":
                    place_supply,
                "items":
                    invoice_items,
                "taxable_value":
                    taxable,
                "cgst":
                    cgst,
                "sgst":
                    sgst,
                "igst":
                    igst,
                "grand_total":
                    grand,
                "is_intra_state":
                    intra,
            }

            st.success(
                t("invoice_saved")
            )

            x, y, z = st.columns(
                3
            )

            x.metric(
                t("taxable_value"),
                money(
                    taxable
                ),
            )

            y.metric(
                (
                    "CGST + SGST"
                    if intra
                    else "IGST"
                ),
                money(
                    cgst + sgst
                    if intra
                    else igst
                ),
            )

            z.metric(
                t("grand_total"),
                money(
                    grand
                ),
            )

            st.download_button(
                t("download_pdf"),
                make_invoice_pdf(
                    new_inv,
                    current_user,
                ),
                f"{clean_filename(invoice_number)}.pdf",
                "application/pdf",
                use_container_width=True,
            )

# ============================================================
# PURCHASES / STOCK IN
# ============================================================

elif menu == "purchases":
    st.title(
        f"📥 {t('create_purchase')}"
    )

    left, right = st.columns(
        2
    )

    supplier_map = {
        s["name"]: s
        for s in suppliers
    }

    with left:
        st.subheader(
            t("suppliers")
        )

        supplier_choice = st.selectbox(
            t("saved_supplier"),
            [
                t("manual_supplier")
            ]
            + list(
                supplier_map.keys()
            ),
            key="purchase_supplier_choice",
        )

        sdata = supplier_map.get(
            supplier_choice,
            {},
        )

        supplier_name = st.text_input(
            t("supplier_name"),
            value=sdata.get(
                "name",
                "",
            ),
        )

        supplier_address = st.text_area(
            t("supplier_address"),
            value=sdata.get(
                "address",
                "",
            ),
        )

        supplier_gstin = st.text_input(
            t("supplier_gstin"),
            value=sdata.get(
                "gstin",
                "",
            ),
        )

        sstate0 = (
            sdata.get(
                "state",
                "Maharashtra",
            )
            if sdata.get(
                "state",
                "Maharashtra",
            ) in STATES
            else "Maharashtra"
        )

        supplier_state = st.selectbox(
            t("supplier_state"),
            STATES,
            index=STATES.index(
                sstate0
            ),
            format_func=lambda x:
                STATE_LABELS.get(
                    x,
                    x,
                ),
        )

    with right:
        st.subheader(
            t("invoice_details")
        )

        bill_number = st.text_input(
            t("purchase_bill_number")
        )

        pur_date = st.date_input(
            t("purchase_date"),
            value=date.today(),
        )

    st.markdown(
        "---"
    )

    st.subheader(
        f"📦 {t('items')}"
    )

    nitems = int(
        st.number_input(
            t("number_of_items"),
            min_value=1,
            max_value=30,
            value=1,
            step=1,
            key="purchase_nitems",
        )
    )

    pmap = {
        p["name"]: p
        for p in products
    }

    purchase_items = []

    if not products:
        st.warning(
            t("no_products")
        )

    for i in range(
        nitems
    ):
        st.markdown(
            f"**{t('item')} "
            f"{i+1}**"
        )

        pchoice = st.selectbox(
            t("saved_product"),
            list(
                pmap.keys()
            )
            if pmap
            else ["-"],
            key=f"pur_pc_{i}",
        )

        pdata = pmap.get(
            pchoice,
            {},
        )

        product_id = (
            int(
                pdata["id"]
            )
            if pdata
            else None
        )

        invdata = (
            INV_MAP.get(
                product_id,
                {},
            )
            if product_id
            else {}
        )

        a, b, c, d, e = st.columns(
            [
                3,
                1.2,
                1,
                1.3,
                1.1,
            ]
        )

        with a:
            desc = st.text_input(
                t("description"),
                value=pdata.get(
                    "name",
                    "",
                ),
                key=f"pur_desc_{i}",
            )

        with b:
            hsn = st.text_input(
                t("hsn"),
                value=pdata.get(
                    "hsn",
                    "",
                ),
                key=f"pur_hsn_{i}",
            )

        with c:
            qty = st.number_input(
                t("quantity"),
                min_value=0.01,
                value=1.0,
                step=1.0,
                key=f"pur_qty_{i}",
            )

        with d:
            rate = st.number_input(
                t("purchase_rate"),
                min_value=0.0,
                value=float(
                    invdata.get(
                        "purchase_rate",
                        0.0,
                    )
                    or 0.0
                ),
                step=10.0,
                key=f"pur_rate_{i}",
            )

        with e:
            opts = [
                0,
                5,
                12,
                18,
                28,
            ]

            default_gst = (
                int(
                    pdata.get(
                        "gst_rate",
                        18,
                    )
                    or 18
                )
                if pdata
                else 18
            )

            if default_gst not in opts:
                default_gst = 18

            gst = st.selectbox(
                t("gst_rate"),
                opts,
                index=opts.index(
                    default_gst
                ),
                key=f"pur_gst_{i}",
            )

        purchase_items.append(
            {
                "product_id":
                    product_id,
                "desc":
                    desc,
                "hsn":
                    hsn,
                "qty":
                    float(qty),
                "rate":
                    float(rate),
                "gst_rate":
                    float(gst),
                "amount":
                    float(qty)
                    * float(rate),
            }
        )

        st.markdown(
            "---"
        )

    if st.button(
        t("save_purchase"),
        use_container_width=True,
        type="primary",
    ):
        if not supplier_name.strip():
            st.error(
                t("supplier_name")
            )

        elif not bill_number.strip():
            st.error(
                t("purchase_bill_number")
            )

        elif (
            not products
            or any(
                not x.get(
                    "product_id"
                )

                for x in purchase_items
            )
        ):
            st.error(
                t("no_products")
            )

        elif any(
            p.get(
                "bill_number"
            )
            == bill_number.strip()

            for p in purchases
        ):
            st.error(
                t("purchase_duplicate")
            )

        else:
            taxable = sum(
                x["amount"]
                for x in purchase_items
            )

            intra = (
                current_user.get(
                    "company_state"
                )
                == supplier_state
            )

            cgst = 0.0
            sgst = 0.0
            igst = 0.0

            for x in purchase_items:
                tax = (
                    x["amount"]
                    * x["gst_rate"]
                    / 100
                )

                if intra:
                    cgst += tax / 2
                    sgst += tax / 2

                else:
                    igst += tax

            grand = (
                taxable
                + cgst
                + sgst
                + igst
            )

            try:
                with engine.begin() as con:
                    result = con.execute(
                        insert(
                            purchases_table
                        ).values(
                            user_id=USER_ID,
                            bill_number=bill_number.strip(),
                            purchase_date=pur_date.strftime("%d-%m-%Y"),
                            supplier_name=supplier_name.strip(),
                            supplier_address=supplier_address.strip(),
                            supplier_gstin=supplier_gstin.strip(),
                            supplier_state=supplier_state,
                            items_json=json.dumps(
                                purchase_items,
                                ensure_ascii=False,
                            ),
                            taxable_value=taxable,
                            cgst=cgst,
                            sgst=sgst,
                            igst=igst,
                            grand_total=grand,
                            is_intra_state=intra,
                            created_at=datetime.utcnow(),
                        )
                    )

                    purchase_id = (
                        result
                        .inserted_primary_key[0]
                    )

                    for item in purchase_items:
                        pid = int(
                            item["product_id"]
                        )

                        invrow = lock_inventory(
                            con,
                            USER_ID,
                            pid,
                        )

                        if invrow:
                            con.execute(
                                update(
                                    product_inventory_table
                                )
                                .where(
                                    product_inventory_table.c.id
                                    == invrow["id"]
                                )
                                .values(
                                    purchase_rate=float(
                                        item["rate"]
                                    ),
                                    updated_at=datetime.utcnow(),
                                )
                            )

                        change_stock(
                            con,
                            USER_ID,
                            pid,
                            float(
                                item["qty"]
                            ),
                            "PURCHASE",
                            "PURCHASE",
                            purchase_id,
                            bill_number.strip(),
                            f"Purchased: "
                            f"{item.get('desc','')}",
                        )

            except IntegrityError:
                st.error(
                    t("purchase_duplicate")
                )

                st.stop()

            if (
                supplier_name.strip()
                and not any(
                    x["name"]
                    .strip()
                    .lower()
                    == supplier_name
                    .strip()
                    .lower()

                    for x in suppliers
                )
            ):
                with engine.begin() as con:
                    con.execute(
                        insert(
                            suppliers_table
                        ).values(
                            user_id=USER_ID,
                            name=supplier_name.strip(),
                            address=supplier_address.strip(),
                            gstin=supplier_gstin.strip(),
                            state=supplier_state,
                            created_at=datetime.utcnow(),
                        )
                    )

            st.success(
                t("purchase_saved")
            )

            a, b, c = st.columns(
                3
            )

            a.metric(
                t("purchase_taxable"),
                money(
                    taxable
                ),
            )

            b.metric(
                t("purchase_gst"),
                money(
                    cgst + sgst + igst
                ),
            )

            c.metric(
                t("grand_total"),
                money(
                    grand
                ),
            )

            st.rerun()

# ============================================================
# CUSTOMERS
# ============================================================

elif menu == "customers":
    st.title(
        f"👥 {t('customers')}"
    )

    with st.expander(
        f"➕ {t('add_customer')}",
        expanded=not customers,
    ):
        with st.form(
            "customer_form",
            clear_on_submit=True,
        ):
            name = st.text_input(
                t("customer_name")
            )

            address = st.text_area(
                t("customer_address")
            )

            gstin = st.text_input(
                t("customer_gstin")
            )

            state_value = st.selectbox(
                t("customer_state"),
                STATES,
                index=STATES.index(
                    "Maharashtra"
                ),
                format_func=lambda s:
                    STATE_LABELS.get(
                        s,
                        s,
                    ),
            )

            add_customer = st.form_submit_button(
                t("save_customer"),
                use_container_width=True,
            )

        if (
            add_customer
            and name.strip()
        ):
            with engine.begin() as con:
                con.execute(
                    insert(
                        customers_table
                    ).values(
                        user_id=USER_ID,
                        name=name.strip(),
                        address=address.strip(),
                        gstin=gstin.strip(),
                        state=state_value,
                        created_at=datetime.utcnow(),
                    )
                )

            st.success(
                t("customer_saved")
            )

            st.rerun()

    if not customers:
        st.info(
            t("no_customers")
        )

    for customer in customers:
        with st.expander(
            customer["name"]
        ):
            st.write(
                f"**{t('address')}:** "
                f"{customer.get('address','')}"
            )

            st.write(
                f"**GSTIN:** "
                f"{customer.get('gstin','')}"
            )

            st.write(
                f"**{t('state')}:** "
                f"{STATE_LABELS.get(customer.get('state',''), customer.get('state',''))}"
            )

            if st.button(
                f"🗑️ {t('delete')}",
                key=(
                    f"delc_"
                    f"{customer['id']}"
                ),
            ):
                with engine.begin() as con:
                    con.execute(
                        delete(
                            customers_table
                        ).where(
                            customers_table.c.id
                            == customer["id"],

                            customers_table.c.user_id
                            == USER_ID,
                        )
                    )

                st.rerun()

# ============================================================
# CUSTOMER LEDGER
# ============================================================

elif menu == "customer_ledger":
    st.title(
        f"📒 {t('customer_ledger')}"
    )

    total_sales_all = sum(
        float(
            inv.get(
                "grand_total",
                0,
            )
            or 0
        )

        for inv in invoices
    )

    total_paid_all = sum(
        float(
            p.get(
                "amount",
                0,
            )
            or 0
        )

        for p in payments
    )

    total_outstanding_all = max(
        0.0,
        total_sales_all
        - total_paid_all,
    )

    l1, l2, l3 = st.columns(
        3
    )

    l1.metric(
        t("total_sales"),
        money(
            total_sales_all
        ),
    )

    l2.metric(
        t("total_paid"),
        money(
            total_paid_all
        ),
    )

    l3.metric(
        t("total_outstanding"),
        money(
            total_outstanding_all
        ),
    )

    customer_names = sorted(
        {
            str(
                inv.get(
                    "customer_name",
                    "",
                )
            ).strip()

            for inv in invoices

            if str(
                inv.get(
                    "customer_name",
                    "",
                )
            ).strip()
        },
        key=str.lower,
    )

    if not customer_names:
        st.info(
            t("no_invoices")
        )

    else:
        search_customer = st.text_input(
            f"🔎 {t('customer_name')}",
            key="customer_ledger_search",
        ).strip().lower()

        for customer_name in customer_names:
            if (
                search_customer
                and search_customer
                not in customer_name.lower()
            ):
                continue

            customer_invoices = [
                inv

                for inv in invoices

                if (
                    str(
                        inv.get(
                            "customer_name",
                            "",
                        )
                    )
                    .strip()
                    .lower()
                    == customer_name.lower()
                )
            ]

            customer_sales_total = sum(
                float(
                    inv.get(
                        "grand_total",
                        0,
                    )
                    or 0
                )

                for inv in customer_invoices
            )

            customer_paid_total = sum(
                float(
                    PAID_MAP.get(
                        int(
                            inv.get(
                                "id",
                                0,
                            )
                            or 0
                        ),
                        0.0,
                    )
                    or 0.0
                )

                for inv in customer_invoices
            )

            customer_balance_total = max(
                0.0,
                customer_sales_total
                - customer_paid_total,
            )

            with st.expander(
                f"{customer_name} | "
                f"{t('total_sales')}: "
                f"{money(customer_sales_total)} | "
                f"{t('balance_amount')}: "
                f"{money(customer_balance_total)}"
            ):
                c1, c2, c3 = st.columns(
                    3
                )

                c1.metric(
                    t("total_sales"),
                    money(
                        customer_sales_total
                    ),
                )

                c2.metric(
                    t("total_paid"),
                    money(
                        customer_paid_total
                    ),
                )

                c3.metric(
                    t("total_outstanding"),
                    money(
                        customer_balance_total
                    ),
                )

                for inv in customer_invoices[::-1]:
                    (
                        paid_amount,
                        balance,
                        status_key,
                    ) = payment_status_for_invoice(
                        inv,
                        PAID_MAP,
                    )

                    st.write(
                        f"**{inv.get('invoice_number','')}** | "
                        f"{inv.get('invoice_date','')} | "
                        f"{money(inv.get('grand_total',0))} | "
                        f"{t(status_key)} | "
                        f"{t('paid_amount')}: "
                        f"{money(paid_amount)} | "
                        f"{t('balance_amount')}: "
                        f"{money(balance)}"
                    )

# ============================================================
# SUPPLIERS
# ============================================================

elif menu == "suppliers":
    st.title(
        f"🏭 {t('suppliers')}"
    )

    with st.expander(
        f"➕ {t('add_supplier')}",
        expanded=not suppliers,
    ):
        with st.form(
            "supplier_form",
            clear_on_submit=True,
        ):
            name = st.text_input(
                t("supplier_name")
            )

            address = st.text_area(
                t("supplier_address")
            )

            gstin = st.text_input(
                t("supplier_gstin")
            )

            phone = st.text_input(
                t("phone")
            )

            email = st.text_input(
                t("email")
            )

            state_value = st.selectbox(
                t("supplier_state"),
                STATES,
                index=STATES.index(
                    "Maharashtra"
                ),
                format_func=lambda x:
                    STATE_LABELS.get(
                        x,
                        x,
                    ),
            )

            add_supplier = st.form_submit_button(
                t("save_supplier"),
                use_container_width=True,
            )

        if (
            add_supplier
            and name.strip()
        ):
            with engine.begin() as con:
                con.execute(
                    insert(
                        suppliers_table
                    ).values(
                        user_id=USER_ID,
                        name=name.strip(),
                        address=address.strip(),
                        gstin=gstin.strip(),
                        phone=phone.strip(),
                        email=email.strip(),
                        state=state_value,
                        created_at=datetime.utcnow(),
                    )
                )

            st.success(
                t("supplier_saved")
            )

            st.rerun()

    if not suppliers:
        st.info(
            t("no_suppliers")
        )

    for supplier in suppliers:
        purchase_count = sum(
            1

            for p in purchases

            if (
                p.get(
                    "supplier_name",
                    "",
                )
                .strip()
                .lower()
                == supplier["name"]
                .strip()
                .lower()
            )
        )

        with st.expander(
            f"{supplier['name']} | "
            f"{purchase_count} "
            f"{t('purchases')}"
        ):
            st.write(
                f"**{t('address')}:** "
                f"{supplier.get('address','')}"
            )

            st.write(
                f"**GSTIN:** "
                f"{supplier.get('gstin','')}"
            )

            st.write(
                f"**{t('phone')}:** "
                f"{supplier.get('phone','')}"
            )

            st.write(
                f"**{t('email')}:** "
                f"{supplier.get('email','')}"
            )

            st.write(
                f"**{t('state')}:** "
                f"{STATE_LABELS.get(supplier.get('state',''), supplier.get('state',''))}"
            )

            if (
                purchase_count == 0
                and st.button(
                    f"🗑️ {t('delete')}",
                    key=(
                        f"dels_"
                        f"{supplier['id']}"
                    ),
                )
            ):
                with engine.begin() as con:
                    con.execute(
                        delete(
                            suppliers_table
                        ).where(
                            suppliers_table.c.id
                            == supplier["id"],

                            suppliers_table.c.user_id
                            == USER_ID,
                        )
                    )

                st.rerun()

# ============================================================
# PRODUCTS
# ============================================================

elif menu == "products":
    st.title(
        f"📦 {t('products')}"
    )

    with st.expander(
        f"➕ {t('add_product')}",
        expanded=not products,
    ):
        with st.form(
            "product_form",
            clear_on_submit=True,
        ):
            name = st.text_input(
                t("product_name")
            )

            sku = st.text_input(
                t("sku")
            )

            hsn = st.text_input(
                t("hsn")
            )

            unit = st.selectbox(
                t("unit"),
                [
                    "Pcs",
                    "Kg",
                    "Gm",
                    "Ltr",
                    "Ml",
                    "Box",
                    "Pack",
                    "Dozen",
                    "Meter",
                    "Service",
                ],
            )

            purchase_rate = st.number_input(
                t("purchase_rate"),
                min_value=0.0,
                value=0.0,
                step=10.0,
            )

            selling_rate = st.number_input(
                t("selling_rate"),
                min_value=0.0,
                value=0.0,
                step=10.0,
            )

            gst = st.selectbox(
                t("gst_rate"),
                [
                    0,
                    5,
                    12,
                    18,
                    28,
                ],
                index=3,
            )

            opening_stock = st.number_input(
                t("opening_stock"),
                min_value=0.0,
                value=0.0,
                step=1.0,
            )

            low_limit = st.number_input(
                t("low_stock_limit"),
                min_value=0.0,
                value=float(
                    app_settings.get(
                        "default_low_stock",
                        5.0,
                    )
                    or 5.0
                ),
                step=1.0,
            )

            add_product = st.form_submit_button(
                t("save_product"),
                use_container_width=True,
            )

        if (
            add_product
            and name.strip()
        ):
            with engine.begin() as con:
                result = con.execute(
                    insert(
                        products_table
                    ).values(
                        user_id=USER_ID,
                        name=name.strip(),
                        hsn=hsn.strip(),
                        rate=float(
                            selling_rate
                        ),
                        gst_rate=float(
                            gst
                        ),
                        created_at=datetime.utcnow(),
                    )
                )

                pid = int(
                    result
                    .inserted_primary_key[0]
                )

                con.execute(
                    insert(
                        product_inventory_table
                    ).values(
                        user_id=USER_ID,
                        product_id=pid,
                        sku=sku.strip(),
                        unit=unit,
                        purchase_rate=float(
                            purchase_rate
                        ),
                        opening_stock=float(
                            opening_stock
                        ),
                        low_stock_limit=float(
                            low_limit
                        ),
                        current_stock=float(
                            opening_stock
                        ),
                        updated_at=datetime.utcnow(),
                    )
                )

                if float(
                    opening_stock
                ) > 0:
                    con.execute(
                        insert(
                            stock_ledger_table
                        ).values(
                            user_id=USER_ID,
                            product_id=pid,
                            movement_type="OPENING",
                            qty_change=float(
                                opening_stock
                            ),
                            balance_after=float(
                                opening_stock
                            ),
                            reference_type="OPENING",
                            reference_id=0,
                            reference_number="OPENING",
                            note="Opening Stock",
                            created_at=datetime.utcnow(),
                        )
                    )

            st.success(
                t("product_saved")
            )

            st.rerun()

    if not products:
        st.info(
            t("no_products")
        )

    inventory_now = inventory_map(
        USER_ID
    )

    for product in products:
        invrow = inventory_now.get(
            int(
                product["id"]
            ),
            {},
        )

        stock_now = float(
            invrow.get(
                "current_stock",
                0,
            )
            or 0
        )

        low_limit = float(
            invrow.get(
                "low_stock_limit",
                0,
            )
            or 0
        )

        label = product["name"]

        if (
            low_limit > 0
            and stock_now <= low_limit
        ):
            label += " ⚠️"

        with st.expander(
            label
        ):
            st.write(
                f"SKU: "
                f"{invrow.get('sku','')} | "
                f"HSN/SAC: "
                f"{product.get('hsn','')} | "
                f"{t('current_stock')}: "
                f"{stock_now:g} "
                f"{invrow.get('unit','Pcs')} | "
                f"{t('purchase_rate')}: "
                f"{money(invrow.get('purchase_rate',0))} | "
                f"{t('selling_rate')}: "
                f"{money(product.get('rate',0))} | "
                f"GST "
                f"{float(product.get('gst_rate',0)):g}%"
            )

            with st.form(
                f"edit_product_"
                f"{product['id']}"
            ):
                ec1, ec2 = st.columns(
                    2
                )

                with ec1:
                    sku2 = st.text_input(
                        t("sku"),
                        value=(
                            invrow.get(
                                "sku",
                                "",
                            )
                            or ""
                        ),
                        key=(
                            f"sku2_"
                            f"{product['id']}"
                        ),
                    )

                    unit_options = [
                        "Pcs",
                        "Kg",
                        "Gm",
                        "Ltr",
                        "Ml",
                        "Box",
                        "Pack",
                        "Dozen",
                        "Meter",
                        "Service",
                    ]

                    unit0 = (
                        invrow.get(
                            "unit",
                            "Pcs",
                        )
                        if invrow.get(
                            "unit",
                            "Pcs",
                        )
                        in unit_options
                        else "Pcs"
                    )

                    unit2 = st.selectbox(
                        t("unit"),
                        unit_options,
                        index=unit_options.index(
                            unit0
                        ),
                        key=(
                            f"unit2_"
                            f"{product['id']}"
                        ),
                    )

                    purchase2 = st.number_input(
                        t("purchase_rate"),
                        min_value=0.0,
                        value=float(
                            invrow.get(
                                "purchase_rate",
                                0,
                            )
                            or 0
                        ),
                        key=(
                            f"pr2_"
                            f"{product['id']}"
                        ),
                    )

                with ec2:
                    sell2 = st.number_input(
                        t("selling_rate"),
                        min_value=0.0,
                        value=float(
                            product.get(
                                "rate",
                                0,
                            )
                            or 0
                        ),
                        key=(
                            f"sr2_"
                            f"{product['id']}"
                        ),
                    )

                    gst_opts = [
                        0,
                        5,
                        12,
                        18,
                        28,
                    ]

                    g0 = int(
                        product.get(
                            "gst_rate",
                            18,
                        )
                        or 18
                    )

                    g0 = (
                        g0
                        if g0 in gst_opts
                        else 18
                    )

                    gst2 = st.selectbox(
                        t("gst_rate"),
                        gst_opts,
                        index=gst_opts.index(
                            g0
                        ),
                        key=(
                            f"g2_"
                            f"{product['id']}"
                        ),
                    )

                    low2 = st.number_input(
                        t("low_stock_limit"),
                        min_value=0.0,
                        value=float(
                            invrow.get(
                                "low_stock_limit",
                                5,
                            )
                            or 0
                        ),
                        key=(
                            f"low2_"
                            f"{product['id']}"
                        ),
                    )

                update_product_btn = st.form_submit_button(
                    t("save_product_changes"),
                    use_container_width=True,
                )

            if update_product_btn:
                with engine.begin() as con:
                    con.execute(
                        update(
                            products_table
                        )
                        .where(
                            products_table.c.id
                            == product["id"],

                            products_table.c.user_id
                            == USER_ID,
                        )
                        .values(
                            rate=float(
                                sell2
                            ),
                            gst_rate=float(
                                gst2
                            ),
                        )
                    )

                    con.execute(
                        update(
                            product_inventory_table
                        )
                        .where(
                            product_inventory_table.c.product_id
                            == product["id"],

                            product_inventory_table.c.user_id
                            == USER_ID,
                        )
                        .values(
                            sku=sku2.strip(),
                            unit=unit2,
                            purchase_rate=float(
                                purchase2
                            ),
                            low_stock_limit=float(
                                low2
                            ),
                            updated_at=datetime.utcnow(),
                        )
                    )

                st.success(
                    t("product_updated")
                )

                st.rerun()

# ============================================================
# STOCK
# ============================================================

elif menu == "stock":
    st.title(
        f"📊 {t('stock')}"
    )

    product_by_id = {
        int(p["id"]): p
        for p in products
    }

    inv_now = get_inventory(
        USER_ID
    )

    total_stock_value = sum(
        float(
            x.get(
                "current_stock",
                0,
            )
            or 0
        )
        * float(
            x.get(
                "purchase_rate",
                0,
            )
            or 0
        )

        for x in inv_now
    )

    low_items = [
        x
        for x in inv_now
        if (
            x.get(
                "unit"
            )
            != "Service"
        )
        and (
            float(
                x.get(
                    "low_stock_limit",
                    0,
                )
                or 0
            )
            > 0
        )
        and (
            float(
                x.get(
                    "current_stock",
                    0,
                )
                or 0
            )
            <= float(
                x.get(
                    "low_stock_limit",
                    0,
                )
                or 0
            )
        )
    ]

    a, b, c = st.columns(
        3
    )

    a.metric(
        t("products"),
        len(products),
    )

    b.metric(
        t("stock_value"),
        money(
            total_stock_value
        ),
    )

    c.metric(
        t("low_stock"),
        len(
            low_items
        ),
    )

    if products:
        with st.expander(
            f"🛠️ {t('stock_adjustment')}"
        ):
            pname = st.selectbox(
                t("product_name"),
                [
                    p["name"]
                    for p in products
                ],
                key="adjust_product",
            )

            p = next(
                x
                for x in products
                if x["name"] == pname
            )

            qty_adj = st.number_input(
                t("adjustment_qty"),
                value=0.0,
                step=1.0,
            )

            reason = st.text_input(
                t("adjustment_reason")
            )

            if st.button(
                t("apply_adjustment"),
                use_container_width=True,
            ):
                if abs(
                    float(
                        qty_adj
                    )
                ) > 0:
                    try:
                        with engine.begin() as con:
                            change_stock(
                                con,
                                USER_ID,
                                int(
                                    p["id"]
                                ),
                                float(
                                    qty_adj
                                ),
                                "ADJUSTMENT",
                                "ADJUSTMENT",
                                0,
                                "ADJ",
                                reason.strip(),
                            )

                        st.success(
                            t("stock_updated")
                        )

                        st.rerun()

                    except ValueError:
                        st.error(
                            t("insufficient_stock")
                        )

    st.subheader(
        t("current_stock")
    )

    for invrow in inv_now:
        p = product_by_id.get(
            int(
                invrow["product_id"]
            ),
            {},
        )

        if not p:
            continue

        low = (
            invrow.get(
                "unit"
            )
            != "Service"
            and (
                float(
                    invrow.get(
                        "low_stock_limit",
                        0,
                    )
                    or 0
                )
                > 0
            )
            and (
                float(
                    invrow.get(
                        "current_stock",
                        0,
                    )
                    or 0
                )
                <= float(
                    invrow.get(
                        "low_stock_limit",
                        0,
                    )
                    or 0
                )
            )
        )

        with st.expander(
            f"{'⚠️ ' if low else ''}"
            f"{p.get('name','Product')} — "
            f"{float(invrow.get('current_stock',0)):g} "
            f"{invrow.get('unit','')}"
        ):
            c1, c2, c3, c4 = st.columns(
                4
            )

            c1.metric(
                t("current_stock"),
                f"{float(invrow.get('current_stock',0)):g} "
                f"{invrow.get('unit','')}",
            )

            c2.metric(
                t("purchase_rate"),
                money(
                    invrow.get(
                        "purchase_rate",
                        0,
                    )
                ),
            )

            c3.metric(
                t("selling_rate"),
                money(
                    p.get(
                        "rate",
                        0,
                    )
                ),
            )

            c4.metric(
                t("stock_value"),
                money(
                    float(
                        invrow.get(
                            "current_stock",
                            0,
                        )
                        or 0
                    )
                    * float(
                        invrow.get(
                            "purchase_rate",
                            0,
                        )
                        or 0
                    )
                ),
            )

    st.markdown(
        "---"
    )

    st.subheader(
        t("stock_ledger")
    )

    ledger = get_stock_ledger(
        USER_ID
    )

    for row in ledger[:100]:
        p = product_by_id.get(
            int(
                row["product_id"]
            ),
            {},
        )

        sign = (
            "+"
            if float(
                row.get(
                    "qty_change",
                    0,
                )
            ) >= 0
            else ""
        )

        st.write(
            f"**{p.get('name','Product')}** | "
            f"{row.get('movement_type','')} | "
            f"{sign}"
            f"{float(row.get('qty_change',0)):g} | "
            f"Balance "
            f"{float(row.get('balance_after',0)):g} | "
            f"{row.get('reference_number','')} | "
            f"{row.get('note','')}"
        )

# ============================================================
# INVOICE HISTORY
# ============================================================

elif menu == "invoice_history":
    st.title(
        f"🕘 {t('invoice_history')}"
    )

    if not invoices:
        st.info(
            t("no_invoices")
        )

    else:
        search = st.text_input(
            f"🔎 {t('search')}"
        ).strip().lower()

        filtered = (
            invoices

            if not search

            else [
                inv

                for inv in invoices

                if (
                    search
                    in inv[
                        "invoice_number"
                    ].lower()
                )
                or (
                    search
                    in inv[
                        "customer_name"
                    ].lower()
                )
            ]
        )

        st.caption(
            f"{len(filtered)} "
            f"{t('found')}"
        )

        for inv in filtered[::-1]:
            (
                paid_amount,
                balance,
                status_key,
            ) = payment_status_for_invoice(
                inv,
                PAID_MAP,
            )

            with st.expander(
                f"{inv['invoice_number']} | "
                f"{inv['customer_name']} | "
                f"{money(inv['grand_total'])} | "
                f"{inv['invoice_date']} | "
                f"{t(status_key)}"
            ):
                st.write(
                    f"**{t('address')}:** "
                    f"{inv.get('customer_address','')}"
                )

                st.write(
                    f"**GSTIN:** "
                    f"{inv.get('customer_gstin','')}"
                )

                st.write(
                    f"**{t('taxable_value')}:** "
                    f"{money(inv.get('taxable_value',0))}"
                )

                st.write(
                    f"**{t('grand_total')}:** "
                    f"{money(inv.get('grand_total',0))}"
                )

                p1, p2, p3 = st.columns(
                    3
                )

                p1.metric(
                    t("payment_status"),
                    t(
                        status_key
                    ),
                )

                p2.metric(
                    t("paid_amount"),
                    money(
                        paid_amount
                    ),
                )

                p3.metric(
                    t("balance_amount"),
                    money(
                        balance
                    ),
                )

                inv_payments = [
                    p

                    for p in payments

                    if (
                        int(
                            p.get(
                                "invoice_id",
                                0,
                            )
                            or 0
                        )
                        == int(
                            inv["id"]
                        )
                    )
                ]

                if inv_payments:
                    st.markdown(
                        f"**{t('payment_history')}**"
                    )

                    for payment in inv_payments[::-1]:
                        pay_col, delete_col = st.columns(
                            [
                                5,
                                1,
                            ]
                        )

                        with pay_col:
                            note_text = (
                                f" | "
                                f"{payment.get('note','')}"

                                if str(
                                    payment.get(
                                        "note",
                                        "",
                                    )
                                ).strip()

                                else ""
                            )

                            st.write(
                                f"{payment.get('payment_date','')} | "
                                f"**{money(payment.get('amount',0))}**"
                                f"{note_text}"
                            )

                        with delete_col:
                            if st.button(
                                "🗑️ Delete",
                                key=(
                                    f"delete_payment_"
                                    f"{inv['id']}_"
                                    f"{payment['id']}"
                                ),
                                use_container_width=True,
                            ):
                                with engine.begin() as con:
                                    con.execute(
                                        delete(
                                            payments_table
                                        ).where(
                                            payments_table.c.id
                                            == int(
                                                payment["id"]
                                            ),

                                            payments_table.c.user_id
                                            == USER_ID,

                                            payments_table.c.invoice_id
                                            == int(
                                                inv["id"]
                                            ),
                                        )
                                    )

                                st.success(
                                    t("payment_deleted")
                                )

                                st.rerun()

                else:
                    st.caption(
                        t("no_payments")
                    )

                if balance > 0.005:
                    with st.form(
                        f"payment_form_"
                        f"{inv['id']}"
                    ):
                        st.markdown(
                            f"**💳 "
                            f"{t('record_payment')}**"
                        )

                        payment_amount = st.number_input(
                            t("payment_amount"),
                            min_value=0.01,
                            max_value=float(
                                balance
                            ),
                            value=float(
                                balance
                            ),
                            step=1.0,
                            key=(
                                f"pay_amount_"
                                f"{inv['id']}"
                            ),
                        )

                        payment_date = st.date_input(
                            t("payment_date"),
                            value=date.today(),
                            key=(
                                f"pay_date_"
                                f"{inv['id']}"
                            ),
                        )

                        payment_note = st.text_input(
                            t("payment_note"),
                            key=(
                                f"pay_note_"
                                f"{inv['id']}"
                            ),
                        )

                        save_payment = st.form_submit_button(
                            t("record_payment"),
                            use_container_width=True,
                            type="primary",
                        )

                    if save_payment:
                        amount_value = float(
                            payment_amount
                        )

                        date_value = payment_date.strftime(
                            "%d-%m-%Y"
                        )

                        note_value = payment_note.strip()

                        signature = (
                            f"{inv['id']}|"
                            f"{amount_value:.2f}|"
                            f"{date_value}|"
                            f"{note_value}"
                        )

                        now_ts = datetime.now().timestamp()

                        last_sig = st.session_state.get(
                            "_last_payment_signature",
                            "",
                        )

                        last_ts = float(
                            st.session_state.get(
                                "_last_payment_time",
                                0.0,
                            )
                            or 0.0
                        )

                        if amount_value <= 0:
                            st.error(
                                t("payment_amount")
                            )

                        elif (
                            amount_value
                            > balance + 0.005
                        ):
                            st.error(
                                t("payment_too_high")
                            )

                        elif (
                            signature == last_sig
                            and (
                                now_ts
                                - last_ts
                            ) < 5
                        ):
                            st.warning(
                                t("payment_duplicate")
                            )

                        else:
                            with engine.begin() as con:
                                con.execute(
                                    insert(
                                        payments_table
                                    ).values(
                                        user_id=USER_ID,
                                        invoice_id=int(
                                            inv["id"]
                                        ),
                                        amount=amount_value,
                                        payment_date=date_value,
                                        note=note_value,
                                        created_at=datetime.utcnow(),
                                    )
                                )

                            st.session_state[
                                "_last_payment_signature"
                            ] = signature

                            st.session_state[
                                "_last_payment_time"
                            ] = now_ts

                            st.success(
                                t("payment_saved")
                            )

                            st.rerun()

                st.download_button(
                    t("download_pdf"),
                    make_invoice_pdf(
                        inv,
                        current_user,
                    ),
                    f"{clean_filename(inv['invoice_number'])}.pdf",
                    "application/pdf",
                    key=(
                        f"hist_"
                        f"{inv['id']}"
                    ),
                )

# ============================================================
# PURCHASE HISTORY
# ============================================================

elif menu == "purchase_history":
    st.title(
        f"📚 {t('purchase_history')}"
    )

    if not purchases:
        st.info(
            t("no_purchases")
        )

    else:
        search = st.text_input(
            f"🔎 {t('search')}",
            key="purchase_search",
        ).strip().lower()

        filtered = (
            purchases

            if not search

            else [
                p

                for p in purchases

                if (
                    search
                    in p.get(
                        "bill_number",
                        "",
                    ).lower()
                )
                or (
                    search
                    in p.get(
                        "supplier_name",
                        "",
                    ).lower()
                )
            ]
        )

        st.caption(
            f"{len(filtered)} "
            f"{t('purchases')}"
        )

        for pur in filtered[::-1]:
            with st.expander(
                f"{pur['bill_number']} | "
                f"{pur['supplier_name']} | "
                f"{money(pur['grand_total'])} | "
                f"{pur['purchase_date']}"
            ):
                st.write(
                    f"**{t('address')}:** "
                    f"{pur.get('supplier_address','')}"
                )

                st.write(
                    f"**GSTIN:** "
                    f"{pur.get('supplier_gstin','')}"
                )

                st.write(
                    f"**{t('purchase_taxable')}:** "
                    f"{money(pur.get('taxable_value',0))}"
                )

                st.write(
                    f"**{t('purchase_gst')}:** "
                    f"{money(float(pur.get('cgst',0)) + float(pur.get('sgst',0)) + float(pur.get('igst',0)))}"
                )

                st.write(
                    f"**{t('grand_total')}:** "
                    f"{money(pur.get('grand_total',0))}"
                )

                for item in pur.get(
                    "items",
                    [],
                ):
                    st.caption(
                        f"{item.get('desc','')} — "
                        f"{float(item.get('qty',0)):g} × "
                        f"{money(item.get('rate',0))}"
                    )

# ============================================================
# REPORTS
# ============================================================

elif menu == "reports":
    st.title(
        f"📈 {t('reports')}"
    )

    r1, r2 = st.columns(
        2
    )

    with r1:
        date_from = st.date_input(
            t("date_from"),
            value=date.today().replace(
                day=1
            ),
            key="report_from",
        )

    with r2:
        date_to = st.date_input(
            t("date_to"),
            value=date.today(),
            key="report_to",
        )

    filtered_invoices = [
        i
        for i in invoices
        if (
            parse_app_date(
                i.get(
                    "invoice_date"
                )
            ) is None
            or (
                date_from
                <= parse_app_date(
                    i.get(
                        "invoice_date"
                    )
                )
                <= date_to
            )
        )
    ]

    filtered_purchases = [
        p
        for p in purchases
        if (
            parse_app_date(
                p.get(
                    "purchase_date"
                )
            ) is None
            or (
                date_from
                <= parse_app_date(
                    p.get(
                        "purchase_date"
                    )
                )
                <= date_to
            )
        )
    ]

    taxable = sum(
        float(
            i.get(
                "taxable_value",
                0,
            )
        )

        for i in filtered_invoices
    )

    cgst_total = sum(
        float(
            i.get(
                "cgst",
                0,
            )
        )

        for i in filtered_invoices
    )

    sgst_total = sum(
        float(
            i.get(
                "sgst",
                0,
            )
        )

        for i in filtered_invoices
    )

    igst_total = sum(
        float(
            i.get(
                "igst",
                0,
            )
        )

        for i in filtered_invoices
    )

    total = sum(
        float(
            i.get(
                "grand_total",
                0,
            )
        )

        for i in filtered_invoices
    )

    purchase_taxable = sum(
        float(
            p.get(
                "taxable_value",
                0,
            )
        )

        for p in filtered_purchases
    )

    purchase_gst = sum(
        float(
            p.get(
                "cgst",
                0,
            )
        )
        + float(
            p.get(
                "sgst",
                0,
            )
        )
        + float(
            p.get(
                "igst",
                0,
            )
        )

        for p in filtered_purchases
    )

    purchase_total = sum(
        float(
            p.get(
                "grand_total",
                0,
            )
        )

        for p in filtered_purchases
    )

    st.subheader(
        t("sales_summary")
    )

    a, b, c = st.columns(
        3
    )

    a.metric(
        t("taxable_sales"),
        money(
            taxable
        ),
    )

    b.metric(
        t("total_gst"),
        money(
            cgst_total
            + sgst_total
            + igst_total
        ),
    )

    c.metric(
        t("total_sales"),
        money(
            total
        ),
    )

    d, e, f = st.columns(
        3
    )

    d.metric(
        t("cgst"),
        money(
            cgst_total
        ),
    )

    e.metric(
        t("sgst"),
        money(
            sgst_total
        ),
    )

    f.metric(
        t("igst"),
        money(
            igst_total
        ),
    )

    st.subheader(
        t("purchase_summary")
    )

    p1, p2, p3 = st.columns(
        3
    )

    p1.metric(
        t("purchase_taxable"),
        money(
            purchase_taxable
        ),
    )

    p2.metric(
        t("purchase_gst"),
        money(
            purchase_gst
        ),
    )

    p3.metric(
        t("total_purchases"),
        money(
            purchase_total
        ),
    )

    st.markdown(
        "---"
    )

    c1, c2 = st.columns(
        2
    )

    with c1:
        st.subheader(
            t("customer_sales")
        )

        customer_totals = {}

        for inv in filtered_invoices:
            customer_totals[
                inv.get(
                    "customer_name",
                    "",
                )
            ] = (
                customer_totals.get(
                    inv.get(
                        "customer_name",
                        "",
                    ),
                    0.0,
                )
                + float(
                    inv.get(
                        "grand_total",
                        0,
                    )
                )
            )

        for name, value in sorted(
            customer_totals.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )[:20]:
            st.write(
                f"{name}: "
                f"**{money(value)}**"
            )

    with c2:
        st.subheader(
            t("supplier_purchases")
        )

        supplier_totals = {}

        for pur in filtered_purchases:
            supplier_totals[
                pur.get(
                    "supplier_name",
                    "",
                )
            ] = (
                supplier_totals.get(
                    pur.get(
                        "supplier_name",
                        "",
                    ),
                    0.0,
                )
                + float(
                    pur.get(
                        "grand_total",
                        0,
                    )
                )
            )

        for name, value in sorted(
            supplier_totals.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )[:20]:
            st.write(
                f"{name}: "
                f"**{money(value)}**"
            )

    st.subheader(
        t("product_sales")
    )

    product_totals = {}

    for inv in filtered_invoices:
        for item in inv.get(
            "items",
            [],
        ):
            name = item.get(
                "desc",
                "",
            )

            product_totals[
                name
            ] = (
                product_totals.get(
                    name,
                    0.0,
                )
                + float(
                    item.get(
                        "amount",
                        0,
                    )
                )
            )

    for name, value in sorted(
        product_totals.items(),
        key=lambda kv: kv[1],
        reverse=True,
    )[:30]:
        st.write(
            f"{name}: "
            f"**{money(value)}**"
        )

# ============================================================
# SETTINGS
# ============================================================

elif menu == "settings":
    st.title(
        f"⚙️ {t('settings')}"
    )

    st.subheader(
        t("company_profile")
    )

    with st.form(
        "settings_form"
    ):
        company_name = st.text_input(
            t("company_name"),
            value=(
                current_user.get(
                    "company_name"
                )
                or ""
            ),
        )

        company_address = st.text_area(
            t("address"),
            value=(
                current_user.get(
                    "company_address"
                )
                or ""
            ),
        )

        company_gstin = st.text_input(
            t("gstin"),
            value=(
                current_user.get(
                    "company_gstin"
                )
                or ""
            ),
        )

        company_phone = st.text_input(
            t("phone"),
            value=(
                current_user.get(
                    "company_phone"
                )
                or ""
            ),
        )

        company_email = st.text_input(
            t("email"),
            value=(
                current_user.get(
                    "company_email"
                )
                or ""
            ),
        )

        state0 = (
            current_user.get(
                "company_state"
            )
            if current_user.get(
                "company_state"
            ) in STATES
            else "Maharashtra"
        )

        company_state = st.selectbox(
            t("state"),
            STATES,
            index=STATES.index(
                state0
            ),
            format_func=lambda s:
                STATE_LABELS.get(
                    s,
                    s,
                ),
        )

        invoice_prefix = st.text_input(
            t("invoice_prefix"),
            value=(
                app_settings.get(
                    "invoice_prefix"
                )
                or "INV"
            ),
        )

        default_low_stock = st.number_input(
            t("default_low_stock"),
            min_value=0.0,
            value=float(
                app_settings.get(
                    "default_low_stock",
                    5.0,
                )
                or 5.0
            ),
            step=1.0,
        )

        save_settings = st.form_submit_button(
            t("save_settings"),
            use_container_width=True,
            type="primary",
        )

    if save_settings:
        with engine.begin() as con:
            con.execute(
                update(
                    users
                )
                .where(
                    users.c.id
                    == USER_ID
                )
                .values(
                    company_name=company_name.strip(),
                    company_address=company_address.strip(),
                    company_gstin=company_gstin.strip(),
                    company_phone=company_phone.strip(),
                    company_email=company_email.strip(),
                    company_state=company_state,
                )
            )

            con.execute(
                update(
                    user_settings_table
                )
                .where(
                    user_settings_table.c.user_id
                    == USER_ID
                )
                .values(
                    invoice_prefix=(
                        invoice_prefix.strip()
                        or "INV"
                    ),
                    default_low_stock=float(
                        default_low_stock
                    ),
                    updated_at=datetime.utcnow(),
                )
            )

        st.success(
            t("settings_saved")
        )

        st.rerun()

    st.markdown(
        "---"
    )

    st.subheader(
        f"💾 {t('backup')}"
    )

    st.caption(
        t("backup_help")
    )

    backup_data = {
        "generated_at":
            datetime.utcnow().isoformat(),

        "business": {
            key: current_user.get(
                key
            )

            for key in [
                "company_name",
                "company_address",
                "company_gstin",
                "company_phone",
                "company_email",
                "company_state",
            ]
        },

        "customers":
            customers,

        "suppliers":
            suppliers,

        "products":
            products,

        "inventory":
            get_inventory(
                USER_ID
            ),

        "purchases":
            purchases,

        "stock_ledger":
            get_stock_ledger(
                USER_ID
            ),

        "invoices":
            invoices,

        "payments":
            get_payments(
                USER_ID
            ),
    }

    st.download_button(
        t("download_backup"),

        json.dumps(
            backup_data,
            ensure_ascii=False,
            indent=2,
            default=str,
        ).encode(
            "utf-8"
        ),

        "gst_sathi_backup.json",

        "application/json",

        use_container_width=True,
    )

    st.markdown(
        "---"
    )

    st.subheader(
        f"📱 {t('phone_install')}"
    )

    st.info(
        t("phone_install_help")
    )
