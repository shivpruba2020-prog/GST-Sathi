import io
import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import streamlit as st
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
# SHIVPRUBA BILLING V5.0 - OFFLINE 10 LANGUAGE EDITION
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_FILE = BASE_DIR / "gst_sathi.db"
APP_NAME = "SHIVPRUBA BILLING"
APP_VERSION = "Version 5.2 | SHIVPRUBA BILLING"


def now_naive():
    return datetime.now().replace(microsecond=0)


def make_icon():
    img = Image.new("RGB", (256, 256), "white")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((16, 16, 240, 240), radius=48, fill=(18, 91, 190))
    d.rounded_rectangle((42, 42, 214, 214), radius=28, fill="white")
    d.text((78, 82), "SB", fill=(18, 91, 190))
    d.text((62, 132), "BILL", fill=(18, 91, 190))
    return img


APP_ICON = make_icon()
st.set_page_config(
    page_title=APP_NAME,
    page_icon="shivpruba_billing_icon_final.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# OFFLINE LANGUAGE PACKS
# No Google Translate / internet dependency.
# ============================================================
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिन्दी - Hindi",
    "mr": "मराठी - Marathi",
    "gu": "ગુજરાતી - Gujarati",
    "bn": "বাংলা - Bengali",
    "ta": "தமிழ் - Tamil",
    "te": "తెలుగు - Telugu",
    "kn": "ಕನ್ನಡ - Kannada",
    "ml": "മലയാളം - Malayalam",
    "pa": "ਪੰਜਾਬੀ - Punjabi",
}

EN = {
    "language": "Language",
    "menu": "Menu",
    "login": "Login",
    "create_account": "Create Account",
    "logout": "Logout",
    "username": "Mobile / Email / Username",
    "password": "Password",
    "confirm_password": "Confirm Password",
    "welcome": "Welcome to SHIVPRUBA BILLING",
    "invalid_login": "Incorrect username or password.",
    "account_exists": "This username already exists.",
    "password_short": "Password must be at least 6 characters.",
    "password_mismatch": "Passwords do not match.",
    "account_created": "Account created successfully.",
    "username_required": "Please enter a username.",
    "business_setup": "Business Setup",
    "business_setup_help": "Enter your business details once. You can change them later in Settings.",
    "save_get_started": "Save & Get Started",
    "company_required": "Company name is required.",
    "dashboard": "Dashboard",
    "new_invoice": "New Invoice",
    "purchases": "Purchases / Stock In",
    "customers": "Customers",
    "customer_ledger": "Customer Ledger",
    "suppliers": "Suppliers",
    "products": "Products",
    "stock": "Stock",
    "invoice_history": "Invoice History",
    "purchase_history": "Purchase History",
    "sales_return": "Sales Return",
"purchase_return": "Purchase Return",
    "reports": "Reports",
    "settings": "Settings",
    "total_invoices": "Total Invoices",
    "total_sales": "Total Sales",
    "today_invoices": "Today's Invoices",
    "total_gst": "Total GST",
    "total_purchases": "Total Purchases",
    "today_purchases": "Today's Purchases",
    "stock_value": "Stock Value",
    "low_stock": "Low Stock",
    "recent_invoices": "Recent Invoices",
    "recent_purchases": "Recent Purchases",
    "no_invoices": "No invoices yet.",
    "no_purchases": "No purchases yet.",
    "create_tax_invoice": "Create Tax Invoice",
    "customer_info": "Customer Information",
    "saved_customer": "Saved Customer",
    "manual_customer": "New / Manual Customer",
    "customer_name": "Customer Name",
    "customer_address": "Customer Address",
    "customer_gstin": "Customer GSTIN (Optional)",
    "customer_state": "Customer State",
    "invoice_details": "Invoice Details",
    "invoice_number": "Invoice Number",
    "invoice_date": "Invoice Date",
    "place_of_supply": "Place of Supply",
    "goods_services": "Goods / Services",
    "number_of_items": "Number of items",
    "item": "Item",
    "saved_product": "Saved Product",
    "custom_item": "Custom Item",
    "description": "Description",
    "hsn_sac": "HSN / SAC",
    "quantity": "Quantity",
    "rate": "Rate",
    "gst_percent": "GST %",
    "current_stock": "Current Stock",
    "calculate_save_invoice": "Calculate & Save Invoice",
    "customer_required": "Please enter the customer name.",
    "invoice_saved": "Invoice saved successfully.",
    "invoice_duplicate": "This invoice number already exists.",
    "insufficient_stock": "Insufficient stock for one or more products.",
    "taxable_value": "Taxable Value",
    "grand_total": "Grand Total",
    "download_pdf": "Download PDF",
    "search_invoice": "Search invoice number or customer name",
    "found": "found",
    "date": "Date",
    "amount": "Amount",
    "address": "Address",
    "add_customer": "Add Customer",
    "save_customer": "Save Customer",
    "customer_saved": "Customer saved.",
    "no_customers": "No saved customers yet.",
    "delete": "Delete",
    "total_paid": "Total Paid",
    "total_outstanding": "Total Outstanding",
    "payment_status": "Payment Status",
    "paid": "Paid",
    "unpaid": "Unpaid",
    "partly_paid": "Partly Paid",
    "paid_amount": "Paid Amount",
    "balance_amount": "Balance Amount",
    "payment_history": "Payment History",
    "no_payments": "No payments recorded yet.",
    "record_payment": "Record Payment",
    "payment_amount": "Payment Amount",
    "payment_date": "Payment Date",
    "payment_note": "Payment Note",
    "payment_saved": "Payment saved successfully.",
    "payment_too_high": "Payment amount cannot be more than the balance amount.",
    "payment_duplicate": "This payment was just submitted. Please wait a few seconds.",
    "payment_deleted": "Payment deleted successfully.",
    "add_supplier": "Add Supplier",
    "supplier_name": "Supplier Name",
    "supplier_address": "Supplier Address",
    "supplier_gstin": "Supplier GSTIN (Optional)",
    "supplier_state": "Supplier State",
    "phone": "Phone",
    "email": "Email",
    "save_supplier": "Save Supplier",
    "supplier_saved": "Supplier saved.",
    "no_suppliers": "No saved suppliers yet.",
    "saved_supplier": "Saved Supplier",
    "manual_supplier": "New / Manual Supplier",
    "supplier_bill_number": "Supplier Bill Number",
    "purchase_date": "Purchase Date",
    "record_purchase": "Record Purchase / Stock In",
    "save_purchase": "Calculate & Save Purchase",
    "purchase_saved": "Purchase saved and stock updated.",
    "purchase_duplicate": "This supplier bill number already exists.",
    "purchase_rate": "Purchase Rate",
    "selling_rate": "Selling Rate",
    "sku": "SKU / Product Code",
    "unit": "Unit",
    "opening_stock": "Opening Stock",
    "low_stock_limit": "Low Stock Limit",
    "add_product": "Add Product / Service",
    "product_name": "Product / Service Name",
    "save_product": "Save Product",
    "product_saved": "Product saved.",
    "no_products": "No saved products yet.",
    "update_product": "Update Product",
    "product_updated": "Product updated.",
    "stock_adjustment": "Stock Adjustment",
    "adjustment_qty": "Adjustment Quantity (+/-)",
    "reason": "Reason",
    "apply_adjustment": "Apply Stock Adjustment",
    "stock_updated": "Stock updated.",
    "stock_ledger": "Stock Ledger",
    "balance": "Balance",
    "sales_summary": "Sales Summary",
    "purchase_summary": "Purchase Summary",
    "taxable_sales": "Taxable Sales",
    "taxable_purchases": "Taxable Purchases",
    "purchase_gst": "Purchase GST",
    "customer_sales": "Customer-wise Sales (Incl. GST)",
    "supplier_purchases": "Supplier-wise Purchases (Incl. GST)",
    "product_sales": "Product-wise Taxable Sales",
    "from_date": "From Date",
    "to_date": "To Date",
    "company_profile": "Company Profile",
    "company_name": "Company Name",
    "gstin": "GSTIN",
    "state": "State",
    "invoice_prefix": "Invoice Prefix",
    "default_low_stock": "Default Low Stock Limit",
    "save_settings": "Save Settings",
    "settings_saved": "Settings saved.",
    "backup": "Backup",
    "download_backup": "Download My Backup",
    "backup_help": "Download a copy of your business profile, customers, suppliers, products, purchases, stock, invoices and payments.",
    "use_on_phone": "Use on Phone",
    "phone_help": "Open the public SHIVPRUBA BILLING link in Chrome or Safari, then choose Add to Home Screen.",
    "version": APP_VERSION,
    "cgst": "CGST",
    "sgst": "SGST",
    "igst": "IGST",
    "product": "Product",
    "service": "Service",
    "purchase": "Purchase",
    "sale": "Sale",
    "opening": "Opening",
    "adjustment": "Adjustment",
    "search": "Search",
    "invoices": "Invoices",
    "payments": "Payments",
}

TR = {"en": EN}

TR["mr"] = {
    **EN,
    "language": "भाषा", "menu": "मेनू", "login": "लॉगिन", "create_account": "खाते तयार करा", "logout": "लॉगआउट",
    "username": "मोबाईल / ईमेल / वापरकर्तानाव", "password": "पासवर्ड", "confirm_password": "पासवर्ड पुन्हा लिहा",
    "welcome": "SHIVPRUBA BILLING मध्ये आपले स्वागत आहे", "invalid_login": "वापरकर्तानाव किंवा पासवर्ड चुकीचा आहे.",
    "account_exists": "हे वापरकर्तानाव आधीपासून अस्तित्वात आहे.", "password_short": "पासवर्ड किमान 6 अक्षरांचा असावा.",
    "password_mismatch": "दोन्ही पासवर्ड जुळत नाहीत.", "account_created": "खाते यशस्वीपणे तयार झाले.", "username_required": "वापरकर्तानाव लिहा.",
    "business_setup": "व्यवसाय माहिती", "business_setup_help": "व्यवसायाची माहिती एकदा भरा. नंतर Settings मध्ये बदल करू शकता.",
    "save_get_started": "सेव्ह करा आणि सुरू करा", "company_required": "कंपनीचे नाव आवश्यक आहे.",
    "dashboard": "डॅशबोर्ड", "new_invoice": "नवीन बिल", "purchases": "खरेदी / स्टॉक इन", "customers": "ग्राहक",
    "customer_ledger": "ग्राहक खातेवही", "suppliers": "पुरवठादार", "products": "उत्पादने", "stock": "स्टॉक",
    "invoice_history": "बिल इतिहास", "purchase_history": "खरेदी इतिहास","sales_return": "विक्री परतावा",
"purchase_return": "खरेदी परतावा", "reports": "अहवाल", "settings": "सेटिंग्ज",
    "total_invoices": "एकूण बिले", "total_sales": "एकूण विक्री", "today_invoices": "आजची बिले", "total_gst": "एकूण GST",
    "total_purchases": "एकूण खरेदी", "today_purchases": "आजची खरेदी", "stock_value": "स्टॉक किंमत", "low_stock": "कमी स्टॉक",
    "recent_invoices": "अलीकडील बिले", "recent_purchases": "अलीकडील खरेदी", "no_invoices": "अजून बिले नाहीत.", "no_purchases": "अजून खरेदी नाही.",
    "create_tax_invoice": "कर बिल तयार करा", "customer_info": "ग्राहक माहिती", "saved_customer": "सेव्ह केलेला ग्राहक", "manual_customer": "नवीन / मॅन्युअल ग्राहक",
    "customer_name": "ग्राहकाचे नाव", "customer_address": "ग्राहकाचा पत्ता", "customer_gstin": "ग्राहक GSTIN (ऐच्छिक)", "customer_state": "ग्राहक राज्य",
    "invoice_details": "बिल तपशील", "invoice_number": "बिल क्रमांक", "invoice_date": "बिल दिनांक", "place_of_supply": "पुरवठ्याचे ठिकाण",
    "goods_services": "वस्तू / सेवा", "number_of_items": "वस्तूंची संख्या", "item": "वस्तू", "saved_product": "सेव्ह केलेले उत्पादन", "custom_item": "इतर वस्तू",
    "description": "वर्णन", "quantity": "प्रमाण", "rate": "दर", "current_stock": "सध्याचा स्टॉक", "calculate_save_invoice": "हिशोब करून बिल सेव्ह करा",
    "customer_required": "ग्राहकाचे नाव लिहा.", "invoice_saved": "बिल यशस्वीपणे सेव्ह झाले.", "invoice_duplicate": "हा बिल क्रमांक आधीपासून आहे.",
    "insufficient_stock": "एका किंवा अधिक उत्पादनांचा स्टॉक अपुरा आहे.", "taxable_value": "करपात्र रक्कम", "grand_total": "एकूण रक्कम", "download_pdf": "PDF डाउनलोड करा",
    "search_invoice": "बिल क्रमांक किंवा ग्राहक शोधा", "found": "मिळाले", "date": "दिनांक", "amount": "रक्कम", "address": "पत्ता",
    "add_customer": "ग्राहक जोडा", "save_customer": "ग्राहक सेव्ह करा", "customer_saved": "ग्राहक सेव्ह झाला.", "no_customers": "सेव्ह केलेले ग्राहक नाहीत.", "delete": "डिलीट",
    "total_paid": "एकूण भरलेले", "total_outstanding": "एकूण बाकी", "payment_status": "पेमेंट स्थिती", "paid": "पूर्ण भरले", "unpaid": "न भरलेले", "partly_paid": "अंशतः भरले",
    "paid_amount": "भरलेली रक्कम", "balance_amount": "बाकी रक्कम", "payment_history": "पेमेंट इतिहास", "no_payments": "अजून पेमेंट नोंदलेले नाही.", "record_payment": "पेमेंट नोंदवा",
    "payment_amount": "पेमेंट रक्कम", "payment_date": "पेमेंट दिनांक", "payment_note": "पेमेंट नोंद", "payment_saved": "पेमेंट सेव्ह झाले.",
    "payment_too_high": "पेमेंट रक्कम बाकी रकमेपेक्षा जास्त असू शकत नाही.", "payment_duplicate": "हे पेमेंट आत्ताच पाठवले आहे. काही सेकंद थांबा.", "payment_deleted": "पेमेंट डिलीट झाले.",
    "add_supplier": "पुरवठादार जोडा", "supplier_name": "पुरवठादाराचे नाव", "supplier_address": "पुरवठादाराचा पत्ता", "supplier_gstin": "पुरवठादार GSTIN (ऐच्छिक)",
    "supplier_state": "पुरवठादार राज्य", "phone": "फोन", "email": "ईमेल", "save_supplier": "पुरवठादार सेव्ह करा", "supplier_saved": "पुरवठादार सेव्ह झाला.",
    "no_suppliers": "सेव्ह केलेले पुरवठादार नाहीत.", "saved_supplier": "सेव्ह केलेला पुरवठादार", "manual_supplier": "नवीन / मॅन्युअल पुरवठादार",
    "supplier_bill_number": "पुरवठादार बिल क्रमांक", "purchase_date": "खरेदी दिनांक", "record_purchase": "खरेदी / स्टॉक इन नोंदवा", "save_purchase": "हिशोब करून खरेदी सेव्ह करा",
    "purchase_saved": "खरेदी सेव्ह झाली आणि स्टॉक अपडेट झाला.", "purchase_duplicate": "हा पुरवठादार बिल क्रमांक आधीपासून आहे.", "purchase_rate": "खरेदी दर", "selling_rate": "विक्री दर",
    "unit": "एकक", "opening_stock": "सुरुवातीचा स्टॉक", "low_stock_limit": "कमी स्टॉक मर्यादा", "add_product": "उत्पादन / सेवा जोडा", "product_name": "उत्पादन / सेवेचे नाव",
    "save_product": "उत्पादन सेव्ह करा", "product_saved": "उत्पादन सेव्ह झाले.", "no_products": "सेव्ह केलेली उत्पादने नाहीत.", "update_product": "उत्पादन अपडेट करा", "product_updated": "उत्पादन अपडेट झाले.",
    "stock_adjustment": "स्टॉक दुरुस्ती", "adjustment_qty": "दुरुस्ती प्रमाण (+/-)", "reason": "कारण", "apply_adjustment": "स्टॉक दुरुस्ती लागू करा", "stock_updated": "स्टॉक अपडेट झाला.", "stock_ledger": "स्टॉक खातेवही", "balance": "शिल्लक",
    "sales_summary": "विक्री सारांश", "purchase_summary": "खरेदी सारांश", "taxable_sales": "करपात्र विक्री", "taxable_purchases": "करपात्र खरेदी", "purchase_gst": "खरेदी GST",
    "customer_sales": "ग्राहकनिहाय विक्री (GST सहित)", "supplier_purchases": "पुरवठादारनिहाय खरेदी (GST सहित)", "product_sales": "उत्पादननिहाय करपात्र विक्री",
    "from_date": "पासून दिनांक", "to_date": "पर्यंत दिनांक", "company_profile": "कंपनी माहिती", "company_name": "कंपनीचे नाव", "state": "राज्य",
    "invoice_prefix": "बिल प्रिफिक्स", "default_low_stock": "डीफॉल्ट कमी स्टॉक मर्यादा", "save_settings": "सेटिंग्ज सेव्ह करा", "settings_saved": "सेटिंग्ज सेव्ह झाल्या.",
    "backup": "बॅकअप", "download_backup": "माझा बॅकअप डाउनलोड करा", "backup_help": "व्यवसाय, ग्राहक, पुरवठादार, उत्पादने, खरेदी, स्टॉक, बिले आणि पेमेंटचा बॅकअप डाउनलोड करा.",
    "use_on_phone": "मोबाईलवर वापरा", "phone_help": "सार्वजनिक SHIVPRUBA BILLING लिंक Chrome किंवा Safari मध्ये उघडा आणि Add to Home Screen निवडा.",
    "product": "उत्पादन", "service": "सेवा", "purchase": "खरेदी", "sale": "विक्री", "opening": "सुरुवातीचा", "adjustment": "दुरुस्ती", "search": "शोधा", "invoices": "बिले", "payments": "पेमेंट",
}

TR["hi"] = {
    **EN,
    "language": "भाषा", "menu": "मेनू", "login": "लॉगिन", "create_account": "खाता बनाएं", "logout": "लॉगआउट",
    "username": "मोबाइल / ईमेल / उपयोगकर्ता नाम", "password": "पासवर्ड", "confirm_password": "पासवर्ड दोबारा लिखें", "welcome": "SHIVPRUBA BILLING में आपका स्वागत है",
    "invalid_login": "उपयोगकर्ता नाम या पासवर्ड गलत है।", "account_exists": "यह उपयोगकर्ता नाम पहले से मौजूद है।", "password_short": "पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।",
    "password_mismatch": "दोनों पासवर्ड मेल नहीं खाते।", "account_created": "खाता सफलतापूर्वक बन गया।", "username_required": "उपयोगकर्ता नाम दर्ज करें।",
    "business_setup": "व्यवसाय सेटअप", "business_setup_help": "व्यवसाय की जानकारी एक बार भरें। बाद में Settings में बदल सकते हैं।", "save_get_started": "सेव करें और शुरू करें", "company_required": "कंपनी का नाम आवश्यक है।",
    "dashboard": "डैशबोर्ड", "new_invoice": "नया बिल", "purchases": "खरीद / स्टॉक इन", "customers": "ग्राहक", "customer_ledger": "ग्राहक खाता", "suppliers": "आपूर्तिकर्ता", "products": "उत्पाद", "stock": "स्टॉक",
    "invoice_history": "बिल इतिहास", "purchase_history": "खरीद इतिहास", "reports": "रिपोर्ट", "settings": "सेटिंग्स",
    "total_invoices": "कुल बिल", "total_sales": "कुल बिक्री", "today_invoices": "आज के बिल", "total_gst": "कुल GST", "total_purchases": "कुल खरीद", "today_purchases": "आज की खरीद", "stock_value": "स्टॉक मूल्य", "low_stock": "कम स्टॉक",
    "recent_invoices": "हाल के बिल", "recent_purchases": "हाल की खरीद", "no_invoices": "अभी कोई बिल नहीं।", "no_purchases": "अभी कोई खरीद नहीं।",
    "create_tax_invoice": "टैक्स इनवॉइस बनाएं", "customer_info": "ग्राहक जानकारी", "saved_customer": "सेव किया ग्राहक", "manual_customer": "नया / मैन्युअल ग्राहक", "customer_name": "ग्राहक का नाम", "customer_address": "ग्राहक का पता",
    "customer_gstin": "ग्राहक GSTIN (वैकल्पिक)", "customer_state": "ग्राहक राज्य", "invoice_details": "बिल विवरण", "invoice_number": "बिल नंबर", "invoice_date": "बिल दिनांक", "place_of_supply": "आपूर्ति स्थान",
    "goods_services": "वस्तु / सेवा", "number_of_items": "वस्तुओं की संख्या", "item": "वस्तु", "saved_product": "सेव किया उत्पाद", "custom_item": "अन्य वस्तु", "description": "विवरण", "quantity": "मात्रा", "rate": "दर", "current_stock": "वर्तमान स्टॉक",
    "calculate_save_invoice": "गणना करके बिल सेव करें", "customer_required": "ग्राहक का नाम दर्ज करें।", "invoice_saved": "बिल सफलतापूर्वक सेव हुआ।", "invoice_duplicate": "यह बिल नंबर पहले से मौजूद है।", "insufficient_stock": "एक या अधिक उत्पादों का स्टॉक कम है।",
    "taxable_value": "कर योग्य राशि", "grand_total": "कुल राशि", "download_pdf": "PDF डाउनलोड करें", "search_invoice": "बिल नंबर या ग्राहक खोजें", "found": "मिले", "date": "दिनांक", "amount": "राशि", "address": "पता",
    "add_customer": "ग्राहक जोड़ें", "save_customer": "ग्राहक सेव करें", "customer_saved": "ग्राहक सेव हुआ।", "no_customers": "कोई सेव ग्राहक नहीं।", "delete": "हटाएं",
    "total_paid": "कुल भुगतान", "total_outstanding": "कुल बकाया", "payment_status": "भुगतान स्थिति", "paid": "भुगतान हुआ", "unpaid": "अभुगतान", "partly_paid": "आंशिक भुगतान", "paid_amount": "भुगतान राशि", "balance_amount": "बाकी राशि",
    "payment_history": "भुगतान इतिहास", "no_payments": "अभी कोई भुगतान दर्ज नहीं।", "record_payment": "भुगतान दर्ज करें", "payment_amount": "भुगतान राशि", "payment_date": "भुगतान दिनांक", "payment_note": "भुगतान नोट", "payment_saved": "भुगतान सेव हुआ।",
    "payment_too_high": "भुगतान राशि बाकी राशि से अधिक नहीं हो सकती।", "payment_duplicate": "यह भुगतान अभी दर्ज किया गया है। कुछ सेकंड प्रतीक्षा करें।", "payment_deleted": "भुगतान हटाया गया।",
    "add_supplier": "आपूर्तिकर्ता जोड़ें", "supplier_name": "आपूर्तिकर्ता नाम", "supplier_address": "आपूर्तिकर्ता पता", "supplier_gstin": "आपूर्तिकर्ता GSTIN (वैकल्पिक)", "supplier_state": "आपूर्तिकर्ता राज्य", "phone": "फोन", "email": "ईमेल",
    "save_supplier": "आपूर्तिकर्ता सेव करें", "supplier_saved": "आपूर्तिकर्ता सेव हुआ।", "no_suppliers": "कोई सेव आपूर्तिकर्ता नहीं।", "saved_supplier": "सेव किया आपूर्तिकर्ता", "manual_supplier": "नया / मैन्युअल आपूर्तिकर्ता",
    "supplier_bill_number": "आपूर्तिकर्ता बिल नंबर", "purchase_date": "खरीद दिनांक", "record_purchase": "खरीद / स्टॉक इन दर्ज करें", "save_purchase": "गणना करके खरीद सेव करें", "purchase_saved": "खरीद सेव हुई और स्टॉक अपडेट हुआ।", "purchase_duplicate": "यह आपूर्तिकर्ता बिल नंबर पहले से मौजूद है।",
    "purchase_rate": "खरीद दर", "selling_rate": "बिक्री दर", "unit": "इकाई", "opening_stock": "प्रारंभिक स्टॉक", "low_stock_limit": "कम स्टॉक सीमा", "add_product": "उत्पाद / सेवा जोड़ें", "product_name": "उत्पाद / सेवा नाम", "save_product": "उत्पाद सेव करें", "product_saved": "उत्पाद सेव हुआ।", "no_products": "कोई सेव उत्पाद नहीं।",
    "update_product": "उत्पाद अपडेट करें", "product_updated": "उत्पाद अपडेट हुआ।", "stock_adjustment": "स्टॉक समायोजन", "adjustment_qty": "समायोजन मात्रा (+/-)", "reason": "कारण", "apply_adjustment": "स्टॉक समायोजन लागू करें", "stock_updated": "स्टॉक अपडेट हुआ।", "stock_ledger": "स्टॉक खाता", "balance": "शेष",
    "sales_summary": "बिक्री सारांश", "purchase_summary": "खरीद सारांश", "taxable_sales": "कर योग्य बिक्री", "taxable_purchases": "कर योग्य खरीद", "purchase_gst": "खरीद GST", "customer_sales": "ग्राहकवार बिक्री (GST सहित)", "supplier_purchases": "आपूर्तिकर्तावार खरीद (GST सहित)", "product_sales": "उत्पादवार कर योग्य बिक्री",
    "from_date": "आरंभ दिनांक", "to_date": "अंत दिनांक", "company_profile": "कंपनी प्रोफाइल", "company_name": "कंपनी का नाम", "state": "राज्य", "invoice_prefix": "बिल प्रीफिक्स", "default_low_stock": "डिफ़ॉल्ट कम स्टॉक सीमा", "save_settings": "सेटिंग्स सेव करें", "settings_saved": "सेटिंग्स सेव हुईं।",
    "backup": "बैकअप", "download_backup": "मेरा बैकअप डाउनलोड करें", "backup_help": "व्यवसाय, ग्राहक, आपूर्तिकर्ता, उत्पाद, खरीद, स्टॉक, बिल और भुगतान का बैकअप डाउनलोड करें।", "use_on_phone": "फोन पर उपयोग करें", "phone_help": "सार्वजनिक SHIVPRUBA BILLING लिंक Chrome या Safari में खोलें और Add to Home Screen चुनें।",
    "product": "उत्पाद", "service": "सेवा", "purchase": "खरीद", "sale": "बिक्री", "opening": "प्रारंभिक", "adjustment": "समायोजन", "search": "खोजें", "invoices": "बिल", "payments": "भुगतान",
}
TR["gu"] = {
    **EN,
    "language": "ભાષા", "menu": "મેનૂ", "login": "લૉગિન", "create_account": "ખાતું બનાવો", "logout": "લૉગઆઉટ",
    "username": "મોબાઇલ / ઈમેલ / વપરાશકર્તા નામ", "password": "પાસવર્ડ", "confirm_password": "પાસવર્ડ ફરી લખો", "welcome": "SHIVPRUBA BILLING માં આપનું સ્વાગત છે",
    "invalid_login": "વપરાશકર્તા નામ અથવા પાસવર્ડ ખોટો છે.", "account_exists": "આ વપરાશકર્તા નામ પહેલેથી હાજર છે.", "password_short": "પાસવર્ડ ઓછામાં ઓછા 6 અક્ષરોનો હોવો જોઈએ.",
    "password_mismatch": "બન્ને પાસવર્ડ મેળ ખાતા નથી.", "account_created": "ખાતું સફળતાપૂર્વક બનાવાયું.", "username_required": "વપરાશકર્તા નામ લખો.",
    "business_setup": "વ્યવસાય સેટઅપ", "business_setup_help": "વ્યવસાયની માહિતી એકવાર ભરો. પછી Settings માં બદલી શકો છો.", "save_get_started": "સેવ કરો અને શરૂ કરો", "company_required": "કંપનીનું નામ જરૂરી છે.",
    "dashboard": "ડેશબોર્ડ", "new_invoice": "નવું બિલ", "purchases": "ખરીદી / સ્ટોક ઇન", "customers": "ગ્રાહકો", "customer_ledger": "ગ્રાહક ખાતાવહી", "suppliers": "સપ્લાયર", "products": "ઉત્પાદનો", "stock": "સ્ટોક",
    "invoice_history": "બિલ ઇતિહાસ", "purchase_history": "ખરીદી ઇતિહાસ", "reports": "અહેવાલ", "settings": "સેટિંગ્સ",
    "total_invoices": "કુલ બિલ", "total_sales": "કુલ વેચાણ", "today_invoices": "આજના બિલ", "total_gst": "કુલ GST", "total_purchases": "કુલ ખરીદી", "today_purchases": "આજની ખરીદી", "stock_value": "સ્ટોક મૂલ્ય", "low_stock": "ઓછો સ્ટોક",
    "recent_invoices": "તાજેતરના બિલ", "recent_purchases": "તાજેતરની ખરીદી", "no_invoices": "હજુ બિલ નથી.", "no_purchases": "હજુ ખરીદી નથી.",
    "create_tax_invoice": "ટેક્સ ઇનવૉઇસ બનાવો", "customer_info": "ગ્રાહક માહિતી", "saved_customer": "સેવ કરેલો ગ્રાહક", "manual_customer": "નવો / મેન્યુઅલ ગ્રાહક", "customer_name": "ગ્રાહકનું નામ", "customer_address": "ગ્રાહકનું સરનામું",
    "customer_gstin": "ગ્રાહક GSTIN (વૈકલ્પિક)", "customer_state": "ગ્રાહક રાજ્ય", "invoice_details": "બિલ વિગતો", "invoice_number": "બિલ નંબર", "invoice_date": "બિલ તારીખ", "place_of_supply": "સપ્લાય સ્થળ",
    "goods_services": "વસ્તુ / સેવા", "number_of_items": "વસ્તુઓની સંખ્યા", "item": "વસ્તુ", "saved_product": "સેવ કરેલું ઉત્પાદન", "custom_item": "અન્ય વસ્તુ", "description": "વર્ણન", "quantity": "જથ્થો", "rate": "દર", "current_stock": "હાલનો સ્ટોક",
    "calculate_save_invoice": "હિસાબ કરીને બિલ સેવ કરો", "customer_required": "ગ્રાહકનું નામ લખો.", "invoice_saved": "બિલ સફળતાપૂર્વક સેવ થયું.", "invoice_duplicate": "આ બિલ નંબર પહેલેથી છે.", "insufficient_stock": "એક અથવા વધુ ઉત્પાદનોનો સ્ટોક ઓછો છે.",
    "taxable_value": "કરપાત્ર રકમ", "grand_total": "કુલ રકમ", "download_pdf": "PDF ડાઉનલોડ કરો", "search_invoice": "બિલ નંબર અથવા ગ્રાહક શોધો", "found": "મળ્યા", "date": "તારીખ", "amount": "રકમ", "address": "સરનામું",
    "add_customer": "ગ્રાહક ઉમેરો", "save_customer": "ગ્રાહક સેવ કરો", "customer_saved": "ગ્રાહક સેવ થયો.", "no_customers": "સેવ કરેલા ગ્રાહકો નથી.", "delete": "ડિલીટ",
    "total_paid": "કુલ ચૂકવેલ", "total_outstanding": "કુલ બાકી", "payment_status": "ચુકવણી સ્થિતિ", "paid": "ચૂકવેલ", "unpaid": "બાકી", "partly_paid": "આંશિક ચૂકવેલ", "paid_amount": "ચૂકવેલ રકમ", "balance_amount": "બાકી રકમ",
    "payment_history": "ચુકવણી ઇતિહાસ", "no_payments": "હજુ કોઈ ચુકવણી નોંધાઈ નથી.", "record_payment": "ચુકવણી નોંધો", "payment_amount": "ચુકવણી રકમ", "payment_date": "ચુકવણી તારીખ", "payment_note": "ચુકવણી નોંધ", "payment_saved": "ચુકવણી સેવ થઈ.",
    "payment_too_high": "ચુકવણી રકમ બાકી રકમથી વધુ હોઈ શકતી નથી.", "payment_duplicate": "આ ચુકવણી હમણાં જ નોંધાઈ છે. થોડા સેકંડ રાહ જુઓ.", "payment_deleted": "ચુકવણી ડિલીટ થઈ.",
    "add_supplier": "સપ્લાયર ઉમેરો", "supplier_name": "સપ્લાયરનું નામ", "supplier_address": "સપ્લાયરનું સરનામું", "supplier_gstin": "સપ્લાયર GSTIN (વૈકલ્પિક)", "supplier_state": "સપ્લાયર રાજ્ય", "phone": "ફોન", "email": "ઈમેલ",
    "save_supplier": "સપ્લાયર સેવ કરો", "supplier_saved": "સપ્લાયર સેવ થયો.", "no_suppliers": "સેવ કરેલા સપ્લાયર નથી.", "saved_supplier": "સેવ કરેલો સપ્લાયર", "manual_supplier": "નવો / મેન્યુઅલ સપ્લાયર",
    "supplier_bill_number": "સપ્લાયર બિલ નંબર", "purchase_date": "ખરીદી તારીખ", "record_purchase": "ખરીદી / સ્ટોક ઇન નોંધો", "save_purchase": "હિસાબ કરીને ખરીદી સેવ કરો", "purchase_saved": "ખરીદી સેવ થઈ અને સ્ટોક અપડેટ થયો.", "purchase_duplicate": "આ સપ્લાયર બિલ નંબર પહેલેથી છે.",
    "purchase_rate": "ખરીદી દર", "selling_rate": "વેચાણ દર", "unit": "એકમ", "opening_stock": "શરૂઆતનો સ્ટોક", "low_stock_limit": "ઓછા સ્ટોકની મર્યાદા", "add_product": "ઉત્પાદન / સેવા ઉમેરો", "product_name": "ઉત્પાદન / સેવાનું નામ", "save_product": "ઉત્પાદન સેવ કરો", "product_saved": "ઉત્પાદન સેવ થયું.", "no_products": "સેવ કરેલા ઉત્પાદનો નથી.",
    "update_product": "ઉત્પાદન અપડેટ કરો", "product_updated": "ઉત્પાદન અપડેટ થયું.", "stock_adjustment": "સ્ટોક સુધારો", "adjustment_qty": "સુધારા જથ્થો (+/-)", "reason": "કારણ", "apply_adjustment": "સ્ટોક સુધારો લાગુ કરો", "stock_updated": "સ્ટોક અપડેટ થયો.", "stock_ledger": "સ્ટોક ખાતાવહી", "balance": "બાકી",
    "sales_summary": "વેચાણ સારાંશ", "purchase_summary": "ખરીદી સારાંશ", "taxable_sales": "કરપાત્ર વેચાણ", "taxable_purchases": "કરપાત્ર ખરીદી", "purchase_gst": "ખરીદી GST", "customer_sales": "ગ્રાહકવાર વેચાણ (GST સહિત)", "supplier_purchases": "સપ્લાયરવાર ખરીદી (GST સહિત)", "product_sales": "ઉત્પાદનવાર કરપાત્ર વેચાણ",
    "from_date": "તારીખથી", "to_date": "તારીખ સુધી", "company_profile": "કંપની પ્રોફાઇલ", "company_name": "કંપનીનું નામ", "state": "રાજ્ય", "invoice_prefix": "બિલ પ્રીફિક્સ", "default_low_stock": "ડિફૉલ્ટ ઓછા સ્ટોકની મર્યાદા", "save_settings": "સેટિંગ્સ સેવ કરો", "settings_saved": "સેટિંગ્સ સેવ થઈ.",
    "backup": "બેકઅપ", "download_backup": "મારો બેકઅપ ડાઉનલોડ કરો", "backup_help": "વ્યવસાય, ગ્રાહક, સપ્લાયર, ઉત્પાદનો, ખરીદી, સ્ટોક, બિલ અને ચુકવણીનો બેકઅપ ડાઉનલોડ કરો.", "use_on_phone": "ફોન પર વાપરો", "phone_help": "જાહેર SHIVPRUBA BILLING લિંક Chrome અથવા Safari માં ખોલો અને Add to Home Screen પસંદ કરો.",
    "product": "ઉત્પાદન", "service": "સેવા", "purchase": "ખરીદી", "sale": "વેચાણ", "opening": "શરૂઆત", "adjustment": "સુધારો", "search": "શોધો", "invoices": "બિલ", "payments": "ચુકવણી",
}

TR["bn"] = {
    **EN,
    "language": "ভাষা", "menu": "মেনু", "login": "লগইন", "create_account": "অ্যাকাউন্ট তৈরি করুন", "logout": "লগআউট",
    "username": "মোবাইল / ইমেল / ব্যবহারকারীর নাম", "password": "পাসওয়ার্ড", "confirm_password": "পাসওয়ার্ড আবার লিখুন", "welcome": "SHIVPRUBA BILLING-এ আপনাকে স্বাগতম",
    "invalid_login": "ব্যবহারকারীর নাম বা পাসওয়ার্ড ভুল।", "account_exists": "এই ব্যবহারকারীর নামটি আগে থেকেই আছে।", "password_short": "পাসওয়ার্ড কমপক্ষে 6 অক্ষরের হতে হবে।", "password_mismatch": "দুইটি পাসওয়ার্ড মিলছে না।", "account_created": "অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে।", "username_required": "ব্যবহারকারীর নাম লিখুন।",
    "business_setup": "ব্যবসা সেটআপ", "business_setup_help": "ব্যবসার তথ্য একবার পূরণ করুন। পরে Settings থেকে পরিবর্তন করতে পারবেন।", "save_get_started": "সেভ করে শুরু করুন", "company_required": "কোম্পানির নাম প্রয়োজন।",
    "dashboard": "ড্যাশবোর্ড", "new_invoice": "নতুন বিল", "purchases": "ক্রয় / স্টক ইন", "customers": "গ্রাহক", "customer_ledger": "গ্রাহক খাতা", "suppliers": "সরবরাহকারী", "products": "পণ্য", "stock": "স্টক",
    "invoice_history": "বিল ইতিহাস", "purchase_history": "ক্রয় ইতিহাস", "reports": "রিপোর্ট", "settings": "সেটিংস",
    "total_invoices": "মোট বিল", "total_sales": "মোট বিক্রয়", "today_invoices": "আজকের বিল", "total_gst": "মোট GST", "total_purchases": "মোট ক্রয়", "today_purchases": "আজকের ক্রয়", "stock_value": "স্টক মূল্য", "low_stock": "কম স্টক",
    "recent_invoices": "সাম্প্রতিক বিল", "recent_purchases": "সাম্প্রতিক ক্রয়", "no_invoices": "এখনও কোনো বিল নেই।", "no_purchases": "এখনও কোনো ক্রয় নেই।",
    "create_tax_invoice": "ট্যাক্স ইনভয়েস তৈরি করুন", "customer_info": "গ্রাহকের তথ্য", "saved_customer": "সেভ করা গ্রাহক", "manual_customer": "নতুন / ম্যানুয়াল গ্রাহক", "customer_name": "গ্রাহকের নাম", "customer_address": "গ্রাহকের ঠিকানা", "customer_gstin": "গ্রাহক GSTIN (ঐচ্ছিক)", "customer_state": "গ্রাহকের রাজ্য",
    "invoice_details": "বিলের বিবরণ", "invoice_number": "বিল নম্বর", "invoice_date": "বিলের তারিখ", "place_of_supply": "সরবরাহের স্থান", "goods_services": "পণ্য / পরিষেবা", "number_of_items": "পণ্যের সংখ্যা", "item": "পণ্য", "saved_product": "সেভ করা পণ্য", "custom_item": "অন্যান্য পণ্য", "description": "বিবরণ", "quantity": "পরিমাণ", "rate": "দর", "current_stock": "বর্তমান স্টক",
    "calculate_save_invoice": "হিসাব করে বিল সেভ করুন", "customer_required": "গ্রাহকের নাম লিখুন।", "invoice_saved": "বিল সফলভাবে সেভ হয়েছে।", "invoice_duplicate": "এই বিল নম্বরটি আগে থেকেই আছে।", "insufficient_stock": "এক বা একাধিক পণ্যের স্টক পর্যাপ্ত নয়।", "taxable_value": "করযোগ্য মূল্য", "grand_total": "মোট পরিমাণ", "download_pdf": "PDF ডাউনলোড করুন", "search_invoice": "বিল নম্বর বা গ্রাহক খুঁজুন", "found": "পাওয়া গেছে", "date": "তারিখ", "amount": "পরিমাণ", "address": "ঠিকানা",
    "add_customer": "গ্রাহক যোগ করুন", "save_customer": "গ্রাহক সেভ করুন", "customer_saved": "গ্রাহক সেভ হয়েছে।", "no_customers": "সেভ করা গ্রাহক নেই।", "delete": "মুছুন",
    "total_paid": "মোট পরিশোধ", "total_outstanding": "মোট বকেয়া", "payment_status": "পেমেন্ট অবস্থা", "paid": "পরিশোধিত", "unpaid": "অপরিশোধিত", "partly_paid": "আংশিক পরিশোধ", "paid_amount": "পরিশোধিত অর্থ", "balance_amount": "বকেয়া অর্থ", "payment_history": "পেমেন্ট ইতিহাস", "no_payments": "এখনও কোনো পেমেন্ট রেকর্ড নেই।", "record_payment": "পেমেন্ট রেকর্ড করুন", "payment_amount": "পেমেন্টের পরিমাণ", "payment_date": "পেমেন্টের তারিখ", "payment_note": "পেমেন্ট নোট", "payment_saved": "পেমেন্ট সেভ হয়েছে।", "payment_too_high": "পেমেন্ট বকেয়ার চেয়ে বেশি হতে পারবে না।", "payment_duplicate": "এই পেমেন্টটি এখনই জমা হয়েছে। কয়েক সেকেন্ড অপেক্ষা করুন।", "payment_deleted": "পেমেন্ট মুছে ফেলা হয়েছে।",
    "add_supplier": "সরবরাহকারী যোগ করুন", "supplier_name": "সরবরাহকারীর নাম", "supplier_address": "সরবরাহকারীর ঠিকানা", "supplier_gstin": "সরবরাহকারী GSTIN (ঐচ্ছিক)", "supplier_state": "সরবরাহকারীর রাজ্য", "phone": "ফোন", "email": "ইমেল", "save_supplier": "সরবরাহকারী সেভ করুন", "supplier_saved": "সরবরাহকারী সেভ হয়েছে।", "no_suppliers": "সেভ করা সরবরাহকারী নেই।", "saved_supplier": "সেভ করা সরবরাহকারী", "manual_supplier": "নতুন / ম্যানুয়াল সরবরাহকারী",
    "supplier_bill_number": "সরবরাহকারীর বিল নম্বর", "purchase_date": "ক্রয়ের তারিখ", "record_purchase": "ক্রয় / স্টক ইন রেকর্ড করুন", "save_purchase": "হিসাব করে ক্রয় সেভ করুন", "purchase_saved": "ক্রয় সেভ হয়েছে এবং স্টক আপডেট হয়েছে।", "purchase_duplicate": "এই সরবরাহকারী বিল নম্বরটি আগে থেকেই আছে।", "purchase_rate": "ক্রয় দর", "selling_rate": "বিক্রয় দর", "unit": "একক", "opening_stock": "প্রারম্ভিক স্টক", "low_stock_limit": "কম স্টক সীমা", "add_product": "পণ্য / পরিষেবা যোগ করুন", "product_name": "পণ্য / পরিষেবার নাম", "save_product": "পণ্য সেভ করুন", "product_saved": "পণ্য সেভ হয়েছে।", "no_products": "সেভ করা পণ্য নেই।", "update_product": "পণ্য আপডেট করুন", "product_updated": "পণ্য আপডেট হয়েছে।",
    "stock_adjustment": "স্টক সমন্বয়", "adjustment_qty": "সমন্বয় পরিমাণ (+/-)", "reason": "কারণ", "apply_adjustment": "স্টক সমন্বয় প্রয়োগ করুন", "stock_updated": "স্টক আপডেট হয়েছে।", "stock_ledger": "স্টক খাতা", "balance": "ব্যালেন্স",
    "sales_summary": "বিক্রয় সারাংশ", "purchase_summary": "ক্রয় সারাংশ", "taxable_sales": "করযোগ্য বিক্রয়", "taxable_purchases": "করযোগ্য ক্রয়", "purchase_gst": "ক্রয় GST", "customer_sales": "গ্রাহকভিত্তিক বিক্রয় (GST সহ)", "supplier_purchases": "সরবরাহকারীভিত্তিক ক্রয় (GST সহ)", "product_sales": "পণ্যভিত্তিক করযোগ্য বিক্রয়", "from_date": "শুরুর তারিখ", "to_date": "শেষ তারিখ", "company_profile": "কোম্পানি প্রোফাইল", "company_name": "কোম্পানির নাম", "state": "রাজ্য", "invoice_prefix": "বিল প্রিফিক্স", "default_low_stock": "ডিফল্ট কম স্টক সীমা", "save_settings": "সেটিংস সেভ করুন", "settings_saved": "সেটিংস সেভ হয়েছে।",
    "backup": "ব্যাকআপ", "download_backup": "আমার ব্যাকআপ ডাউনলোড করুন", "backup_help": "ব্যবসা, গ্রাহক, সরবরাহকারী, পণ্য, ক্রয়, স্টক, বিল ও পেমেন্টের ব্যাকআপ ডাউনলোড করুন।", "use_on_phone": "ফোনে ব্যবহার করুন", "phone_help": "পাবলিক SHIVPRUBA BILLING লিংক Chrome বা Safari-তে খুলে Add to Home Screen নির্বাচন করুন।",
    "product": "পণ্য", "service": "পরিষেবা", "purchase": "ক্রয়", "sale": "বিক্রয়", "opening": "প্রারম্ভিক", "adjustment": "সমন্বয়", "search": "খুঁজুন", "invoices": "বিল", "payments": "পেমেন্ট",
}
TR["ta"] = {
    **EN,
    "language": "மொழி", "menu": "மெனு", "login": "உள்நுழைவு", "create_account": "கணக்கு உருவாக்கு", "logout": "வெளியேறு",
    "username": "மொபைல் / மின்னஞ்சல் / பயனர் பெயர்", "password": "கடவுச்சொல்", "confirm_password": "கடவுச்சொல் மீண்டும்", "welcome": "SHIVPRUBA BILLING-க்கு வரவேற்கிறோம்",
    "invalid_login": "பயனர் பெயர் அல்லது கடவுச்சொல் தவறானது.", "account_exists": "இந்த பயனர் பெயர் ஏற்கனவே உள்ளது.", "password_short": "கடவுச்சொல் குறைந்தது 6 எழுத்துகள் இருக்க வேண்டும்.", "password_mismatch": "கடவுச்சொற்கள் பொருந்தவில்லை.", "account_created": "கணக்கு வெற்றிகரமாக உருவாக்கப்பட்டது.", "username_required": "பயனர் பெயரை உள்ளிடவும்.",
    "business_setup": "வணிக அமைப்பு", "business_setup_help": "வணிக விவரங்களை ஒருமுறை உள்ளிடுங்கள். பின்னர் Settings-ல் மாற்றலாம்.", "save_get_started": "சேமித்து தொடங்கு", "company_required": "நிறுவனப் பெயர் அவசியம்.",
    "dashboard": "டாஷ்போர்டு", "new_invoice": "புதிய பில்", "purchases": "கொள்முதல் / ஸ்டாக் இன்", "customers": "வாடிக்கையாளர்கள்", "customer_ledger": "வாடிக்கையாளர் கணக்கு", "suppliers": "சப்ளையர்கள்", "products": "பொருட்கள்", "stock": "ஸ்டாக்",
    "invoice_history": "பில் வரலாறு", "purchase_history": "கொள்முதல் வரலாறு", "reports": "அறிக்கைகள்", "settings": "அமைப்புகள்",
    "total_invoices": "மொத்த பில்கள்", "total_sales": "மொத்த விற்பனை", "today_invoices": "இன்றைய பில்கள்", "total_gst": "மொத்த GST", "total_purchases": "மொத்த கொள்முதல்", "today_purchases": "இன்றைய கொள்முதல்", "stock_value": "ஸ்டாக் மதிப்பு", "low_stock": "குறைந்த ஸ்டாக்",
    "recent_invoices": "சமீபத்திய பில்கள்", "recent_purchases": "சமீபத்திய கொள்முதல்", "no_invoices": "இன்னும் பில்கள் இல்லை.", "no_purchases": "இன்னும் கொள்முதல் இல்லை.",
    "create_tax_invoice": "வரி பில் உருவாக்கு", "customer_info": "வாடிக்கையாளர் தகவல்", "saved_customer": "சேமித்த வாடிக்கையாளர்", "manual_customer": "புதிய / கைமுறை வாடிக்கையாளர்", "customer_name": "வாடிக்கையாளர் பெயர்", "customer_address": "வாடிக்கையாளர் முகவரி", "customer_gstin": "வாடிக்கையாளர் GSTIN (விருப்பம்)", "customer_state": "வாடிக்கையாளர் மாநிலம்",
    "invoice_details": "பில் விவரங்கள்", "invoice_number": "பில் எண்", "invoice_date": "பில் தேதி", "place_of_supply": "விநியோக இடம்", "goods_services": "பொருட்கள் / சேவைகள்", "number_of_items": "பொருட்களின் எண்ணிக்கை", "item": "பொருள்", "saved_product": "சேமித்த பொருள்", "custom_item": "மற்ற பொருள்", "description": "விளக்கம்", "quantity": "அளவு", "rate": "விலை", "current_stock": "தற்போதைய ஸ்டாக்",
    "calculate_save_invoice": "கணக்கிட்டு பில் சேமி", "customer_required": "வாடிக்கையாளர் பெயரை உள்ளிடவும்.", "invoice_saved": "பில் வெற்றிகரமாக சேமிக்கப்பட்டது.", "invoice_duplicate": "இந்த பில் எண் ஏற்கனவே உள்ளது.", "insufficient_stock": "ஒரு அல்லது அதற்கு மேற்பட்ட பொருட்களுக்கு போதுமான ஸ்டாக் இல்லை.", "taxable_value": "வரி விதிக்கப்படும் மதிப்பு", "grand_total": "மொத்த தொகை", "download_pdf": "PDF பதிவிறக்கு", "search_invoice": "பில் எண் அல்லது வாடிக்கையாளரைத் தேடு", "found": "கிடைத்தது", "date": "தேதி", "amount": "தொகை", "address": "முகவரி",
    "add_customer": "வாடிக்கையாளரைச் சேர்", "save_customer": "வாடிக்கையாளரை சேமி", "customer_saved": "வாடிக்கையாளர் சேமிக்கப்பட்டார்.", "no_customers": "சேமித்த வாடிக்கையாளர்கள் இல்லை.", "delete": "நீக்கு",
    "total_paid": "மொத்தம் செலுத்தியது", "total_outstanding": "மொத்த நிலுவை", "payment_status": "கட்டண நிலை", "paid": "செலுத்தப்பட்டது", "unpaid": "செலுத்தப்படவில்லை", "partly_paid": "பகுதி செலுத்தப்பட்டது", "paid_amount": "செலுத்திய தொகை", "balance_amount": "நிலுவை தொகை", "payment_history": "கட்டண வரலாறு", "no_payments": "இன்னும் கட்டணம் பதிவு செய்யப்படவில்லை.", "record_payment": "கட்டணம் பதிவு செய்", "payment_amount": "கட்டண தொகை", "payment_date": "கட்டண தேதி", "payment_note": "கட்டண குறிப்பு", "payment_saved": "கட்டணம் சேமிக்கப்பட்டது.", "payment_too_high": "கட்டண தொகை நிலுவையை விட அதிகமாக இருக்க முடியாது.", "payment_duplicate": "இந்த கட்டணம் இப்போது பதிவு செய்யப்பட்டது. சில விநாடிகள் காத்திருக்கவும்.", "payment_deleted": "கட்டணம் நீக்கப்பட்டது.",
    "add_supplier": "சப்ளையரைச் சேர்", "supplier_name": "சப்ளையர் பெயர்", "supplier_address": "சப்ளையர் முகவரி", "supplier_gstin": "சப்ளையர் GSTIN (விருப்பம்)", "supplier_state": "சப்ளையர் மாநிலம்", "phone": "தொலைபேசி", "email": "மின்னஞ்சல்", "save_supplier": "சப்ளையரை சேமி", "supplier_saved": "சப்ளையர் சேமிக்கப்பட்டார்.", "no_suppliers": "சேமித்த சப்ளையர்கள் இல்லை.", "saved_supplier": "சேமித்த சப்ளையர்", "manual_supplier": "புதிய / கைமுறை சப்ளையர்",
    "supplier_bill_number": "சப்ளையர் பில் எண்", "purchase_date": "கொள்முதல் தேதி", "record_purchase": "கொள்முதல் / ஸ்டாக் இன் பதிவு செய்", "save_purchase": "கணக்கிட்டு கொள்முதல் சேமி", "purchase_saved": "கொள்முதல் சேமிக்கப்பட்டு ஸ்டாக் புதுப்பிக்கப்பட்டது.", "purchase_duplicate": "இந்த சப்ளையர் பில் எண் ஏற்கனவே உள்ளது.", "purchase_rate": "கொள்முதல் விலை", "selling_rate": "விற்பனை விலை", "unit": "அலகு", "opening_stock": "தொடக்க ஸ்டாக்", "low_stock_limit": "குறைந்த ஸ்டாக் வரம்பு", "add_product": "பொருள் / சேவை சேர்", "product_name": "பொருள் / சேவை பெயர்", "save_product": "பொருளை சேமி", "product_saved": "பொருள் சேமிக்கப்பட்டது.", "no_products": "சேமித்த பொருட்கள் இல்லை.", "update_product": "பொருளை புதுப்பி", "product_updated": "பொருள் புதுப்பிக்கப்பட்டது.",
    "stock_adjustment": "ஸ்டாக் சரிசெய்தல்", "adjustment_qty": "சரிசெய்தல் அளவு (+/-)", "reason": "காரணம்", "apply_adjustment": "ஸ்டாக் சரிசெய்தலை பயன்படுத்து", "stock_updated": "ஸ்டாக் புதுப்பிக்கப்பட்டது.", "stock_ledger": "ஸ்டாக் கணக்கு", "balance": "மீதம்",
    "sales_summary": "விற்பனை சுருக்கம்", "purchase_summary": "கொள்முதல் சுருக்கம்", "taxable_sales": "வரி விதிக்கப்படும் விற்பனை", "taxable_purchases": "வரி விதிக்கப்படும் கொள்முதல்", "purchase_gst": "கொள்முதல் GST", "customer_sales": "வாடிக்கையாளர் வாரியான விற்பனை (GST உடன்)", "supplier_purchases": "சப்ளையர் வாரியான கொள்முதல் (GST உடன்)", "product_sales": "பொருள் வாரியான வரிவிதிப்பு விற்பனை", "from_date": "தொடக்க தேதி", "to_date": "முடிவு தேதி", "company_profile": "நிறுவன விவரம்", "company_name": "நிறுவனப் பெயர்", "state": "மாநிலம்", "invoice_prefix": "பில் முன்னொட்டு", "default_low_stock": "இயல்புநிலை குறைந்த ஸ்டாக் வரம்பு", "save_settings": "அமைப்புகளை சேமி", "settings_saved": "அமைப்புகள் சேமிக்கப்பட்டன.",
    "backup": "காப்புப்பிரதி", "download_backup": "என் காப்புப்பிரதியை பதிவிறக்கு", "backup_help": "வணிகம், வாடிக்கையாளர்கள், சப்ளையர்கள், பொருட்கள், கொள்முதல், ஸ்டாக், பில்கள் மற்றும் கட்டணங்களின் காப்புப்பிரதியை பதிவிறக்கவும்.", "use_on_phone": "மொபைலில் பயன்படுத்து", "phone_help": "பொது SHIVPRUBA BILLING இணைப்பை Chrome அல்லது Safari-ல் திறந்து Add to Home Screen தேர்வு செய்யவும்.",
    "product": "பொருள்", "service": "சேவை", "purchase": "கொள்முதல்", "sale": "விற்பனை", "opening": "தொடக்கம்", "adjustment": "சரிசெய்தல்", "search": "தேடு", "invoices": "பில்கள்", "payments": "கட்டணங்கள்",
}

TR["te"] = {
    **EN,
    "language": "భాష", "menu": "మెను", "login": "లాగిన్", "create_account": "ఖాతా సృష్టించండి", "logout": "లాగౌట్",
    "username": "మొబైల్ / ఇమెయిల్ / వినియోగదారు పేరు", "password": "పాస్‌వర్డ్", "confirm_password": "పాస్‌వర్డ్ మళ్లీ నమోదు చేయండి", "welcome": "SHIVPRUBA BILLING కు స్వాగతం",
    "invalid_login": "వినియోగదారు పేరు లేదా పాస్‌వర్డ్ తప్పు.", "account_exists": "ఈ వినియోగదారు పేరు ఇప్పటికే ఉంది.", "password_short": "పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి.", "password_mismatch": "పాస్‌వర్డ్లు సరిపోలడం లేదు.", "account_created": "ఖాతా విజయవంతంగా సృష్టించబడింది.", "username_required": "వినియోగదారు పేరును నమోదు చేయండి.",
    "business_setup": "వ్యాపార సెటప్", "business_setup_help": "వ్యాపార వివరాలను ఒకసారి నమోదు చేయండి. తరువాత Settings లో మార్చవచ్చు.", "save_get_started": "సేవ్ చేసి ప్రారంభించండి", "company_required": "కంపెనీ పేరు అవసరం.",
    "dashboard": "డాష్‌బోర్డ్", "new_invoice": "కొత్త బిల్", "purchases": "కొనుగోలు / స్టాక్ ఇన్", "customers": "కస్టమర్లు", "customer_ledger": "కస్టమర్ లెడ్జర్", "suppliers": "సరఫరాదారులు", "products": "ఉత్పత్తులు", "stock": "స్టాక్",
    "invoice_history": "బిల్ చరిత్ర", "purchase_history": "కొనుగోలు చరిత్ర", "reports": "రిపోర్టులు", "settings": "సెట్టింగ్స్",
    "total_invoices": "మొత్తం బిల్లులు", "total_sales": "మొత్తం అమ్మకాలు", "today_invoices": "ఈరోజు బిల్లులు", "total_gst": "మొత్తం GST", "total_purchases": "మొత్తం కొనుగోలు", "today_purchases": "ఈరోజు కొనుగోలు", "stock_value": "స్టాక్ విలువ", "low_stock": "తక్కువ స్టాక్",
    "recent_invoices": "ఇటీవలి బిల్లులు", "recent_purchases": "ఇటీవలి కొనుగోలు", "no_invoices": "ఇంకా బిల్లులు లేవు.", "no_purchases": "ఇంకా కొనుగోలు లేదు.",
    "create_tax_invoice": "పన్ను బిల్ సృష్టించండి", "customer_info": "కస్టమర్ సమాచారం", "saved_customer": "సేవ్ చేసిన కస్టమర్", "manual_customer": "కొత్త / మాన్యువల్ కస్టమర్", "customer_name": "కస్టమర్ పేరు", "customer_address": "కస్టమర్ చిరునామా", "customer_gstin": "కస్టమర్ GSTIN (ఐచ్ఛికం)", "customer_state": "కస్టమర్ రాష్ట్రం",
    "invoice_details": "బిల్ వివరాలు", "invoice_number": "బిల్ నంబర్", "invoice_date": "బిల్ తేదీ", "place_of_supply": "సరఫరా స్థలం", "goods_services": "వస్తువులు / సేవలు", "number_of_items": "వస్తువుల సంఖ్య", "item": "వస్తువు", "saved_product": "సేవ్ చేసిన ఉత్పత్తి", "custom_item": "ఇతర వస్తువు", "description": "వివరణ", "quantity": "పరిమాణం", "rate": "ధర", "current_stock": "ప్రస్తుత స్టాక్",
    "calculate_save_invoice": "లెక్కించి బిల్ సేవ్ చేయండి", "customer_required": "కస్టమర్ పేరు నమోదు చేయండి.", "invoice_saved": "బిల్ విజయవంతంగా సేవ్ అయింది.", "invoice_duplicate": "ఈ బిల్ నంబర్ ఇప్పటికే ఉంది.", "insufficient_stock": "ఒకటి లేదా ఎక్కువ ఉత్పత్తులకు సరిపడా స్టాక్ లేదు.", "taxable_value": "పన్ను విధించదగిన విలువ", "grand_total": "మొత్తం మొత్తం", "download_pdf": "PDF డౌన్‌లోడ్", "search_invoice": "బిల్ నంబర్ లేదా కస్టమర్‌ను వెతకండి", "found": "కనిపించాయి", "date": "తేదీ", "amount": "మొత్తం", "address": "చిరునామా",
    "add_customer": "కస్టమర్‌ను జోడించండి", "save_customer": "కస్టమర్ సేవ్ చేయండి", "customer_saved": "కస్టమర్ సేవ్ అయ్యారు.", "no_customers": "సేవ్ చేసిన కస్టమర్లు లేరు.", "delete": "తొలగించు",
    "total_paid": "మొత్తం చెల్లింపు", "total_outstanding": "మొత్తం బాకీ", "payment_status": "చెల్లింపు స్థితి", "paid": "చెల్లించబడింది", "unpaid": "చెల్లించలేదు", "partly_paid": "భాగంగా చెల్లించబడింది", "paid_amount": "చెల్లించిన మొత్తం", "balance_amount": "బాకీ మొత్తం", "payment_history": "చెల్లింపు చరిత్ర", "no_payments": "ఇంకా చెల్లింపులు నమోదు కాలేదు.", "record_payment": "చెల్లింపు నమోదు చేయండి", "payment_amount": "చెల్లింపు మొత్తం", "payment_date": "చెల్లింపు తేదీ", "payment_note": "చెల్లింపు గమనిక", "payment_saved": "చెల్లింపు సేవ్ అయింది.", "payment_too_high": "చెల్లింపు మొత్తం బాకీ కంటే ఎక్కువ ఉండకూడదు.", "payment_duplicate": "ఈ చెల్లింపు ఇప్పుడే నమోదు అయింది. కొన్ని సెకన్లు వేచి ఉండండి.", "payment_deleted": "చెల్లింపు తొలగించబడింది.",
    "add_supplier": "సరఫరాదారుని జోడించండి", "supplier_name": "సరఫరాదారు పేరు", "supplier_address": "సరఫరాదారు చిరునామా", "supplier_gstin": "సరఫరాదారు GSTIN (ఐచ్ఛికం)", "supplier_state": "సరఫరాదారు రాష్ట్రం", "phone": "ఫోన్", "email": "ఇమెయిల్", "save_supplier": "సరఫరాదారుని సేవ్ చేయండి", "supplier_saved": "సరఫరాదారు సేవ్ అయ్యారు.", "no_suppliers": "సేవ్ చేసిన సరఫరాదారులు లేరు.", "saved_supplier": "సేవ్ చేసిన సరఫరాదారు", "manual_supplier": "కొత్త / మాన్యువల్ సరఫరాదారు",
    "supplier_bill_number": "సరఫరాదారు బిల్ నంబర్", "purchase_date": "కొనుగోలు తేదీ", "record_purchase": "కొనుగోలు / స్టాక్ ఇన్ నమోదు చేయండి", "save_purchase": "లెక్కించి కొనుగోలు సేవ్ చేయండి", "purchase_saved": "కొనుగోలు సేవ్ అయి స్టాక్ అప్‌డేట్ అయింది.", "purchase_duplicate": "ఈ సరఫరాదారు బిల్ నంబర్ ఇప్పటికే ఉంది.", "purchase_rate": "కొనుగోలు ధర", "selling_rate": "అమ్మకపు ధర", "unit": "యూనిట్", "opening_stock": "ప్రారంభ స్టాక్", "low_stock_limit": "తక్కువ స్టాక్ పరిమితి", "add_product": "ఉత్పత్తి / సేవ జోడించండి", "product_name": "ఉత్పత్తి / సేవ పేరు", "save_product": "ఉత్పత్తి సేవ్ చేయండి", "product_saved": "ఉత్పత్తి సేవ్ అయింది.", "no_products": "సేవ్ చేసిన ఉత్పత్తులు లేవు.", "update_product": "ఉత్పత్తి అప్‌డేట్", "product_updated": "ఉత్పత్తి అప్‌డేట్ అయింది.",
    "stock_adjustment": "స్టాక్ సర్దుబాటు", "adjustment_qty": "సర్దుబాటు పరిమాణం (+/-)", "reason": "కారణం", "apply_adjustment": "స్టాక్ సర్దుబాటు అమలు చేయండి", "stock_updated": "స్టాక్ అప్‌డేట్ అయింది.", "stock_ledger": "స్టాక్ లెడ్జర్", "balance": "బ్యాలెన్స్",
    "sales_summary": "అమ్మకాల సారాంశం", "purchase_summary": "కొనుగోలు సారాంశం", "taxable_sales": "పన్ను విధించదగిన అమ్మకాలు", "taxable_purchases": "పన్ను విధించదగిన కొనుగోలు", "purchase_gst": "కొనుగోలు GST", "customer_sales": "కస్టమర్ వారీ అమ్మకాలు (GST తో)", "supplier_purchases": "సరఫరాదారు వారీ కొనుగోలు (GST తో)", "product_sales": "ఉత్పత్తి వారీ పన్ను అమ్మకాలు", "from_date": "ప్రారంభ తేదీ", "to_date": "ముగింపు తేదీ", "company_profile": "కంపెనీ ప్రొఫైల్", "company_name": "కంపెనీ పేరు", "state": "రాష్ట్రం", "invoice_prefix": "బిల్ ప్రిఫిక్స్", "default_low_stock": "డిఫాల్ట్ తక్కువ స్టాక్ పరిమితి", "save_settings": "సెట్టింగ్స్ సేవ్ చేయండి", "settings_saved": "సెట్టింగ్స్ సేవ్ అయ్యాయి.",
    "backup": "బ్యాకప్", "download_backup": "నా బ్యాకప్ డౌన్‌లోడ్", "backup_help": "వ్యాపారం, కస్టమర్లు, సరఫరాదారులు, ఉత్పత్తులు, కొనుగోలు, స్టాక్, బిల్లులు మరియు చెల్లింపుల బ్యాకప్ డౌన్‌లోడ్ చేయండి.", "use_on_phone": "ఫోన్‌లో ఉపయోగించండి", "phone_help": "పబ్లిక్ SHIVPRUBA BILLING లింక్‌ను Chrome లేదా Safari లో తెరిచి Add to Home Screen ఎంచుకోండి.",
    "product": "ఉత్పత్తి", "service": "సేవ", "purchase": "కొనుగోలు", "sale": "అమ్మకం", "opening": "ప్రారంభం", "adjustment": "సర్దుబాటు", "search": "వెతకండి", "invoices": "బిల్లులు", "payments": "చెల్లింపులు",
}
TR["kn"] = {
    **EN,
    "language": "ಭಾಷೆ", "menu": "ಮೆನು", "login": "ಲಾಗಿನ್", "create_account": "ಖಾತೆ ರಚಿಸಿ", "logout": "ಲಾಗೌಟ್",
    "username": "ಮೊಬೈಲ್ / ಇಮೇಲ್ / ಬಳಕೆದಾರ ಹೆಸರು", "password": "ಪಾಸ್‌ವರ್ಡ್", "confirm_password": "ಪಾಸ್‌ವರ್ಡ್ ಮತ್ತೆ ನಮೂದಿಸಿ", "welcome": "SHIVPRUBA BILLING ಗೆ ಸ್ವಾಗತ",
    "invalid_login": "ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಪಾಸ್‌ವರ್ಡ್ ತಪ್ಪಾಗಿದೆ.", "account_exists": "ಈ ಬಳಕೆದಾರ ಹೆಸರು ಈಗಾಗಲೇ ಇದೆ.", "password_short": "ಪಾಸ್‌ವರ್ಡ್ ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳಿರಬೇಕು.", "password_mismatch": "ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ.", "account_created": "ಖಾತೆ ಯಶಸ್ವಿಯಾಗಿ ರಚಿಸಲಾಗಿದೆ.", "username_required": "ಬಳಕೆದಾರ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.",
    "business_setup": "ವ್ಯವಹಾರ ಸೆಟಪ್", "business_setup_help": "ವ್ಯವಹಾರದ ವಿವರಗಳನ್ನು ಒಮ್ಮೆ ನಮೂದಿಸಿ. ನಂತರ Settings ನಲ್ಲಿ ಬದಲಾಯಿಸಬಹುದು.", "save_get_started": "ಸೇವ್ ಮಾಡಿ ಪ್ರಾರಂಭಿಸಿ", "company_required": "ಕಂಪನಿಯ ಹೆಸರು ಅಗತ್ಯ.",
    "dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", "new_invoice": "ಹೊಸ ಬಿಲ್", "purchases": "ಖರೀದಿ / ಸ್ಟಾಕ್ ಇನ್", "customers": "ಗ್ರಾಹಕರು", "customer_ledger": "ಗ್ರಾಹಕ ಲೆಡ್ಜರ್", "suppliers": "ಪೂರೈಕೆದಾರರು", "products": "ಉತ್ಪನ್ನಗಳು", "stock": "ಸ್ಟಾಕ್",
    "invoice_history": "ಬಿಲ್ ಇತಿಹಾಸ", "purchase_history": "ಖರೀದಿ ಇತಿಹಾಸ", "reports": "ವರದಿಗಳು", "settings": "ಸೆಟ್ಟಿಂಗ್ಸ್",
    "total_invoices": "ಒಟ್ಟು ಬಿಲ್ಲುಗಳು", "total_sales": "ಒಟ್ಟು ಮಾರಾಟ", "today_invoices": "ಇಂದಿನ ಬಿಲ್ಲುಗಳು", "total_gst": "ಒಟ್ಟು GST", "total_purchases": "ಒಟ್ಟು ಖರೀದಿ", "today_purchases": "ಇಂದಿನ ಖರೀದಿ", "stock_value": "ಸ್ಟಾಕ್ ಮೌಲ್ಯ", "low_stock": "ಕಡಿಮೆ ಸ್ಟಾಕ್",
    "recent_invoices": "ಇತ್ತೀಚಿನ ಬಿಲ್ಲುಗಳು", "recent_purchases": "ಇತ್ತೀಚಿನ ಖರೀದಿ", "no_invoices": "ಇನ್ನೂ ಬಿಲ್ಲುಗಳಿಲ್ಲ.", "no_purchases": "ಇನ್ನೂ ಖರೀದಿ ಇಲ್ಲ.",
    "create_tax_invoice": "ತೆರಿಗೆ ಬಿಲ್ ರಚಿಸಿ", "customer_info": "ಗ್ರಾಹಕ ಮಾಹಿತಿ", "saved_customer": "ಸೇವ್ ಮಾಡಿದ ಗ್ರಾಹಕ", "manual_customer": "ಹೊಸ / ಮ್ಯಾನುಯಲ್ ಗ್ರಾಹಕ", "customer_name": "ಗ್ರಾಹಕರ ಹೆಸರು", "customer_address": "ಗ್ರಾಹಕರ ವಿಳಾಸ", "customer_gstin": "ಗ್ರಾಹಕ GSTIN (ಐಚ್ಛಿಕ)", "customer_state": "ಗ್ರಾಹಕ ರಾಜ್ಯ",
    "invoice_details": "ಬಿಲ್ ವಿವರಗಳು", "invoice_number": "ಬಿಲ್ ಸಂಖ್ಯೆ", "invoice_date": "ಬಿಲ್ ದಿನಾಂಕ", "place_of_supply": "ಪೂರೈಕೆ ಸ್ಥಳ", "goods_services": "ವಸ್ತುಗಳು / ಸೇವೆಗಳು", "number_of_items": "ವಸ್ತುಗಳ ಸಂಖ್ಯೆ", "item": "ವಸ್ತು", "saved_product": "ಸೇವ್ ಮಾಡಿದ ಉತ್ಪನ್ನ", "custom_item": "ಇತರೆ ವಸ್ತು", "description": "ವಿವರಣೆ", "quantity": "ಪ್ರಮಾಣ", "rate": "ದರ", "current_stock": "ಪ್ರಸ್ತುತ ಸ್ಟಾಕ್",
    "calculate_save_invoice": "ಲೆಕ್ಕ ಮಾಡಿ ಬಿಲ್ ಸೇವ್ ಮಾಡಿ", "customer_required": "ಗ್ರಾಹಕರ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.", "invoice_saved": "ಬಿಲ್ ಯಶಸ್ವಿಯಾಗಿ ಸೇವ್ ಆಯಿತು.", "invoice_duplicate": "ಈ ಬಿಲ್ ಸಂಖ್ಯೆ ಈಗಾಗಲೇ ಇದೆ.", "insufficient_stock": "ಒಂದು ಅಥವಾ ಹೆಚ್ಚಿನ ಉತ್ಪನ್ನಗಳಿಗೆ ಸಾಕಷ್ಟು ಸ್ಟಾಕ್ ಇಲ್ಲ.", "taxable_value": "ತೆರಿಗೆ ವಿಧಿಸಬಹುದಾದ ಮೌಲ್ಯ", "grand_total": "ಒಟ್ಟು ಮೊತ್ತ", "download_pdf": "PDF ಡೌನ್‌ಲೋಡ್", "search_invoice": "ಬಿಲ್ ಸಂಖ್ಯೆ ಅಥವಾ ಗ್ರಾಹಕರನ್ನು ಹುಡುಕಿ", "found": "ಸಿಕ್ಕಿವೆ", "date": "ದಿನಾಂಕ", "amount": "ಮೊತ್ತ", "address": "ವಿಳಾಸ",
    "add_customer": "ಗ್ರಾಹಕರನ್ನು ಸೇರಿಸಿ", "save_customer": "ಗ್ರಾಹಕರನ್ನು ಸೇವ್ ಮಾಡಿ", "customer_saved": "ಗ್ರಾಹಕ ಸೇವ್ ಆಗಿದ್ದಾರೆ.", "no_customers": "ಸೇವ್ ಮಾಡಿದ ಗ್ರಾಹಕರು ಇಲ್ಲ.", "delete": "ಅಳಿಸಿ",
    "total_paid": "ಒಟ್ಟು ಪಾವತಿ", "total_outstanding": "ಒಟ್ಟು ಬಾಕಿ", "payment_status": "ಪಾವತಿ ಸ್ಥಿತಿ", "paid": "ಪಾವತಿಸಲಾಗಿದೆ", "unpaid": "ಪಾವತಿಸಿಲ್ಲ", "partly_paid": "ಭಾಗಶಃ ಪಾವತಿ", "paid_amount": "ಪಾವತಿಸಿದ ಮೊತ್ತ", "balance_amount": "ಬಾಕಿ ಮೊತ್ತ", "payment_history": "ಪಾವತಿ ಇತಿಹಾಸ", "no_payments": "ಇನ್ನೂ ಪಾವತಿ ದಾಖಲಾಗಿಲ್ಲ.", "record_payment": "ಪಾವತಿ ದಾಖಲಿಸಿ", "payment_amount": "ಪಾವತಿ ಮೊತ್ತ", "payment_date": "ಪಾವತಿ ದಿನಾಂಕ", "payment_note": "ಪಾವತಿ ಟಿಪ್ಪಣಿ", "payment_saved": "ಪಾವತಿ ಸೇವ್ ಆಯಿತು.", "payment_too_high": "ಪಾವತಿ ಮೊತ್ತ ಬಾಕಿಗಿಂತ ಹೆಚ್ಚು ಇರಬಾರದು.", "payment_duplicate": "ಈ ಪಾವತಿ ಈಗಷ್ಟೇ ದಾಖಲಾಗಿದೆ. ಕೆಲವು ಸೆಕೆಂಡ್ ಕಾಯಿರಿ.", "payment_deleted": "ಪಾವತಿ ಅಳಿಸಲಾಗಿದೆ.",
    "add_supplier": "ಪೂರೈಕೆದಾರರನ್ನು ಸೇರಿಸಿ", "supplier_name": "ಪೂರೈಕೆದಾರರ ಹೆಸರು", "supplier_address": "ಪೂರೈಕೆದಾರರ ವಿಳಾಸ", "supplier_gstin": "ಪೂರೈಕೆದಾರ GSTIN (ಐಚ್ಛಿಕ)", "supplier_state": "ಪೂರೈಕೆದಾರ ರಾಜ್ಯ", "phone": "ಫೋನ್", "email": "ಇಮೇಲ್", "save_supplier": "ಪೂರೈಕೆದಾರರನ್ನು ಸೇವ್ ಮಾಡಿ", "supplier_saved": "ಪೂರೈಕೆದಾರ ಸೇವ್ ಆಗಿದ್ದಾರೆ.", "no_suppliers": "ಸೇವ್ ಮಾಡಿದ ಪೂರೈಕೆದಾರರು ಇಲ್ಲ.", "saved_supplier": "ಸೇವ್ ಮಾಡಿದ ಪೂರೈಕೆದಾರ", "manual_supplier": "ಹೊಸ / ಮ್ಯಾನುಯಲ್ ಪೂರೈಕೆದಾರ",
    "supplier_bill_number": "ಪೂರೈಕೆದಾರ ಬಿಲ್ ಸಂಖ್ಯೆ", "purchase_date": "ಖರೀದಿ ದಿನಾಂಕ", "record_purchase": "ಖರೀದಿ / ಸ್ಟಾಕ್ ಇನ್ ದಾಖಲಿಸಿ", "save_purchase": "ಲೆಕ್ಕ ಮಾಡಿ ಖರೀದಿ ಸೇವ್ ಮಾಡಿ", "purchase_saved": "ಖರೀದಿ ಸೇವ್ ಆಗಿ ಸ್ಟಾಕ್ ಅಪ್‌ಡೇಟ್ ಆಯಿತು.", "purchase_duplicate": "ಈ ಪೂರೈಕೆದಾರ ಬಿಲ್ ಸಂಖ್ಯೆ ಈಗಾಗಲೇ ಇದೆ.", "purchase_rate": "ಖರೀದಿ ದರ", "selling_rate": "ಮಾರಾಟ ದರ", "unit": "ಘಟಕ", "opening_stock": "ಆರಂಭಿಕ ಸ್ಟಾಕ್", "low_stock_limit": "ಕಡಿಮೆ ಸ್ಟಾಕ್ ಮಿತಿ", "add_product": "ಉತ್ಪನ್ನ / ಸೇವೆ ಸೇರಿಸಿ", "product_name": "ಉತ್ಪನ್ನ / ಸೇವೆ ಹೆಸರು", "save_product": "ಉತ್ಪನ್ನ ಸೇವ್ ಮಾಡಿ", "product_saved": "ಉತ್ಪನ್ನ ಸೇವ್ ಆಯಿತು.", "no_products": "ಸೇವ್ ಮಾಡಿದ ಉತ್ಪನ್ನಗಳು ಇಲ್ಲ.", "update_product": "ಉತ್ಪನ್ನ ಅಪ್‌ಡೇಟ್", "product_updated": "ಉತ್ಪನ್ನ ಅಪ್‌ಡೇಟ್ ಆಯಿತು.",
    "stock_adjustment": "ಸ್ಟಾಕ್ ಸರಿಪಡಿಕೆ", "adjustment_qty": "ಸರಿಪಡಿಕೆ ಪ್ರಮಾಣ (+/-)", "reason": "ಕಾರಣ", "apply_adjustment": "ಸ್ಟಾಕ್ ಸರಿಪಡಿಕೆ ಅನ್ವಯಿಸಿ", "stock_updated": "ಸ್ಟಾಕ್ ಅಪ್‌ಡೇಟ್ ಆಯಿತು.", "stock_ledger": "ಸ್ಟಾಕ್ ಲೆಡ್ಜರ್", "balance": "ಬಾಕಿ",
    "sales_summary": "ಮಾರಾಟ ಸಾರಾಂಶ", "purchase_summary": "ಖರೀದಿ ಸಾರಾಂಶ", "taxable_sales": "ತೆರಿಗೆ ವಿಧಿಸಬಹುದಾದ ಮಾರಾಟ", "taxable_purchases": "ತೆರಿಗೆ ವಿಧಿಸಬಹುದಾದ ಖರೀದಿ", "purchase_gst": "ಖರೀದಿ GST", "customer_sales": "ಗ್ರಾಹಕರವಾರು ಮಾರಾಟ (GST ಸಹಿತ)", "supplier_purchases": "ಪೂರೈಕೆದಾರವಾರು ಖರೀದಿ (GST ಸಹಿತ)", "product_sales": "ಉತ್ಪನ್ನವಾರು ತೆರಿಗೆ ಮಾರಾಟ", "from_date": "ಆರಂಭ ದಿನಾಂಕ", "to_date": "ಕೊನೆಯ ದಿನಾಂಕ", "company_profile": "ಕಂಪನಿ ಪ್ರೊಫೈಲ್", "company_name": "ಕಂಪನಿಯ ಹೆಸರು", "state": "ರಾಜ್ಯ", "invoice_prefix": "ಬಿಲ್ ಪ್ರಿಫಿಕ್ಸ್", "default_low_stock": "ಡಿಫಾಲ್ಟ್ ಕಡಿಮೆ ಸ್ಟಾಕ್ ಮಿತಿ", "save_settings": "ಸೆಟ್ಟಿಂಗ್ಸ್ ಸೇವ್ ಮಾಡಿ", "settings_saved": "ಸೆಟ್ಟಿಂಗ್ಸ್ ಸೇವ್ ಆಗಿವೆ.",
    "backup": "ಬ್ಯಾಕಪ್", "download_backup": "ನನ್ನ ಬ್ಯಾಕಪ್ ಡೌನ್‌ಲೋಡ್", "backup_help": "ವ್ಯವಹಾರ, ಗ್ರಾಹಕರು, ಪೂರೈಕೆದಾರರು, ಉತ್ಪನ್ನಗಳು, ಖರೀದಿ, ಸ್ಟಾಕ್, ಬಿಲ್ಲುಗಳು ಮತ್ತು ಪಾವತಿಗಳ ಬ್ಯಾಕಪ್ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ.", "use_on_phone": "ಫೋನ್‌ನಲ್ಲಿ ಬಳಸಿ", "phone_help": "ಸಾರ್ವಜನಿಕ SHIVPRUBA BILLING ಲಿಂಕ್ ಅನ್ನು Chrome ಅಥವಾ Safari ನಲ್ಲಿ ತೆರೆಯಿರಿ ಮತ್ತು Add to Home Screen ಆಯ್ಕೆಮಾಡಿ.",
    "product": "ಉತ್ಪನ್ನ", "service": "ಸೇವೆ", "purchase": "ಖರೀದಿ", "sale": "ಮಾರಾಟ", "opening": "ಆರಂಭಿಕ", "adjustment": "ಸರಿಪಡಿಕೆ", "search": "ಹುಡುಕಿ", "invoices": "ಬಿಲ್ಲುಗಳು", "payments": "ಪಾವತಿಗಳು",
}

TR["ml"] = {
    **EN,
    "language": "ഭാഷ", "menu": "മെനു", "login": "ലോഗിൻ", "create_account": "അക്കൗണ്ട് സൃഷ്ടിക്കുക", "logout": "ലോഗൗട്ട്",
    "username": "മൊബൈൽ / ഇമെയിൽ / ഉപയോക്തൃനാമം", "password": "പാസ്‌വേഡ്", "confirm_password": "പാസ്‌വേഡ് വീണ്ടും നൽകുക", "welcome": "SHIVPRUBA BILLING ലേക്ക് സ്വാഗതം",
    "invalid_login": "ഉപയോക്തൃനാമം അല്ലെങ്കിൽ പാസ്‌വേഡ് തെറ്റാണ്.", "account_exists": "ഈ ഉപയോക്തൃനാമം ഇതിനകം നിലവിലുണ്ട്.", "password_short": "പാസ്‌വേഡ് കുറഞ്ഞത് 6 അക്ഷരങ്ങളെങ്കിലും വേണം.", "password_mismatch": "പാസ്‌വേഡുകൾ പൊരുത്തപ്പെടുന്നില്ല.", "account_created": "അക്കൗണ്ട് വിജയകരമായി സൃഷ്ടിച്ചു.", "username_required": "ഉപയോക്തൃനാമം നൽകുക.",
    "business_setup": "ബിസിനസ് സജ്ജീകരണം", "business_setup_help": "ബിസിനസ് വിവരങ്ങൾ ഒരിക്കൽ നൽകുക. പിന്നീട് Settings ൽ മാറ്റാം.", "save_get_started": "സേവ് ചെയ്ത് ആരംഭിക്കുക", "company_required": "കമ്പനിയുടെ പേര് ആവശ്യമാണ്.",
    "dashboard": "ഡാഷ്ബോർഡ്", "new_invoice": "പുതിയ ബിൽ", "purchases": "വാങ്ങൽ / സ്റ്റോക്ക് ഇൻ", "customers": "ഉപഭോക്താക്കൾ", "customer_ledger": "ഉപഭോക്തൃ ലെഡ്ജർ", "suppliers": "സപ്ലയർമാർ", "products": "ഉൽപ്പന്നങ്ങൾ", "stock": "സ്റ്റോക്ക്",
    "invoice_history": "ബിൽ ചരിത്രം", "purchase_history": "വാങ്ങൽ ചരിത്രം", "reports": "റിപ്പോർട്ടുകൾ", "settings": "സെറ്റിംഗ്സ്",
    "total_invoices": "ആകെ ബില്ലുകൾ", "total_sales": "ആകെ വിൽപ്പന", "today_invoices": "ഇന്നത്തെ ബില്ലുകൾ", "total_gst": "ആകെ GST", "total_purchases": "ആകെ വാങ്ങൽ", "today_purchases": "ഇന്നത്തെ വാങ്ങൽ", "stock_value": "സ്റ്റോക്ക് മൂല്യം", "low_stock": "കുറഞ്ഞ സ്റ്റോക്ക്",
    "recent_invoices": "സമീപകാല ബില്ലുകൾ", "recent_purchases": "സമീപകാല വാങ്ങലുകൾ", "no_invoices": "ഇനിയും ബില്ലുകളില്ല.", "no_purchases": "ഇനിയും വാങ്ങലുകളില്ല.",
    "create_tax_invoice": "നികുതി ബിൽ സൃഷ്ടിക്കുക", "customer_info": "ഉപഭോക്തൃ വിവരം", "saved_customer": "സേവ് ചെയ്ത ഉപഭോക്താവ്", "manual_customer": "പുതിയ / മാനുവൽ ഉപഭോക്താവ്", "customer_name": "ഉപഭോക്താവിന്റെ പേര്", "customer_address": "ഉപഭോക്താവിന്റെ വിലാസം", "customer_gstin": "ഉപഭോക്തൃ GSTIN (ഐച്ഛികം)", "customer_state": "ഉപഭോക്താവിന്റെ സംസ്ഥാനം",
    "invoice_details": "ബിൽ വിശദാംശങ്ങൾ", "invoice_number": "ബിൽ നമ്പർ", "invoice_date": "ബിൽ തീയതി", "place_of_supply": "വിതരണ സ്ഥലം", "goods_services": "വസ്തുക്കൾ / സേവനങ്ങൾ", "number_of_items": "വസ്തുക്കളുടെ എണ്ണം", "item": "വസ്തു", "saved_product": "സേവ് ചെയ്ത ഉൽപ്പന്നം", "custom_item": "മറ്റൊരു വസ്തു", "description": "വിവരണം", "quantity": "അളവ്", "rate": "നിരക്ക്", "current_stock": "നിലവിലെ സ്റ്റോക്ക്",
    "calculate_save_invoice": "കണക്കാക്കി ബിൽ സേവ് ചെയ്യുക", "customer_required": "ഉപഭോക്താവിന്റെ പേര് നൽകുക.", "invoice_saved": "ബിൽ വിജയകരമായി സേവ് ചെയ്തു.", "invoice_duplicate": "ഈ ബിൽ നമ്പർ ഇതിനകം നിലവിലുണ്ട്.", "insufficient_stock": "ഒന്നോ അതിലധികമോ ഉൽപ്പന്നങ്ങൾക്ക് മതിയായ സ്റ്റോക്ക് ഇല്ല.", "taxable_value": "നികുതിയോഗ്യ മൂല്യം", "grand_total": "ആകെ തുക", "download_pdf": "PDF ഡൗൺലോഡ്", "search_invoice": "ബിൽ നമ്പർ അല്ലെങ്കിൽ ഉപഭോക്താവിനെ തിരയുക", "found": "കണ്ടെത്തി", "date": "തീയതി", "amount": "തുക", "address": "വിലാസം",
    "add_customer": "ഉപഭോക്താവിനെ ചേർക്കുക", "save_customer": "ഉപഭോക്താവിനെ സേവ് ചെയ്യുക", "customer_saved": "ഉപഭോക്താവ് സേവ് ചെയ്തു.", "no_customers": "സേവ് ചെയ്ത ഉപഭോക്താക്കൾ ഇല്ല.", "delete": "നീക്കം ചെയ്യുക",
    "total_paid": "ആകെ അടച്ചത്", "total_outstanding": "ആകെ ബാക്കി", "payment_status": "പേയ്മെന്റ് നില", "paid": "അടച്ചു", "unpaid": "അടച്ചിട്ടില്ല", "partly_paid": "ഭാഗികമായി അടച്ചു", "paid_amount": "അടച്ച തുക", "balance_amount": "ബാക്കി തുക", "payment_history": "പേയ്മെന്റ് ചരിത്രം", "no_payments": "ഇനിയും പേയ്മെന്റ് രേഖപ്പെടുത്തിയിട്ടില്ല.", "record_payment": "പേയ്മെന്റ് രേഖപ്പെടുത്തുക", "payment_amount": "പേയ്മെന്റ് തുക", "payment_date": "പേയ്മെന്റ് തീയതി", "payment_note": "പേയ്മെന്റ് കുറിപ്പ്", "payment_saved": "പേയ്മെന്റ് സേവ് ചെയ്തു.", "payment_too_high": "പേയ്മെന്റ് തുക ബാക്കിയേക്കാൾ കൂടുതലാകരുത്.", "payment_duplicate": "ഈ പേയ്മെന്റ് ഇപ്പോൾ തന്നെ രേഖപ്പെടുത്തി. കുറച്ച് സെക്കൻഡ് കാത്തിരിക്കൂ.", "payment_deleted": "പേയ്മെന്റ് നീക്കം ചെയ്തു.",
    "add_supplier": "സപ്ലയറിനെ ചേർക്കുക", "supplier_name": "സപ്ലയറുടെ പേര്", "supplier_address": "സപ്ലയറുടെ വിലാസം", "supplier_gstin": "സപ്ലയർ GSTIN (ഐച്ഛികം)", "supplier_state": "സപ്ലയർ സംസ്ഥാനം", "phone": "ഫോൺ", "email": "ഇമെയിൽ", "save_supplier": "സപ്ലയറിനെ സേവ് ചെയ്യുക", "supplier_saved": "സപ്ലയർ സേവ് ചെയ്തു.", "no_suppliers": "സേവ് ചെയ്ത സപ്ലയർമാർ ഇല്ല.", "saved_supplier": "സേവ് ചെയ്ത സപ്ലയർ", "manual_supplier": "പുതിയ / മാനുവൽ സപ്ലയർ",
    "supplier_bill_number": "സപ്ലയർ ബിൽ നമ്പർ", "purchase_date": "വാങ്ങൽ തീയതി", "record_purchase": "വാങ്ങൽ / സ്റ്റോക്ക് ഇൻ രേഖപ്പെടുത്തുക", "save_purchase": "കണക്കാക്കി വാങ്ങൽ സേവ് ചെയ്യുക", "purchase_saved": "വാങ്ങൽ സേവ് ചെയ്തു, സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്തു.", "purchase_duplicate": "ഈ സപ്ലയർ ബിൽ നമ്പർ ഇതിനകം നിലവിലുണ്ട്.", "purchase_rate": "വാങ്ങൽ നിരക്ക്", "selling_rate": "വിൽപ്പന നിരക്ക്", "unit": "യൂണിറ്റ്", "opening_stock": "ആരംഭ സ്റ്റോക്ക്", "low_stock_limit": "കുറഞ്ഞ സ്റ്റോക്ക് പരിധി", "add_product": "ഉൽപ്പന്നം / സേവനം ചേർക്കുക", "product_name": "ഉൽപ്പന്നം / സേവനത്തിന്റെ പേര്", "save_product": "ഉൽപ്പന്നം സേവ് ചെയ്യുക", "product_saved": "ഉൽപ്പന്നം സേവ് ചെയ്തു.", "no_products": "സേവ് ചെയ്ത ഉൽപ്പന്നങ്ങൾ ഇല്ല.", "update_product": "ഉൽപ്പന്നം അപ്ഡേറ്റ് ചെയ്യുക", "product_updated": "ഉൽപ്പന്നം അപ്ഡേറ്റ് ചെയ്തു.",
    "stock_adjustment": "സ്റ്റോക്ക് ക്രമീകരണം", "adjustment_qty": "ക്രമീകരണ അളവ് (+/-)", "reason": "കാരണം", "apply_adjustment": "സ്റ്റോക്ക് ക്രമീകരണം പ്രയോഗിക്കുക", "stock_updated": "സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്തു.", "stock_ledger": "സ്റ്റോക്ക് ലെഡ്ജർ", "balance": "ബാക്കി",
    "sales_summary": "വിൽപ്പന സംഗ്രഹം", "purchase_summary": "വാങ്ങൽ സംഗ്രഹം", "taxable_sales": "നികുതിയോഗ്യ വിൽപ്പന", "taxable_purchases": "നികുതിയോഗ്യ വാങ്ങൽ", "purchase_gst": "വാങ്ങൽ GST", "customer_sales": "ഉപഭോക്താവനുസരിച്ചുള്ള വിൽപ്പന (GST ഉൾപ്പെടെ)", "supplier_purchases": "സപ്ലയറനുസരിച്ചുള്ള വാങ്ങൽ (GST ഉൾപ്പെടെ)", "product_sales": "ഉൽപ്പന്നാനുസരിച്ചുള്ള നികുതിയോഗ്യ വിൽപ്പന", "from_date": "ആരംഭ തീയതി", "to_date": "അവസാന തീയതി", "company_profile": "കമ്പനി പ്രൊഫൈൽ", "company_name": "കമ്പനിയുടെ പേര്", "state": "സംസ്ഥാനം", "invoice_prefix": "ബിൽ പ്രിഫിക്സ്", "default_low_stock": "ഡിഫോൾട്ട് കുറഞ്ഞ സ്റ്റോക്ക് പരിധി", "save_settings": "സെറ്റിംഗ്സ് സേവ് ചെയ്യുക", "settings_saved": "സെറ്റിംഗ്സ് സേവ് ചെയ്തു.",
    "backup": "ബാക്കപ്പ്", "download_backup": "എന്റെ ബാക്കപ്പ് ഡൗൺലോഡ്", "backup_help": "ബിസിനസ്, ഉപഭോക്താക്കൾ, സപ്ലയർമാർ, ഉൽപ്പന്നങ്ങൾ, വാങ്ങൽ, സ്റ്റോക്ക്, ബില്ലുകൾ, പേയ്മെന്റുകൾ എന്നിവയുടെ ബാക്കപ്പ് ഡൗൺലോഡ് ചെയ്യുക.", "use_on_phone": "ഫോണിൽ ഉപയോഗിക്കുക", "phone_help": "പബ്ലിക് SHIVPRUBA BILLING ലിങ്ക് Chrome അല്ലെങ്കിൽ Safari-ൽ തുറന്ന് Add to Home Screen തിരഞ്ഞെടുക്കുക.",
    "product": "ഉൽപ്പന്നം", "service": "സേവനം", "purchase": "വാങ്ങൽ", "sale": "വിൽപ്പന", "opening": "ആരംഭം", "adjustment": "ക്രമീകരണം", "search": "തിരയുക", "invoices": "ബില്ലുകൾ", "payments": "പേയ്മെന്റുകൾ",
}

TR["pa"] = {
    **EN,
    "language": "ਭਾਸ਼ਾ", "menu": "ਮੇਨੂ", "login": "ਲਾਗਇਨ", "create_account": "ਖਾਤਾ ਬਣਾਓ", "logout": "ਲਾਗਆਉਟ",
    "username": "ਮੋਬਾਈਲ / ਈਮੇਲ / ਯੂਜ਼ਰ ਨਾਮ", "password": "ਪਾਸਵਰਡ", "confirm_password": "ਪਾਸਵਰਡ ਮੁੜ ਲਿਖੋ", "welcome": "SHIVPRUBA BILLING ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ",
    "invalid_login": "ਯੂਜ਼ਰ ਨਾਮ ਜਾਂ ਪਾਸਵਰਡ ਗਲਤ ਹੈ।", "account_exists": "ਇਹ ਯੂਜ਼ਰ ਨਾਮ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ।", "password_short": "ਪਾਸਵਰਡ ਘੱਟੋ-ਘੱਟ 6 ਅੱਖਰਾਂ ਦਾ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ।", "password_mismatch": "ਪਾਸਵਰਡ ਮਿਲਦੇ ਨਹੀਂ ਹਨ।", "account_created": "ਖਾਤਾ ਸਫਲਤਾਪੂਰਵਕ ਬਣ ਗਿਆ।", "username_required": "ਯੂਜ਼ਰ ਨਾਮ ਦਰਜ ਕਰੋ।",
    "business_setup": "ਕਾਰੋਬਾਰ ਸੈਟਅਪ", "business_setup_help": "ਕਾਰੋਬਾਰ ਦੀ ਜਾਣਕਾਰੀ ਇੱਕ ਵਾਰ ਭਰੋ। ਬਾਅਦ ਵਿੱਚ Settings ਵਿੱਚ ਬਦਲ ਸਕਦੇ ਹੋ।", "save_get_started": "ਸੇਵ ਕਰੋ ਅਤੇ ਸ਼ੁਰੂ ਕਰੋ", "company_required": "ਕੰਪਨੀ ਦਾ ਨਾਮ ਲਾਜ਼ਮੀ ਹੈ।",
    "dashboard": "ਡੈਸ਼ਬੋਰਡ", "new_invoice": "ਨਵਾਂ ਬਿੱਲ", "purchases": "ਖਰੀਦ / ਸਟਾਕ ਇਨ", "customers": "ਗਾਹਕ", "customer_ledger": "ਗਾਹਕ ਖਾਤਾ", "suppliers": "ਸਪਲਾਇਰ", "products": "ਉਤਪਾਦ", "stock": "ਸਟਾਕ",
    "invoice_history": "ਬਿੱਲ ਇਤਿਹਾਸ", "purchase_history": "ਖਰੀਦ ਇਤਿਹਾਸ", "reports": "ਰਿਪੋਰਟਾਂ", "settings": "ਸੈਟਿੰਗਜ਼",
    "total_invoices": "ਕੁੱਲ ਬਿੱਲ", "total_sales": "ਕੁੱਲ ਵਿਕਰੀ", "today_invoices": "ਅੱਜ ਦੇ ਬਿੱਲ", "total_gst": "ਕੁੱਲ GST", "total_purchases": "ਕੁੱਲ ਖਰੀਦ", "today_purchases": "ਅੱਜ ਦੀ ਖਰੀਦ", "stock_value": "ਸਟਾਕ ਮੁੱਲ", "low_stock": "ਘੱਟ ਸਟਾਕ",
    "recent_invoices": "ਹਾਲੀਆ ਬਿੱਲ", "recent_purchases": "ਹਾਲੀਆ ਖਰੀਦ", "no_invoices": "ਅਜੇ ਕੋਈ ਬਿੱਲ ਨਹੀਂ।", "no_purchases": "ਅਜੇ ਕੋਈ ਖਰੀਦ ਨਹੀਂ।",
    "create_tax_invoice": "ਟੈਕਸ ਬਿੱਲ ਬਣਾਓ", "customer_info": "ਗਾਹਕ ਜਾਣਕਾਰੀ", "saved_customer": "ਸੇਵ ਕੀਤਾ ਗਾਹਕ", "manual_customer": "ਨਵਾਂ / ਮੈਨੂਅਲ ਗਾਹਕ", "customer_name": "ਗਾਹਕ ਦਾ ਨਾਮ", "customer_address": "ਗਾਹਕ ਦਾ ਪਤਾ", "customer_gstin": "ਗਾਹਕ GSTIN (ਵਿਕਲਪਿਕ)", "customer_state": "ਗਾਹਕ ਰਾਜ",
    "invoice_details": "ਬਿੱਲ ਵੇਰਵਾ", "invoice_number": "ਬਿੱਲ ਨੰਬਰ", "invoice_date": "ਬਿੱਲ ਮਿਤੀ", "place_of_supply": "ਸਪਲਾਈ ਸਥਾਨ", "goods_services": "ਸਮਾਨ / ਸੇਵਾਵਾਂ", "number_of_items": "ਆਈਟਮਾਂ ਦੀ ਗਿਣਤੀ", "item": "ਆਈਟਮ", "saved_product": "ਸੇਵ ਕੀਤਾ ਉਤਪਾਦ", "custom_item": "ਹੋਰ ਆਈਟਮ", "description": "ਵੇਰਵਾ", "quantity": "ਮਾਤਰਾ", "rate": "ਦਰ", "current_stock": "ਮੌਜੂਦਾ ਸਟਾਕ",
    "calculate_save_invoice": "ਹਿਸਾਬ ਕਰਕੇ ਬਿੱਲ ਸੇਵ ਕਰੋ", "customer_required": "ਗਾਹਕ ਦਾ ਨਾਮ ਦਰਜ ਕਰੋ।", "invoice_saved": "ਬਿੱਲ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋਇਆ।", "invoice_duplicate": "ਇਹ ਬਿੱਲ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ।", "insufficient_stock": "ਇੱਕ ਜਾਂ ਵੱਧ ਉਤਪਾਦਾਂ ਲਈ ਸਟਾਕ ਘੱਟ ਹੈ।", "taxable_value": "ਟੈਕਸ ਯੋਗ ਮੁੱਲ", "grand_total": "ਕੁੱਲ ਰਕਮ", "download_pdf": "PDF ਡਾਊਨਲੋਡ", "search_invoice": "ਬਿੱਲ ਨੰਬਰ ਜਾਂ ਗਾਹਕ ਖੋਜੋ", "found": "ਮਿਲੇ", "date": "ਮਿਤੀ", "amount": "ਰਕਮ", "address": "ਪਤਾ",
    "add_customer": "ਗਾਹਕ ਜੋੜੋ", "save_customer": "ਗਾਹਕ ਸੇਵ ਕਰੋ", "customer_saved": "ਗਾਹਕ ਸੇਵ ਹੋ ਗਿਆ।", "no_customers": "ਕੋਈ ਸੇਵ ਕੀਤਾ ਗਾਹਕ ਨਹੀਂ।", "delete": "ਹਟਾਓ",
    "total_paid": "ਕੁੱਲ ਭੁਗਤਾਨ", "total_outstanding": "ਕੁੱਲ ਬਕਾਇਆ", "payment_status": "ਭੁਗਤਾਨ ਸਥਿਤੀ", "paid": "ਭੁਗਤਾਨ ਹੋਇਆ", "unpaid": "ਭੁਗਤਾਨ ਨਹੀਂ", "partly_paid": "ਅੰਸ਼ਿਕ ਭੁਗਤਾਨ", "paid_amount": "ਭੁਗਤਾਨ ਰਕਮ", "balance_amount": "ਬਕਾਇਆ ਰਕਮ", "payment_history": "ਭੁਗਤਾਨ ਇਤਿਹਾਸ", "no_payments": "ਅਜੇ ਕੋਈ ਭੁਗਤਾਨ ਦਰਜ ਨਹੀਂ।", "record_payment": "ਭੁਗਤਾਨ ਦਰਜ ਕਰੋ", "payment_amount": "ਭੁਗਤਾਨ ਰਕਮ", "payment_date": "ਭੁਗਤਾਨ ਮਿਤੀ", "payment_note": "ਭੁਗਤਾਨ ਨੋਟ", "payment_saved": "ਭੁਗਤਾਨ ਸੇਵ ਹੋਇਆ।", "payment_too_high": "ਭੁਗਤਾਨ ਰਕਮ ਬਕਾਇਆ ਤੋਂ ਵੱਧ ਨਹੀਂ ਹੋ ਸਕਦੀ।", "payment_duplicate": "ਇਹ ਭੁਗਤਾਨ ਹੁਣੇ ਦਰਜ ਹੋਇਆ ਹੈ। ਕੁਝ ਸਕਿੰਟ ਉਡੀਕ ਕਰੋ।", "payment_deleted": "ਭੁਗਤਾਨ ਹਟਾਇਆ ਗਿਆ।",
    "add_supplier": "ਸਪਲਾਇਰ ਜੋੜੋ", "supplier_name": "ਸਪਲਾਇਰ ਦਾ ਨਾਮ", "supplier_address": "ਸਪਲਾਇਰ ਦਾ ਪਤਾ", "supplier_gstin": "ਸਪਲਾਇਰ GSTIN (ਵਿਕਲਪਿਕ)", "supplier_state": "ਸਪਲਾਇਰ ਰਾਜ", "phone": "ਫੋਨ", "email": "ਈਮੇਲ", "save_supplier": "ਸਪਲਾਇਰ ਸੇਵ ਕਰੋ", "supplier_saved": "ਸਪਲਾਇਰ ਸੇਵ ਹੋ ਗਿਆ।", "no_suppliers": "ਕੋਈ ਸੇਵ ਕੀਤਾ ਸਪਲਾਇਰ ਨਹੀਂ।", "saved_supplier": "ਸੇਵ ਕੀਤਾ ਸਪਲਾਇਰ", "manual_supplier": "ਨਵਾਂ / ਮੈਨੂਅਲ ਸਪਲਾਇਰ",
    "supplier_bill_number": "ਸਪਲਾਇਰ ਬਿੱਲ ਨੰਬਰ", "purchase_date": "ਖਰੀਦ ਮਿਤੀ", "record_purchase": "ਖਰੀਦ / ਸਟਾਕ ਇਨ ਦਰਜ ਕਰੋ", "save_purchase": "ਹਿਸਾਬ ਕਰਕੇ ਖਰੀਦ ਸੇਵ ਕਰੋ", "purchase_saved": "ਖਰੀਦ ਸੇਵ ਹੋਈ ਅਤੇ ਸਟਾਕ ਅਪਡੇਟ ਹੋਇਆ।", "purchase_duplicate": "ਇਹ ਸਪਲਾਇਰ ਬਿੱਲ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ।", "purchase_rate": "ਖਰੀਦ ਦਰ", "selling_rate": "ਵਿਕਰੀ ਦਰ", "unit": "ਇਕਾਈ", "opening_stock": "ਸ਼ੁਰੂਆਤੀ ਸਟਾਕ", "low_stock_limit": "ਘੱਟ ਸਟਾਕ ਸੀਮਾ", "add_product": "ਉਤਪਾਦ / ਸੇਵਾ ਜੋੜੋ", "product_name": "ਉਤਪਾਦ / ਸੇਵਾ ਦਾ ਨਾਮ", "save_product": "ਉਤਪਾਦ ਸੇਵ ਕਰੋ", "product_saved": "ਉਤਪਾਦ ਸੇਵ ਹੋਇਆ।", "no_products": "ਕੋਈ ਸੇਵ ਕੀਤਾ ਉਤਪਾਦ ਨਹੀਂ।", "update_product": "ਉਤਪਾਦ ਅਪਡੇਟ ਕਰੋ", "product_updated": "ਉਤਪਾਦ ਅਪਡੇਟ ਹੋਇਆ।",
    "stock_adjustment": "ਸਟਾਕ ਸੋਧ", "adjustment_qty": "ਸੋਧ ਮਾਤਰਾ (+/-)", "reason": "ਕਾਰਨ", "apply_adjustment": "ਸਟਾਕ ਸੋਧ ਲਾਗੂ ਕਰੋ", "stock_updated": "ਸਟਾਕ ਅਪਡੇਟ ਹੋਇਆ।", "stock_ledger": "ਸਟਾਕ ਖਾਤਾ", "balance": "ਬਕਾਇਆ",
    "sales_summary": "ਵਿਕਰੀ ਸੰਖੇਪ", "purchase_summary": "ਖਰੀਦ ਸੰਖੇਪ", "taxable_sales": "ਟੈਕਸ ਯੋਗ ਵਿਕਰੀ", "taxable_purchases": "ਟੈਕਸ ਯੋਗ ਖਰੀਦ", "purchase_gst": "ਖਰੀਦ GST", "customer_sales": "ਗਾਹਕ ਅਨੁਸਾਰ ਵਿਕਰੀ (GST ਸਮੇਤ)", "supplier_purchases": "ਸਪਲਾਇਰ ਅਨੁਸਾਰ ਖਰੀਦ (GST ਸਮੇਤ)", "product_sales": "ਉਤਪਾਦ ਅਨੁਸਾਰ ਟੈਕਸ ਯੋਗ ਵਿਕਰੀ", "from_date": "ਸ਼ੁਰੂ ਮਿਤੀ", "to_date": "ਅੰਤ ਮਿਤੀ", "company_profile": "ਕੰਪਨੀ ਪ੍ਰੋਫਾਈਲ", "company_name": "ਕੰਪਨੀ ਦਾ ਨਾਮ", "state": "ਰਾਜ", "invoice_prefix": "ਬਿੱਲ ਪ੍ਰਿਫਿਕਸ", "default_low_stock": "ਡਿਫਾਲਟ ਘੱਟ ਸਟਾਕ ਸੀਮਾ", "save_settings": "ਸੈਟਿੰਗਜ਼ ਸੇਵ ਕਰੋ", "settings_saved": "ਸੈਟਿੰਗਜ਼ ਸੇਵ ਹੋਈਆਂ।",
    "backup": "ਬੈਕਅਪ", "download_backup": "ਮੇਰਾ ਬੈਕਅਪ ਡਾਊਨਲੋਡ", "backup_help": "ਕਾਰੋਬਾਰ, ਗਾਹਕ, ਸਪਲਾਇਰ, ਉਤਪਾਦ, ਖਰੀਦ, ਸਟਾਕ, ਬਿੱਲ ਅਤੇ ਭੁਗਤਾਨ ਦਾ ਬੈਕਅਪ ਡਾਊਨਲੋਡ ਕਰੋ।", "use_on_phone": "ਫੋਨ 'ਤੇ ਵਰਤੋ", "phone_help": "ਪਬਲਿਕ SHIVPRUBA BILLING ਲਿੰਕ Chrome ਜਾਂ Safari ਵਿੱਚ ਖੋਲ੍ਹੋ ਅਤੇ Add to Home Screen ਚੁਣੋ।",
    "product": "ਉਤਪਾਦ", "service": "ਸੇਵਾ", "purchase": "ਖਰੀਦ", "sale": "ਵਿਕਰੀ", "opening": "ਸ਼ੁਰੂਆਤ", "adjustment": "ਸੋਧ", "search": "ਖੋਜੋ", "invoices": "ਬਿੱਲ", "payments": "ਭੁਗਤਾਨ",
}
# ============================================================
# V5.1 - SALES RETURN / PURCHASE RETURN LANGUAGE LABELS
# ============================================================

TR["hi"].update({
    "sales_return": "बिक्री वापसी",
    "purchase_return": "खरीद वापसी",
})

TR["gu"].update({
    "sales_return": "વેચાણ પરત",
    "purchase_return": "ખરીદી પરત",
})

TR["bn"].update({
    "sales_return": "বিক্রয় ফেরত",
    "purchase_return": "ক্রয় ফেরত",
})

TR["ta"].update({
    "sales_return": "விற்பனைத் திருப்பம்",
    "purchase_return": "கொள்முதல் திருப்பம்",
})

TR["te"].update({
    "sales_return": "అమ్మకాల వాపసు",
    "purchase_return": "కొనుగోలు వాపసు",
})

TR["kn"].update({
    "sales_return": "ಮಾರಾಟ ವಾಪಸಿ",
    "purchase_return": "ಖರೀದಿ ವಾಪಸಿ",
})

TR["ml"].update({
    "sales_return": "വിൽപ്പന മടക്കം",
    "purchase_return": "വാങ്ങൽ മടക്കം",
})

TR["pa"].update({
    "sales_return": "ਵਿਕਰੀ ਵਾਪਸੀ",
    "purchase_return": "ਖਰੀਦ ਵਾਪਸੀ",
})
# ============================================================
# V5.3 - EXPENSES LANGUAGE LABELS
# ============================================================

TR["en"].update({
    "expenses": "Expenses",
    "expense_date": "Date",
    "expense_category": "Category",
    "expense_amount": "Amount",
    "expense_note": "Note",
    "save_expense": "Save Expense",
    "expense_history": "Expense History",
    "no_expenses": "No expenses found.",
    "expense_saved": "Expense saved successfully.",
    "expense_amount_required": "Please enter an amount greater than 0.",
})

TR["hi"].update({
    "expenses": "खर्च",
    "expense_date": "तारीख",
    "expense_category": "श्रेणी",
    "expense_amount": "राशि",
    "expense_note": "टिप्पणी",
    "save_expense": "खर्च सहेजें",
    "expense_history": "खर्च इतिहास",
    "no_expenses": "कोई खर्च नहीं मिला।",
    "expense_saved": "खर्च सफलतापूर्वक सहेजा गया।",
    "expense_amount_required": "कृपया 0 से अधिक राशि दर्ज करें।",
})

TR["mr"].update({
    "expenses": "खर्च",
    "expense_date": "दिनांक",
    "expense_category": "श्रेणी",
    "expense_amount": "रक्कम",
    "expense_note": "नोंद",
    "save_expense": "खर्च जतन करा",
    "expense_history": "खर्च इतिहास",
    "no_expenses": "कोणताही खर्च आढळला नाही.",
    "expense_saved": "खर्च यशस्वीपणे जतन झाला.",
    "expense_amount_required": "कृपया 0 पेक्षा जास्त रक्कम टाका.",
})

TR["gu"].update({
    "expenses": "ખર્ચ",
    "expense_date": "તારીખ",
    "expense_category": "શ્રેણી",
    "expense_amount": "રકમ",
    "expense_note": "નોંધ",
    "save_expense": "ખર્ચ સાચવો",
    "expense_history": "ખર્ચ ઇતિહાસ",
    "no_expenses": "કોઈ ખર્ચ મળ્યો નથી.",
    "expense_saved": "ખર્ચ સફળતાપૂર્વક સાચવાયો.",
    "expense_amount_required": "કૃપા કરીને 0 કરતાં વધુ રકમ દાખલ કરો.",
})

TR["bn"].update({
    "expenses": "খরচ",
    "expense_date": "তারিখ",
    "expense_category": "বিভাগ",
    "expense_amount": "পরিমাণ",
    "expense_note": "নোট",
    "save_expense": "খরচ সংরক্ষণ করুন",
    "expense_history": "খরচের ইতিহাস",
    "no_expenses": "কোনো খরচ পাওয়া যায়নি।",
    "expense_saved": "খরচ সফলভাবে সংরক্ষিত হয়েছে।",
    "expense_amount_required": "অনুগ্রহ করে ০-এর বেশি পরিমাণ লিখুন।",
})

TR["ta"].update({
    "expenses": "செலவுகள்",
    "expense_date": "தேதி",
    "expense_category": "வகை",
    "expense_amount": "தொகை",
    "expense_note": "குறிப்பு",
    "save_expense": "செலவை சேமிக்கவும்",
    "expense_history": "செலவு வரலாறு",
    "no_expenses": "செலவுகள் எதுவும் இல்லை.",
    "expense_saved": "செலவு வெற்றிகரமாக சேமிக்கப்பட்டது.",
    "expense_amount_required": "0-ஐ விட அதிகமான தொகையை உள்ளிடவும்.",
})

TR["te"].update({
    "expenses": "ఖర్చులు",
    "expense_date": "తేదీ",
    "expense_category": "వర్గం",
    "expense_amount": "మొత్తం",
    "expense_note": "గమనిక",
    "save_expense": "ఖర్చును సేవ్ చేయండి",
    "expense_history": "ఖర్చుల చరిత్ర",
    "no_expenses": "ఖర్చులు ఏవీ కనబడలేదు.",
    "expense_saved": "ఖర్చు విజయవంతంగా సేవ్ చేయబడింది.",
    "expense_amount_required": "దయచేసి 0 కంటే ఎక్కువ మొత్తాన్ని నమోదు చేయండి.",
})

TR["kn"].update({
    "expenses": "ವೆಚ್ಚಗಳು",
    "expense_date": "ದಿನಾಂಕ",
    "expense_category": "ವರ್ಗ",
    "expense_amount": "ಮೊತ್ತ",
    "expense_note": "ಟಿಪ್ಪಣಿ",
    "save_expense": "ವೆಚ್ಚವನ್ನು ಉಳಿಸಿ",
    "expense_history": "ವೆಚ್ಚ ಇತಿಹಾಸ",
    "no_expenses": "ಯಾವುದೇ ವೆಚ್ಚಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
    "expense_saved": "ವೆಚ್ಚ ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ.",
    "expense_amount_required": "ದಯವಿಟ್ಟು 0 ಕ್ಕಿಂತ ಹೆಚ್ಚಿನ ಮೊತ್ತವನ್ನು ನಮೂದಿಸಿ.",
})

TR["ml"].update({
    "expenses": "ചെലവുകൾ",
    "expense_date": "തീയതി",
    "expense_category": "വിഭാഗം",
    "expense_amount": "തുക",
    "expense_note": "കുറിപ്പ്",
    "save_expense": "ചെലവ് സംരക്ഷിക്കുക",
    "expense_history": "ചെലവ് ചരിത്രം",
    "no_expenses": "ചെലവുകളൊന്നും കണ്ടെത്തിയില്ല.",
    "expense_saved": "ചെലവ് വിജയകരമായി സംരക്ഷിച്ചു.",
    "expense_amount_required": "ദയവായി 0-ൽ കൂടുതലുള്ള തുക നൽകുക.",
})

TR["pa"].update({
    "expenses": "ਖਰਚੇ",
    "expense_date": "ਤਾਰੀਖ",
    "expense_category": "ਸ਼੍ਰੇਣੀ",
    "expense_amount": "ਰਕਮ",
    "expense_note": "ਨੋਟ",
    "save_expense": "ਖਰਚਾ ਸੰਭਾਲੋ",
    "expense_history": "ਖਰਚਿਆਂ ਦਾ ਇਤਿਹਾਸ",
    "no_expenses": "ਕੋਈ ਖਰਚਾ ਨਹੀਂ ਮਿਲਿਆ।",
    "expense_saved": "ਖਰਚਾ ਸਫਲਤਾਪੂਰਵਕ ਸੰਭਾਲਿਆ ਗਿਆ।",
    "expense_amount_required": "ਕਿਰਪਾ ਕਰਕੇ 0 ਤੋਂ ਵੱਧ ਰਕਮ ਦਰਜ ਕਰੋ।",
})

# ============================================================
# V5.3 - REPORT EXPENSE / PROFIT LABELS
# ============================================================

TR["en"].update({
    "total_expenses": "Total Expenses",
    "estimated_profit_loss": "Estimated Profit / Loss",
})

TR["hi"].update({
    "total_expenses": "कुल खर्च",
    "estimated_profit_loss": "अनुमानित लाभ / हानि",
})

TR["mr"].update({
    "total_expenses": "एकूण खर्च",
    "estimated_profit_loss": "अंदाजे नफा / तोटा",
})

TR["gu"].update({
    "total_expenses": "કુલ ખર્ચ",
    "estimated_profit_loss": "અંદાજિત નફો / નુકસાન",
})

TR["bn"].update({
    "total_expenses": "মোট খরচ",
    "estimated_profit_loss": "আনুমানিক লাভ / ক্ষতি",
})

TR["ta"].update({
    "total_expenses": "மொத்த செலவுகள்",
    "estimated_profit_loss": "மதிப்பிடப்பட்ட லாபம் / நஷ்டம்",
})

TR["te"].update({
    "total_expenses": "మొత్తం ఖర్చులు",
    "estimated_profit_loss": "అంచనా లాభం / నష్టం",
})

TR["kn"].update({
    "total_expenses": "ಒಟ್ಟು ವೆಚ್ಚಗಳು",
    "estimated_profit_loss": "ಅಂದಾಜು ಲಾಭ / ನಷ್ಟ",
})

TR["ml"].update({
    "total_expenses": "ആകെ ചെലവുകൾ",
    "estimated_profit_loss": "കണക്കാക്കിയ ലാഭം / നഷ്ടം",
})

TR["pa"].update({
    "total_expenses": "ਕੁੱਲ ਖਰਚੇ",
    "estimated_profit_loss": "ਅੰਦਾਜ਼ਨ ਲਾਭ / ਨੁਕਸਾਨ",
})
# ============================================================
# V5.3 - EDIT / DELETE HISTORY LABELS
# ============================================================

TR["en"].update({
    "edit_delete_history": "Edit / Delete History",
    "change_history": "Change History",
    "edit_record": "Edit Record",
    "delete_record": "Delete Record",
    "record_type": "Record Type",
    "action": "Action",
    "old_data": "Previous Data",
    "new_data": "New Data",
    "edited": "Edited",
    "deleted": "Deleted",
    "confirm_delete": "I confirm that I want to delete this record.",
    "expense_updated": "Expense updated successfully.",
    "expense_deleted": "Expense deleted successfully.",
    "no_change_history": "No edit or delete history yet.",
})

TR["mr"].update({
    "edit_delete_history": "बदल / डिलीट इतिहास",
    "change_history": "बदल इतिहास",
    "edit_record": "नोंद बदला",
    "delete_record": "नोंद डिलीट करा",
    "record_type": "नोंद प्रकार",
    "action": "क्रिया",
    "old_data": "जुनी माहिती",
    "new_data": "नवीन माहिती",
    "edited": "बदलले",
    "deleted": "डिलीट केले",
    "confirm_delete": "ही नोंद डिलीट करायची आहे याची मी खात्री देतो.",
    "expense_updated": "खर्च यशस्वीपणे अपडेट झाला.",
    "expense_deleted": "खर्च यशस्वीपणे डिलीट झाला.",
    "no_change_history": "अजून कोणताही बदल किंवा डिलीट इतिहास नाही.",
})
# ============================================================
# V5.4 - EDIT / DELETE HISTORY - REMAINING 8 LANGUAGES
# ============================================================

TR["hi"].update({
    "edit_delete_history": "संपादन / हटाने का इतिहास",
    "change_history": "परिवर्तन इतिहास",
    "edit_record": "रिकॉर्ड संपादित करें",
    "delete_record": "रिकॉर्ड हटाएं",
    "record_type": "रिकॉर्ड प्रकार",
    "action": "कार्रवाई",
    "old_data": "पिछला डेटा",
    "new_data": "नया डेटा",
    "edited": "संपादित",
    "deleted": "हटाया गया",
    "confirm_delete": "मैं पुष्टि करता हूँ कि मैं यह रिकॉर्ड हटाना चाहता हूँ।",
    "expense_updated": "खर्च सफलतापूर्वक अपडेट किया गया।",
    "expense_deleted": "खर्च सफलतापूर्वक हटाया गया।",
    "no_change_history": "अभी तक कोई संपादन या हटाने का इतिहास नहीं है।",
})

TR["gu"].update({
    "edit_delete_history": "ફેરફાર / કાઢી નાખવાનો ઇતિહાસ",
    "change_history": "ફેરફાર ઇતિહાસ",
    "edit_record": "રેકોર્ડમાં ફેરફાર કરો",
    "delete_record": "રેકોર્ડ કાઢી નાખો",
    "record_type": "રેકોર્ડ પ્રકાર",
    "action": "ક્રિયા",
    "old_data": "પહેલાનો ડેટા",
    "new_data": "નવો ડેટા",
    "edited": "ફેરફાર કરેલ",
    "deleted": "કાઢી નાખેલ",
    "confirm_delete": "હું ખાતરી કરું છું કે હું આ રેકોર્ડ કાઢી નાખવા માંગું છું.",
    "expense_updated": "ખર્ચ સફળતાપૂર્વક અપડેટ થયો.",
    "expense_deleted": "ખર્ચ સફળતાપૂર્વક કાઢી નાખવામાં આવ્યો.",
    "no_change_history": "હજુ સુધી કોઈ ફેરફાર અથવા કાઢી નાખવાનો ઇતિહાસ નથી.",
})

TR["bn"].update({
    "edit_delete_history": "সম্পাদনা / মুছে ফেলার ইতিহাস",
    "change_history": "পরিবর্তনের ইতিহাস",
    "edit_record": "রেকর্ড সম্পাদনা করুন",
    "delete_record": "রেকর্ড মুছুন",
    "record_type": "রেকর্ডের ধরন",
    "action": "কার্যক্রম",
    "old_data": "পূর্ববর্তী তথ্য",
    "new_data": "নতুন তথ্য",
    "edited": "সম্পাদিত",
    "deleted": "মুছে ফেলা হয়েছে",
    "confirm_delete": "আমি নিশ্চিত করছি যে আমি এই রেকর্ডটি মুছে ফেলতে চাই।",
    "expense_updated": "খরচ সফলভাবে আপডেট হয়েছে।",
    "expense_deleted": "খরচ সফলভাবে মুছে ফেলা হয়েছে।",
    "no_change_history": "এখনও কোনো সম্পাদনা বা মুছে ফেলার ইতিহাস নেই।",
})

TR["ta"].update({
    "edit_delete_history": "திருத்தம் / நீக்கல் வரலாறு",
    "change_history": "மாற்ற வரலாறு",
    "edit_record": "பதிவைத் திருத்து",
    "delete_record": "பதிவை நீக்கு",
    "record_type": "பதிவு வகை",
    "action": "செயல்",
    "old_data": "முந்தைய தரவு",
    "new_data": "புதிய தரவு",
    "edited": "திருத்தப்பட்டது",
    "deleted": "நீக்கப்பட்டது",
    "confirm_delete": "இந்த பதிவை நீக்க விரும்புகிறேன் என்பதை உறுதிப்படுத்துகிறேன்.",
    "expense_updated": "செலவு வெற்றிகரமாக புதுப்பிக்கப்பட்டது.",
    "expense_deleted": "செலவு வெற்றிகரமாக நீக்கப்பட்டது.",
    "no_change_history": "இதுவரை திருத்தம் அல்லது நீக்கல் வரலாறு இல்லை.",
})

TR["te"].update({
    "edit_delete_history": "సవరింపు / తొలగింపు చరిత్ర",
    "change_history": "మార్పుల చరిత్ర",
    "edit_record": "రికార్డును సవరించండి",
    "delete_record": "రికార్డును తొలగించండి",
    "record_type": "రికార్డు రకం",
    "action": "చర్య",
    "old_data": "మునుపటి డేటా",
    "new_data": "కొత్త డేటా",
    "edited": "సవరించబడింది",
    "deleted": "తొలగించబడింది",
    "confirm_delete": "ఈ రికార్డును తొలగించాలని నేను నిర్ధారిస్తున్నాను.",
    "expense_updated": "ఖర్చు విజయవంతంగా నవీకరించబడింది.",
    "expense_deleted": "ఖర్చు విజయవంతంగా తొలగించబడింది.",
    "no_change_history": "ఇంకా సవరింపు లేదా తొలగింపు చరిత్ర లేదు.",
})

TR["kn"].update({
    "edit_delete_history": "ತಿದ್ದುಪಡಿ / ಅಳಿಸುವಿಕೆ ಇತಿಹಾಸ",
    "change_history": "ಬದಲಾವಣೆ ಇತಿಹಾಸ",
    "edit_record": "ದಾಖಲೆಯನ್ನು ತಿದ್ದುಪಡಿ ಮಾಡಿ",
    "delete_record": "ದಾಖಲೆಯನ್ನು ಅಳಿಸಿ",
    "record_type": "ದಾಖಲೆ ಪ್ರಕಾರ",
    "action": "ಕ್ರಿಯೆ",
    "old_data": "ಹಿಂದಿನ ಮಾಹಿತಿ",
    "new_data": "ಹೊಸ ಮಾಹಿತಿ",
    "edited": "ತಿದ್ದುಪಡಿ ಮಾಡಲಾಗಿದೆ",
    "deleted": "ಅಳಿಸಲಾಗಿದೆ",
    "confirm_delete": "ಈ ದಾಖಲೆಯನ್ನು ಅಳಿಸಲು ನಾನು ದೃಢೀಕರಿಸುತ್ತೇನೆ.",
    "expense_updated": "ವೆಚ್ಚವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ.",
    "expense_deleted": "ವೆಚ್ಚವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಅಳಿಸಲಾಗಿದೆ.",
    "no_change_history": "ಇನ್ನೂ ಯಾವುದೇ ತಿದ್ದುಪಡಿ ಅಥವಾ ಅಳಿಸುವಿಕೆ ಇತಿಹಾಸ ಇಲ್ಲ.",
})

TR["ml"].update({
    "edit_delete_history": "തിരുത്തൽ / ഇല്ലാതാക്കൽ ചരിത്രം",
    "change_history": "മാറ്റങ്ങളുടെ ചരിത്രം",
    "edit_record": "രേഖ തിരുത്തുക",
    "delete_record": "രേഖ ഇല്ലാതാക്കുക",
    "record_type": "രേഖയുടെ തരം",
    "action": "നടപടി",
    "old_data": "മുൻ വിവരങ്ങൾ",
    "new_data": "പുതിയ വിവരങ്ങൾ",
    "edited": "തിരുത്തി",
    "deleted": "ഇല്ലാതാക്കി",
    "confirm_delete": "ഈ രേഖ ഇല്ലാതാക്കണമെന്ന് ഞാൻ സ്ഥിരീകരിക്കുന്നു.",
    "expense_updated": "ചെലവ് വിജയകരമായി പുതുക്കി.",
    "expense_deleted": "ചെലവ് വിജയകരമായി ഇല്ലാതാക്കി.",
    "no_change_history": "ഇതുവരെ തിരുത്തൽ അല്ലെങ്കിൽ ഇല്ലാതാക്കൽ ചരിത്രമില്ല.",
})

TR["pa"].update({
    "edit_delete_history": "ਸੋਧ / ਮਿਟਾਉਣ ਦਾ ਇਤਿਹਾਸ",
    "change_history": "ਬਦਲਾਅ ਇਤਿਹਾਸ",
    "edit_record": "ਰਿਕਾਰਡ ਸੋਧੋ",
    "delete_record": "ਰਿਕਾਰਡ ਮਿਟਾਓ",
    "record_type": "ਰਿਕਾਰਡ ਦੀ ਕਿਸਮ",
    "action": "ਕਾਰਵਾਈ",
    "old_data": "ਪਿਛਲਾ ਡਾਟਾ",
    "new_data": "ਨਵਾਂ ਡਾਟਾ",
    "edited": "ਸੋਧਿਆ ਗਿਆ",
    "deleted": "ਮਿਟਾਇਆ ਗਿਆ",
    "confirm_delete": "ਮੈਂ ਪੁਸ਼ਟੀ ਕਰਦਾ ਹਾਂ ਕਿ ਮੈਂ ਇਹ ਰਿਕਾਰਡ ਮਿਟਾਉਣਾ ਚਾਹੁੰਦਾ ਹਾਂ।",
    "expense_updated": "ਖਰਚਾ ਸਫਲਤਾਪੂਰਵਕ ਅਪਡੇਟ ਹੋਇਆ।",
    "expense_deleted": "ਖਰਚਾ ਸਫਲਤਾਪੂਰਵਕ ਮਿਟਾਇਆ ਗਿਆ।",
    "no_change_history": "ਹਾਲੇ ਕੋਈ ਸੋਧ ਜਾਂ ਮਿਟਾਉਣ ਦਾ ਇਤਿਹਾਸ ਨਹੀਂ ਹੈ।",
})

# ============================================================
# V5.1 - PURCHASE RETURN COMPLETE LANGUAGE MESSAGES
# ============================================================

TR["en"].update({
    "return_quantity_required": "Please enter return quantity.",
    "return_recently_saved": "This return was just saved. Please wait a few seconds.",
    "purchase_return_saved": "Purchase Return saved",
    "purchase_return_exists": "This Purchase Return already exists.",
})

TR["mr"].update({
    "return_quantity_required": "परताव्याचे प्रमाण टाका.",
    "return_recently_saved": "हा परतावा आत्ताच सेव्ह झाला आहे. कृपया काही सेकंद थांबा.",
    "purchase_return_saved": "खरेदी परतावा सेव्ह झाला",
    "purchase_return_exists": "हा खरेदी परतावा आधीपासून अस्तित्वात आहे.",
})

TR["hi"].update({
    "return_quantity_required": "वापसी की मात्रा दर्ज करें।",
    "return_recently_saved": "यह वापसी अभी सेव हुई है। कृपया कुछ सेकंड प्रतीक्षा करें।",
    "purchase_return_saved": "खरीद वापसी सेव हुई",
    "purchase_return_exists": "यह खरीद वापसी पहले से मौजूद है।",
})

TR["gu"].update({
    "return_quantity_required": "પરત કરવાની માત્રા દાખલ કરો.",
    "return_recently_saved": "આ પરત હમણાં જ સેવ થઈ છે. કૃપા કરીને થોડા સેકંડ રાહ જુઓ.",
    "purchase_return_saved": "ખરીદી પરત સેવ થઈ",
    "purchase_return_exists": "આ ખરીદી પરત પહેલેથી હાજર છે.",
})

TR["bn"].update({
    "return_quantity_required": "ফেরতের পরিমাণ লিখুন।",
    "return_recently_saved": "এই ফেরতটি এখনই সেভ হয়েছে। অনুগ্রহ করে কয়েক সেকেন্ড অপেক্ষা করুন।",
    "purchase_return_saved": "ক্রয় ফেরত সেভ হয়েছে",
    "purchase_return_exists": "এই ক্রয় ফেরতটি আগে থেকেই আছে।",
})

TR["ta"].update({
    "return_quantity_required": "திருப்பி அளவை உள்ளிடவும்.",
    "return_recently_saved": "இந்த திருப்பம் இப்போது சேமிக்கப்பட்டது. சில விநாடிகள் காத்திருக்கவும்.",
    "purchase_return_saved": "கொள்முதல் திருப்பம் சேமிக்கப்பட்டது",
    "purchase_return_exists": "இந்த கொள்முதல் திருப்பம் ஏற்கனவே உள்ளது.",
})

TR["te"].update({
    "return_quantity_required": "వాపసు పరిమాణాన్ని నమోదు చేయండి.",
    "return_recently_saved": "ఈ వాపసు ఇప్పుడే సేవ్ అయింది. దయచేసి కొన్ని సెకన్లు వేచి ఉండండి.",
    "purchase_return_saved": "కొనుగోలు వాపసు సేవ్ అయింది",
    "purchase_return_exists": "ఈ కొనుగోలు వాపసు ఇప్పటికే ఉంది.",
})

TR["kn"].update({
    "return_quantity_required": "ವಾಪಸಿ ಪ್ರಮಾಣವನ್ನು ನಮೂದಿಸಿ.",
    "return_recently_saved": "ಈ ವಾಪಸಿ ಈಗಷ್ಟೇ ಸೇವ್ ಆಗಿದೆ. ದಯವಿಟ್ಟು ಕೆಲವು ಸೆಕೆಂಡು ಕಾಯಿರಿ.",
    "purchase_return_saved": "ಖರೀದಿ ವಾಪಸಿ ಸೇವ್ ಆಗಿದೆ",
    "purchase_return_exists": "ಈ ಖರೀದಿ ವಾಪಸಿ ಈಗಾಗಲೇ ಇದೆ.",
})

TR["ml"].update({
    "return_quantity_required": "മടക്കാനുള്ള അളവ് നൽകുക.",
    "return_recently_saved": "ഈ മടക്കം ഇപ്പോൾ തന്നെ സേവ് ചെയ്തു. ദയവായി കുറച്ച് സെക്കൻഡ് കാത്തിരിക്കുക.",
    "purchase_return_saved": "വാങ്ങൽ മടക്കം സേവ് ചെയ്തു",
    "purchase_return_exists": "ഈ വാങ്ങൽ മടക്കം ഇതിനകം നിലവിലുണ്ട്.",
})

TR["pa"].update({
    "return_quantity_required": "ਵਾਪਸੀ ਦੀ ਮਾਤਰਾ ਦਰਜ ਕਰੋ।",
    "return_recently_saved": "ਇਹ ਵਾਪਸੀ ਹੁਣੇ ਹੀ ਸੇਵ ਹੋਈ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਕੁਝ ਸਕਿੰਟ ਉਡੀਕ ਕਰੋ।",
    "purchase_return_saved": "ਖਰੀਦ ਵਾਪਸੀ ਸੇਵ ਹੋਈ",
    "purchase_return_exists": "ਇਹ ਖਰੀਦ ਵਾਪਸੀ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ।",
})
# ============================================================
# V5.5 - COMPLETE UI LANGUAGE FIXES
# ============================================================

TR["en"].update({
    "save_changes": "Save Changes",
    "sales_return_credit": "Sales Return Credit",
    "invoice_paid_total_error": "Invoice cannot be updated because the new total is lower than the amount already paid.",
    "invoice_updated": "Invoice updated successfully.",
    "invoice_has_sales_return": "This invoice has a Sales Return. Delete the related Sales Return first before deleting this invoice.",
    "invoice_deleted": "Invoice deleted successfully.",
    "invoice_delete_failed": "Invoice could not be deleted",
    "sales_return_saved": "Sales Return saved",
    "sales_return_exists": "This Sales Return already exists.",
    "no_visible_changes": "No visible field changes were found.",
    "no_previous_record": "No previous record information available.",
    "export_excel_csv": "Excel / CSV Export",
    "export_data_from": "Export data from",
    "export_to": "to",
    "download_excel": "Download Excel",
    "download_csv_files": "Download CSV Files",
    "excel_export_failed": "Excel export could not start",
    "backup_keep_safe": "Keep this backup file safe. It contains your business records.",
    "restore_backup": "Restore Backup",
    "restore_help": "Upload a SHIVPRUBA BILLING backup file. Restore will replace the current business data of this account.",
    "upload_backup_file": "Upload Backup File (.json)",
    "invalid_backup_missing": "Invalid backup file. Missing",
    "backup_valid": "Backup file is valid.",
    "backup_read_failed": "Could not read backup file",
    "restore_confirm_replace": "I understand that current business data will be replaced.",
    "restore_type_confirm": "Type RESTORE to confirm",
    "restore_my_backup": "Restore My Backup",
    "backup_restored": "Backup restored successfully. Business data has been recovered.",
    "restore_integrity_failed": "Restore stopped because duplicate or invalid database data was found",
    "restore_failed": "Restore failed. No partial restore was saved. Error",
})

TR["mr"].update({
    "save_changes": "बदल सेव्ह करा", "sales_return_credit": "विक्री परतावा क्रेडिट",
    "invoice_paid_total_error": "नवीन बिलाची एकूण रक्कम आधीच मिळालेल्या पेमेंटपेक्षा कमी असल्यामुळे बिल अपडेट करता येणार नाही.",
    "invoice_updated": "बिल यशस्वीपणे अपडेट झाले.", "invoice_has_sales_return": "या बिलावर विक्री परतावा आहे. हे बिल डिलीट करण्यापूर्वी संबंधित विक्री परतावा डिलीट करा.",
    "invoice_deleted": "बिल यशस्वीपणे डिलीट झाले.", "invoice_delete_failed": "बिल डिलीट करता आले नाही",
    "sales_return_saved": "विक्री परतावा सेव्ह झाला", "sales_return_exists": "हा विक्री परतावा आधीपासून अस्तित्वात आहे.",
    "no_visible_changes": "दिसणाऱ्या माहितीमध्ये कोणताही बदल आढळला नाही.", "no_previous_record": "मागील नोंदीची माहिती उपलब्ध नाही.",
    "export_excel_csv": "Excel / CSV निर्यात", "export_data_from": "या दिनांकापासून डेटा निर्यात", "export_to": "ते",
    "download_excel": "Excel डाउनलोड करा", "download_csv_files": "CSV फाइल्स डाउनलोड करा", "excel_export_failed": "Excel निर्यात सुरू करता आली नाही",
    "backup_keep_safe": "ही बॅकअप फाइल सुरक्षित ठेवा. यात तुमच्या व्यवसायाच्या नोंदी आहेत.", "restore_backup": "बॅकअप पुनर्संचयित करा",
    "restore_help": "SHIVPRUBA BILLING ची बॅकअप फाइल अपलोड करा. पुनर्संचयित केल्यावर या खात्याचा सध्याचा व्यवसाय डेटा बदलला जाईल.",
    "upload_backup_file": "बॅकअप फाइल अपलोड करा (.json)", "invalid_backup_missing": "अवैध बॅकअप फाइल. हे विभाग उपलब्ध नाहीत",
    "backup_valid": "बॅकअप फाइल वैध आहे.", "backup_read_failed": "बॅकअप फाइल वाचता आली नाही",
    "restore_confirm_replace": "सध्याचा व्यवसाय डेटा बदलला जाईल हे मला समजले आहे.", "restore_type_confirm": "पुष्टीसाठी RESTORE टाइप करा",
    "restore_my_backup": "माझा बॅकअप पुनर्संचयित करा", "backup_restored": "बॅकअप यशस्वीपणे पुनर्संचयित झाला. व्यवसाय डेटा परत मिळाला आहे.",
    "restore_integrity_failed": "डुप्लिकेट किंवा अवैध डेटाबेस डेटा आढळल्यामुळे पुनर्संचयित करणे थांबवले", "restore_failed": "पुनर्संचयित करणे अयशस्वी. अपूर्ण डेटा सेव्ह केलेला नाही. त्रुटी",
})

TR["hi"].update({
    "save_changes": "बदलाव सेव करें", "sales_return_credit": "बिक्री वापसी क्रेडिट", "invoice_paid_total_error": "नई बिल राशि पहले से प्राप्त भुगतान से कम है, इसलिए बिल अपडेट नहीं किया जा सकता।",
    "invoice_updated": "बिल सफलतापूर्वक अपडेट हुआ।", "invoice_has_sales_return": "इस बिल पर बिक्री वापसी है। बिल हटाने से पहले संबंधित बिक्री वापसी हटाएं।", "invoice_deleted": "बिल सफलतापूर्वक हटाया गया।", "invoice_delete_failed": "बिल हटाया नहीं जा सका",
    "sales_return_saved": "बिक्री वापसी सेव हुई", "sales_return_exists": "यह बिक्री वापसी पहले से मौजूद है।", "no_visible_changes": "दिखाई देने वाली जानकारी में कोई बदलाव नहीं मिला।", "no_previous_record": "पिछले रिकॉर्ड की जानकारी उपलब्ध नहीं है।",
    "export_excel_csv": "Excel / CSV निर्यात", "export_data_from": "इस तारीख से डेटा निर्यात", "export_to": "तक", "download_excel": "Excel डाउनलोड करें", "download_csv_files": "CSV फाइलें डाउनलोड करें", "excel_export_failed": "Excel निर्यात शुरू नहीं हो सका",
    "backup_keep_safe": "इस बैकअप फाइल को सुरक्षित रखें। इसमें आपके व्यवसाय के रिकॉर्ड हैं।", "restore_backup": "बैकअप पुनर्स्थापित करें", "restore_help": "SHIVPRUBA BILLING बैकअप फाइल अपलोड करें। पुनर्स्थापना इस खाते के वर्तमान व्यवसाय डेटा को बदल देगी।", "upload_backup_file": "बैकअप फाइल अपलोड करें (.json)",
    "invalid_backup_missing": "अमान्य बैकअप फाइल। ये भाग नहीं मिले", "backup_valid": "बैकअप फाइल मान्य है।", "backup_read_failed": "बैकअप फाइल पढ़ी नहीं जा सकी", "restore_confirm_replace": "मैं समझता हूँ कि वर्तमान व्यवसाय डेटा बदल दिया जाएगा।", "restore_type_confirm": "पुष्टि के लिए RESTORE टाइप करें", "restore_my_backup": "मेरा बैकअप पुनर्स्थापित करें", "backup_restored": "बैकअप सफलतापूर्वक पुनर्स्थापित हुआ। व्यवसाय डेटा वापस मिल गया है।", "restore_integrity_failed": "डुप्लिकेट या अमान्य डेटाबेस डेटा मिलने के कारण पुनर्स्थापना रोक दी गई", "restore_failed": "पुनर्स्थापना विफल रही। अधूरा डेटा सेव नहीं किया गया। त्रुटि",
})

TR["gu"].update({
    "save_changes":"ફેરફારો સેવ કરો","sales_return_credit":"વેચાણ પરત ક્રેડિટ","invoice_paid_total_error":"નવી બિલ રકમ પહેલેથી મળેલા ચુકવણી કરતાં ઓછી હોવાથી બિલ અપડેટ કરી શકાતું નથી.","invoice_updated":"બિલ સફળતાપૂર્વક અપડેટ થયું.","invoice_has_sales_return":"આ બિલમાં વેચાણ પરત છે. બિલ કાઢતા પહેલાં સંબંધિત વેચાણ પરત કાઢો.","invoice_deleted":"બિલ સફળતાપૂર્વક કાઢી નાખ્યું.","invoice_delete_failed":"બિલ કાઢી શકાયું નથી","sales_return_saved":"વેચાણ પરત સેવ થયું","sales_return_exists":"આ વેચાણ પરત પહેલેથી હાજર છે.","no_visible_changes":"દેખાતી માહિતીમાં કોઈ ફેરફાર મળ્યો નથી.","no_previous_record":"પહેલાના રેકોર્ડની માહિતી ઉપલબ્ધ નથી.","export_excel_csv":"Excel / CSV નિકાસ","export_data_from":"આ તારીખથી ડેટા નિકાસ","export_to":"થી","download_excel":"Excel ડાઉનલોડ કરો","download_csv_files":"CSV ફાઇલો ડાઉનલોડ કરો","excel_export_failed":"Excel નિકાસ શરૂ થઈ શકી નથી","backup_keep_safe":"આ બેકઅપ ફાઇલ સુરક્ષિત રાખો. તેમાં તમારા વ્યવસાયના રેકોર્ડ છે.","restore_backup":"બેકઅપ પુનઃસ્થાપિત કરો","restore_help":"SHIVPRUBA BILLING બેકઅપ ફાઇલ અપલોડ કરો. પુનઃસ્થાપન આ ખાતાનો હાલનો વ્યવસાય ડેટા બદલી દેશે.","upload_backup_file":"બેકઅપ ફાઇલ અપલોડ કરો (.json)","invalid_backup_missing":"અમાન્ય બેકઅપ ફાઇલ. આ વિભાગો નથી","backup_valid":"બેકઅપ ફાઇલ માન્ય છે.","backup_read_failed":"બેકઅપ ફાઇલ વાંચી શકાઈ નથી","restore_confirm_replace":"હું સમજું છું કે હાલનો વ્યવસાય ડેટા બદલાઈ જશે.","restore_type_confirm":"પુષ્ટિ માટે RESTORE લખો","restore_my_backup":"મારો બેકઅપ પુનઃસ્થાપિત કરો","backup_restored":"બેકઅપ સફળતાપૂર્વક પુનઃસ્થાપિત થયો. વ્યવસાય ડેટા પાછો મળ્યો છે.","restore_integrity_failed":"ડુપ્લિકેટ અથવા અમાન્ય ડેટાબેસ ડેટાને કારણે પુનઃસ્થાપન અટક્યું","restore_failed":"પુનઃસ્થાપન નિષ્ફળ ગયું. અધૂરો ડેટા સેવ થયો નથી. ભૂલ",
})

TR["bn"].update({
    "save_changes":"পরিবর্তন সেভ করুন","sales_return_credit":"বিক্রয় ফেরত ক্রেডিট","invoice_paid_total_error":"নতুন বিলের মোট পরিমাণ ইতিমধ্যে প্রাপ্ত পেমেন্টের চেয়ে কম হওয়ায় বিল আপডেট করা যাবে না।","invoice_updated":"বিল সফলভাবে আপডেট হয়েছে।","invoice_has_sales_return":"এই বিলে বিক্রয় ফেরত আছে। বিল মুছার আগে সংশ্লিষ্ট বিক্রয় ফেরত মুছুন।","invoice_deleted":"বিল সফলভাবে মুছে ফেলা হয়েছে।","invoice_delete_failed":"বিল মুছে ফেলা যায়নি","sales_return_saved":"বিক্রয় ফেরত সেভ হয়েছে","sales_return_exists":"এই বিক্রয় ফেরত আগে থেকেই আছে।","no_visible_changes":"দৃশ্যমান তথ্যে কোনো পরিবর্তন পাওয়া যায়নি।","no_previous_record":"পূর্ববর্তী রেকর্ডের তথ্য পাওয়া যায়নি।","export_excel_csv":"Excel / CSV রপ্তানি","export_data_from":"এই তারিখ থেকে ডেটা রপ্তানি","export_to":"থেকে","download_excel":"Excel ডাউনলোড করুন","download_csv_files":"CSV ফাইল ডাউনলোড করুন","excel_export_failed":"Excel রপ্তানি শুরু করা যায়নি","backup_keep_safe":"এই ব্যাকআপ ফাইলটি নিরাপদে রাখুন। এতে আপনার ব্যবসার রেকর্ড রয়েছে।","restore_backup":"ব্যাকআপ পুনরুদ্ধার করুন","restore_help":"SHIVPRUBA BILLING ব্যাকআপ ফাইল আপলোড করুন। পুনরুদ্ধার করলে এই অ্যাকাউন্টের বর্তমান ব্যবসার ডেটা প্রতিস্থাপিত হবে।","upload_backup_file":"ব্যাকআপ ফাইল আপলোড করুন (.json)","invalid_backup_missing":"অবৈধ ব্যাকআপ ফাইল। এই অংশগুলো নেই","backup_valid":"ব্যাকআপ ফাইল বৈধ।","backup_read_failed":"ব্যাকআপ ফাইল পড়া যায়নি","restore_confirm_replace":"আমি বুঝেছি যে বর্তমান ব্যবসার ডেটা প্রতিস্থাপিত হবে।","restore_type_confirm":"নিশ্চিত করতে RESTORE লিখুন","restore_my_backup":"আমার ব্যাকআপ পুনরুদ্ধার করুন","backup_restored":"ব্যাকআপ সফলভাবে পুনরুদ্ধার হয়েছে। ব্যবসার ডেটা ফিরে এসেছে।","restore_integrity_failed":"ডুপ্লিকেট বা অবৈধ ডেটাবেস ডেটার কারণে পুনরুদ্ধার বন্ধ হয়েছে","restore_failed":"পুনরুদ্ধার ব্যর্থ হয়েছে। আংশিক ডেটা সেভ হয়নি। ত্রুটি",
})

TR["ta"].update({
    "save_changes":"மாற்றங்களை சேமிக்கவும்","sales_return_credit":"விற்பனைத் திருப்பம் கிரெடிட்","invoice_paid_total_error":"புதிய பில் மொத்தம் ஏற்கனவே பெறப்பட்ட கட்டணத்தை விட குறைவாக இருப்பதால் பில்லை புதுப்பிக்க முடியாது.","invoice_updated":"பில் வெற்றிகரமாக புதுப்பிக்கப்பட்டது.","invoice_has_sales_return":"இந்த பில்லில் விற்பனைத் திருப்பம் உள்ளது. பில்லை நீக்கும் முன் தொடர்புடைய திருப்பத்தை நீக்கவும்.","invoice_deleted":"பில் வெற்றிகரமாக நீக்கப்பட்டது.","invoice_delete_failed":"பில்லை நீக்க முடியவில்லை","sales_return_saved":"விற்பனைத் திருப்பம் சேமிக்கப்பட்டது","sales_return_exists":"இந்த விற்பனைத் திருப்பம் ஏற்கனவே உள்ளது.","no_visible_changes":"காணக்கூடிய தகவலில் மாற்றம் இல்லை.","no_previous_record":"முந்தைய பதிவு தகவல் கிடைக்கவில்லை.","export_excel_csv":"Excel / CSV ஏற்றுமதி","export_data_from":"இந்த தேதியிலிருந்து தரவை ஏற்றுமதி","export_to":"வரை","download_excel":"Excel பதிவிறக்கவும்","download_csv_files":"CSV கோப்புகளை பதிவிறக்கவும்","excel_export_failed":"Excel ஏற்றுமதி தொடங்க முடியவில்லை","backup_keep_safe":"இந்த காப்பு கோப்பை பாதுகாப்பாக வைத்திருங்கள். இதில் உங்கள் வணிக பதிவுகள் உள்ளன.","restore_backup":"காப்பை மீட்டமைக்கவும்","restore_help":"SHIVPRUBA BILLING காப்பு கோப்பை பதிவேற்றவும். மீட்டமைத்தால் தற்போதைய வணிக தரவு மாற்றப்படும்.","upload_backup_file":"காப்பு கோப்பை பதிவேற்றவும் (.json)","invalid_backup_missing":"தவறான காப்பு கோப்பு. இவை இல்லை","backup_valid":"காப்பு கோப்பு செல்லுபடியாகும்.","backup_read_failed":"காப்பு கோப்பை படிக்க முடியவில்லை","restore_confirm_replace":"தற்போதைய வணிக தரவு மாற்றப்படும் என்பதை புரிந்துகொண்டேன்.","restore_type_confirm":"உறுதிப்படுத்த RESTORE என தட்டச்சு செய்யவும்","restore_my_backup":"என் காப்பை மீட்டமைக்கவும்","backup_restored":"காப்பு வெற்றிகரமாக மீட்டமைக்கப்பட்டது. வணிக தரவு மீட்கப்பட்டது.","restore_integrity_failed":"நகல் அல்லது தவறான தரவுத்தள தரவு காரணமாக மீட்டமைப்பு நிறுத்தப்பட்டது","restore_failed":"மீட்டமைப்பு தோல்வியடைந்தது. பகுதி தரவு சேமிக்கப்படவில்லை. பிழை",
})

TR["te"].update({
    "save_changes":"మార్పులను సేవ్ చేయండి","sales_return_credit":"అమ్మకాల వాపసు క్రెడిట్","invoice_paid_total_error":"కొత్త బిల్లు మొత్తం ఇప్పటికే అందుకున్న చెల్లింపుకంటే తక్కువగా ఉన్నందున బిల్లును అప్‌డేట్ చేయలేము.","invoice_updated":"బిల్లు విజయవంతంగా అప్‌డేట్ అయింది.","invoice_has_sales_return":"ఈ బిల్లుకు అమ్మకాల వాపసు ఉంది. బిల్లును తొలగించే ముందు సంబంధిత వాపసును తొలగించండి.","invoice_deleted":"బిల్లు విజయవంతంగా తొలగించబడింది.","invoice_delete_failed":"బిల్లును తొలగించలేకపోయాం","sales_return_saved":"అమ్మకాల వాపసు సేవ్ అయింది","sales_return_exists":"ఈ అమ్మకాల వాపసు ఇప్పటికే ఉంది.","no_visible_changes":"కనిపించే సమాచారంలో మార్పులు లేవు.","no_previous_record":"మునుపటి రికార్డు సమాచారం అందుబాటులో లేదు.","export_excel_csv":"Excel / CSV ఎగుమతి","export_data_from":"ఈ తేదీ నుండి డేటా ఎగుమతి","export_to":"వరకు","download_excel":"Excel డౌన్‌లోడ్ చేయండి","download_csv_files":"CSV ఫైళ్లను డౌన్‌లోడ్ చేయండి","excel_export_failed":"Excel ఎగుమతి ప్రారంభించలేకపోయాం","backup_keep_safe":"ఈ బ్యాకప్ ఫైల్‌ను సురక్షితంగా ఉంచండి. ఇందులో మీ వ్యాపార రికార్డులు ఉన్నాయి.","restore_backup":"బ్యాకప్ పునరుద్ధరించండి","restore_help":"SHIVPRUBA BILLING బ్యాకప్ ఫైల్‌ను అప్‌లోడ్ చేయండి. పునరుద్ధరణ ప్రస్తుత వ్యాపార డేటాను భర్తీ చేస్తుంది.","upload_backup_file":"బ్యాకప్ ఫైల్ అప్‌లోడ్ చేయండి (.json)","invalid_backup_missing":"చెల్లని బ్యాకప్ ఫైల్. ఇవి లేవు","backup_valid":"బ్యాకప్ ఫైల్ చెల్లుబాటు అవుతుంది.","backup_read_failed":"బ్యాకప్ ఫైల్ చదవలేకపోయాం","restore_confirm_replace":"ప్రస్తుత వ్యాపార డేటా భర్తీ అవుతుందని నాకు అర్థమైంది.","restore_type_confirm":"నిర్ధారించడానికి RESTORE టైప్ చేయండి","restore_my_backup":"నా బ్యాకప్ పునరుద్ధరించండి","backup_restored":"బ్యాకప్ విజయవంతంగా పునరుద్ధరించబడింది. వ్యాపార డేటా తిరిగి పొందబడింది.","restore_integrity_failed":"డూప్లికేట్ లేదా చెల్లని డేటాబేస్ డేటా కారణంగా పునరుద్ధరణ ఆగింది","restore_failed":"పునరుద్ధరణ విఫలమైంది. పాక్షిక డేటా సేవ్ కాలేదు. లోపం",
})

TR["kn"].update({
    "save_changes":"ಬದಲಾವಣೆಗಳನ್ನು ಸೇವ್ ಮಾಡಿ","sales_return_credit":"ಮಾರಾಟ ವಾಪಸಿ ಕ್ರೆಡಿಟ್","invoice_paid_total_error":"ಹೊಸ ಬಿಲ್ ಮೊತ್ತ ಈಗಾಗಲೇ ಪಡೆದ ಪಾವತಿಗಿಂತ ಕಡಿಮೆ ಇರುವುದರಿಂದ ಬಿಲ್ ಅಪ್‌ಡೇಟ್ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ.","invoice_updated":"ಬಿಲ್ ಯಶಸ್ವಿಯಾಗಿ ಅಪ್‌ಡೇಟ್ ಆಯಿತು.","invoice_has_sales_return":"ಈ ಬಿಲ್‌ಗೆ ಮಾರಾಟ ವಾಪಸಿ ಇದೆ. ಬಿಲ್ ಅಳಿಸುವ ಮೊದಲು ಸಂಬಂಧಿತ ವಾಪಸಿಯನ್ನು ಅಳಿಸಿ.","invoice_deleted":"ಬಿಲ್ ಯಶಸ್ವಿಯಾಗಿ ಅಳಿಸಲಾಗಿದೆ.","invoice_delete_failed":"ಬಿಲ್ ಅಳಿಸಲಾಗಲಿಲ್ಲ","sales_return_saved":"ಮಾರಾಟ ವಾಪಸಿ ಸೇವ್ ಆಯಿತು","sales_return_exists":"ಈ ಮಾರಾಟ ವಾಪಸಿ ಈಗಾಗಲೇ ಇದೆ.","no_visible_changes":"ಕಾಣುವ ಮಾಹಿತಿಯಲ್ಲಿ ಯಾವುದೇ ಬದಲಾವಣೆ ಕಂಡುಬಂದಿಲ್ಲ.","no_previous_record":"ಹಿಂದಿನ ದಾಖಲೆಯ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.","export_excel_csv":"Excel / CSV ರಫ್ತು","export_data_from":"ಈ ದಿನಾಂಕದಿಂದ ಡೇಟಾ ರಫ್ತು","export_to":"ವರೆಗೆ","download_excel":"Excel ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ","download_csv_files":"CSV ಫೈಲ್‌ಗಳನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ","excel_export_failed":"Excel ರಫ್ತು ಪ್ರಾರಂಭಿಸಲಾಗಲಿಲ್ಲ","backup_keep_safe":"ಈ ಬ್ಯಾಕಪ್ ಫೈಲ್ ಅನ್ನು ಸುರಕ್ಷಿತವಾಗಿ ಇಡಿ. ಇದರಲ್ಲಿ ನಿಮ್ಮ ವ್ಯವಹಾರ ದಾಖಲೆಗಳಿವೆ.","restore_backup":"ಬ್ಯಾಕಪ್ ಮರುಸ್ಥಾಪಿಸಿ","restore_help":"SHIVPRUBA BILLING ಬ್ಯಾಕಪ್ ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ. ಮರುಸ್ಥಾಪನೆ ಪ್ರಸ್ತುತ ವ್ಯವಹಾರ ಡೇಟಾವನ್ನು ಬದಲಿಸುತ್ತದೆ.","upload_backup_file":"ಬ್ಯಾಕಪ್ ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (.json)","invalid_backup_missing":"ಅಮಾನ್ಯ ಬ್ಯಾಕಪ್ ಫೈಲ್. ಇವು ಕಾಣೆಯಾಗಿದೆ","backup_valid":"ಬ್ಯಾಕಪ್ ಫೈಲ್ ಮಾನ್ಯವಾಗಿದೆ.","backup_read_failed":"ಬ್ಯಾಕಪ್ ಫೈಲ್ ಓದಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ","restore_confirm_replace":"ಪ್ರಸ್ತುತ ವ್ಯವಹಾರ ಡೇಟಾ ಬದಲಾಗುತ್ತದೆ ಎಂದು ನನಗೆ ಅರ್ಥವಾಗಿದೆ.","restore_type_confirm":"ದೃಢೀಕರಿಸಲು RESTORE ಟೈಪ್ ಮಾಡಿ","restore_my_backup":"ನನ್ನ ಬ್ಯಾಕಪ್ ಮರುಸ್ಥಾಪಿಸಿ","backup_restored":"ಬ್ಯಾಕಪ್ ಯಶಸ್ವಿಯಾಗಿ ಮರುಸ್ಥಾಪಿಸಲಾಗಿದೆ. ವ್ಯವಹಾರ ಡೇಟಾ ಮರಳಿ ಬಂದಿದೆ.","restore_integrity_failed":"ನಕಲಿ ಅಥವಾ ಅಮಾನ್ಯ ಡೇಟಾಬೇಸ್ ಡೇಟಾದ ಕಾರಣ ಮರುಸ್ಥಾಪನೆ ನಿಂತಿದೆ","restore_failed":"ಮರುಸ್ಥಾಪನೆ ವಿಫಲವಾಗಿದೆ. ಭಾಗಶಃ ಡೇಟಾ ಸೇವ್ ಆಗಿಲ್ಲ. ದೋಷ",
})

TR["ml"].update({
    "save_changes":"മാറ്റങ്ങൾ സേവ് ചെയ്യുക","sales_return_credit":"വിൽപ്പന മടക്കം ക്രെഡിറ്റ്","invoice_paid_total_error":"പുതിയ ബിൽ തുക ഇതിനകം ലഭിച്ച പേയ്മെന്റിനേക്കാൾ കുറവായതിനാൽ ബിൽ അപ്ഡേറ്റ് ചെയ്യാനാകില്ല.","invoice_updated":"ബിൽ വിജയകരമായി അപ്ഡേറ്റ് ചെയ്തു.","invoice_has_sales_return":"ഈ ബില്ലിന് വിൽപ്പന മടക്കം ഉണ്ട്. ബിൽ ഡിലീറ്റ് ചെയ്യുന്നതിന് മുമ്പ് ബന്ധപ്പെട്ട മടക്കം ഡിലീറ്റ് ചെയ്യുക.","invoice_deleted":"ബിൽ വിജയകരമായി ഡിലീറ്റ് ചെയ്തു.","invoice_delete_failed":"ബിൽ ഡിലീറ്റ് ചെയ്യാനായില്ല","sales_return_saved":"വിൽപ്പന മടക്കം സേവ് ചെയ്തു","sales_return_exists":"ഈ വിൽപ്പന മടക്കം ഇതിനകം നിലവിലുണ്ട്.","no_visible_changes":"കാണുന്ന വിവരങ്ങളിൽ മാറ്റമൊന്നും കണ്ടെത്തിയില്ല.","no_previous_record":"മുൻ രേഖയുടെ വിവരം ലഭ്യമല്ല.","export_excel_csv":"Excel / CSV കയറ്റുമതി","export_data_from":"ഈ തീയതി മുതൽ ഡാറ്റ കയറ്റുമതി","export_to":"വരെ","download_excel":"Excel ഡൗൺലോഡ് ചെയ്യുക","download_csv_files":"CSV ഫയലുകൾ ഡൗൺലോഡ് ചെയ്യുക","excel_export_failed":"Excel കയറ്റുമതി ആരംഭിക്കാനായില്ല","backup_keep_safe":"ഈ ബാക്കപ്പ് ഫയൽ സുരക്ഷിതമായി സൂക്ഷിക്കുക. ഇതിൽ നിങ്ങളുടെ ബിസിനസ് രേഖകളുണ്ട്.","restore_backup":"ബാക്കപ്പ് പുനഃസ്ഥാപിക്കുക","restore_help":"SHIVPRUBA BILLING ബാക്കപ്പ് ഫയൽ അപ്‌ലോഡ് ചെയ്യുക. പുനഃസ്ഥാപനം നിലവിലെ ബിസിനസ് ഡാറ്റ മാറ്റിസ്ഥാപിക്കും.","upload_backup_file":"ബാക്കപ്പ് ഫയൽ അപ്‌ലോഡ് ചെയ്യുക (.json)","invalid_backup_missing":"അസാധുവായ ബാക്കപ്പ് ഫയൽ. ഇവ ലഭ്യമല്ല","backup_valid":"ബാക്കപ്പ് ഫയൽ സാധുവാണ്.","backup_read_failed":"ബാക്കപ്പ് ഫയൽ വായിക്കാനായില്ല","restore_confirm_replace":"നിലവിലെ ബിസിനസ് ഡാറ്റ മാറ്റിസ്ഥാപിക്കുമെന്ന് ഞാൻ മനസ്സിലാക്കുന്നു.","restore_type_confirm":"സ്ഥിരീകരിക്കാൻ RESTORE ടൈപ്പ് ചെയ്യുക","restore_my_backup":"എന്റെ ബാക്കപ്പ് പുനഃസ്ഥാപിക്കുക","backup_restored":"ബാക്കപ്പ് വിജയകരമായി പുനഃസ്ഥാപിച്ചു. ബിസിനസ് ഡാറ്റ വീണ്ടെടുത്തു.","restore_integrity_failed":"ഡ്യൂപ്ലിക്കേറ്റ് അല്ലെങ്കിൽ അസാധുവായ ഡാറ്റാബേസ് ഡാറ്റ കാരണം പുനഃസ്ഥാപനം നിർത്തി","restore_failed":"പുനഃസ്ഥാപനം പരാജയപ്പെട്ടു. ഭാഗിക ഡാറ്റ സേവ് ചെയ്തിട്ടില്ല. പിശക്",
})

TR["pa"].update({
    "save_changes":"ਤਬਦੀਲੀਆਂ ਸੇਵ ਕਰੋ","sales_return_credit":"ਵਿਕਰੀ ਵਾਪਸੀ ਕਰੈਡਿਟ","invoice_paid_total_error":"ਨਵੀਂ ਬਿੱਲ ਰਕਮ ਪਹਿਲਾਂ ਮਿਲੀ ਭੁਗਤਾਨ ਰਕਮ ਤੋਂ ਘੱਟ ਹੋਣ ਕਰਕੇ ਬਿੱਲ ਅਪਡੇਟ ਨਹੀਂ ਕੀਤਾ ਜਾ ਸਕਦਾ।","invoice_updated":"ਬਿੱਲ ਸਫਲਤਾਪੂਰਵਕ ਅਪਡੇਟ ਹੋਇਆ।","invoice_has_sales_return":"ਇਸ ਬਿੱਲ ਨਾਲ ਵਿਕਰੀ ਵਾਪਸੀ ਹੈ। ਬਿੱਲ ਮਿਟਾਉਣ ਤੋਂ ਪਹਿਲਾਂ ਸੰਬੰਧਿਤ ਵਾਪਸੀ ਮਿਟਾਓ।","invoice_deleted":"ਬਿੱਲ ਸਫਲਤਾਪੂਰਵਕ ਮਿਟਾਇਆ ਗਿਆ।","invoice_delete_failed":"ਬਿੱਲ ਮਿਟਾਇਆ ਨਹੀਂ ਜਾ ਸਕਿਆ","sales_return_saved":"ਵਿਕਰੀ ਵਾਪਸੀ ਸੇਵ ਹੋਈ","sales_return_exists":"ਇਹ ਵਿਕਰੀ ਵਾਪਸੀ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ।","no_visible_changes":"ਦਿੱਖ ਰਹੀ ਜਾਣਕਾਰੀ ਵਿੱਚ ਕੋਈ ਤਬਦੀਲੀ ਨਹੀਂ ਮਿਲੀ।","no_previous_record":"ਪਿਛਲੇ ਰਿਕਾਰਡ ਦੀ ਜਾਣਕਾਰੀ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।","export_excel_csv":"Excel / CSV ਨਿਰਯਾਤ","export_data_from":"ਇਸ ਮਿਤੀ ਤੋਂ ਡਾਟਾ ਨਿਰਯਾਤ","export_to":"ਤੱਕ","download_excel":"Excel ਡਾਊਨਲੋਡ ਕਰੋ","download_csv_files":"CSV ਫਾਈਲਾਂ ਡਾਊਨਲੋਡ ਕਰੋ","excel_export_failed":"Excel ਨਿਰਯਾਤ ਸ਼ੁਰੂ ਨਹੀਂ ਹੋ ਸਕਿਆ","backup_keep_safe":"ਇਸ ਬੈਕਅਪ ਫਾਈਲ ਨੂੰ ਸੁਰੱਖਿਅਤ ਰੱਖੋ। ਇਸ ਵਿੱਚ ਤੁਹਾਡੇ ਕਾਰੋਬਾਰ ਦੇ ਰਿਕਾਰਡ ਹਨ।","restore_backup":"ਬੈਕਅਪ ਮੁੜ-ਬਹਾਲ ਕਰੋ","restore_help":"SHIVPRUBA BILLING ਬੈਕਅਪ ਫਾਈਲ ਅਪਲੋਡ ਕਰੋ। ਮੁੜ-ਬਹਾਲੀ ਮੌਜੂਦਾ ਕਾਰੋਬਾਰੀ ਡਾਟਾ ਬਦਲ ਦੇਵੇਗੀ।","upload_backup_file":"ਬੈਕਅਪ ਫਾਈਲ ਅਪਲੋਡ ਕਰੋ (.json)","invalid_backup_missing":"ਗਲਤ ਬੈਕਅਪ ਫਾਈਲ। ਇਹ ਭਾਗ ਨਹੀਂ ਮਿਲੇ","backup_valid":"ਬੈਕਅਪ ਫਾਈਲ ਠੀਕ ਹੈ।","backup_read_failed":"ਬੈਕਅਪ ਫਾਈਲ ਪੜ੍ਹੀ ਨਹੀਂ ਜਾ ਸਕੀ","restore_confirm_replace":"ਮੈਂ ਸਮਝਦਾ ਹਾਂ ਕਿ ਮੌਜੂਦਾ ਕਾਰੋਬਾਰੀ ਡਾਟਾ ਬਦਲਿਆ ਜਾਵੇਗਾ।","restore_type_confirm":"ਪੁਸ਼ਟੀ ਲਈ RESTORE ਟਾਈਪ ਕਰੋ","restore_my_backup":"ਮੇਰਾ ਬੈਕਅਪ ਮੁੜ-ਬਹਾਲ ਕਰੋ","backup_restored":"ਬੈਕਅਪ ਸਫਲਤਾਪੂਰਵਕ ਮੁੜ-ਬਹਾਲ ਹੋਇਆ। ਕਾਰੋਬਾਰੀ ਡਾਟਾ ਵਾਪਸ ਮਿਲ ਗਿਆ ਹੈ।","restore_integrity_failed":"ਡੁਪਲੀਕੇਟ ਜਾਂ ਗਲਤ ਡਾਟਾਬੇਸ ਡਾਟਾ ਕਾਰਨ ਮੁੜ-ਬਹਾਲੀ ਰੋਕੀ ਗਈ","restore_failed":"ਮੁੜ-ਬਹਾਲੀ ਅਸਫਲ ਰਹੀ। ਅਧੂਰਾ ਡਾਟਾ ਸੇਵ ਨਹੀਂ ਹੋਇਆ। ਗਲਤੀ",
})

# ============================================================
# V5.3 - OUTSTANDING / PAYMENT REMINDER LANGUAGE LABELS
# ============================================================

TR["en"].update({
    "payment_reminder": "Outstanding / Payment Reminder",
    "customers_with_outstanding": "Customers with Outstanding",
    "pending_invoices": "Pending Invoices",
    "outstanding_amount": "Outstanding Amount",
    "reminder_message": "Payment Reminder Message",
    "no_outstanding": "No outstanding payments found.",
    "download_reminder": "Download Reminder",
})

TR["mr"].update({
    "payment_reminder": "बाकी रक्कम / पेमेंट रिमाइंडर",
    "customers_with_outstanding": "बाकी असलेले ग्राहक",
    "pending_invoices": "बाकी बिले",
    "outstanding_amount": "बाकी रक्कम",
    "reminder_message": "पेमेंट रिमाइंडर संदेश",
    "no_outstanding": "कोणतीही बाकी रक्कम नाही.",
    "download_reminder": "रिमाइंडर डाउनलोड करा",
})

TR["hi"].update({
    "payment_reminder": "बकाया / भुगतान रिमाइंडर",
    "customers_with_outstanding": "बकाया वाले ग्राहक",
    "pending_invoices": "बकाया बिल",
    "outstanding_amount": "बकाया राशि",
    "reminder_message": "भुगतान रिमाइंडर संदेश",
    "no_outstanding": "कोई बकाया भुगतान नहीं है।",
    "download_reminder": "रिमाइंडर डाउनलोड करें",
})

TR["gu"].update({
    "payment_reminder": "બાકી રકમ / ચુકવણી રિમાઇન્ડર",
    "customers_with_outstanding": "બાકી ધરાવતા ગ્રાહકો",
    "pending_invoices": "બાકી બિલ",
    "outstanding_amount": "બાકી રકમ",
    "reminder_message": "ચુકવણી રિમાઇન્ડર સંદેશ",
    "no_outstanding": "કોઈ બાકી ચુકવણી નથી.",
    "download_reminder": "રિમાઇન્ડર ડાઉનલોડ કરો",
})

TR["bn"].update({
    "payment_reminder": "বকেয়া / পেমেন্ট রিমাইন্ডার",
    "customers_with_outstanding": "বকেয়া থাকা গ্রাহক",
    "pending_invoices": "বকেয়া বিল",
    "outstanding_amount": "বকেয়া পরিমাণ",
    "reminder_message": "পেমেন্ট রিমাইন্ডার বার্তা",
    "no_outstanding": "কোনো বকেয়া পেমেন্ট নেই।",
    "download_reminder": "রিমাইন্ডার ডাউনলোড করুন",
})

TR["ta"].update({
    "payment_reminder": "நிலுவை / கட்டண நினைவூட்டல்",
    "customers_with_outstanding": "நிலுவை உள்ள வாடிக்கையாளர்கள்",
    "pending_invoices": "நிலுவை பில்கள்",
    "outstanding_amount": "நிலுவை தொகை",
    "reminder_message": "கட்டண நினைவூட்டல் செய்தி",
    "no_outstanding": "நிலுவை கட்டணம் எதுவும் இல்லை.",
    "download_reminder": "நினைவூட்டலை பதிவிறக்கு",
})

TR["te"].update({
    "payment_reminder": "బాకీ / చెల్లింపు రిమైండర్",
    "customers_with_outstanding": "బాకీ ఉన్న కస్టమర్లు",
    "pending_invoices": "బాకీ బిల్లులు",
    "outstanding_amount": "బాకీ మొత్తం",
    "reminder_message": "చెల్లింపు రిమైండర్ సందేశం",
    "no_outstanding": "బాకీ చెల్లింపులు లేవు.",
    "download_reminder": "రిమైండర్ డౌన్‌లోడ్",
})

TR["kn"].update({
    "payment_reminder": "ಬಾಕಿ / ಪಾವತಿ ರಿಮೈಂಡರ್",
    "customers_with_outstanding": "ಬಾಕಿ ಇರುವ ಗ್ರಾಹಕರು",
    "pending_invoices": "ಬಾಕಿ ಬಿಲ್ಲುಗಳು",
    "outstanding_amount": "ಬಾಕಿ ಮೊತ್ತ",
    "reminder_message": "ಪಾವತಿ ರಿಮೈಂಡರ್ ಸಂದೇಶ",
    "no_outstanding": "ಯಾವುದೇ ಬಾಕಿ ಪಾವತಿಗಳಿಲ್ಲ.",
    "download_reminder": "ರಿಮೈಂಡರ್ ಡೌನ್‌ಲೋಡ್",
})

TR["ml"].update({
    "payment_reminder": "കുടിശ്ശിക / പേയ്മെന്റ് റിമൈൻഡർ",
    "customers_with_outstanding": "കുടിശ്ശികയുള്ള ഉപഭോക്താക്കൾ",
    "pending_invoices": "കുടിശ്ശിക ബില്ലുകൾ",
    "outstanding_amount": "കുടിശ്ശിക തുക",
    "reminder_message": "പേയ്മെന്റ് റിമൈൻഡർ സന്ദേശം",
    "no_outstanding": "കുടിശ്ശിക പേയ്മെന്റുകളില്ല.",
    "download_reminder": "റിമൈൻഡർ ഡൗൺലോഡ്",
})

TR["pa"].update({
    "payment_reminder": "ਬਕਾਇਆ / ਭੁਗਤਾਨ ਰਿਮਾਈਂਡਰ",
    "customers_with_outstanding": "ਬਕਾਇਆ ਵਾਲੇ ਗਾਹਕ",
    "pending_invoices": "ਬਕਾਇਆ ਬਿੱਲ",
    "outstanding_amount": "ਬਕਾਇਆ ਰਕਮ",
    "reminder_message": "ਭੁਗਤਾਨ ਰਿਮਾਈਂਡਰ ਸੁਨੇਹਾ",
    "no_outstanding": "ਕੋਈ ਬਕਾਇਆ ਭੁਗਤਾਨ ਨਹੀਂ ਹੈ।",
    "download_reminder": "ਰਿਮਾਈਂਡਰ ਡਾਊਨਲੋਡ ਕਰੋ",
})

# ============================================================
# V5.2 - QUOTATION / ESTIMATE - ALL 10 LANGUAGES
# ============================================================

TR["en"].update({
    "quotation": "Quotation / Estimate",
    "create_quotation": "Create Quotation / Estimate",
    "quotation_details": "Quotation Details",
    "quotation_number": "Quotation Number",
    "quotation_date": "Quotation Date",
    "valid_until": "Valid Until",
    "save_quotation": "Save Quotation",
    "quotation_saved": "Quotation saved successfully.",
    "quotation_duplicate": "This quotation number already exists.",
    "saved_quotations": "Saved Quotations",
    "no_quotations": "No quotations yet.",
    "quotation_stock_note": "Saving a quotation does not change stock.",
    "search_quotation": "Search quotation number or customer name",
    "quotation_validity_error": "Valid Until date cannot be before the Quotation Date.",
})

TR["mr"].update({
    "quotation": "कोटेशन / अंदाजपत्रक",
    "create_quotation": "कोटेशन / अंदाजपत्रक तयार करा",
    "quotation_details": "कोटेशन तपशील",
    "quotation_number": "कोटेशन क्रमांक",
    "quotation_date": "कोटेशन दिनांक",
    "valid_until": "वैधता दिनांक",
    "save_quotation": "कोटेशन सेव्ह करा",
    "quotation_saved": "कोटेशन यशस्वीपणे सेव्ह झाले.",
    "quotation_duplicate": "हा कोटेशन क्रमांक आधीपासून आहे.",
    "saved_quotations": "सेव्ह केलेली कोटेशन्स",
    "no_quotations": "अजून कोटेशन नाही.",
    "quotation_stock_note": "कोटेशन सेव्ह केल्याने स्टॉकमध्ये कोणताही बदल होत नाही.",
    "search_quotation": "कोटेशन क्रमांक किंवा ग्राहक शोधा",
    "quotation_validity_error": "वैधता दिनांक हा कोटेशन दिनांकाच्या आधी असू शकत नाही.",
})

TR["hi"].update({
    "quotation": "कोटेशन / अनुमान",
    "create_quotation": "कोटेशन / अनुमान बनाएं",
    "quotation_details": "कोटेशन विवरण",
    "quotation_number": "कोटेशन नंबर",
    "quotation_date": "कोटेशन तारीख",
    "valid_until": "मान्य तिथि",
    "save_quotation": "कोटेशन सेव करें",
    "quotation_saved": "कोटेशन सफलतापूर्वक सेव हुआ।",
    "quotation_duplicate": "यह कोटेशन नंबर पहले से मौजूद है।",
    "saved_quotations": "सेव किए गए कोटेशन",
    "no_quotations": "अभी कोई कोटेशन नहीं है।",
    "quotation_stock_note": "कोटेशन सेव करने से स्टॉक में कोई बदलाव नहीं होगा।",
    "search_quotation": "कोटेशन नंबर या ग्राहक खोजें",
    "quotation_validity_error": "मान्य तिथि कोटेशन तारीख से पहले नहीं हो सकती।",
})

TR["gu"].update({
    "quotation": "ક્વોટેશન / અંદાજ",
    "create_quotation": "ક્વોટેશન / અંદાજ બનાવો",
    "quotation_details": "ક્વોટેશન વિગતો",
    "quotation_number": "ક્વોટેશન નંબર",
    "quotation_date": "ક્વોટેશન તારીખ",
    "valid_until": "માન્ય તારીખ",
    "save_quotation": "ક્વોટેશન સેવ કરો",
    "quotation_saved": "ક્વોટેશન સફળતાપૂર્વક સેવ થયું.",
    "quotation_duplicate": "આ ક્વોટેશન નંબર પહેલેથી હાજર છે.",
    "saved_quotations": "સેવ કરેલા ક્વોટેશન",
    "no_quotations": "હજુ કોઈ ક્વોટેશન નથી.",
    "quotation_stock_note": "ક્વોટેશન સેવ કરવાથી સ્ટોકમાં કોઈ ફેરફાર થતો નથી.",
    "search_quotation": "ક્વોટેશન નંબર અથવા ગ્રાહક શોધો",
    "quotation_validity_error": "માન્ય તારીખ ક્વોટેશન તારીખ પહેલાં હોઈ શકે નહીં.",
})

TR["bn"].update({
    "quotation": "কোটেশন / প্রাক্কলন",
    "create_quotation": "কোটেশন / প্রাক্কলন তৈরি করুন",
    "quotation_details": "কোটেশন বিবরণ",
    "quotation_number": "কোটেশন নম্বর",
    "quotation_date": "কোটেশন তারিখ",
    "valid_until": "বৈধতার তারিখ",
    "save_quotation": "কোটেশন সেভ করুন",
    "quotation_saved": "কোটেশন সফলভাবে সেভ হয়েছে।",
    "quotation_duplicate": "এই কোটেশন নম্বরটি আগে থেকেই আছে।",
    "saved_quotations": "সেভ করা কোটেশন",
    "no_quotations": "এখনও কোনো কোটেশন নেই।",
    "quotation_stock_note": "কোটেশন সেভ করলে স্টকে কোনো পরিবর্তন হয় না।",
    "search_quotation": "কোটেশন নম্বর বা গ্রাহক খুঁজুন",
    "quotation_validity_error": "বৈধতার তারিখ কোটেশন তারিখের আগে হতে পারে না।",
})

TR["ta"].update({
    "quotation": "விலை முன்மொழிவு / மதிப்பீடு",
    "create_quotation": "விலை முன்மொழிவு / மதிப்பீடு உருவாக்கு",
    "quotation_details": "விலை முன்மொழிவு விவரங்கள்",
    "quotation_number": "விலை முன்மொழிவு எண்",
    "quotation_date": "விலை முன்மொழிவு தேதி",
    "valid_until": "செல்லுபடியாகும் தேதி",
    "save_quotation": "விலை முன்மொழிவை சேமிக்கவும்",
    "quotation_saved": "விலை முன்மொழிவு வெற்றிகரமாக சேமிக்கப்பட்டது.",
    "quotation_duplicate": "இந்த விலை முன்மொழிவு எண் ஏற்கனவே உள்ளது.",
    "saved_quotations": "சேமித்த விலை முன்மொழிவுகள்",
    "no_quotations": "இன்னும் விலை முன்மொழிவுகள் இல்லை.",
    "quotation_stock_note": "விலை முன்மொழிவை சேமிப்பதால் ஸ்டாக் மாறாது.",
    "search_quotation": "விலை முன்மொழிவு எண் அல்லது வாடிக்கையாளரை தேடவும்",
    "quotation_validity_error": "செல்லுபடியாகும் தேதி விலை முன்மொழிவு தேதிக்கு முன் இருக்க முடியாது.",
})

TR["te"].update({
    "quotation": "కొటేషన్ / అంచనా",
    "create_quotation": "కొటేషన్ / అంచనా రూపొందించండి",
    "quotation_details": "కొటేషన్ వివరాలు",
    "quotation_number": "కొటేషన్ నంబర్",
    "quotation_date": "కొటేషన్ తేదీ",
    "valid_until": "చెల్లుబాటు తేదీ",
    "save_quotation": "కొటేషన్ సేవ్ చేయండి",
    "quotation_saved": "కొటేషన్ విజయవంతంగా సేవ్ అయింది.",
    "quotation_duplicate": "ఈ కొటేషన్ నంబర్ ఇప్పటికే ఉంది.",
    "saved_quotations": "సేవ్ చేసిన కొటేషన్లు",
    "no_quotations": "ఇంకా కొటేషన్లు లేవు.",
    "quotation_stock_note": "కొటేషన్ సేవ్ చేయడం వల్ల స్టాక్ మారదు.",
    "search_quotation": "కొటేషన్ నంబర్ లేదా కస్టమర్‌ను వెతకండి",
    "quotation_validity_error": "చెల్లుబాటు తేదీ కొటేషన్ తేదీకి ముందు ఉండకూడదు.",
})

TR["kn"].update({
    "quotation": "ಕೊಟೇಶನ್ / ಅಂದಾಜು",
    "create_quotation": "ಕೊಟೇಶನ್ / ಅಂದಾಜು ರಚಿಸಿ",
    "quotation_details": "ಕೊಟೇಶನ್ ವಿವರಗಳು",
    "quotation_number": "ಕೊಟೇಶನ್ ಸಂಖ್ಯೆ",
    "quotation_date": "ಕೊಟೇಶನ್ ದಿನಾಂಕ",
    "valid_until": "ಮಾನ್ಯ ದಿನಾಂಕ",
    "save_quotation": "ಕೊಟೇಶನ್ ಸೇವ್ ಮಾಡಿ",
    "quotation_saved": "ಕೊಟೇಶನ್ ಯಶಸ್ವಿಯಾಗಿ ಸೇವ್ ಆಗಿದೆ.",
    "quotation_duplicate": "ಈ ಕೊಟೇಶನ್ ಸಂಖ್ಯೆ ಈಗಾಗಲೇ ಇದೆ.",
    "saved_quotations": "ಸೇವ್ ಮಾಡಿದ ಕೊಟೇಶನ್‌ಗಳು",
    "no_quotations": "ಇನ್ನೂ ಕೊಟೇಶನ್‌ಗಳಿಲ್ಲ.",
    "quotation_stock_note": "ಕೊಟೇಶನ್ ಸೇವ್ ಮಾಡುವುದರಿಂದ ಸ್ಟಾಕ್ ಬದಲಾಗುವುದಿಲ್ಲ.",
    "search_quotation": "ಕೊಟೇಶನ್ ಸಂಖ್ಯೆ ಅಥವಾ ಗ್ರಾಹಕರನ್ನು ಹುಡುಕಿ",
    "quotation_validity_error": "ಮಾನ್ಯ ದಿನಾಂಕ ಕೊಟೇಶನ್ ದಿನಾಂಕಕ್ಕಿಂತ ಮೊದಲು ಇರಬಾರದು.",
})

TR["ml"].update({
    "quotation": "ക്വട്ടേഷൻ / എസ്റ്റിമേറ്റ്",
    "create_quotation": "ക്വട്ടേഷൻ / എസ്റ്റിമേറ്റ് തയ്യാറാക്കുക",
    "quotation_details": "ക്വട്ടേഷൻ വിശദാംശങ്ങൾ",
    "quotation_number": "ക്വട്ടേഷൻ നമ്പർ",
    "quotation_date": "ക്വട്ടേഷൻ തീയതി",
    "valid_until": "സാധുത തീയതി",
    "save_quotation": "ക്വട്ടേഷൻ സേവ് ചെയ്യുക",
    "quotation_saved": "ക്വട്ടേഷൻ വിജയകരമായി സേവ് ചെയ്തു.",
    "quotation_duplicate": "ഈ ക്വട്ടേഷൻ നമ്പർ ഇതിനകം നിലവിലുണ്ട്.",
    "saved_quotations": "സേവ് ചെയ്ത ക്വട്ടേഷനുകൾ",
    "no_quotations": "ഇതുവരെ ക്വട്ടേഷനുകളില്ല.",
    "quotation_stock_note": "ക്വട്ടേഷൻ സേവ് ചെയ്യുന്നത് സ്റ്റോക്കിൽ മാറ്റമുണ്ടാക്കില്ല.",
    "search_quotation": "ക്വട്ടേഷൻ നമ്പർ അല്ലെങ്കിൽ ഉപഭോക്താവിനെ തിരയുക",
    "quotation_validity_error": "സാധുത തീയതി ക്വട്ടേഷൻ തീയതിക്ക് മുമ്പാകരുത്.",
})

TR["pa"].update({
    "quotation": "ਕੋਟੇਸ਼ਨ / ਅੰਦਾਜ਼ਾ",
    "create_quotation": "ਕੋਟੇਸ਼ਨ / ਅੰਦਾਜ਼ਾ ਬਣਾਓ",
    "quotation_details": "ਕੋਟੇਸ਼ਨ ਵੇਰਵੇ",
    "quotation_number": "ਕੋਟੇਸ਼ਨ ਨੰਬਰ",
    "quotation_date": "ਕੋਟੇਸ਼ਨ ਮਿਤੀ",
    "valid_until": "ਮਿਆਦ ਦੀ ਮਿਤੀ",
    "save_quotation": "ਕੋਟੇਸ਼ਨ ਸੇਵ ਕਰੋ",
    "quotation_saved": "ਕੋਟੇਸ਼ਨ ਸਫਲਤਾਪੂਰਵਕ ਸੇਵ ਹੋਇਆ।",
    "quotation_duplicate": "ਇਹ ਕੋਟੇਸ਼ਨ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ।",
    "saved_quotations": "ਸੇਵ ਕੀਤੇ ਕੋਟੇਸ਼ਨ",
    "no_quotations": "ਹਾਲੇ ਕੋਈ ਕੋਟੇਸ਼ਨ ਨਹੀਂ ਹੈ।",
    "quotation_stock_note": "ਕੋਟੇਸ਼ਨ ਸੇਵ ਕਰਨ ਨਾਲ ਸਟਾਕ ਵਿੱਚ ਕੋਈ ਬਦਲਾਅ ਨਹੀਂ ਹੁੰਦਾ।",
    "search_quotation": "ਕੋਟੇਸ਼ਨ ਨੰਬਰ ਜਾਂ ਗਾਹਕ ਖੋਜੋ",
    "quotation_validity_error": "ਮਿਆਦ ਦੀ ਮਿਤੀ ਕੋਟੇਸ਼ਨ ਮਿਤੀ ਤੋਂ ਪਹਿਲਾਂ ਨਹੀਂ ਹੋ ਸਕਦੀ।",
})

# ============================================================
# GLOBAL DESIGN - INDIC FONT + MATRA/VOWEL-MARK FIX + MOBILE
# ============================================================
st.markdown(
    """

     <style>
   /* =========================================================
   FINAL FIX - MATERIAL ICONS + INDIAN LANGUAGE TEXT CLIPPING
   ========================================================= */

/* Streamlit Material icons must keep their own icon font.
   Otherwise keyboard_arrow_right appears as normal text. */
[data-testid="stIconMaterial"],
.material-symbols-rounded,
.material-symbols-outlined,
.material-icons {
    font-family: "Material Symbols Rounded" !important;
    font-weight: normal !important;
    font-style: normal !important;
    font-size: 1.25rem !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: "liga" !important;
    -webkit-font-smoothing: antialiased !important;
    font-feature-settings: "liga" !important;
}

/* Do not clip Marathi/Hindi/Gujarati/Tamil/Telugu/etc. characters */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"],
[data-testid="stHeadingWithActionElements"],
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
label {
    overflow: visible !important;
    text-overflow: clip !important;
}

/* Extra vertical room for Indian vowel marks / matras */
h1 {
    line-height: 1.55 !important;
    padding-top: 0.14em !important;
    padding-bottom: 0.18em !important;
}

h2 {
    line-height: 1.55 !important;
    padding-top: 0.12em !important;
    padding-bottom: 0.16em !important;
}

h3, h4, h5, h6 {
    line-height: 1.55 !important;
    padding-top: 0.10em !important;
    padding-bottom: 0.14em !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p,
label,
button {
    line-height: 1.55 !important;
}

/* Expander text and rows */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    line-height: 1.55 !important;
    overflow: visible !important;
    padding-top: 0.08em !important;
    padding-bottom: 0.08em !important;
} {
        border-right: 1px solid rgba(120,140,170,.25);
    }

    /* Important for Devanagari/Gujarati/Bengali/Tamil etc. vowel marks */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stHeading"],
    [data-testid="stHeadingWithActionElements"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"] p,
    label, button, [role="tab"], [role="radiogroup"] label {
        line-height: 1.58 !important;
        overflow: visible !important;
        white-space: normal !important;
        padding-top: .08em !important;
        padding-bottom: .10em !important;
    }

    h1 {
        line-height: 1.48 !important;
        padding-top: .12em !important;
        padding-bottom: .18em !important;
        margin-bottom: .30em !important;
        overflow: visible !important;
    }

    h2, h3 {
        line-height: 1.52 !important;
        padding-top: .10em !important;
        padding-bottom: .14em !important;
        overflow: visible !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #17345f 0%, #245a9f 100%) !important;
        border: 1px solid rgba(255,255,255,.14) !important;
        border-radius: 18px !important;
        padding: 15px 17px !important;
        min-height: 116px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,.16) !important;
        overflow: visible !important;
    }

    [data-testid="stMetric"] * {
        color: #ffffff !important;
        overflow: visible !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: .92rem !important;
        font-weight: 700 !important;
        line-height: 1.45 !important;
        min-height: 2.5em !important;
        white-space: normal !important;
        overflow: visible !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.62rem !important;
        font-weight: 800 !important;
        line-height: 1.25 !important;
        overflow: visible !important;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #123c74 0%, #1976d2 100%) !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #145a46 0%, #16a085 100%) !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #8a4b08 0%, #f39c12 100%) !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #56348c 0%, #8e44ad 100%) !important;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        min-height: 3rem;
        border-radius: 12px;
        font-weight: 700;
        line-height: 1.45 !important;
        white-space: normal !important;
        padding-top: .55rem !important;
        padding-bottom: .55rem !important;
    }

    [data-baseweb="select"] *,
    [data-baseweb="input"] *,
    [data-baseweb="textarea"] * {
        line-height: 1.50 !important;
        overflow: visible !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
        line-height: 1.50 !important;
        white-space: normal !important;
        overflow: visible !important;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: .45rem;
            padding-right: .45rem;
            padding-top: 4rem;
        }

        h1 {
            font-size: 1.48rem !important;
            line-height: 1.55 !important;
            padding-top: .12em !important;
            padding-bottom: .18em !important;
        }
        h2 { font-size: 1.22rem !important; line-height: 1.55 !important; }
        h3 { font-size: 1.05rem !important; line-height: 1.55 !important; }

        [data-testid="stHorizontalBlock"] {
            gap: .45rem !important;
        }

        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: .48rem !important;
            align-items: stretch !important;
        }

        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > * {
            min-width: 0 !important;
            width: auto !important;
            flex: none !important;
        }

        [data-testid="stMetric"] {
            min-height: 86px !important;
            padding: 9px 10px !important;
            border-radius: 12px !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: .72rem !important;
            line-height: 1.40 !important;
            min-height: 2.7em !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.02rem !important;
            line-height: 1.25 !important;
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

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands",
    "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh",
    "Lakshadweep", "Puducherry", "Other",
]


STATE_LABELS = {
    "en": {s: s for s in STATES},
    "mr": dict(zip(STATES, [
        "आंध्र प्रदेश", "अरुणाचल प्रदेश", "आसाम", "बिहार", "छत्तीसगड", "गोवा", "गुजरात",
        "हरियाणा", "हिमाचल प्रदेश", "झारखंड", "कर्नाटक", "केरळ", "मध्य प्रदेश", "महाराष्ट्र",
        "मणिपूर", "मेघालय", "मिझोराम", "नागालँड", "ओडिशा", "पंजाब", "राजस्थान", "सिक्कीम", "तामिळनाडू",
        "तेलंगणा", "त्रिपुरा", "उत्तर प्रदेश", "उत्तराखंड", "पश्चिम बंगाल", "अंदमान आणि निकोबार बेटे",
        "चंदीगड", "दादरा आणि नगर हवेली आणि दमण आणि दीव", "दिल्ली", "जम्मू आणि काश्मीर", "लडाख",
        "लक्षद्वीप", "पुदुच्चेरी", "इतर"
    ])),
    "hi": dict(zip(STATES, [
        "आंध्र प्रदेश", "अरुणाचल प्रदेश", "असम", "बिहार", "छत्तीसगढ़", "गोवा", "गुजरात",
        "हरियाणा", "हिमाचल प्रदेश", "झारखंड", "कर्नाटक", "केरल", "मध्य प्रदेश", "महाराष्ट्र",
        "मणिपुर", "मेघालय", "मिज़ोरम", "नागालैंड", "ओडिशा", "पंजाब", "राजस्थान", "सिक्किम", "तमिलनाडु",
        "तेलंगाना", "त्रिपुरा", "उत्तर प्रदेश", "उत्तराखंड", "पश्चिम बंगाल", "अंडमान और निकोबार द्वीपसमूह",
        "चंडीगढ़", "दादरा और नगर हवेली और दमन और दीव", "दिल्ली", "जम्मू और कश्मीर", "लद्दाख",
        "लक्षद्वीप", "पुडुचेरी", "अन्य"
    ])),
    "gu": dict(zip(STATES, [
        "આંધ્ર પ્રદેશ", "અરુણાચલ પ્રદેશ", "આસામ", "બિહાર", "છત્તીસગઢ", "ગોવા", "ગુજરાત",
        "હરિયાણા", "હિમાચલ પ્રદેશ", "ઝારખંડ", "કર્ણાટક", "કેરળ", "મધ્ય પ્રદેશ", "મહારાષ્ટ્ર",
        "મણિપુર", "મેઘાલય", "મિઝોરમ", "નાગાલેન્ડ", "ઓડિશા", "પંજાબ", "રાજસ્થાન", "સિક્કિમ", "તમિલનાડુ",
        "તેલંગાણા", "ત્રિપુરા", "ઉત્તર પ્રદેશ", "ઉત્તરાખંડ", "પશ્ચિમ બંગાળ", "અંદમાન અને નિકોબાર ટાપુઓ",
        "ચંડીગઢ", "દાદરા અને નગર હવેલી અને દમણ અને દીવ", "દિલ્હી", "જમ્મુ અને કાશ્મીર", "લદ્દાખ",
        "લક્ષદ્વીપ", "પુડુચેરી", "અન્ય"
    ])),
    "bn": dict(zip(STATES, [
        "অন্ধ্র প্রদেশ", "অরুণাচল প্রদেশ", "অসম", "বিহার", "ছত্তিশগড়", "গোয়া", "গুজরাট",
        "হরিয়ানা", "হিমাচল প্রদেশ", "ঝাড়খণ্ড", "কর্ণাটক", "কেরালা", "মধ্য প্রদেশ", "মহারাষ্ট্র",
        "মণিপুর", "মেঘালয়", "মিজোরাম", "নাগাল্যান্ড", "ওডিশা", "পাঞ্জাব", "রাজস্থান", "সিকিম", "তামিলনাড়ু",
        "তেলেঙ্গানা", "ত্রিপুরা", "উত্তর প্রদেশ", "উত্তরাখণ্ড", "পশ্চিমবঙ্গ", "আন্দামান ও নিকোবর দ্বীপপুঞ্জ",
        "চণ্ডীগড়", "দাদরা ও নগর হাভেলি এবং দমন ও দিউ", "দিল্লি", "জম্মু ও কাশ্মীর", "লাদাখ",
        "লাক্ষাদ্বীপ", "পুদুচেরি", "অন্যান্য"
    ])),
    "ta": dict(zip(STATES, [
        "ஆந்திரப் பிரதேசம்", "அருணாச்சலப் பிரதேசம்", "அசாம்", "பீகார்", "சத்தீஸ்கர்", "கோவா", "குஜராத்",
        "ஹரியானா", "ஹிமாச்சலப் பிரதேசம்", "ஜார்கண்ட்", "கர்நாடகா", "கேரளா", "மத்தியப் பிரதேசம்", "மகாராஷ்டிரா",
        "மணிப்பூர்", "மேகாலயா", "மிசோரம்", "நாகாலாந்து", "ஒடிஷா", "பஞ்சாப்", "ராஜஸ்தான்", "சிக்கிம்", "தமிழ்நாடு",
        "தெலங்கானா", "திரிபுரா", "உத்தரப் பிரதேசம்", "உத்தராகண்ட்", "மேற்கு வங்காளம்", "அந்தமான் மற்றும் நிக்கோபார் தீவுகள்",
        "சண்டிகர்", "தாத்ரா மற்றும் நகர் ஹவேலி மற்றும் டாமன் மற்றும் டையூ", "டெல்லி", "ஜம்மு மற்றும் காஷ்மீர்", "லடாக்",
        "லட்சத்தீவு", "புதுச்சேரி", "மற்றவை"
    ])),
    "te": dict(zip(STATES, [
        "ఆంధ్ర ప్రదేశ్", "అరుణాచల్ ప్రదేశ్", "అస్సాం", "బీహార్", "ఛత్తీస్‌గఢ్", "గోవా", "గుజరాత్",
        "హర్యానా", "హిమాచల్ ప్రదేశ్", "జార్ఖండ్", "కర్ణాటక", "కేరళ", "మధ్య ప్రదేశ్", "మహారాష్ట్ర",
        "మణిపూర్", "మేఘాలయ", "మిజోరం", "నాగాలాండ్", "ఒడిశా", "పంజాబ్", "రాజస్థాన్", "సిక్కిం", "తమిళనాడు",
        "తెలంగాణ", "త్రిపుర", "ఉత్తర ప్రదేశ్", "ఉత్తరాఖండ్", "పశ్చిమ బెంగాల్", "అండమాన్ మరియు నికోబార్ దీవులు",
        "చండీగఢ్", "దాద్రా మరియు నగర్ హవేలీ మరియు దమన్ మరియు దీవ్", "ఢిల్లీ", "జమ్మూ మరియు కాశ్మీర్", "లడఖ్",
        "లక్షద్వీప్", "పుదుచ్చేరి", "ఇతర"
    ])),
    "kn": dict(zip(STATES, [
        "ಆಂಧ್ರ ಪ್ರದೇಶ", "ಅರುಣಾಚಲ ಪ್ರದೇಶ", "ಅಸ್ಸಾಂ", "ಬಿಹಾರ", "ಛತ್ತೀಸ್‌ಗಢ", "ಗೋವಾ", "ಗುಜರಾತ್",
        "ಹರಿಯಾಣ", "ಹಿಮಾಚಲ ಪ್ರದೇಶ", "ಝಾರ್ಖಂಡ್", "ಕರ್ನಾಟಕ", "ಕೇರಳ", "ಮಧ್ಯ ಪ್ರದೇಶ", "ಮಹಾರಾಷ್ಟ್ರ",
        "ಮಣಿಪುರ", "ಮೇಘಾಲಯ", "ಮಿಜೋರಾಂ", "ನಾಗಾಲ್ಯಾಂಡ್", "ಒಡಿಶಾ", "ಪಂಜಾಬ್", "ರಾಜಸ್ಥಾನ", "ಸಿಕ್ಕಿಂ", "ತಮಿಳುನಾಡು",
        "ತೆಲಂಗಾಣ", "ತ್ರಿಪುರ", "ಉತ್ತರ ಪ್ರದೇಶ", "ಉತ್ತರಾಖಂಡ", "ಪಶ್ಚಿಮ ಬಂಗಾಳ", "ಅಂಡಮಾನ್ ಮತ್ತು ನಿಕೋಬಾರ್ ದ್ವೀಪಗಳು",
        "ಚಂಡೀಗಢ", "ದಾದ್ರಾ ಮತ್ತು ನಗರ ಹವೇಲಿ ಮತ್ತು ದಮನ್ ಮತ್ತು ದಿಯು", "ದೆಹಲಿ", "ಜಮ್ಮು ಮತ್ತು ಕಾಶ್ಮೀರ", "ಲಡಾಖ್",
        "ಲಕ್ಷದ್ವೀಪ", "ಪುದುಚೇರಿ", "ಇತರೆ"
    ])),
    "ml": dict(zip(STATES, [
        "ആന്ധ്ര പ്രദേശ്", "അരുണാചൽ പ്രദേശ്", "അസം", "ബിഹാർ", "ഛത്തീസ്ഗഢ്", "ഗോവ", "ഗുജറാത്ത്",
        "ഹരിയാന", "ഹിമാചൽ പ്രദേശ്", "ഝാർഖണ്ഡ്", "കർണാടക", "കേരളം", "മധ്യ പ്രദേശ്", "മഹാരാഷ്ട്ര",
        "മണിപ്പൂർ", "മേഘാലയ", "മിസോറം", "നാഗാലാൻഡ്", "ഒഡിഷ", "പഞ്ചാബ്", "രാജസ്ഥാൻ", "സിക്കിം", "തമിഴ്നാട്",
        "തെലങ്കാന", "ത്രിപുര", "ഉത്തർ പ്രദേശ്", "ഉത്തരാഖണ്ഡ്", "പശ്ചിമ ബംഗാൾ", "അണ്ടമാൻ നിക്കോബാർ ദ്വീപുകൾ",
        "ചണ്ഡീഗഢ്", "ദാദ്ര നഗർ ഹവേലി, ദമൻ ദിയു", "ഡൽഹി", "ജമ്മു കാശ്മീർ", "ലഡാക്ക്",
        "ലക്ഷദ്വീപ്", "പുതുച്ചേരി", "മറ്റുള്ളവ"
    ])),
    "pa": dict(zip(STATES, [
        "ਆਂਧਰਾ ਪ੍ਰਦੇਸ਼", "ਅਰੁਣਾਚਲ ਪ੍ਰਦੇਸ਼", "ਅਸਾਮ", "ਬਿਹਾਰ", "ਛੱਤੀਸਗੜ੍ਹ", "ਗੋਆ", "ਗੁਜਰਾਤ",
        "ਹਰਿਆਣਾ", "ਹਿਮਾਚਲ ਪ੍ਰਦੇਸ਼", "ਝਾਰਖੰਡ", "ਕਰਨਾਟਕ", "ਕੇਰਲ", "ਮੱਧ ਪ੍ਰਦੇਸ਼", "ਮਹਾਰਾਸ਼ਟਰ",
        "ਮਣੀਪੁਰ", "ਮੇਘਾਲਿਆ", "ਮਿਜ਼ੋਰਮ", "ਨਾਗਾਲੈਂਡ", "ਓਡੀਸ਼ਾ", "ਪੰਜਾਬ", "ਰਾਜਸਥਾਨ", "ਸਿੱਕਿਮ", "ਤਾਮਿਲਨਾਡੂ",
        "ਤੇਲੰਗਾਨਾ", "ਤ੍ਰਿਪੁਰਾ", "ਉੱਤਰ ਪ੍ਰਦੇਸ਼", "ਉੱਤਰਾਖੰਡ", "ਪੱਛਮੀ ਬੰਗਾਲ", "ਅੰਡਮਾਨ ਅਤੇ ਨਿਕੋਬਾਰ ਟਾਪੂ",
        "ਚੰਡੀਗੜ੍ਹ", "ਦਾਦਰਾ ਅਤੇ ਨਗਰ ਹਵੇਲੀ ਅਤੇ ਦਮਣ ਅਤੇ ਦੀਵ", "ਦਿੱਲੀ", "ਜੰਮੂ ਅਤੇ ਕਸ਼ਮੀਰ", "ਲੱਦਾਖ",
        "ਲਕਸ਼ਦੀਪ", "ਪੁਡੂਚੇਰੀ", "ਹੋਰ"
    ])),
}

UNIT_LABELS = {
    "en": {"Pcs":"Pcs","Kg":"Kg","Gm":"Gm","Ltr":"Ltr","Ml":"Ml","Box":"Box","Pack":"Pack","Dozen":"Dozen","Meter":"Meter","Service":"Service"},
    "mr": {"Pcs":"नग","Kg":"किलो","Gm":"ग्रॅम","Ltr":"लिटर","Ml":"मिली","Box":"बॉक्स","Pack":"पॅक","Dozen":"डझन","Meter":"मीटर","Service":"सेवा"},
    "hi": {"Pcs":"नग","Kg":"किलो","Gm":"ग्राम","Ltr":"लीटर","Ml":"मिली","Box":"बॉक्स","Pack":"पैक","Dozen":"दर्जन","Meter":"मीटर","Service":"सेवा"},
    "gu": {"Pcs":"નંગ","Kg":"કિલો","Gm":"ગ્રામ","Ltr":"લિટર","Ml":"મિલી","Box":"બોક્સ","Pack":"પેક","Dozen":"ડઝન","Meter":"મીટર","Service":"સેવા"},
    "bn": {"Pcs":"পিস","Kg":"কেজি","Gm":"গ্রাম","Ltr":"লিটার","Ml":"মিলি","Box":"বক্স","Pack":"প্যাক","Dozen":"ডজন","Meter":"মিটার","Service":"পরিষেবা"},
    "ta": {"Pcs":"எண்","Kg":"கிலோ","Gm":"கிராம்","Ltr":"லிட்டர்","Ml":"மில்லி","Box":"பெட்டி","Pack":"பேக்","Dozen":"டஜன்","Meter":"மீட்டர்","Service":"சேவை"},
    "te": {"Pcs":"నగ","Kg":"కిలో","Gm":"గ్రామ్","Ltr":"లీటర్","Ml":"మిల్లీ","Box":"బాక్స్","Pack":"ప్యాక్","Dozen":"డజన్","Meter":"మీటర్","Service":"సేవ"},
    "kn": {"Pcs":"ನಗ","Kg":"ಕಿಲೋ","Gm":"ಗ್ರಾಂ","Ltr":"ಲೀಟರ್","Ml":"ಮಿಲಿ","Box":"ಬಾಕ್ಸ್","Pack":"ಪ್ಯಾಕ್","Dozen":"ಡಜನ್","Meter":"ಮೀಟರ್","Service":"ಸೇವೆ"},
    "ml": {"Pcs":"എണ്ണം","Kg":"കിലോ","Gm":"ഗ്രാം","Ltr":"ലിറ്റർ","Ml":"മില്ലി","Box":"ബോക്സ്","Pack":"പാക്ക്","Dozen":"ഡസൻ","Meter":"മീറ്റർ","Service":"സേവനം"},
    "pa": {"Pcs":"ਨਗ","Kg":"ਕਿਲੋ","Gm":"ਗ੍ਰਾਮ","Ltr":"ਲੀਟਰ","Ml":"ਮਿਲੀ","Box":"ਬਾਕਸ","Pack":"ਪੈਕ","Dozen":"ਦਰਜਨ","Meter":"ਮੀਟਰ","Service":"ਸੇਵਾ"},
}


def state_label(value):
    return STATE_LABELS.get(selected_lang, STATE_LABELS["en"]).get(value, value)


def unit_label(value):
    return UNIT_LABELS.get(selected_lang, UNIT_LABELS["en"]).get(value, value)

LEGACY_LANGUAGE_MAP = {
    "English": "en", "हिन्दी - Hindi": "hi", "मराठी - Marathi": "mr", "ગુજરાતી - Gujarati": "gu",
    "বাংলা - Bengali": "bn", "தமிழ் - Tamil": "ta", "తెలుగు - Telugu": "te", "ಕನ್ನಡ - Kannada": "kn",
    "മലയാളം - Malayalam": "ml", "ਪੰਜਾਬੀ - Punjabi": "pa",
}


def normalize_lang(value):
    value = str(value or "").strip()
    if value in LANGUAGE_NAMES:
        return value
    if value in LEGACY_LANGUAGE_MAP:
        return LEGACY_LANGUAGE_MAP[value]
    low = value.lower()
    for code, name in LANGUAGE_NAMES.items():
        if low == name.lower() or low in name.lower():
            return code
    return "en"


# ============================================================
# DATABASE TABLES - SAME TABLE NAMES TO KEEP EXISTING DATA
# ============================================================
metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(255), nullable=False, unique=True),
    Column("password_hash", String(500), nullable=False),
    Column("preferred_language", String(120), nullable=False, default="en"),
    Column("setup_complete", Boolean, nullable=False, default=False),
    Column("company_name", String(300), default=""),
    Column("company_address", Text, default=""),
    Column("company_gstin", String(40), default=""),
    Column("company_phone", String(80), default=""),
    Column("company_email", String(255), default=""),
    Column("company_state", String(120), default="Maharashtra"),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)

customers_table = Table(
    "customers", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("name", String(300), nullable=False),
    Column("address", Text, default=""),
    Column("gstin", String(40), default=""),
    Column("state", String(120), default="Maharashtra"),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)

products_table = Table(
    "products", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("name", String(300), nullable=False),
    Column("hsn", String(80), default=""),
    Column("rate", Float, nullable=False, default=0.0),
    Column("gst_rate", Float, nullable=False, default=18.0),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)

invoices_table = Table(
    "invoices", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("invoice_number", String(120), nullable=False),
    Column("invoice_date", String(20), nullable=False),
    Column("customer_name", String(300), nullable=False),
    Column("customer_address", Text, default=""),
    Column("customer_gstin", String(40), default=""),
    Column("customer_state", String(120), default=""),
    Column("place_of_supply", String(120), default=""),
    Column("items_json", Text, nullable=False),
    Column("taxable_value", Float, nullable=False, default=0.0),
    Column("cgst", Float, nullable=False, default=0.0),
    Column("sgst", Float, nullable=False, default=0.0),
    Column("igst", Float, nullable=False, default=0.0),
    Column("grand_total", Float, nullable=False, default=0.0),
    Column("is_intra_state", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, default=now_naive),
    UniqueConstraint("user_id", "invoice_number", name="uq_invoice_user_number"),
)

suppliers_table = Table(
    "suppliers", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("name", String(300), nullable=False),
    Column("address", Text, default=""),
    Column("gstin", String(40), default=""),
    Column("phone", String(80), default=""),
    Column("email", String(255), default=""),
    Column("state", String(120), default="Maharashtra"),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)

product_inventory_table = Table(
    "product_inventory", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("product_id", Integer, ForeignKey("products.id"), nullable=False, index=True),
    Column("sku", String(120), default=""),
    Column("unit", String(50), default="Pcs"),
    Column("purchase_rate", Float, nullable=False, default=0.0),
    Column("opening_stock", Float, nullable=False, default=0.0),
    Column("low_stock_limit", Float, nullable=False, default=5.0),
    Column("current_stock", Float, nullable=False, default=0.0),
    Column("updated_at", DateTime, nullable=False, default=now_naive),
    UniqueConstraint("user_id", "product_id", name="uq_inventory_user_product"),
)

purchases_table = Table(
    "purchases", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("bill_number", String(120), nullable=False),
    Column("purchase_date", String(20), nullable=False),
    Column("supplier_name", String(300), nullable=False),
    Column("supplier_address", Text, default=""),
    Column("supplier_gstin", String(40), default=""),
    Column("supplier_state", String(120), default=""),
    Column("items_json", Text, nullable=False),
    Column("taxable_value", Float, nullable=False, default=0.0),
    Column("cgst", Float, nullable=False, default=0.0),
    Column("sgst", Float, nullable=False, default=0.0),
    Column("igst", Float, nullable=False, default=0.0),
    Column("grand_total", Float, nullable=False, default=0.0),
    Column("is_intra_state", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, default=now_naive),
    UniqueConstraint("user_id", "bill_number", name="uq_purchase_user_bill"),
)
# ============================================================
# V5.2 - QUOTATIONS / ESTIMATES
# ============================================================

quotations_table = Table(
    "quotations", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("quotation_number", String(120), nullable=False),
    Column("quotation_date", String(20), nullable=False),
    Column("valid_until", String(20), nullable=False),
    Column("customer_name", String(300), nullable=False),
    Column("customer_address", Text, default=""),
    Column("customer_gstin", String(40), default=""),
    Column("customer_state", String(120), default=""),
    Column("place_of_supply", String(120), default=""),
    Column("items_json", Text, nullable=False),
    Column("taxable_value", Float, nullable=False, default=0.0),
    Column("cgst", Float, nullable=False, default=0.0),
    Column("sgst", Float, nullable=False, default=0.0),
    Column("igst", Float, nullable=False, default=0.0),
    Column("grand_total", Float, nullable=False, default=0.0),
    Column("is_intra_state", Boolean, nullable=False, default=True),
    Column("created_at", DateTime, nullable=False, default=now_naive),
    UniqueConstraint("user_id", "quotation_number", name="uq_quotation_user_number"),
)

# ============================================================
# V5.1 - SALES RETURN / PURCHASE RETURN
# ============================================================

sales_returns_table = Table(
    "sales_returns", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),

    Column("original_invoice_id", Integer, ForeignKey("invoices.id"), nullable=False),
    Column("original_invoice_number", String(120), nullable=False),

    Column("return_number", String(120), nullable=False),
    Column("return_date", String(20), nullable=False),

    Column("customer_name", String(300), nullable=False),
    Column("reason", Text, default=""),

    Column("items_json", Text, nullable=False),

    Column("taxable_value", Float, nullable=False, default=0.0),
    Column("cgst", Float, nullable=False, default=0.0),
    Column("sgst", Float, nullable=False, default=0.0),
    Column("igst", Float, nullable=False, default=0.0),
    Column("grand_total", Float, nullable=False, default=0.0),

    Column("created_at", DateTime, nullable=False, default=now_naive),

    UniqueConstraint(
        "user_id",
        "return_number",
        name="uq_sales_return_user_number"
    ),
)


purchase_returns_table = Table(
    "purchase_returns", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),

    Column("original_purchase_id", Integer, ForeignKey("purchases.id"), nullable=False),
    Column("original_bill_number", String(120), nullable=False),

    Column("return_number", String(120), nullable=False),
    Column("return_date", String(20), nullable=False),

    Column("supplier_name", String(300), nullable=False),
    Column("reason", Text, default=""),

    Column("items_json", Text, nullable=False),

    Column("taxable_value", Float, nullable=False, default=0.0),
    Column("cgst", Float, nullable=False, default=0.0),
    Column("sgst", Float, nullable=False, default=0.0),
    Column("igst", Float, nullable=False, default=0.0),
    Column("grand_total", Float, nullable=False, default=0.0),

    Column("created_at", DateTime, nullable=False, default=now_naive),

    UniqueConstraint(
        "user_id",
        "return_number",
        name="uq_purchase_return_user_number"
    ),
)
expenses_table = Table(
    "expenses",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("expense_date", String(20), nullable=False),
    Column("category", String(100), nullable=False),
    Column("amount", Float, nullable=False, default=0.0),
    Column("note", Text, default=""),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)
# ============================================================
# V5.3 - EDIT / DELETE CHANGE HISTORY
# ============================================================

change_history_table = Table(
    "change_history",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("record_type", String(50), nullable=False),
    Column("record_id", Integer, nullable=False, default=0),
    Column("record_number", String(150), default=""),
    Column("action", String(30), nullable=False),
    Column("old_data_json", Text, default=""),
    Column("new_data_json", Text, default=""),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)

stock_ledger_table = Table(
    "stock_ledger", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("product_id", Integer, ForeignKey("products.id"), nullable=False, index=True),
    Column("movement_type", String(40), nullable=False),
    Column("qty_change", Float, nullable=False, default=0.0),
    Column("balance_after", Float, nullable=False, default=0.0),
    Column("reference_type", String(40), default=""),
    Column("reference_id", Integer, default=0),
    Column("reference_number", String(120), default=""),
    Column("note", Text, default=""),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)

user_settings_table = Table(
    "user_settings", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True),
    Column("invoice_prefix", String(30), nullable=False, default="INV"),
    Column("default_low_stock", Float, nullable=False, default=5.0),
    Column("created_at", DateTime, nullable=False, default=now_naive),
    Column("updated_at", DateTime, nullable=False, default=now_naive),
)

payments_table = Table(
    "payments", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("invoice_id", Integer, ForeignKey("invoices.id"), nullable=False, index=True),
    Column("amount", Float, nullable=False, default=0.0),
    Column("payment_date", String(20), nullable=False),
    Column("note", Text, default=""),
    Column("created_at", DateTime, nullable=False, default=now_naive),
)


def get_secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


@st.cache_resource
def get_engine():
    db_url = get_secret("DATABASE_URL", "") or os.environ.get("DATABASE_URL", "")
    if not db_url:
        db_url = f"sqlite:///{LOCAL_DB_FILE.as_posix()}"
    if db_url.startswith("postgres://"):
        db_url = "postgresql+psycopg2://" + db_url[len("postgres://"):]
    elif db_url.startswith("postgresql://"):
        db_url = "postgresql+psycopg2://" + db_url[len("postgresql://"):]
    kwargs = {"pool_pre_ping": True}
    if db_url.startswith("sqlite:"):
        kwargs["connect_args"] = {"check_same_thread": False}
    eng = create_engine(db_url, **kwargs)
    metadata.create_all(eng)
    return eng


engine = get_engine()


def row_dict(row):
    return dict(row._mapping) if row is not None else None


def fetch_all(table, user_id, order_col=None, desc=False):
    stmt = select(table).where(table.c.user_id == user_id)
    if order_col is not None:
        stmt = stmt.order_by(order_col.desc() if desc else order_col)
    with engine.connect() as con:
        return [row_dict(r) for r in con.execute(stmt).all()]


def get_user(user_id):
    if not user_id:
        return None
    with engine.connect() as con:
        return row_dict(con.execute(select(users).where(users.c.id == int(user_id))).first())


def get_user_by_username(username):
    username = str(username or "").strip().lower()
    with engine.connect() as con:
        return row_dict(con.execute(select(users).where(users.c.username == username)).first())


def get_customers(user_id):
    return fetch_all(customers_table, user_id, customers_table.c.name)


def get_products(user_id):
    return fetch_all(products_table, user_id, products_table.c.name)


def get_suppliers(user_id):
    return fetch_all(suppliers_table, user_id, suppliers_table.c.name)


def get_inventory(user_id):
    return fetch_all(product_inventory_table, user_id, product_inventory_table.c.product_id)


def get_stock_ledger(user_id):
    return fetch_all(stock_ledger_table, user_id, stock_ledger_table.c.id, desc=True)


def get_payments(user_id):
    return fetch_all(payments_table, user_id, payments_table.c.id)


def get_invoices(user_id):
    rows = fetch_all(invoices_table, user_id, invoices_table.c.id)
    out = []
    for d in rows:
        try:
            d["items"] = json.loads(d.get("items_json") or "[]")
        except Exception:
            d["items"] = []
        out.append(d)
    return out


def get_purchases(user_id):
    rows = fetch_all(purchases_table, user_id, purchases_table.c.id)
    out = []
    for d in rows:
        try:
            d["items"] = json.loads(d.get("items_json") or "[]")
        except Exception:
            d["items"] = []
        out.append(d)
    return out
def get_quotations(user_id):
    rows = fetch_all(quotations_table, user_id, quotations_table.c.id)
    out = []
    for d in rows:
        try:
            d["items"] = json.loads(d.get("items_json") or "[]")
        except Exception:
            d["items"] = []
        out.append(d)
    return out


def get_sales_returns(user_id):
    rows = fetch_all(sales_returns_table, user_id, sales_returns_table.c.id)
    out = []
    for d in rows:
        try:
            d["items"] = json.loads(d.get("items_json") or "[]")
        except Exception:
            d["items"] = []
        out.append(d)
    return out


def get_purchase_returns(user_id):
    rows = fetch_all(purchase_returns_table, user_id, purchase_returns_table.c.id)
    out = []
    for d in rows:
        try:
            d["items"] = json.loads(d.get("items_json") or "[]")
        except Exception:
            d["items"] = []
        out.append(d)
    return out
def get_change_history(user_id):
    rows = fetch_all(
        change_history_table,
        user_id,
        change_history_table.c.id,
        desc=True,
    )

    out = []

    for row in rows:
        try:
            row["old_data"] = json.loads(
                row.get("old_data_json") or "{}"
            )
        except Exception:
            row["old_data"] = {}

        try:
            row["new_data"] = json.loads(
                row.get("new_data_json") or "{}"
            )
        except Exception:
            row["new_data"] = {}

        out.append(row)

    return out


def log_change(
    con,
    user_id,
    record_type,
    record_id,
    record_number,
    action,
    old_data=None,
    new_data=None,
):
    con.execute(
        insert(change_history_table).values(
            user_id=user_id,
            record_type=str(record_type or ""),
            record_id=int(record_id or 0),
            record_number=str(record_number or ""),
            action=str(action or ""),
            old_data_json=json.dumps(
                old_data or {},
                ensure_ascii=False,
                default=str,
            ),
            new_data_json=json.dumps(
                new_data or {},
                ensure_ascii=False,
                default=str,
            ),
            created_at=now_naive(),
        )
    )


def ensure_user_settings(user_id):
    with engine.begin() as con:
        row = con.execute(select(user_settings_table).where(user_settings_table.c.user_id == user_id)).first()
        if not row:
            con.execute(insert(user_settings_table).values(
                user_id=user_id, invoice_prefix="INV", default_low_stock=5.0,
                created_at=now_naive(), updated_at=now_naive()
            ))
    with engine.connect() as con:
        return row_dict(con.execute(select(user_settings_table).where(user_settings_table.c.user_id == user_id)).first())


def ensure_inventory_rows(user_id, products):
    settings = ensure_user_settings(user_id)
    default_low = float(settings.get("default_low_stock", 5.0) or 5.0)
    with engine.begin() as con:
        existing = {int(r.product_id) for r in con.execute(
            select(product_inventory_table.c.product_id).where(product_inventory_table.c.user_id == user_id)
        ).all()}
        for p in products:
            pid = int(p["id"])
            if pid not in existing:
                con.execute(insert(product_inventory_table).values(
                    user_id=user_id, product_id=pid, sku="", unit="Pcs", purchase_rate=0.0,
                    opening_stock=0.0, low_stock_limit=default_low, current_stock=0.0,
                    updated_at=now_naive()
                ))


def inventory_map(user_id):
    return {int(x["product_id"]): x for x in get_inventory(user_id)}


def lock_inventory(con, user_id, product_id):
    stmt = select(product_inventory_table).where(
        product_inventory_table.c.user_id == user_id,
        product_inventory_table.c.product_id == product_id,
    ).with_for_update()
    return row_dict(con.execute(stmt).first())


def change_stock(con, user_id, product_id, qty_change, movement_type,
                 reference_type="", reference_id=0, reference_number="", note=""):
    inv = lock_inventory(con, user_id, product_id)
    if not inv:
        con.execute(insert(product_inventory_table).values(
            user_id=user_id, product_id=product_id, sku="", unit="Pcs", purchase_rate=0.0,
            opening_stock=0.0, low_stock_limit=5.0, current_stock=0.0, updated_at=now_naive()
        ))
        inv = lock_inventory(con, user_id, product_id)
    new_balance = float(inv.get("current_stock", 0) or 0) + float(qty_change)
    if new_balance < -1e-9:
        raise ValueError("INSUFFICIENT_STOCK")
    new_balance = max(0.0, new_balance)
    con.execute(update(product_inventory_table).where(product_inventory_table.c.id == inv["id"]).values(
        current_stock=new_balance, updated_at=now_naive()
    ))
    con.execute(insert(stock_ledger_table).values(
        user_id=user_id, product_id=product_id, movement_type=movement_type,
        qty_change=float(qty_change), balance_after=new_balance,
        reference_type=reference_type, reference_id=int(reference_id or 0),
        reference_number=reference_number or "", note=note or "", created_at=now_naive()
    ))
    return new_balance


def make_paid_map(payment_rows):
    out = {}
    for p in payment_rows:
        iid = int(p.get("invoice_id", 0) or 0)
        out[iid] = out.get(iid, 0.0) + float(p.get("amount", 0) or 0)
    return out


def payment_status_for_invoice(inv, paid_map):
    total = float(inv.get("grand_total", 0) or 0)
    paid_amount = float(paid_map.get(int(inv.get("id", 0) or 0), 0.0) or 0.0)
    balance = max(0.0, total - paid_amount)
    if total <= 0.005 or balance <= 0.005:
        key = "paid"
    elif paid_amount > 0.005:
        key = "partly_paid"
    else:
        key = "unpaid"
    return paid_amount, balance, key


def money(value):
    return f"₹ {float(value or 0):,.2f}"


def clean_filename(value):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(value)).strip("_") or "invoice"


def parse_app_date(value):
    try:
        return datetime.strptime(str(value), "%d-%m-%Y").date()
    except Exception:
        return None

# ============================================================
# SESSION + LANGUAGE SELECTOR
# ============================================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "guest_lang" not in st.session_state:
    st.session_state.guest_lang = "en"

current_user = get_user(st.session_state.user_id)
if current_user:
    initial_lang = normalize_lang(current_user.get("preferred_language", "en"))
else:
    initial_lang = normalize_lang(st.session_state.get("guest_lang", "en"))

language_codes = list(LANGUAGE_NAMES.keys())
selected_lang = st.sidebar.selectbox(
    "🌐 भाषा / Language",
    language_codes,
    index=language_codes.index(initial_lang) if initial_lang in language_codes else 0,
    format_func=lambda code: LANGUAGE_NAMES[code],
    key="language_selector",
)
st.session_state.guest_lang = selected_lang


def t(key):
    return TR.get(selected_lang, EN).get(key, EN.get(key, key))


st.sidebar.title("🧾 SHIVPRUBA BILLING")

# ============================================================
# LOGIN / SIGNUP
# ============================================================
if not current_user:
    st.title(f"🧾 {t('welcome')}")
    tab1, tab2 = st.tabs([t("login"), t("create_account")])

    with tab1:
        with st.form("login_form"):
            login_username = st.text_input(t("username"))
            login_password = st.text_input(t("password"), type="password")
            login_submit = st.form_submit_button(t("login"), use_container_width=True, type="primary")
        if login_submit:
            found = get_user_by_username(login_username)
            if found and check_password_hash(found["password_hash"], login_password):
                st.session_state.user_id = int(found["id"])
                with engine.begin() as con:
                    con.execute(update(users).where(users.c.id == int(found["id"])).values(
                        preferred_language=selected_lang
                    ))
                st.rerun()
            else:
                st.error(t("invalid_login"))

    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input(t("username"), key="signup_username")
            new_password = st.text_input(t("password"), type="password", key="signup_password")
            confirm_password = st.text_input(t("confirm_password"), type="password")
            signup_submit = st.form_submit_button(t("create_account"), use_container_width=True, type="primary")
        if signup_submit:
            uname = new_username.strip().lower()
            if len(uname) < 3:
                st.error(t("username_required"))
            elif len(new_password) < 6:
                st.error(t("password_short"))
            elif new_password != confirm_password:
                st.error(t("password_mismatch"))
            else:
                try:
                    with engine.begin() as con:
                        result = con.execute(insert(users).values(
                            username=uname,
                            password_hash=generate_password_hash(new_password),
                            preferred_language=selected_lang,
                            setup_complete=False,
                            company_state="Maharashtra",
                            created_at=now_naive(),
                        ))
                        new_id = int(result.inserted_primary_key[0])
                    st.session_state.user_id = new_id
                    st.success(t("account_created"))
                    st.rerun()
                except IntegrityError:
                    st.error(t("account_exists"))
    st.stop()

# ============================================================
# LOGGED USER + SAVE SELECTED LANGUAGE
# ============================================================
current_user = get_user(st.session_state.user_id)
USER_ID = int(current_user["id"])
current_saved_lang = normalize_lang(current_user.get("preferred_language", "en"))
if selected_lang != current_saved_lang:
    with engine.begin() as con:
        con.execute(update(users).where(users.c.id == USER_ID).values(preferred_language=selected_lang))
    current_user["preferred_language"] = selected_lang

# ============================================================
# FIRST BUSINESS SETUP
# ============================================================
if not current_user.get("setup_complete", False):
    st.title(f"🏪 {t('business_setup')}")
    st.caption(t("business_setup_help"))
    with st.form("business_setup_form"):
        company_name = st.text_input(t("company_name"), value=current_user.get("company_name") or "")
        company_address = st.text_area(t("address"), value=current_user.get("company_address") or "")
        company_gstin = st.text_input(t("gstin"), value=current_user.get("company_gstin") or "")
        company_phone = st.text_input(t("phone"), value=current_user.get("company_phone") or "")
        company_email = st.text_input(t("email"), value=current_user.get("company_email") or "")
        state0 = current_user.get("company_state") if current_user.get("company_state") in STATES else "Maharashtra"
        company_state = st.selectbox(t("state"), STATES, index=STATES.index(state0), format_func=state_label)
        setup_submit = st.form_submit_button(t("save_get_started"), use_container_width=True, type="primary")
    if setup_submit:
        if not company_name.strip():
            st.error(t("company_required"))
        else:
            with engine.begin() as con:
                con.execute(update(users).where(users.c.id == USER_ID).values(
                    setup_complete=True,
                    company_name=company_name.strip(),
                    company_address=company_address.strip(),
                    company_gstin=company_gstin.strip(),
                    company_phone=company_phone.strip(),
                    company_email=company_email.strip(),
                    company_state=company_state,
                    preferred_language=selected_lang,
                ))
            st.rerun()
    st.stop()

# ============================================================
# PDF FONT / PDF
# ============================================================
PDF_FONT_CACHE = {}


def register_pdf_font(lang_code):
    if lang_code in PDF_FONT_CACHE:
        return PDF_FONT_CACHE[lang_code]
    candidates = {
        "hi": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"],
        "mr": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"],
        "gu": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf"],
        "bn": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf"],
        "ta": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf"],
        "te": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf"],
        "kn": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf"],
        "ml": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf"],
        "pa": ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/noto/NotoSansGurmukhi-Regular.ttf"],
        "en": ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    }.get(lang_code, [])
    candidates += ["C:/Windows/Fonts/Nirmala.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    font_name = "Helvetica"
    for path in candidates:
        if os.path.exists(path):
            try:
                font_name = f"SBFont_{lang_code}"
                pdfmetrics.registerFont(TTFont(font_name, path))
                break
            except Exception:
                continue
    PDF_FONT_CACHE[lang_code] = font_name
    return font_name


def pdf_safe(text, font_name):
    s = str(text or "")
    if font_name == "Helvetica":
        return s.encode("latin-1", "replace").decode("latin-1")
    return s


def pdf_text(pdf, x, y, text, size=9, bold=False):
    font_name = register_pdf_font(selected_lang)
    if font_name == "Helvetica" and bold:
        font_name = "Helvetica-Bold"
    pdf.setFont(font_name, size)
    pdf.drawString(x, y, pdf_safe(text, font_name))



def make_whatsapp_invoice_url(inv, business):
    company_name = str(
        business.get("company_name") or APP_NAME
    ).strip()

    invoice_number = str(
        inv.get("invoice_number", "")
    ).strip()

    customer_name = str(
        inv.get("customer_name", "")
    ).strip()

    invoice_date = str(
        inv.get("invoice_date", "")
    ).strip()

    grand_total = float(
        inv.get("grand_total", 0) or 0
    )

    message = (
        f"{company_name}\n\n"
        f"Invoice: {invoice_number}\n"
        f"Date: {invoice_date}\n"
        f"Customer: {customer_name}\n"
        f"Amount: ₹{grand_total:,.2f}\n\n"
        f"Thank you!"
    )

    return "https://wa.me/?text=" + quote(message)


def make_invoice_pdf(inv, business):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle(f"{APP_NAME} - {inv['invoice_number']}")

    # ===== INVOICE TITLE =====
    pdf_text(
        pdf,
        18 * mm,
        height - 18 * mm,
        t("create_tax_invoice"),
        15,
        True
    )

    # ===== LEFT SIDE : COMPANY DETAILS =====
    left_x = 18 * mm
    company_y = height - 30 * mm

    pdf_text(
        pdf,
        left_x,
        company_y,
        business.get("company_name", ""),
        12,
        True
    )

    company_y -= 7 * mm

    company_address = business.get("company_address", "")
    address_words = company_address.split()
    address_lines = []
    current_line = ""

    for word in address_words:
        test_line = current_line + (" " if current_line else "") + word

        if pdfmetrics.stringWidth(
            test_line,
            "Helvetica",
            9
        ) <= 88 * mm:
            current_line = test_line
        else:
            if current_line:
                address_lines.append(current_line)
            current_line = word

    if current_line:
        address_lines.append(current_line)

    for line in address_lines:
        pdf_text(
            pdf,
            left_x,
            company_y,
            line,
            9
        )
        company_y -= 5 * mm

    company_y -= 7 * mm

    pdf_text(
        pdf,
        left_x,
        company_y,
        f"GSTIN: {business.get('company_gstin', '')}",
        9
    )

    company_y -= 7 * mm

    pdf_text(
        pdf,
        left_x,
        company_y,
        f"{t('phone')}: {business.get('company_phone', '')}",
        9
    )

    # ===== RIGHT SIDE : INVOICE DETAILS =====
    right_x = 115 * mm
    invoice_y = height - 30 * mm

    pdf_text(
        pdf,
        right_x,
        invoice_y,
        f"{t('invoice_number')}: {inv.get('invoice_number', '')}",
        9,
        True
    )

    invoice_y -= 8 * mm

    pdf_text(
        pdf,
        right_x,
        invoice_y,
        f"{t('date')}: {inv.get('invoice_date', '')}",
        9
    )

    invoice_y -= 8 * mm

    pdf_text(
        pdf,
        right_x,
        invoice_y,
        f"{t('place_of_supply')}: {inv.get('place_of_supply', '')}",
        9
    )

    # ===== SEPARATOR LINE =====
    y = height - 70 * mm
    pdf.line(18 * mm, y, 192 * mm, y)

    y -= 8 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        t("customer_info"),
        10,
        True
    )

    y -= 7 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        inv.get("customer_name", ""),
        10,
        True
    )

    y -= 6 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        inv.get("customer_address", ""),
        9
    )

    y -= 6 * mm

    pdf_text(
        pdf,
        18 * mm,
        y,
        f"GSTIN: {inv.get('customer_gstin', '') or '--'}",
        9
    )

    y -= 10 * mm
    pdf.line(18 * mm, y, 192 * mm, y)

    y -= 7 * mm

    headers = [
        "#",
        t("description"),
        t("hsn_sac"),
        t("quantity"),
        t("rate"),
        "GST%",
        t("amount")
    ]

    xs = [18, 28, 92, 116, 132, 157, 174]

    for x, header in zip(xs, headers):
        pdf_text(
            pdf,
            x * mm,
            y,
            header,
            8,
            True
        )

    y -= 6 * mm
    pdf.line(18 * mm, y, 192 * mm, y)

    y -= 6 * mm

    for index, item in enumerate(inv.get("items", []), 1):
        if y < 45 * mm:
            pdf.showPage()
            y = height - 25 * mm

        pdf_text(
            pdf,
            18 * mm,
            y,
            index,
            8
        )

        pdf_text(
            pdf,
            28 * mm,
            y,
            str(item.get("desc", ""))[:28],
            8
        )

        pdf_text(
            pdf,
            92 * mm,
            y,
            item.get("hsn", ""),
            8
        )

        pdf_text(
            pdf,
            116 * mm,
            y,
            f"{float(item.get('qty', 0)):g}",
            8
        )

        pdf_text(
            pdf,
            132 * mm,
            y,
            f"{float(item.get('rate', 0)):,.2f}",
            8
        )

        pdf_text(
            pdf,
            157 * mm,
            y,
            f"{float(item.get('gst_rate', 0)):g}",
            8
        )

        pdf_text(
            pdf,
            174 * mm,
            y,
            f"{float(item.get('amount', 0)):,.2f}",
            8
        )

        y -= 7 * mm

    y -= 3 * mm
    pdf.line(112 * mm, y, 192 * mm, y)

    y -= 7 * mm

    pdf_text(
        pdf,
        120 * mm,
        y,
        t("taxable_value"),
        8
    )

    pdf_text(
        pdf,
        170 * mm,
        y,
        f"{float(inv.get('taxable_value', 0)):,.2f}",
        8
    )

    y -= 6 * mm

    if inv.get("is_intra_state"):
        pdf_text(
            pdf,
            120 * mm,
            y,
            "CGST",
            8
        )

        pdf_text(
            pdf,
            170 * mm,
            y,
            f"{float(inv.get('cgst', 0)):,.2f}",
            8
        )

        y -= 6 * mm

        pdf_text(
            pdf,
            120 * mm,
            y,
            "SGST",
            8
        )

        pdf_text(
            pdf,
            170 * mm,
            y,
            f"{float(inv.get('sgst', 0)):,.2f}",
            8
        )

    else:
        pdf_text(
            pdf,
            120 * mm,
            y,
            "IGST",
            8
        )

        pdf_text(
            pdf,
            170 * mm,
            y,
            f"{float(inv.get('igst', 0)):,.2f}",
            8
        )

    y -= 8 * mm
    pdf.line(112 * mm, y, 192 * mm, y)

    y -= 8 * mm

    pdf_text(
        pdf,
        120 * mm,
        y,
        t("grand_total"),
        10,
        True
    )

    pdf_text(
        pdf,
        166 * mm,
        y,
        f"Rs. {float(inv.get('grand_total', 0)):,.2f}",
        10,
        True
    )

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()

def make_quotation_pdf(quote, business):
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        pdf.setTitle(f"{APP_NAME} - {quote['quotation_number']}")
        
        # ========================================================
        # SMALL HELPER - WRAP LONG COMPANY ADDRESS
        # ========================================================
        def draw_wrapped_address(pdf_obj, x, y, text, max_width, font_size=9, line_gap=5 * mm):
            font_name = register_pdf_font(selected_lang)
            safe_text = pdf_safe(text, font_name)
            pdf_obj.setFont(font_name, font_size)

            words = safe_text.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = word if not current_line else f"{current_line} {word}"
                if pdfmetrics.stringWidth(test_line, font_name, font_size) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            # Maximum 2 lines for company address
            lines = lines[:2]

            current_y = y
            for line in lines:
                pdf_obj.drawString(x, current_y, line)
                current_y -= line_gap

            return current_y
        # ========================================================
        # HEADER
        # ========================================================
        pdf_text(
            pdf,
            18 * mm,
            height - 18 * mm,
            t("quotation"),
            15,
            True
        )

        # ========================================================
        # LEFT SIDE - COMPANY DETAILS
        # ========================================================
        pdf_text(
            pdf,
            18 * mm,
            height - 29 * mm,
            business.get("company_name", ""),
            13,
            True
        )

        # Company address gets only left-side space.
        # This prevents overlap with quotation details.
        address_end_y = draw_wrapped_address(
            pdf,
            18 * mm,
            height - 36 * mm,
            business.get("company_address", ""),
            max_width=88 * mm,
            font_size=9,
            line_gap=5 * mm,
        )

        pdf_text(
            pdf,
            18 * mm,
            address_end_y - 2 * mm,
            f"GSTIN: {business.get('company_gstin', '')}",
            9
        )

        pdf_text(
            pdf,
            18 * mm,
            address_end_y - 9 * mm,
            f"{t('phone')}: {business.get('company_phone', '')}",
            9
        )

        # ========================================================
        # RIGHT SIDE - QUOTATION DETAILS
        # ========================================================
        pdf_text(
            pdf,
            112 * mm,
            height - 29 * mm,
            f"{t('quotation_number')}: {quote['quotation_number']}",
            9,
            True
        )

        pdf_text(
            pdf,
            112 * mm,
            height - 37 * mm,
            f"{t('quotation_date')}: {quote['quotation_date']}",
            9
        )

        pdf_text(
            pdf,
            112 * mm,
            height - 45 * mm,
            f"{t('valid_until')}: {quote.get('valid_until', '')}",
            9
        )

        pdf_text(
            pdf,
            112 * mm,
            height - 53 * mm,
            f"{t('place_of_supply')}: {quote.get('place_of_supply', '')}",
            8
        )

        # ========================================================
        # CUSTOMER INFORMATION
        # ========================================================
        y = height - 72 * mm

        pdf.line(
            18 * mm,
            y,
            192 * mm,
            y
        )

        y -= 8 * mm

        pdf_text(
            pdf,
            18 * mm,
            y,
            t("customer_info"),
            10,
            True
        )

        y -= 7 * mm

        pdf_text(
            pdf,
            18 * mm,
            y,
            quote.get("customer_name", ""),
            10,
            True
        )

        y -= 6 * mm

        pdf_text(
            pdf,
            18 * mm,
            y,
            quote.get("customer_address", ""),
            9
        )

        y -= 6 * mm

        pdf_text(
            pdf,
            18 * mm,
            y,
            f"GSTIN: {quote.get('customer_gstin', '')}",
            9
        )

        # ========================================================
        # ITEM TABLE
        # ========================================================
        y -= 10 * mm

        pdf.line(
            18 * mm,
            y,
            192 * mm,
            y
        )

        y -= 7 * mm

        headers = [
            "#",
            t("description"),
            t("hsn_sac"),
            t("quantity"),
            t("rate"),
            "GST%",
            t("amount"),
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

        for x, header in zip(xs, headers):
            pdf_text(
                pdf,
                x * mm,
                y,
                header,
                8,
                True
            )

        y -= 6 * mm

        pdf.line(
            18 * mm,
            y,
            192 * mm,
            y
        )

        y -= 6 * mm

        for index, item in enumerate(
            quote.get("items", []),
            1
        ):
            if y < 45 * mm:
                pdf.showPage()
                y = height - 25 * mm

            pdf_text(
                pdf,
                18 * mm,
                y,
                index,
                8
            )

            pdf_text(
                pdf,
                28 * mm,
                y,
                str(item.get("desc", ""))[:28],
                8
            )

            pdf_text(
                pdf,
                92 * mm,
                y,
                item.get("hsn", ""),
                8
            )

            pdf_text(
                pdf,
                116 * mm,
                y,
                f"{float(item.get('qty', 0)):g}",
                8
            )

            pdf_text(
                pdf,
                132 * mm,
                y,
                f"{float(item.get('rate', 0)):,.2f}",
                8
            )

            pdf_text(
                pdf,
                157 * mm,
                y,
                f"{float(item.get('gst_rate', 0)):g}",
                8
            )

            pdf_text(
                pdf,
                174 * mm,
                y,
                f"{float(item.get('amount', 0)):,.2f}",
                8
            )

            y -= 7 * mm

        # ========================================================
        # TOTALS
        # ========================================================
        y -= 3 * mm

        pdf.line(
            112 * mm,
            y,
            192 * mm,
            y
        )

        y -= 7 * mm

        pdf_text(
            pdf,
            120 * mm,
            y,
            t("taxable_value"),
            8
        )

        pdf_text(
            pdf,
            170 * mm,
            y,
            f"{float(quote.get('taxable_value', 0)):,.2f}",
            8
        )

        y -= 6 * mm

        if quote.get("is_intra_state"):

            pdf_text(
                pdf,
                120 * mm,
                y,
                "CGST",
                8
            )

            pdf_text(
                pdf,
                170 * mm,
                y,
                f"{float(quote.get('cgst', 0)):,.2f}",
                8
            )

            y -= 6 * mm

            pdf_text(
                pdf,
                120 * mm,
                y,
                "SGST",
                8
            )

            pdf_text(
                pdf,
                170 * mm,
                y,
                f"{float(quote.get('sgst', 0)):,.2f}",
                8
            )

        else:

            pdf_text(
                pdf,
                120 * mm,
                y,
                "IGST",
                8
            )

            pdf_text(
                pdf,
                170 * mm,
                y,
                f"{float(quote.get('igst', 0)):,.2f}",
                8
            )

        y -= 8 * mm

        pdf.line(
            112 * mm,
            y,
            192 * mm,
            y
        )

        y -= 8 * mm

        pdf_text(
            pdf,
            120 * mm,
            y,
            t("grand_total"),
            10,
            True
        )

        pdf_text(
            pdf,
            166 * mm,
            y,
            f"Rs. {float(quote.get('grand_total', 0)):,.2f}",
            10,
            True
        )

        # ========================================================
        # STOCK NOTE
        # ========================================================
        y -= 16 * mm

        pdf_text(
            pdf,
            18 * mm,
            y,
            t("quotation_stock_note"),
            8
        )

        pdf.save()
        buffer.seek(0)

        return buffer.getvalue()

# ============================================================
# LOAD USER DATA
# ============================================================
current_user = get_user(USER_ID)
customers = get_customers(USER_ID)
products = get_products(USER_ID)
ensure_inventory_rows(USER_ID, products)
suppliers = get_suppliers(USER_ID)
purchases = get_purchases(USER_ID)
invoices = get_invoices(USER_ID)
quotations = get_quotations(USER_ID)
sales_returns = get_sales_returns(USER_ID)
purchase_returns = get_purchase_returns(USER_ID)
payments = get_payments(USER_ID)
inventory = get_inventory(USER_ID)
stock_ledger = get_stock_ledger(USER_ID)
app_settings = ensure_user_settings(USER_ID)
INV_MAP = {int(x["product_id"]): x for x in inventory}
PAID_MAP = make_paid_map(payments)

# ============================================================
# MENU
# ============================================================
MENU_ICONS = {
    "dashboard": "🏠",
    "new_invoice": "🧾",
    "quotation": "📄",
    "purchases": "📥",
    "customers": "👥",
    "customer_ledger": "📒",
    "payment_reminder": "🔔",
    "suppliers": "🏭",
    "products": "📦",
    "stock": "📊",
    "invoice_history": "🕘",
    "purchase_history": "📚",
    "sales_return": "↩️",
"purchase_return": "🔄",
    "expenses": "💸",
    "edit_delete_history": "📝",
    "reports": "📈",
    "settings": "⚙️",
}

menu = st.sidebar.radio(
    t("menu"),
    list(MENU_ICONS.keys()),
    format_func=lambda key: f"{MENU_ICONS[key]} {t(key)}",
)
st.sidebar.markdown("---")
st.sidebar.caption(current_user.get("company_name", ""))
st.sidebar.caption(t("version"))
if st.sidebar.button(f"🚪 {t('logout')}", use_container_width=True):
    st.session_state.user_id = None
    st.rerun()

# ============================================================
# DASHBOARD
# ============================================================
if menu == "dashboard":
    st.title(f"🏠 {t('dashboard')}")

    # --------------------------------------------------------
    # MAIN TOTALS
    # --------------------------------------------------------
    total_sales = sum(
        float(i.get("grand_total", 0) or 0)
        for i in invoices
    )

    total_tax = sum(
        float(i.get("cgst", 0) or 0)
        + float(i.get("sgst", 0) or 0)
        + float(i.get("igst", 0) or 0)
        for i in invoices
    )

    total_purchases = sum(
        float(p.get("grand_total", 0) or 0)
        for p in purchases
    )

    stock_value = sum(
        float(x.get("current_stock", 0) or 0)
        * float(x.get("purchase_rate", 0) or 0)
        for x in inventory
    )

    # --------------------------------------------------------
    # EXPENSES
    # --------------------------------------------------------
    with engine.connect() as con:
        dashboard_expenses = [
            row_dict(r)
            for r in con.execute(
                select(expenses_table).where(
                    expenses_table.c.user_id == USER_ID
                )
            ).all()
        ]

    total_expenses = sum(
        float(e.get("amount", 0) or 0)
        for e in dashboard_expenses
    )

    # --------------------------------------------------------
    # SALES RETURNS
    # --------------------------------------------------------
    total_sales_returns = sum(
        float(r.get("grand_total", 0) or 0)
        for r in sales_returns
    )

    # --------------------------------------------------------
    # PURCHASE RETURNS
    # --------------------------------------------------------
    total_purchase_returns = sum(
        float(r.get("grand_total", 0) or 0)
        for r in purchase_returns
    )

    # --------------------------------------------------------
    # NET SALES / PURCHASES / PROFIT-LOSS
    # --------------------------------------------------------
    net_sales_dashboard = (
        total_sales
        - total_sales_returns
    )

    net_purchases_dashboard = (
        total_purchases
        - total_purchase_returns
    )

    estimated_profit_loss_dashboard = (
        net_sales_dashboard
        - net_purchases_dashboard
        - total_expenses
    )

    # --------------------------------------------------------
    # TODAY COUNTS
    # --------------------------------------------------------
    today_str = date.today().strftime("%d-%m-%Y")

    today_count = sum(
        1
        for i in invoices
        if i.get("invoice_date") == today_str
    )

    today_purchase_count = sum(
        1
        for p in purchases
        if p.get("purchase_date") == today_str
    )

    # --------------------------------------------------------
    # LOW STOCK
    # --------------------------------------------------------
    low_items = [
        x
        for x in inventory
        if x.get("unit") != "Service"
        and float(x.get("low_stock_limit", 0) or 0) > 0
        and float(x.get("current_stock", 0) or 0)
        <= float(x.get("low_stock_limit", 0) or 0)
    ]

    # --------------------------------------------------------
    # DASHBOARD CARDS - ROW 1
    # --------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        t("total_invoices"),
        len(invoices),
    )

    c2.metric(
        t("total_sales"),
        money(total_sales),
    )

    c3.metric(
        t("today_invoices"),
        today_count,
    )

    c4.metric(
        t("total_gst"),
        money(total_tax),
    )

    # --------------------------------------------------------
    # DASHBOARD CARDS - ROW 2
    # --------------------------------------------------------
    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        t("total_purchases"),
        money(total_purchases),
    )

    c6.metric(
        t("today_purchases"),
        today_purchase_count,
    )

    c7.metric(
        t("stock_value"),
        money(stock_value),
    )

    c8.metric(
        t("low_stock"),
        len(low_items),
    )

    # --------------------------------------------------------
    # V5.3 - EXPENSES + PROFIT / LOSS CARDS
    # --------------------------------------------------------
    c9, c10 = st.columns(2)

    c9.metric(
        t("total_expenses"),
        money(total_expenses),
    )

    c10.metric(
        t("estimated_profit_loss"),
        money(estimated_profit_loss_dashboard),
    )

    # --------------------------------------------------------
    # LOW STOCK WARNING
    # --------------------------------------------------------
    if low_items:
        product_by_id = {
            int(p["id"]): p
            for p in products
        }

        names = []

        for x in low_items[:8]:
            p = product_by_id.get(
                int(x["product_id"]),
                {},
            )

            names.append(
                f"{p.get('name', t('product'))}: "
                f"{float(x.get('current_stock', 0)):g} "
                f"{x.get('unit', '')}"
            )

        st.warning(
            "⚠️ "
            + t("low_stock")
            + ": "
            + " | ".join(names)
        )

    # --------------------------------------------------------
    # RECENT INVOICES / PURCHASES
    # --------------------------------------------------------
    st.markdown("---")

    left_recent, right_recent = st.columns(2)

    with left_recent:
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
                    use_container_width=True,
                )

    with right_recent:
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
    st.title(f"🧾 {t('create_tax_invoice')}")

    left, right = st.columns(2)
    customer_map = {c["name"]: c for c in customers}
    with left:
        st.subheader(t("customer_info"))
        choice = st.selectbox(t("saved_customer"), [t("manual_customer")] + list(customer_map.keys()))
        cdata = customer_map.get(choice, {})
        customer_name = st.text_input(t("customer_name"), value=cdata.get("name", ""), key=f"cn_{choice}")
        customer_address = st.text_area(t("customer_address"), value=cdata.get("address", ""), key=f"ca_{choice}")
        customer_gstin = st.text_input(t("customer_gstin"), value=cdata.get("gstin", ""), key=f"cg_{choice}")
        cstate = cdata.get("state", "Maharashtra") if cdata.get("state", "Maharashtra") in STATES else "Maharashtra"
        customer_state = st.selectbox(t("customer_state"), STATES, index=STATES.index(cstate), format_func=state_label, key=f"cs_{choice}")

    with right:
        st.subheader(t("invoice_details"))
        prefix = (app_settings.get("invoice_prefix") or "INV").strip() or "INV"
        suggested = f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{len(invoices)+1:03d}"
        invoice_number = st.text_input(t("invoice_number"), value=suggested)
        inv_date = st.date_input(t("invoice_date"), value=date.today())
        place_supply = st.selectbox(
            t("place_of_supply"), STATES,
            index=STATES.index(customer_state) if customer_state in STATES else STATES.index("Maharashtra"),
            format_func=state_label
        )

    st.markdown("---")
    st.subheader(f"📦 {t('goods_services')}")
    nitems = int(st.number_input(t("number_of_items"), min_value=1, max_value=20, value=1, step=1))
    pmap = {p["name"]: p for p in products}
    invoice_items = []

    for i in range(nitems):
        st.markdown(f"**{t('item')} {i+1}**")
        pchoice = st.selectbox(t("saved_product"), [t("custom_item")] + list(pmap.keys()), key=f"pc_{i}")
        pdata = pmap.get(pchoice, {})
        product_id = int(pdata["id"]) if pdata else None
        invdata = INV_MAP.get(product_id, {}) if product_id else {}
        if product_id:
            st.caption(f"{t('current_stock')}: {float(invdata.get('current_stock',0) or 0):g} {unit_label(invdata.get('unit','Pcs'))}")

        a, b, c, d, e = st.columns([3, 1.2, 1, 1.3, 1.1])
        with a:
            desc = st.text_input(t("description"), value=pdata.get("name", ""), key=f"desc_{i}_{pchoice}")
        with b:
            hsn = st.text_input(t("hsn_sac"), value=pdata.get("hsn", ""), key=f"hsn_{i}_{pchoice}")
        with c:
            qty = st.number_input(t("quantity"), min_value=0.01, value=1.0, step=1.0, key=f"qty_{i}")
        with d:
            rate = st.number_input(t("rate"), min_value=0.0, value=float(pdata.get("rate", 0.0) or 0.0), step=10.0, key=f"rate_{i}_{pchoice}")
        with e:
            opts = [0, 5, 12, 18, 28]
            default_gst = int(pdata.get("gst_rate", 18) or 18) if pdata else 18
            if default_gst not in opts:
                default_gst = 18
            gst = st.selectbox(t("gst_percent"), opts, index=opts.index(default_gst), key=f"gst_{i}_{pchoice}")

        track_stock = bool(product_id and invdata.get("unit") != "Service")
        if track_stock and float(qty) > float(invdata.get("current_stock", 0) or 0):
            st.warning(t("insufficient_stock"))
        invoice_items.append({
            "product_id": product_id,
            "track_stock": track_stock,
            "desc": desc,
            "hsn": hsn,
            "qty": float(qty),
            "rate": float(rate),
            "gst_rate": float(gst),
            "amount": float(qty) * float(rate),
        })
        st.markdown("---")

    if st.button(t("calculate_save_invoice"), use_container_width=True, type="primary"):
        if not customer_name.strip():
            st.error(t("customer_required"))
        elif any(i["invoice_number"] == invoice_number.strip() for i in invoices):
            st.error(t("invoice_duplicate"))
        elif any(
            x.get("track_stock") and x.get("product_id")
            and float(x.get("qty", 0)) > float(INV_MAP.get(int(x["product_id"]), {}).get("current_stock", 0) or 0)
            for x in invoice_items
        ):
            st.error(t("insufficient_stock"))
        else:
            taxable = sum(x["amount"] for x in invoice_items)
            intra = current_user.get("company_state") == place_supply
            cgst = sgst = igst = 0.0
            for x in invoice_items:
                tax = x["amount"] * x["gst_rate"] / 100.0
                if intra:
                    cgst += tax / 2.0
                    sgst += tax / 2.0
                else:
                    igst += tax
            grand = taxable + cgst + sgst + igst
            try:
                with engine.begin() as con:
                    result = con.execute(insert(invoices_table).values(
                        user_id=USER_ID,
                        invoice_number=invoice_number.strip(),
                        invoice_date=inv_date.strftime("%d-%m-%Y"),
                        customer_name=customer_name.strip(),
                        customer_address=customer_address.strip(),
                        customer_gstin=customer_gstin.strip(),
                        customer_state=customer_state,
                        place_of_supply=place_supply,
                        items_json=json.dumps(invoice_items, ensure_ascii=False),
                        taxable_value=taxable, cgst=cgst, sgst=sgst, igst=igst,
                        grand_total=grand, is_intra_state=intra, created_at=now_naive(),
                    ))
                    inv_id = int(result.inserted_primary_key[0])
                    for item in invoice_items:
                        if item.get("product_id") and item.get("track_stock"):
                            change_stock(
                                con, USER_ID, int(item["product_id"]), -float(item["qty"]),
                                "SALE", "INVOICE", inv_id, invoice_number.strip(),
                                f"{t('sale')}: {item.get('desc','')}"
                            )
            except IntegrityError:
                st.error(t("invoice_duplicate")); st.stop()
            except ValueError as exc:
                if str(exc) == "INSUFFICIENT_STOCK":
                    st.error(t("insufficient_stock")); st.stop()
                raise

            if customer_name.strip() and not any(
                c["name"].strip().lower() == customer_name.strip().lower() for c in customers
            ):
                with engine.begin() as con:
                    con.execute(insert(customers_table).values(
                        user_id=USER_ID, name=customer_name.strip(), address=customer_address.strip(),
                        gstin=customer_gstin.strip(), state=customer_state, created_at=now_naive()
                    ))

            new_inv = {
                "id": inv_id, "invoice_number": invoice_number.strip(),
                "invoice_date": inv_date.strftime("%d-%m-%Y"),
                "customer_name": customer_name.strip(), "customer_address": customer_address.strip(),
                "customer_gstin": customer_gstin.strip(), "customer_state": customer_state,
                "place_of_supply": place_supply, "items": invoice_items,
                "taxable_value": taxable, "cgst": cgst, "sgst": sgst, "igst": igst,
                "grand_total": grand, "is_intra_state": intra,
            }
            st.success(t("invoice_saved"))
            x, y, z = st.columns(3)
            x.metric(t("taxable_value"), money(taxable))
            y.metric("CGST + SGST" if intra else "IGST", money(cgst + sgst if intra else igst))
            z.metric(t("grand_total"), money(grand))
            st.download_button(
                t("download_pdf"), make_invoice_pdf(new_inv, current_user),
                f"{clean_filename(invoice_number)}.pdf", "application/pdf",
                use_container_width=True,
            )

# ============================================================
# V5.2 - QUOTATION / ESTIMATE
# ============================================================
elif menu == "quotation":
    st.title(f"📄 {t('create_quotation')}")
    st.info(t("quotation_stock_note"))

    q_left, q_right = st.columns(2)
    customer_map = {c["name"]: c for c in customers}

    with q_left:
        st.subheader(t("customer_info"))
        q_choice = st.selectbox(
            t("saved_customer"),
            [t("manual_customer")] + list(customer_map.keys()),
            key="quotation_customer_choice",
        )
        q_cdata = customer_map.get(q_choice, {})
        q_customer_name = st.text_input(
            t("customer_name"),
            value=q_cdata.get("name", ""),
            key=f"quotation_customer_name_{q_choice}",
        )
        q_customer_address = st.text_area(
            t("customer_address"),
            value=q_cdata.get("address", ""),
            key=f"quotation_customer_address_{q_choice}",
        )
        q_customer_gstin = st.text_input(
            t("customer_gstin"),
            value=q_cdata.get("gstin", ""),
            key=f"quotation_customer_gstin_{q_choice}",
        )
        q_state0 = (
            q_cdata.get("state", "Maharashtra")
            if q_cdata.get("state", "Maharashtra") in STATES
            else "Maharashtra"
        )
        q_customer_state = st.selectbox(
            t("customer_state"),
            STATES,
            index=STATES.index(q_state0),
            format_func=state_label,
            key=f"quotation_customer_state_{q_choice}",
        )

    with q_right:
        st.subheader(t("quotation_details"))
        q_suggested = f"QT-{datetime.now().strftime('%Y%m%d')}-{len(quotations)+1:03d}"
        quotation_number = st.text_input(
            t("quotation_number"),
            value=q_suggested,
            key="quotation_number_input",
        )
        quotation_date = st.date_input(
            t("quotation_date"),
            value=date.today(),
            key="quotation_date_input",
        )
        valid_until = st.date_input(
            t("valid_until"),
            value=date.today() + timedelta(days=7),
            key="quotation_valid_until_input",
        )
        q_place_supply = st.selectbox(
            t("place_of_supply"),
            STATES,
            index=(
                STATES.index(q_customer_state)
                if q_customer_state in STATES
                else STATES.index("Maharashtra")
            ),
            format_func=state_label,
            key="quotation_place_supply",
        )

    st.markdown("---")
    st.subheader(f"📦 {t('goods_services')}")

    q_nitems = int(
        st.number_input(
            t("number_of_items"),
            min_value=1,
            max_value=20,
            value=1,
            step=1,
            key="quotation_item_count",
        )
    )
    q_pmap = {p["name"]: p for p in products}
    quotation_items = []

    for i in range(q_nitems):
        st.markdown(f"**{t('item')} {i+1}**")
        q_pchoice = st.selectbox(
            t("saved_product"),
            [t("custom_item")] + list(q_pmap.keys()),
            key=f"quotation_product_choice_{i}",
        )
        q_pdata = q_pmap.get(q_pchoice, {})
        q_product_id = int(q_pdata["id"]) if q_pdata else None
        q_invdata = INV_MAP.get(q_product_id, {}) if q_product_id else {}

        if q_product_id:
            st.caption(
                f"{t('current_stock')}: "
                f"{float(q_invdata.get('current_stock',0) or 0):g} "
                f"{unit_label(q_invdata.get('unit','Pcs'))}"
            )

        qa, qb, qc, qd, qe = st.columns([3, 1.2, 1, 1.3, 1.1])
        with qa:
            q_desc = st.text_input(
                t("description"),
                value=q_pdata.get("name", ""),
                key=f"quotation_desc_{i}_{q_pchoice}",
            )
        with qb:
            q_hsn = st.text_input(
                t("hsn_sac"),
                value=q_pdata.get("hsn", ""),
                key=f"quotation_hsn_{i}_{q_pchoice}",
            )
        with qc:
            q_qty = st.number_input(
                t("quantity"),
                min_value=0.01,
                value=1.0,
                step=1.0,
                key=f"quotation_qty_{i}",
            )
        with qd:
            q_rate = st.number_input(
                t("rate"),
                min_value=0.0,
                value=float(q_pdata.get("rate", 0.0) or 0.0),
                step=10.0,
                key=f"quotation_rate_{i}_{q_pchoice}",
            )
        with qe:
            q_opts = [0, 5, 12, 18, 28]
            q_default_gst = int(q_pdata.get("gst_rate", 18) or 18) if q_pdata else 18
            if q_default_gst not in q_opts:
                q_default_gst = 18
            q_gst = st.selectbox(
                t("gst_percent"),
                q_opts,
                index=q_opts.index(q_default_gst),
                key=f"quotation_gst_{i}_{q_pchoice}",
            )

        q_track_stock = bool(q_product_id and q_invdata.get("unit") != "Service")
        quotation_items.append({
            "product_id": q_product_id,
            "track_stock": q_track_stock,
            "desc": q_desc,
            "hsn": q_hsn,
            "qty": float(q_qty),
            "rate": float(q_rate),
            "gst_rate": float(q_gst),
            "amount": float(q_qty) * float(q_rate),
        })
        st.markdown("---")

    q_taxable = sum(x["amount"] for x in quotation_items)
    q_intra = current_user.get("company_state") == q_place_supply
    q_cgst = q_sgst = q_igst = 0.0
    for x in quotation_items:
        q_tax = x["amount"] * x["gst_rate"] / 100.0
        if q_intra:
            q_cgst += q_tax / 2.0
            q_sgst += q_tax / 2.0
        else:
            q_igst += q_tax
    q_grand = q_taxable + q_cgst + q_sgst + q_igst

    qm1, qm2, qm3 = st.columns(3)
    qm1.metric(t("taxable_value"), money(q_taxable))
    qm2.metric("CGST + SGST" if q_intra else "IGST", money(q_cgst + q_sgst if q_intra else q_igst))
    qm3.metric(t("grand_total"), money(q_grand))

    if st.button(
        t("save_quotation"),
        use_container_width=True,
        type="primary",
        key="save_quotation_button",
    ):
        if not q_customer_name.strip():
            st.error(t("customer_required"))
        elif valid_until < quotation_date:
            st.error(t("quotation_validity_error"))
        elif any(
            str(q.get("quotation_number", "")).strip().lower()
            == quotation_number.strip().lower()
            for q in quotations
        ):
            st.error(t("quotation_duplicate"))
        else:
            try:
                with engine.begin() as con:
                    result = con.execute(
                        insert(quotations_table).values(
                            user_id=USER_ID,
                            quotation_number=quotation_number.strip(),
                            quotation_date=quotation_date.strftime("%d-%m-%Y"),
                            valid_until=valid_until.strftime("%d-%m-%Y"),
                            customer_name=q_customer_name.strip(),
                            customer_address=q_customer_address.strip(),
                            customer_gstin=q_customer_gstin.strip(),
                            customer_state=q_customer_state,
                            place_of_supply=q_place_supply,
                            items_json=json.dumps(quotation_items, ensure_ascii=False),
                            taxable_value=q_taxable,
                            cgst=q_cgst,
                            sgst=q_sgst,
                            igst=q_igst,
                            grand_total=q_grand,
                            is_intra_state=q_intra,
                            created_at=now_naive(),
                        )
                    )
                    quotation_id = int(result.inserted_primary_key[0])
            except IntegrityError:
                st.error(t("quotation_duplicate"))
                st.stop()

            if q_customer_name.strip() and not any(
                c["name"].strip().lower() == q_customer_name.strip().lower()
                for c in customers
            ):
                with engine.begin() as con:
                    con.execute(
                        insert(customers_table).values(
                            user_id=USER_ID,
                            name=q_customer_name.strip(),
                            address=q_customer_address.strip(),
                            gstin=q_customer_gstin.strip(),
                            state=q_customer_state,
                            created_at=now_naive(),
                        )
                    )

            new_quote = {
                "id": quotation_id,
                "quotation_number": quotation_number.strip(),
                "quotation_date": quotation_date.strftime("%d-%m-%Y"),
                "valid_until": valid_until.strftime("%d-%m-%Y"),
                "customer_name": q_customer_name.strip(),
                "customer_address": q_customer_address.strip(),
                "customer_gstin": q_customer_gstin.strip(),
                "customer_state": q_customer_state,
                "place_of_supply": q_place_supply,
                "items": quotation_items,
                "taxable_value": q_taxable,
                "cgst": q_cgst,
                "sgst": q_sgst,
                "igst": q_igst,
                "grand_total": q_grand,
                "is_intra_state": q_intra,
            }
            quotations.append(new_quote)

            st.success(t("quotation_saved"))
            st.download_button(
                t("download_pdf"),
                make_quotation_pdf(new_quote, current_user),
                f"{clean_filename(quotation_number)}.pdf",
                "application/pdf",
                use_container_width=True,
                key=f"new_quotation_pdf_{quotation_id}",
            )

    st.markdown("---")
    st.subheader(f"📚 {t('saved_quotations')}")

    if not quotations:
        st.info(t("no_quotations"))
    else:
        q_search = st.text_input(
            f"🔎 {t('search_quotation')}",
            key="quotation_history_search",
        ).strip().lower()
        filtered_quotes = quotations if not q_search else [
            q for q in quotations
            if q_search in str(q.get("quotation_number", "")).lower()
            or q_search in str(q.get("customer_name", "")).lower()
        ]
        st.caption(f"{len(filtered_quotes)} {t('found')}")

        for quote in filtered_quotes[::-1]:
            with st.expander(
                f"{quote.get('quotation_number','')} | "
                f"{quote.get('customer_name','')} | "
                f"{money(quote.get('grand_total',0))} | "
                f"{quote.get('quotation_date','')}"
            ):
                st.write(f"**{t('valid_until')}:** {quote.get('valid_until','')}")
                st.write(f"**{t('address')}:** {quote.get('customer_address','')}")
                st.write(f"**GSTIN:** {quote.get('customer_gstin','')}")
                st.write(f"**{t('taxable_value')}:** {money(quote.get('taxable_value',0))}")
                st.write(f"**{t('grand_total')}:** {money(quote.get('grand_total',0))}")
                for q_item in quote.get("items", []):
                    st.caption(
                        f"{q_item.get('desc','')} — "
                        f"{float(q_item.get('qty',0)):g} × "
                        f"{money(q_item.get('rate',0))}"
                    )
                st.download_button(
                    t("download_pdf"),
                    make_quotation_pdf(quote, current_user),
                    f"{clean_filename(quote.get('quotation_number','quotation'))}.pdf",
                    "application/pdf",
                    key=f"quotation_hist_pdf_{quote.get('id')}",
                    use_container_width=True,
                )

# ============================================================
# PURCHASES / STOCK IN
# ============================================================
elif menu == "purchases":
    st.title(f"📥 {t('record_purchase')}")
    left, right = st.columns(2)
    supplier_map = {s["name"]: s for s in suppliers}

    with left:
        st.subheader(t("suppliers"))
        supplier_choice = st.selectbox(
            t("saved_supplier"),
            [t("manual_supplier")] + list(supplier_map.keys()),
            key="purchase_supplier_choice",
        )
        sdata = supplier_map.get(supplier_choice, {})
        supplier_name = st.text_input(t("supplier_name"), value=sdata.get("name", ""), key="purchase_supplier_name")
        supplier_address = st.text_area(t("supplier_address"), value=sdata.get("address", ""), key="purchase_supplier_address")
        supplier_gstin = st.text_input(t("supplier_gstin"), value=sdata.get("gstin", ""), key="purchase_supplier_gstin")
        sstate0 = sdata.get("state", "Maharashtra") if sdata.get("state", "Maharashtra") in STATES else "Maharashtra"
        supplier_state = st.selectbox(t("supplier_state"), STATES, index=STATES.index(sstate0), format_func=state_label, key="purchase_supplier_state")

    with right:
        st.subheader(t("invoice_details"))
        bill_number = st.text_input(t("supplier_bill_number"))
        pur_date = st.date_input(t("purchase_date"), value=date.today())

    st.markdown("---")
    st.subheader(f"📦 {t('goods_services')}")
    nitems = int(st.number_input(t("number_of_items"), min_value=1, max_value=30, value=1, step=1, key="purchase_nitems"))
    pmap = {p["name"]: p for p in products}
    purchase_items = []

    if not products:
        st.warning(t("no_products"))

    for i in range(nitems):
        st.markdown(f"**{t('item')} {i+1}**")
        choices = list(pmap.keys()) if pmap else ["-"]
        pchoice = st.selectbox(t("saved_product"), choices, key=f"pur_pc_{i}")
        pdata = pmap.get(pchoice, {})
        product_id = int(pdata["id"]) if pdata else None
        invdata = INV_MAP.get(product_id, {}) if product_id else {}

        a, b, c, d, e = st.columns([3, 1.2, 1, 1.3, 1.1])
        with a:
            desc = st.text_input(t("description"), value=pdata.get("name", ""), key=f"pur_desc_{i}")
        with b:
            hsn = st.text_input(t("hsn_sac"), value=pdata.get("hsn", ""), key=f"pur_hsn_{i}")
        with c:
            qty = st.number_input(t("quantity"), min_value=0.01, value=1.0, step=1.0, key=f"pur_qty_{i}")
        with d:
            rate = st.number_input(
                t("purchase_rate"), min_value=0.0,
                value=float(invdata.get("purchase_rate", 0.0) or 0.0),
                step=10.0, key=f"pur_rate_{i}"
            )
        with e:
            opts = [0, 5, 12, 18, 28]
            default_gst = int(pdata.get("gst_rate", 18) or 18) if pdata else 18
            if default_gst not in opts:
                default_gst = 18
            gst = st.selectbox(t("gst_percent"), opts, index=opts.index(default_gst), key=f"pur_gst_{i}")

        purchase_items.append({
            "product_id": product_id,
            "desc": desc,
            "hsn": hsn,
            "qty": float(qty),
            "rate": float(rate),
            "gst_rate": float(gst),
            "amount": float(qty) * float(rate),
        })
        st.markdown("---")

    if st.button(t("save_purchase"), use_container_width=True, type="primary"):
        if not supplier_name.strip():
            st.error(t("supplier_name"))
        elif not bill_number.strip():
            st.error(t("supplier_bill_number"))
        elif not products or any(not x.get("product_id") for x in purchase_items):
            st.error(t("no_products"))
        elif any(p.get("bill_number") == bill_number.strip() for p in purchases):
            st.error(t("purchase_duplicate"))
        else:
            taxable = sum(x["amount"] for x in purchase_items)
            intra = current_user.get("company_state") == supplier_state
            cgst = sgst = igst = 0.0
            for x in purchase_items:
                tax = x["amount"] * x["gst_rate"] / 100.0
                if intra:
                    cgst += tax / 2.0
                    sgst += tax / 2.0
                else:
                    igst += tax
            grand = taxable + cgst + sgst + igst

            try:
                with engine.begin() as con:
                    result = con.execute(insert(purchases_table).values(
                        user_id=USER_ID,
                        bill_number=bill_number.strip(),
                        purchase_date=pur_date.strftime("%d-%m-%Y"),
                        supplier_name=supplier_name.strip(),
                        supplier_address=supplier_address.strip(),
                        supplier_gstin=supplier_gstin.strip(),
                        supplier_state=supplier_state,
                        items_json=json.dumps(purchase_items, ensure_ascii=False),
                        taxable_value=taxable, cgst=cgst, sgst=sgst, igst=igst,
                        grand_total=grand, is_intra_state=intra, created_at=now_naive(),
                    ))
                    purchase_id = int(result.inserted_primary_key[0])
                    for item in purchase_items:
                        pid = int(item["product_id"])
                        invrow = lock_inventory(con, USER_ID, pid)
                        if invrow:
                            con.execute(update(product_inventory_table).where(
                                product_inventory_table.c.id == invrow["id"]
                            ).values(
                                purchase_rate=float(item["rate"]),
                                updated_at=now_naive(),
                            ))
                        change_stock(
                            con, USER_ID, pid, float(item["qty"]),
                            "PURCHASE", "PURCHASE", purchase_id, bill_number.strip(),
                            f"{t('purchase')}: {item.get('desc','')}"
                        )
            except IntegrityError:
                st.error(t("purchase_duplicate"))
                st.stop()

            if supplier_name.strip() and not any(
                s["name"].strip().lower() == supplier_name.strip().lower() for s in suppliers
            ):
                with engine.begin() as con:
                    con.execute(insert(suppliers_table).values(
                        user_id=USER_ID,
                        name=supplier_name.strip(),
                        address=supplier_address.strip(),
                        gstin=supplier_gstin.strip(),
                        phone="", email="", state=supplier_state,
                        created_at=now_naive(),
                    ))

            st.success(t("purchase_saved"))
            a, b, c = st.columns(3)
            a.metric(t("taxable_purchases"), money(taxable))
            b.metric(t("purchase_gst"), money(cgst + sgst + igst))
            c.metric(t("grand_total"), money(grand))
            st.rerun()

# ============================================================
# CUSTOMERS
# ============================================================
elif menu == "customers":
    st.title(f"👥 {t('customers')}")
    with st.expander(f"➕ {t('add_customer')}", expanded=not customers):
        with st.form("customer_form", clear_on_submit=True):
            name = st.text_input(t("customer_name"))
            address = st.text_area(t("customer_address"))
            gstin = st.text_input(t("customer_gstin"))
            state_value = st.selectbox(t("customer_state"), STATES, index=STATES.index("Maharashtra"), format_func=state_label)
            add_customer = st.form_submit_button(t("save_customer"), use_container_width=True)
        if add_customer and name.strip():
            with engine.begin() as con:
                con.execute(insert(customers_table).values(
                    user_id=USER_ID, name=name.strip(), address=address.strip(),
                    gstin=gstin.strip(), state=state_value, created_at=now_naive()
                ))
            st.success(t("customer_saved"))
            st.rerun()

    if not customers:
        st.info(t("no_customers"))

    for customer in customers:
        with st.expander(customer["name"]):
            st.write(f"**{t('address')}:** {customer.get('address','')}")
            st.write(f"**GSTIN:** {customer.get('gstin','')}")
            st.write(f"**{t('state')}:** {state_label(customer.get('state',''))}")
            if st.button(f"🗑️ {t('delete')}", key=f"delc_{customer['id']}"):
                with engine.begin() as con:
                    con.execute(delete(customers_table).where(
                        customers_table.c.id == customer["id"],
                        customers_table.c.user_id == USER_ID,
                    ))
                st.rerun()

# ============================================================
# CUSTOMER LEDGER
# ============================================================
elif menu == "customer_ledger":
    st.title(f"📒 {t('customer_ledger')}")
    total_sales_all = sum(float(inv.get("grand_total", 0) or 0) for inv in invoices)
    total_paid_all = sum(float(p.get("amount", 0) or 0) for p in payments)
    total_outstanding_all = max(0.0, total_sales_all - total_paid_all)

    l1, l2, l3 = st.columns(3)
    l1.metric(t("total_sales"), money(total_sales_all))
    l2.metric(t("total_paid"), money(total_paid_all))
    l3.metric(t("total_outstanding"), money(total_outstanding_all))

    customer_names = sorted({
        str(inv.get("customer_name", "")).strip()
        for inv in invoices if str(inv.get("customer_name", "")).strip()
    }, key=str.lower)

    if not customer_names:
        st.info(t("no_invoices"))
    else:
        search_customer = st.text_input(f"🔎 {t('customer_name')}", key="customer_ledger_search").strip().lower()
        for customer_name in customer_names:
            if search_customer and search_customer not in customer_name.lower():
                continue
            customer_invoices = [
                inv for inv in invoices
                if str(inv.get("customer_name", "")).strip().lower() == customer_name.lower()
            ]
            sales_total = sum(float(inv.get("grand_total", 0) or 0) for inv in customer_invoices)
            paid_total = sum(float(PAID_MAP.get(int(inv.get("id", 0) or 0), 0.0) or 0.0) for inv in customer_invoices)
            balance_total = max(0.0, sales_total - paid_total)

            with st.expander(f"{customer_name} | {t('total_sales')}: {money(sales_total)} | {t('balance_amount')}: {money(balance_total)}"):
                c1, c2, c3 = st.columns(3)
                c1.metric(t("total_sales"), money(sales_total))
                c2.metric(t("total_paid"), money(paid_total))
                c3.metric(t("total_outstanding"), money(balance_total))
                for inv in customer_invoices[::-1]:
                    paid_amount, balance, status_key = payment_status_for_invoice(inv, PAID_MAP)
                    st.write(
                        f"**{inv.get('invoice_number','')}** | {inv.get('invoice_date','')} | "
                        f"{money(inv.get('grand_total',0))} | {t(status_key)} | "
                        f"{t('paid_amount')}: {money(paid_amount)} | {t('balance_amount')}: {money(balance)}"
                    )
                    # ============================================================
# V5.3 - OUTSTANDING / PAYMENT REMINDER
# ============================================================
elif menu == "payment_reminder":
    st.title(f"🔔 {t('payment_reminder')}")

    # --------------------------------------------------------
    # CALCULATE SALES RETURN CREDIT PER INVOICE
    # --------------------------------------------------------
    return_credit_by_invoice = {}

    for ret in sales_returns:
        invoice_id = int(
            ret.get("original_invoice_id", 0) or 0
        )

        return_credit_by_invoice[invoice_id] = (
            return_credit_by_invoice.get(invoice_id, 0.0)
            + float(ret.get("grand_total", 0) or 0)
        )

    # --------------------------------------------------------
    # BUILD CUSTOMER OUTSTANDING DATA
    # --------------------------------------------------------
    outstanding_by_customer = {}

    total_outstanding_all = 0.0
    total_pending_invoices = 0

    for inv in invoices:
        invoice_id = int(inv.get("id", 0) or 0)

        invoice_total = float(
            inv.get("grand_total", 0) or 0
        )

        sales_return_credit = float(
            return_credit_by_invoice.get(
                invoice_id,
                0.0,
            )
            or 0.0
        )

        net_invoice_total = max(
            0.0,
            invoice_total - sales_return_credit,
        )

        paid_amount = float(
            PAID_MAP.get(
                invoice_id,
                0.0,
            )
            or 0.0
        )

        balance_amount = max(
            0.0,
            net_invoice_total - paid_amount,
        )

        if balance_amount <= 0.005:
            continue

        customer_name = str(
            inv.get(
                "customer_name",
                "",
            )
            or ""
        ).strip()

        if not customer_name:
            customer_name = "Customer"

        customer_key = customer_name.lower()

        if customer_key not in outstanding_by_customer:
            outstanding_by_customer[customer_key] = {
                "name": customer_name,
                "total": 0.0,
                "invoices": [],
            }

        outstanding_by_customer[customer_key]["total"] += (
            balance_amount
        )

        outstanding_by_customer[customer_key]["invoices"].append({
            "invoice_number": inv.get(
                "invoice_number",
                "",
            ),
            "invoice_date": inv.get(
                "invoice_date",
                "",
            ),
            "original_total": invoice_total,
            "return_credit": sales_return_credit,
            "net_total": net_invoice_total,
            "paid": paid_amount,
            "balance": balance_amount,
        })

        total_outstanding_all += balance_amount
        total_pending_invoices += 1

    outstanding_customers = list(
        outstanding_by_customer.values()
    )

    outstanding_customers.sort(
        key=lambda row: row["total"],
        reverse=True,
    )

    # --------------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------------
    oc1, oc2, oc3 = st.columns(3)

    oc1.metric(
        t("outstanding_amount"),
        money(total_outstanding_all),
    )

    oc2.metric(
        t("customers_with_outstanding"),
        len(outstanding_customers),
    )

    oc3.metric(
        t("pending_invoices"),
        total_pending_invoices,
    )

    st.markdown("---")

    if not outstanding_customers:
        st.success(t("no_outstanding"))

    else:
        reminder_search = st.text_input(
            f"🔎 {t('customer_name')}",
            key="payment_reminder_search",
        ).strip().lower()

        visible_customers = [
            row
            for row in outstanding_customers
            if not reminder_search
            or reminder_search in row["name"].lower()
        ]

        st.caption(
            f"{len(visible_customers)} "
            f"{t('customers_with_outstanding')}"
        )

        # ----------------------------------------------------
        # REMINDER MESSAGE TEMPLATES
        # ----------------------------------------------------
        def build_reminder_message(
            customer_name,
            balance,
            pending_rows,
        ):
            company_name = str(
                current_user.get(
                    "company_name",
                    "SHIVPRUBA BILLING",
                )
                or "SHIVPRUBA BILLING"
            )

            invoice_lines = []

            for row in pending_rows:
                invoice_lines.append(
                    f"{row['invoice_number']} "
                    f"({row['invoice_date']}) - "
                    f"{money(row['balance'])}"
                )

            invoices_text = "\n".join(
                invoice_lines
            )

            messages = {
                "en": (
                    f"Hello {customer_name},\n\n"
                    f"This is a payment reminder from {company_name}.\n"
                    f"Your outstanding amount is {money(balance)}.\n\n"
                    f"Pending invoices:\n{invoices_text}\n\n"
                    f"Kindly arrange the pending payment at your convenience.\n"
                    f"Thank you."
                ),

                "mr": (
                    f"नमस्कार {customer_name},\n\n"
                    f"{company_name} कडून पेमेंटची आठवण करून देत आहोत.\n"
                    f"आपली बाकी रक्कम {money(balance)} आहे.\n\n"
                    f"बाकी बिले:\n{invoices_text}\n\n"
                    f"कृपया सोयीप्रमाणे बाकी पेमेंट पूर्ण करावे.\n"
                    f"धन्यवाद."
                ),

                "hi": (
                    f"नमस्ते {customer_name},\n\n"
                    f"{company_name} की ओर से भुगतान की याद दिलाई जा रही है।\n"
                    f"आपकी बकाया राशि {money(balance)} है।\n\n"
                    f"बकाया बिल:\n{invoices_text}\n\n"
                    f"कृपया सुविधानुसार बकाया भुगतान कर दें।\n"
                    f"धन्यवाद।"
                ),

                "gu": (
                    f"નમસ્તે {customer_name},\n\n"
                    f"{company_name} તરફથી ચુકવણીની યાદ અપાવવામાં આવે છે.\n"
                    f"તમારી બાકી રકમ {money(balance)} છે.\n\n"
                    f"બાકી બિલ:\n{invoices_text}\n\n"
                    f"કૃપા કરીને અનુકૂળ સમયે બાકી ચુકવણી કરો.\n"
                    f"આભાર."
                ),

                "bn": (
                    f"নমস্কার {customer_name},\n\n"
                    f"{company_name} থেকে পেমেন্টের কথা স্মরণ করিয়ে দেওয়া হচ্ছে।\n"
                    f"আপনার বকেয়া পরিমাণ {money(balance)}।\n\n"
                    f"বকেয়া বিল:\n{invoices_text}\n\n"
                    f"অনুগ্রহ করে সুবিধামতো বকেয়া পরিশোধ করুন।\n"
                    f"ধন্যবাদ।"
                ),

                "ta": (
                    f"வணக்கம் {customer_name},\n\n"
                    f"{company_name} சார்பாக கட்டண நினைவூட்டல்.\n"
                    f"உங்களின் நிலுவை தொகை {money(balance)}.\n\n"
                    f"நிலுவை பில்கள்:\n{invoices_text}\n\n"
                    f"தயவுசெய்து வசதியான நேரத்தில் நிலுவை தொகையை செலுத்தவும்.\n"
                    f"நன்றி."
                ),

                "te": (
                    f"నమస్కారం {customer_name},\n\n"
                    f"{company_name} నుండి చెల్లింపు రిమైండర్.\n"
                    f"మీ బాకీ మొత్తం {money(balance)}.\n\n"
                    f"బాకీ బిల్లులు:\n{invoices_text}\n\n"
                    f"దయచేసి వీలైనప్పుడు బాకీ చెల్లించండి.\n"
                    f"ధన్యవాదాలు."
                ),

                "kn": (
                    f"ನಮಸ್ಕಾರ {customer_name},\n\n"
                    f"{company_name} ವತಿಯಿಂದ ಪಾವತಿ ನೆನಪಿಸುವ ಸಂದೇಶ.\n"
                    f"ನಿಮ್ಮ ಬಾಕಿ ಮೊತ್ತ {money(balance)}.\n\n"
                    f"ಬಾಕಿ ಬಿಲ್ಲುಗಳು:\n{invoices_text}\n\n"
                    f"ದಯವಿಟ್ಟು ಅನುಕೂಲವಾದ ಸಮಯದಲ್ಲಿ ಬಾಕಿ ಪಾವತಿಸಿ.\n"
                    f"ಧನ್ಯವಾದಗಳು."
                ),

                "ml": (
                    f"നമസ്കാരം {customer_name},\n\n"
                    f"{company_name}ൽ നിന്നുള്ള പേയ്മെന്റ് ഓർമ്മപ്പെടുത്തലാണ്.\n"
                    f"നിങ്ങളുടെ കുടിശ്ശിക തുക {money(balance)} ആണ്.\n\n"
                    f"കുടിശ്ശിക ബില്ലുകൾ:\n{invoices_text}\n\n"
                    f"സൗകര്യപ്രദമായ സമയത്ത് കുടിശ്ശിക അടയ്ക്കുക.\n"
                    f"നന്ദി."
                ),

                "pa": (
                    f"ਸਤ ਸ੍ਰੀ ਅਕਾਲ {customer_name},\n\n"
                    f"{company_name} ਵੱਲੋਂ ਭੁਗਤਾਨ ਦੀ ਯਾਦ ਦਿਵਾਈ ਜਾ ਰਹੀ ਹੈ।\n"
                    f"ਤੁਹਾਡੀ ਬਕਾਇਆ ਰਕਮ {money(balance)} ਹੈ।\n\n"
                    f"ਬਕਾਇਆ ਬਿੱਲ:\n{invoices_text}\n\n"
                    f"ਕਿਰਪਾ ਕਰਕੇ ਸੁਵਿਧਾ ਅਨੁਸਾਰ ਬਕਾਇਆ ਭੁਗਤਾਨ ਕਰੋ।\n"
                    f"ਧੰਨਵਾਦ।"
                ),
            }

            return messages.get(
                selected_lang,
                messages["en"],
            )

        # ----------------------------------------------------
        # CUSTOMER-WISE OUTSTANDING
        # ----------------------------------------------------
        for reminder_index, customer in enumerate(
            visible_customers
        ):
            customer_name = customer["name"]
            customer_total = float(
                customer["total"]
                or 0
            )

            pending_rows = customer[
                "invoices"
            ]

            with st.expander(
                f"🔔 {customer_name} | "
                f"{t('outstanding_amount')}: "
                f"{money(customer_total)}"
            ):

                rc1, rc2 = st.columns(2)

                rc1.metric(
                    t("outstanding_amount"),
                    money(customer_total),
                )

                rc2.metric(
                    t("pending_invoices"),
                    len(pending_rows),
                )

                st.markdown(
                    f"**{t('pending_invoices')}**"
                )

                for pending in pending_rows:
                    st.write(
                        f"**{pending['invoice_number']}**"
                        f" | {pending['invoice_date']}"
                        f" | {t('grand_total')}: "
                        f"{money(pending['net_total'])}"
                        f" | {t('paid_amount')}: "
                        f"{money(pending['paid'])}"
                        f" | {t('balance_amount')}: "
                        f"{money(pending['balance'])}"
                    )

                    if (
                        float(
                            pending.get(
                                "return_credit",
                                0,
                            )
                            or 0
                        )
                        > 0.005
                    ):
                        st.caption(
                            f"{t('sales_return_credit')}: "
                            f"{money(pending['return_credit'])}"
                        )

                st.markdown("---")

                reminder_message = (
                    build_reminder_message(
                        customer_name,
                        customer_total,
                        pending_rows,
                    )
                )

                st.markdown(
                    f"**💬 {t('reminder_message')}**"
                )

                st.text_area(
                    t("reminder_message"),
                    value=reminder_message,
                    height=220,
                    key=(
                        "reminder_message_"
                        f"{reminder_index}"
                    ),
                )

                reminder_file_name = re.sub(
                    r"[^A-Za-z0-9_-]+",
                    "_",
                    customer_name,
                ).strip("_")

                if not reminder_file_name:
                    reminder_file_name = (
                        "customer"
                    )

                st.download_button(
                    f"⬇️ {t('download_reminder')}",
                    data=reminder_message.encode(
                        "utf-8"
                    ),
                    file_name=(
                        f"payment_reminder_"
                        f"{reminder_file_name}.txt"
                    ),
                    mime="text/plain",
                    use_container_width=True,
                    key=(
                        "download_reminder_"
                        f"{reminder_index}"
                    ),
                )

# ============================================================
# SUPPLIERS
# ============================================================
elif menu == "suppliers":
    st.title(f"🏭 {t('suppliers')}")
    with st.expander(f"➕ {t('add_supplier')}", expanded=not suppliers):
        with st.form("supplier_form", clear_on_submit=True):
            name = st.text_input(t("supplier_name"))
            address = st.text_area(t("supplier_address"))
            gstin = st.text_input(t("supplier_gstin"))
            phone = st.text_input(t("phone"))
            email = st.text_input(t("email"))
            state_value = st.selectbox(t("supplier_state"), STATES, index=STATES.index("Maharashtra"), format_func=state_label)
            add_supplier = st.form_submit_button(t("save_supplier"), use_container_width=True)
        if add_supplier and name.strip():
            with engine.begin() as con:
                con.execute(insert(suppliers_table).values(
                    user_id=USER_ID, name=name.strip(), address=address.strip(), gstin=gstin.strip(),
                    phone=phone.strip(), email=email.strip(), state=state_value, created_at=now_naive()
                ))
            st.success(t("supplier_saved"))
            st.rerun()

    if not suppliers:
        st.info(t("no_suppliers"))

    for supplier in suppliers:
        purchase_count = sum(
            1 for p in purchases
            if p.get("supplier_name", "").strip().lower() == supplier["name"].strip().lower()
        )
        with st.expander(f"{supplier['name']} | {purchase_count} {t('purchases')}"):
            st.write(f"**{t('address')}:** {supplier.get('address','')}")
            st.write(f"**GSTIN:** {supplier.get('gstin','')}")
            st.write(f"**{t('phone')}:** {supplier.get('phone','')}")
            st.write(f"**{t('email')}:** {supplier.get('email','')}")
            st.write(f"**{t('state')}:** {state_label(supplier.get('state',''))}")
            if purchase_count == 0 and st.button(f"🗑️ {t('delete')}", key=f"dels_{supplier['id']}"):
                with engine.begin() as con:
                    con.execute(delete(suppliers_table).where(
                        suppliers_table.c.id == supplier["id"],
                        suppliers_table.c.user_id == USER_ID,
                    ))
                st.rerun()

# ============================================================
# PRODUCTS
# ============================================================
elif menu == "products":
    st.title(f"📦 {t('products')}")

    with st.expander(f"➕ {t('add_product')}", expanded=not products):
        with st.form("product_form", clear_on_submit=True):
            name = st.text_input(t("product_name"))
            sku = st.text_input(t("sku"))
            hsn = st.text_input(t("hsn_sac"))
            unit = st.selectbox(t("unit"), ["Pcs", "Kg", "Gm", "Ltr", "Ml", "Box", "Pack", "Dozen", "Meter", "Service"], format_func=unit_label)
            purchase_rate = st.number_input(t("purchase_rate"), min_value=0.0, value=0.0, step=10.0)
            selling_rate = st.number_input(t("selling_rate"), min_value=0.0, value=0.0, step=10.0)
            gst = st.selectbox(t("gst_percent"), [0, 5, 12, 18, 28], index=3)
            opening_stock = st.number_input(t("opening_stock"), min_value=0.0, value=0.0, step=1.0)
            low_limit = st.number_input(
                t("low_stock_limit"), min_value=0.0,
                value=float(app_settings.get("default_low_stock", 5.0) or 5.0), step=1.0
            )
            add_product = st.form_submit_button(t("save_product"), use_container_width=True)

        if add_product and name.strip():
            with engine.begin() as con:
                result = con.execute(insert(products_table).values(
                    user_id=USER_ID, name=name.strip(), hsn=hsn.strip(),
                    rate=float(selling_rate), gst_rate=float(gst), created_at=now_naive()
                ))
                pid = int(result.inserted_primary_key[0])
                con.execute(insert(product_inventory_table).values(
                    user_id=USER_ID, product_id=pid, sku=sku.strip(), unit=unit,
                    purchase_rate=float(purchase_rate), opening_stock=float(opening_stock),
                    low_stock_limit=float(low_limit), current_stock=float(opening_stock), updated_at=now_naive()
                ))
                if float(opening_stock) > 0:
                    con.execute(insert(stock_ledger_table).values(
                        user_id=USER_ID, product_id=pid, movement_type="OPENING",
                        qty_change=float(opening_stock), balance_after=float(opening_stock),
                        reference_type="OPENING", reference_id=0, reference_number="OPENING",
                        note=t("opening_stock"), created_at=now_naive()
                    ))
            st.success(t("product_saved"))
            st.rerun()

    if not products:
        st.info(t("no_products"))

    inventory_now = inventory_map(USER_ID)
    for product in products:
        invrow = inventory_now.get(int(product["id"]), {})
        stock_now = float(invrow.get("current_stock", 0) or 0)
        low_limit = float(invrow.get("low_stock_limit", 0) or 0)
        label = product["name"]
        if low_limit > 0 and stock_now <= low_limit and invrow.get("unit") != "Service":
            label += " ⚠️"

        with st.expander(label):
            st.write(
                f"SKU: {invrow.get('sku','')} | HSN/SAC: {product.get('hsn','')} | "
                f"{t('current_stock')}: {stock_now:g} {unit_label(invrow.get('unit','Pcs'))} | "
                f"{t('purchase_rate')}: {money(invrow.get('purchase_rate',0))} | "
                f"{t('selling_rate')}: {money(product.get('rate',0))} | GST {float(product.get('gst_rate',0)):g}%"
            )

            with st.form(f"edit_product_{product['id']}"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    sku2 = st.text_input(t("sku"), value=invrow.get("sku", "") or "", key=f"sku2_{product['id']}")
                    unit_options = ["Pcs", "Kg", "Gm", "Ltr", "Ml", "Box", "Pack", "Dozen", "Meter", "Service"]
                    unit0 = invrow.get("unit", "Pcs") if invrow.get("unit", "Pcs") in unit_options else "Pcs"
                    unit2 = st.selectbox(t("unit"), unit_options, index=unit_options.index(unit0), format_func=unit_label, key=f"unit2_{product['id']}")
                    purchase2 = st.number_input(
                        t("purchase_rate"), min_value=0.0,
                        value=float(invrow.get("purchase_rate", 0) or 0),
                        key=f"pr2_{product['id']}"
                    )
                with ec2:
                    sell2 = st.number_input(
                        t("selling_rate"), min_value=0.0,
                        value=float(product.get("rate", 0) or 0),
                        key=f"sr2_{product['id']}"
                    )
                    gst_opts = [0, 5, 12, 18, 28]
                    g0 = int(product.get("gst_rate", 18) or 18)
                    if g0 not in gst_opts:
                        g0 = 18
                    gst2 = st.selectbox(t("gst_percent"), gst_opts, index=gst_opts.index(g0), key=f"g2_{product['id']}")
                    low2 = st.number_input(
                        t("low_stock_limit"), min_value=0.0,
                        value=float(invrow.get("low_stock_limit", 5) or 0),
                        key=f"low2_{product['id']}"
                    )
                update_product_btn = st.form_submit_button(t("update_product"), use_container_width=True)

            if update_product_btn:
                with engine.begin() as con:
                    con.execute(update(products_table).where(
                        products_table.c.id == product["id"],
                        products_table.c.user_id == USER_ID,
                    ).values(rate=float(sell2), gst_rate=float(gst2)))
                    con.execute(update(product_inventory_table).where(
                        product_inventory_table.c.product_id == product["id"],
                        product_inventory_table.c.user_id == USER_ID,
                    ).values(
                        sku=sku2.strip(), unit=unit2, purchase_rate=float(purchase2),
                        low_stock_limit=float(low2), updated_at=now_naive()
                    ))
                st.success(t("product_updated"))
                st.rerun()

# ============================================================
# STOCK
# ============================================================
elif menu == "stock":
    st.title(f"📊 {t('stock')}")
    product_by_id = {int(p["id"]): p for p in products}
    inv_now = get_inventory(USER_ID)
    total_stock_value = sum(
        float(x.get("current_stock", 0) or 0) * float(x.get("purchase_rate", 0) or 0)
        for x in inv_now
    )
    low_items = [
        x for x in inv_now
        if x.get("unit") != "Service"
        and float(x.get("low_stock_limit", 0) or 0) > 0
        and float(x.get("current_stock", 0) or 0) <= float(x.get("low_stock_limit", 0) or 0)
    ]

    a, b, c = st.columns(3)
    a.metric(t("products"), len(products))
    b.metric(t("stock_value"), money(total_stock_value))
    c.metric(t("low_stock"), len(low_items))

    if products:
        with st.expander(f"🛠️ {t('stock_adjustment')}"):
            pname = st.selectbox(t("product_name"), [p["name"] for p in products], key="adjust_product")
            p = next(x for x in products if x["name"] == pname)
            qty_adj = st.number_input(t("adjustment_qty"), value=0.0, step=1.0)
            reason = st.text_input(t("reason"))
            if st.button(t("apply_adjustment"), use_container_width=True):
                if abs(float(qty_adj)) > 0:
                    try:
                        with engine.begin() as con:
                            change_stock(
                                con, USER_ID, int(p["id"]), float(qty_adj),
                                "ADJUSTMENT", "ADJUSTMENT", 0, "ADJ", reason.strip()
                            )
                        st.success(t("stock_updated"))
                        st.rerun()
                    except ValueError:
                        st.error(t("insufficient_stock"))

    st.subheader(t("current_stock"))
    for invrow in inv_now:
        p = product_by_id.get(int(invrow["product_id"]), {})
        if not p:
            continue
        low = (
            invrow.get("unit") != "Service"
            and float(invrow.get("low_stock_limit", 0) or 0) > 0
            and float(invrow.get("current_stock", 0) or 0) <= float(invrow.get("low_stock_limit", 0) or 0)
        )
        with st.expander(
            f"{'⚠️ ' if low else ''}{p.get('name',t('product'))} — "
            f"{float(invrow.get('current_stock',0)):g} {unit_label(invrow.get('unit',''))}"
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t("current_stock"), f"{float(invrow.get('current_stock',0)):g} {unit_label(invrow.get('unit',''))}")
            c2.metric(t("purchase_rate"), money(invrow.get("purchase_rate",0)))
            c3.metric(t("selling_rate"), money(p.get("rate",0)))
            c4.metric(
                t("stock_value"),
                money(float(invrow.get("current_stock",0) or 0) * float(invrow.get("purchase_rate",0) or 0))
            )

    st.markdown("---")
    st.subheader(t("stock_ledger"))
    ledger = get_stock_ledger(USER_ID)
    for row in ledger[:100]:
        p = product_by_id.get(int(row["product_id"]), {})
        sign = "+" if float(row.get("qty_change", 0)) >= 0 else ""
        movement = row.get("movement_type", "")
        movement_label = {
            "OPENING": t("opening"),
            "PURCHASE": t("purchase"),
            "SALE": t("sale"),
            "ADJUSTMENT": t("adjustment"),
        }.get(movement, movement)
        st.write(
            f"**{p.get('name',t('product'))}** | {movement_label} | "
            f"{sign}{float(row.get('qty_change',0)):g} | {t('balance')} "
            f"{float(row.get('balance_after',0)):g} | {row.get('reference_number','')} | {row.get('note','')}"
        )

# ============================================================
# INVOICE HISTORY + PAYMENTS + EDIT / DELETE
# ============================================================

elif menu == "invoice_history":
    st.title(f"🕘 {t('invoice_history')}")

    if not invoices:
        st.info(t("no_invoices"))

    else:
        search_text = st.text_input(
            f"🔎 {t('search_invoice')}"
        ).strip().lower()

        filtered = invoices if not search_text else [
            inv for inv in invoices
            if search_text in str(inv.get("invoice_number", "")).lower()
            or search_text in str(inv.get("customer_name", "")).lower()
        ]

        st.caption(f"{len(filtered)} {t('found')}")

        for inv in filtered[::-1]:

            paid_amount, balance, status_key = payment_status_for_invoice(
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

                # ------------------------------------------------
                # INVOICE DETAILS
                # ------------------------------------------------

                st.write(
                    f"**{t('address')}:** "
                    f"{inv.get('customer_address', '')}"
                )

                st.write(
                    f"**GSTIN:** "
                    f"{inv.get('customer_gstin', '')}"
                )

                st.write(
                    f"**{t('taxable_value')}:** "
                    f"{money(inv.get('taxable_value', 0))}"
                )

                st.write(
                    f"**{t('grand_total')}:** "
                    f"{money(inv.get('grand_total', 0))}"
                )

                # ------------------------------------------------
                # PAYMENT STATUS
                # ------------------------------------------------

                p1, p2, p3 = st.columns(3)

                p1.metric(
                    t("payment_status"),
                    t(status_key),
                )

                p2.metric(
                    t("paid_amount"),
                    money(paid_amount),
                )

                p3.metric(
                    t("balance_amount"),
                    money(balance),
                )

                # ------------------------------------------------
                # PAYMENT HISTORY
                # ------------------------------------------------

                inv_payments = [
                    p for p in payments
                    if int(p.get("invoice_id", 0) or 0)
                    == int(inv["id"])
                ]

                if inv_payments:

                    st.markdown(
                        f"**{t('payment_history')}**"
                    )

                    for payment in inv_payments[::-1]:

                        pay_col, delete_col = st.columns([5, 1])

                        with pay_col:

                            note_text = (
                                f" | {payment.get('note', '')}"
                                if str(
                                    payment.get("note", "")
                                ).strip()
                                else ""
                            )

                            st.write(
                                f"{payment.get('payment_date', '')}"
                                f" | "
                                f"**{money(payment.get('amount', 0))}**"
                                f"{note_text}"
                            )

                        with delete_col:

                            if st.button(
                                f"🗑️ {t('delete')}",
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
                                            == int(payment["id"]),
                                            payments_table.c.user_id
                                            == USER_ID,
                                            payments_table.c.invoice_id
                                            == int(inv["id"]),
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

                # ------------------------------------------------
                # RECORD PAYMENT
                # ------------------------------------------------

                if balance > 0.005:

                    with st.form(
                        f"payment_form_{inv['id']}"
                    ):

                        st.markdown(
                            f"**💳 {t('record_payment')}**"
                        )

                        payment_amount = st.number_input(
                            t("payment_amount"),
                            min_value=0.01,
                            max_value=float(balance),
                            value=float(balance),
                            step=1.0,
                            key=f"pay_amount_{inv['id']}",
                        )

                        payment_date_value = st.date_input(
                            t("payment_date"),
                            value=date.today(),
                            key=f"pay_date_{inv['id']}",
                        )

                        payment_note = st.text_input(
                            t("payment_note"),
                            key=f"pay_note_{inv['id']}",
                        )

                        save_payment = (
                            st.form_submit_button(
                                t("record_payment"),
                                use_container_width=True,
                                type="primary",
                            )
                        )

                    if save_payment:

                        amount_value = float(
                            payment_amount
                        )

                        date_value = (
                            payment_date_value.strftime(
                                "%d-%m-%Y"
                            )
                        )

                        note_value = (
                            payment_note.strip()
                        )

                        signature = (
                            f"{inv['id']}|"
                            f"{amount_value:.2f}|"
                            f"{date_value}|"
                            f"{note_value}"
                        )

                        now_ts = (
                            datetime.now().timestamp()
                        )

                        last_sig = (
                            st.session_state.get(
                                "_last_payment_signature",
                                "",
                            )
                        )

                        last_ts = float(
                            st.session_state.get(
                                "_last_payment_time",
                                0.0,
                            )
                            or 0.0
                        )

                        if (
                            amount_value
                            > balance + 0.005
                        ):

                            st.error(
                                t("payment_too_high")
                            )

                        elif (
                            signature == last_sig
                            and
                            (now_ts - last_ts) < 5
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
                                        created_at=now_naive(),
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

                # ------------------------------------------------
                # DOWNLOAD PDF
                # ------------------------------------------------

                st.download_button(
                    t("download_pdf"),
                    make_invoice_pdf(
                        inv,
                        current_user,
                    ),
                    (
                        f"{clean_filename(inv['invoice_number'])}"
                        f".pdf"
                    ),
                    "application/pdf",
                    key=f"hist_{inv['id']}",
                    use_container_width=True,
                )

                whatsapp_url = make_whatsapp_invoice_url(
                    inv,
                    current_user,
                )

                st.link_button(
                    "🟢 Share on WhatsApp",
                    whatsapp_url,
                    use_container_width=True,
                )

                st.markdown("---")

                # =================================================
                # EDIT INVOICE
                # =================================================

                with st.expander(
                    f"✏️ {t('edit_record')}"
                ):

                    old_invoice_date = (
                        parse_app_date(
                            inv.get("invoice_date", "")
                        )
                        or date.today()
                    )

                    current_customer_state = (
                        inv.get(
                            "customer_state",
                            "Maharashtra",
                        )
                        or "Maharashtra"
                    )

                    if (
                        current_customer_state
                        not in STATES
                    ):
                        current_customer_state = (
                            "Maharashtra"
                        )

                    current_place_supply = (
                        inv.get(
                            "place_of_supply",
                            current_customer_state,
                        )
                        or current_customer_state
                    )

                    if current_place_supply not in STATES:
                        current_place_supply = (
                            current_customer_state
                        )

                    st.caption(
                        f"{t('invoice_number')}: "
                        f"{inv['invoice_number']}"
                    )

                    with st.form(
                        f"edit_invoice_form_{inv['id']}"
                    ):

                        edit_invoice_date = (
                            st.date_input(
                                t("invoice_date"),
                                value=old_invoice_date,
                                key=(
                                    f"edit_inv_date_"
                                    f"{inv['id']}"
                                ),
                            )
                        )

                        edit_customer_name = (
                            st.text_input(
                                t("customer_name"),
                                value=str(
                                    inv.get(
                                        "customer_name",
                                        "",
                                    )
                                ),
                                key=(
                                    f"edit_inv_name_"
                                    f"{inv['id']}"
                                ),
                            )
                        )

                        edit_customer_address = (
                            st.text_area(
                                t("customer_address"),
                                value=str(
                                    inv.get(
                                        "customer_address",
                                        "",
                                    )
                                ),
                                key=(
                                    f"edit_inv_address_"
                                    f"{inv['id']}"
                                ),
                            )
                        )

                        edit_customer_gstin = (
                            st.text_input(
                                t("customer_gstin"),
                                value=str(
                                    inv.get(
                                        "customer_gstin",
                                        "",
                                    )
                                ),
                                key=(
                                    f"edit_inv_gstin_"
                                    f"{inv['id']}"
                                ),
                            )
                        )

                        edit_customer_state = (
                            st.selectbox(
                                t("customer_state"),
                                STATES,
                                index=STATES.index(
                                    current_customer_state
                                ),
                                format_func=state_label,
                                key=(
                                    f"edit_inv_state_"
                                    f"{inv['id']}"
                                ),
                            )
                        )

                        edit_place_supply = (
                            st.selectbox(
                                t("place_of_supply"),
                                STATES,
                                index=STATES.index(
                                    current_place_supply
                                ),
                                format_func=state_label,
                                key=(
                                    f"edit_inv_supply_"
                                    f"{inv['id']}"
                                ),
                            )
                        )

                        save_invoice_edit = (
                            st.form_submit_button(
                                f"💾 {t('save_changes')}",
                                use_container_width=True,
                                type="primary",
                            )
                        )

                    if save_invoice_edit:

                        if not edit_customer_name.strip():

                            st.error(
                                t("customer_required")
                            )

                        else:

                            # ------------------------------------
                            # Recalculate GST only if place of
                            # supply changes.
                            # Items / quantities are NOT changed.
                            # ------------------------------------

                            invoice_items = list(
                                inv.get("items", [])
                                or []
                            )

                            new_taxable = 0.0
                            new_cgst = 0.0
                            new_sgst = 0.0
                            new_igst = 0.0

                            new_intra = (
                                current_user.get(
                                    "company_state",
                                    "Maharashtra",
                                )
                                == edit_place_supply
                            )

                            for item in invoice_items:

                                qty = float(
                                    item.get(
                                        "qty",
                                        0,
                                    )
                                    or 0
                                )

                                rate = float(
                                    item.get(
                                        "rate",
                                        0,
                                    )
                                    or 0
                                )

                                gst_rate = float(
                                    item.get(
                                        "gst_rate",
                                        0,
                                    )
                                    or 0
                                )

                                item_amount = (
                                    qty * rate
                                )

                                new_taxable += (
                                    item_amount
                                )

                                tax_amount = (
                                    item_amount
                                    * gst_rate
                                    / 100.0
                                )

                                if new_intra:

                                    new_cgst += (
                                        tax_amount / 2
                                    )

                                    new_sgst += (
                                        tax_amount / 2
                                    )

                                else:

                                    new_igst += (
                                        tax_amount
                                    )

                            new_grand_total = (
                                new_taxable
                                + new_cgst
                                + new_sgst
                                + new_igst
                            )

                            # Do not allow edited invoice total
                            # below already received payment.
                            if (
                                new_grand_total
                                + 0.005
                                < paid_amount
                            ):

                                st.error(
                                    t("invoice_paid_total_error")
                                )

                            else:

                                old_data = {
                                    "invoice_number":
                                        inv.get(
                                            "invoice_number",
                                            "",
                                        ),
                                    "invoice_date":
                                        inv.get(
                                            "invoice_date",
                                            "",
                                        ),
                                    "customer_name":
                                        inv.get(
                                            "customer_name",
                                            "",
                                        ),
                                    "customer_address":
                                        inv.get(
                                            "customer_address",
                                            "",
                                        ),
                                    "customer_gstin":
                                        inv.get(
                                            "customer_gstin",
                                            "",
                                        ),
                                    "customer_state":
                                        inv.get(
                                            "customer_state",
                                            "",
                                        ),
                                    "place_of_supply":
                                        inv.get(
                                            "place_of_supply",
                                            "",
                                        ),
                                    "taxable_value":
                                        float(
                                            inv.get(
                                                "taxable_value",
                                                0,
                                            )
                                            or 0
                                        ),
                                    "cgst":
                                        float(
                                            inv.get(
                                                "cgst",
                                                0,
                                            )
                                            or 0
                                        ),
                                    "sgst":
                                        float(
                                            inv.get(
                                                "sgst",
                                                0,
                                            )
                                            or 0
                                        ),
                                    "igst":
                                        float(
                                            inv.get(
                                                "igst",
                                                0,
                                            )
                                            or 0
                                        ),
                                    "grand_total":
                                        float(
                                            inv.get(
                                                "grand_total",
                                                0,
                                            )
                                            or 0
                                        ),
                                }

                                new_data = {
                                    "invoice_number":
                                        inv.get(
                                            "invoice_number",
                                            "",
                                        ),
                                    "invoice_date":
                                        edit_invoice_date.strftime(
                                            "%d-%m-%Y"
                                        ),
                                    "customer_name":
                                        edit_customer_name.strip(),
                                    "customer_address":
                                        edit_customer_address.strip(),
                                    "customer_gstin":
                                        edit_customer_gstin.strip(),
                                    "customer_state":
                                        edit_customer_state,
                                    "place_of_supply":
                                        edit_place_supply,
                                    "taxable_value":
                                        float(
                                            new_taxable
                                        ),
                                    "cgst":
                                        float(
                                            new_cgst
                                        ),
                                    "sgst":
                                        float(
                                            new_sgst
                                        ),
                                    "igst":
                                        float(
                                            new_igst
                                        ),
                                    "grand_total":
                                        float(
                                            new_grand_total
                                        ),
                                }

                                with engine.begin() as con:

                                    con.execute(
                                        update(
                                            invoices_table
                                        )
                                        .where(
                                            invoices_table.c.id
                                            == int(
                                                inv["id"]
                                            ),
                                            invoices_table.c.user_id
                                            == USER_ID,
                                        )
                                        .values(
                                            invoice_date=(
                                                edit_invoice_date.strftime(
                                                    "%d-%m-%Y"
                                                )
                                            ),
                                            customer_name=(
                                                edit_customer_name.strip()
                                            ),
                                            customer_address=(
                                                edit_customer_address.strip()
                                            ),
                                            customer_gstin=(
                                                edit_customer_gstin.strip()
                                            ),
                                            customer_state=(
                                                edit_customer_state
                                            ),
                                            place_of_supply=(
                                                edit_place_supply
                                            ),
                                            taxable_value=(
                                                float(
                                                    new_taxable
                                                )
                                            ),
                                            cgst=float(
                                                new_cgst
                                            ),
                                            sgst=float(
                                                new_sgst
                                            ),
                                            igst=float(
                                                new_igst
                                            ),
                                            grand_total=float(
                                                new_grand_total
                                            ),
                                            is_intra_state=(
                                                new_intra
                                            ),
                                        )
                                    )

                                    log_change(
                                        con,
                                        user_id=USER_ID,
                                        record_type="INVOICE",
                                        record_id=int(
                                            inv["id"]
                                        ),
                                        record_number=str(
                                            inv.get(
                                                "invoice_number",
                                                "",
                                            )
                                        ),
                                        action="EDIT",
                                        old_data=old_data,
                                        new_data=new_data,
                                    )

                                st.success(
                                    t("invoice_updated")
                                )

                                st.rerun()

                # =================================================
                # DELETE INVOICE
                # =================================================

                with st.expander(
                    f"🗑️ {t('delete_record')}"
                ):

                    related_sales_returns = [
                        r
                        for r in globals().get(
                            "sales_returns",
                            [],
                        )
                        if int(
                            r.get(
                                "original_invoice_id",
                                0,
                            )
                            or 0
                        )
                        == int(inv["id"])
                    ]

                    if related_sales_returns:

                        st.warning(
                            t("invoice_has_sales_return")
                        )

                    else:

                        confirm_invoice_delete = (
                            st.checkbox(
                                t("confirm_delete"),
                                key=(
                                    f"confirm_invoice_delete_"
                                    f"{inv['id']}"
                                ),
                            )
                        )

                        if st.button(
                            f"🗑️ {t('delete_record')}",
                            key=(
                                f"delete_invoice_"
                                f"{inv['id']}"
                            ),
                            use_container_width=True,
                            disabled=(
                                not confirm_invoice_delete
                            ),
                        ):

                            delete_old_data = {
                                "invoice_number":
                                    inv.get(
                                        "invoice_number",
                                        "",
                                    ),
                                "invoice_date":
                                    inv.get(
                                        "invoice_date",
                                        "",
                                    ),
                                "customer_name":
                                    inv.get(
                                        "customer_name",
                                        "",
                                    ),
                                "customer_address":
                                    inv.get(
                                        "customer_address",
                                        "",
                                    ),
                                "customer_gstin":
                                    inv.get(
                                        "customer_gstin",
                                        "",
                                    ),
                                "customer_state":
                                    inv.get(
                                        "customer_state",
                                        "",
                                    ),
                                "place_of_supply":
                                    inv.get(
                                        "place_of_supply",
                                        "",
                                    ),
                                "taxable_value":
                                    float(
                                        inv.get(
                                            "taxable_value",
                                            0,
                                        )
                                        or 0
                                    ),
                                "cgst":
                                    float(
                                        inv.get(
                                            "cgst",
                                            0,
                                        )
                                        or 0
                                    ),
                                "sgst":
                                    float(
                                        inv.get(
                                            "sgst",
                                            0,
                                        )
                                        or 0
                                    ),
                                "igst":
                                    float(
                                        inv.get(
                                            "igst",
                                            0,
                                        )
                                        or 0
                                    ),
                                "grand_total":
                                    float(
                                        inv.get(
                                            "grand_total",
                                            0,
                                        )
                                        or 0
                                    ),
                                "items":
                                    list(
                                        inv.get(
                                            "items",
                                            [],
                                        )
                                        or []
                                    ),
                                "paid_amount":
                                    float(
                                        paid_amount
                                    ),
                            }

                            try:

                                with engine.begin() as con:

                                    # -----------------------------
                                    # Return sold stock
                                    # -----------------------------

                                    for item in (
                                        inv.get(
                                            "items",
                                            [],
                                        )
                                        or []
                                    ):

                                        product_id = (
                                            item.get(
                                                "product_id"
                                            )
                                        )

                                        track_stock = bool(
                                            item.get(
                                                "track_stock"
                                            )
                                        )

                                        qty = float(
                                            item.get(
                                                "qty",
                                                0,
                                            )
                                            or 0
                                        )

                                        if (
                                            product_id
                                            and
                                            track_stock
                                            and
                                            qty > 0
                                        ):

                                            change_stock(
                                                con,
                                                USER_ID,
                                                int(
                                                    product_id
                                                ),
                                                qty,
                                                "INVOICE_DELETE",
                                                "INVOICE",
                                                int(
                                                    inv["id"]
                                                ),
                                                str(
                                                    inv.get(
                                                        "invoice_number",
                                                        "",
                                                    )
                                                ),
                                                (
                                                    "Stock returned "
                                                    "because invoice "
                                                    "was deleted"
                                                ),
                                            )

                                    # -----------------------------
                                    # Log delete BEFORE deleting
                                    # invoice
                                    # -----------------------------

                                    log_change(
                                        con,
                                        user_id=USER_ID,
                                        record_type="INVOICE",
                                        record_id=int(
                                            inv["id"]
                                        ),
                                        record_number=str(
                                            inv.get(
                                                "invoice_number",
                                                "",
                                            )
                                        ),
                                        action="DELETE",
                                        old_data=(
                                            delete_old_data
                                        ),
                                        new_data={},
                                    )

                                    # -----------------------------
                                    # Delete payments first
                                    # -----------------------------

                                    con.execute(
                                        delete(
                                            payments_table
                                        ).where(
                                            payments_table.c.user_id
                                            == USER_ID,
                                            payments_table.c.invoice_id
                                            == int(
                                                inv["id"]
                                            ),
                                        )
                                    )

                                    # -----------------------------
                                    # Delete invoice
                                    # -----------------------------

                                    con.execute(
                                        delete(
                                            invoices_table
                                        ).where(
                                            invoices_table.c.id
                                            == int(
                                                inv["id"]
                                            ),
                                            invoices_table.c.user_id
                                            == USER_ID,
                                        )
                                    )

                                st.success(
                                    t("invoice_deleted")
                                )

                                st.rerun()

                            except Exception as exc:

                                st.error(
                                    f"{t('invoice_delete_failed')}: {exc}"
                                )


# ============================================================
# PURCHASE HISTORY
# ============================================================

# ============================================================
# PURCHASE HISTORY
# ============================================================
elif menu == "purchase_history":
    st.title(f"📚 {t('purchase_history')}")
    if not purchases:
        st.info(t("no_purchases"))
    else:
        search_text = st.text_input(f"🔎 {t('search')}", key="purchase_search").strip().lower()
        filtered = purchases if not search_text else [
            p for p in purchases
            if search_text in p.get("bill_number", "").lower()
            or search_text in p.get("supplier_name", "").lower()
        ]
        st.caption(f"{len(filtered)} {t('found')}")
        for pur in filtered[::-1]:
            with st.expander(
                f"{pur['bill_number']} | {pur['supplier_name']} | {money(pur['grand_total'])} | {pur['purchase_date']}"
            ):
                st.write(f"**{t('address')}:** {pur.get('supplier_address','')}")
                st.write(f"**GSTIN:** {pur.get('supplier_gstin','')}")
                st.write(f"**{t('taxable_purchases')}:** {money(pur.get('taxable_value',0))}")
                purchase_tax = (
                    float(pur.get("cgst", 0) or 0)
                    + float(pur.get("sgst", 0) or 0)
                    + float(pur.get("igst", 0) or 0)
                )
                st.write(f"**{t('purchase_gst')}:** {money(purchase_tax)}")
                st.write(f"**{t('grand_total')}:** {money(pur.get('grand_total',0))}")
                for item in pur.get("items", []):
                    st.caption(
                        f"{item.get('desc','')} — {float(item.get('qty',0)):g} × {money(item.get('rate',0))}"
                    )
                    # ============================================================
# SALES RETURN
# ============================================================
elif menu == "sales_return":
    st.title(f"↩️ {t('sales_return')}")

    if not invoices:
        st.info(t("no_invoices"))
    else:
        invoice_map = {
            f"{inv.get('invoice_number','')} | {inv.get('customer_name','')} | {money(inv.get('grand_total',0))}": inv
            for inv in invoices
        }

        selected_label = st.selectbox(
            t("invoice_number"),
            list(invoice_map.keys()),
            key="sales_return_invoice",
        )

        selected_invoice = invoice_map[selected_label]
        selected_invoice_id = int(selected_invoice["id"])

        st.write(f"**{t('customer_name')}:** {selected_invoice.get('customer_name','')}")
        st.write(f"**{t('date')}:** {selected_invoice.get('invoice_date','')}")
        st.write(f"**{t('grand_total')}:** {money(selected_invoice.get('grand_total',0))}")

        st.markdown("---")

        return_date = st.date_input(
            t("date"),
            value=date.today(),
            key="sales_return_date",
        )

        reason = st.text_input(
            t("reason"),
            key="sales_return_reason",
        )

        previous_returns = [
            r for r in sales_returns
            if int(r.get("original_invoice_id", 0) or 0) == selected_invoice_id
        ]

        return_items = []

        for idx, item in enumerate(selected_invoice.get("items", [])):
            desc = item.get("desc", "")
            sold_qty = float(item.get("qty", 0) or 0)
            rate = float(item.get("rate", 0) or 0)
            gst_rate = float(item.get("gst_rate", 0) or 0)
            product_id = item.get("product_id")

            already_returned = 0.0

            for old_return in previous_returns:
                for old_item in old_return.get("items", []):
                    old_product_id = old_item.get("product_id")
                    old_desc = str(old_item.get("desc", "")).strip().lower()
                    old_rate = float(old_item.get("rate", 0) or 0)
                    old_gst_rate = float(old_item.get("gst_rate", 0) or 0)

                    same_product = (
                        product_id is not None
                        and old_product_id is not None
                        and str(product_id) == str(old_product_id)
                        and old_desc == str(desc).strip().lower()
                        and abs(old_rate - rate) < 0.0001
                        and abs(old_gst_rate - gst_rate) < 0.0001
                    )

                    same_non_product_item = (
                        product_id is None
                        and old_product_id is None
                        and old_desc == str(desc).strip().lower()
                        and abs(old_rate - rate) < 0.0001
                        and abs(old_gst_rate - gst_rate) < 0.0001
                    )

                    if same_product or same_non_product_item:
                        already_returned += float(old_item.get("qty", 0) or 0)

            remaining_qty = max(0.0, sold_qty - already_returned)

            st.write(f"**{desc}**")
            st.caption(
                f"{t('quantity')}: {sold_qty:g}  |  ↩ {already_returned:g}  |  ✓ {remaining_qty:g}"
            )

            qty_return = st.number_input(
                f"{t('quantity')} - {desc}",
                min_value=0.0,
                max_value=float(remaining_qty),
                value=0.0,
                step=1.0,
                key=f"sales_return_qty_{selected_invoice['id']}_{idx}",
                disabled=remaining_qty <= 0,
            )

            if qty_return > 0:
                return_items.append({
                    "product_id": product_id,
                    "track_stock": item.get("track_stock", False),
                    "desc": desc,
                    "hsn": item.get("hsn", ""),
                    "qty": float(qty_return),
                    "rate": rate,
                    "gst_rate": gst_rate,
                    "amount": float(qty_return) * rate,
                })

        st.markdown("---")

        if st.button(
            t("sales_return"),
            use_container_width=True,
            type="primary",
            key="save_sales_return",
        ):
            if not return_items:
                st.warning(t("return_quantity_required"))
            else:
                return_signature = json.dumps(
                    {
                        "invoice_id": selected_invoice_id,
                        "return_date": return_date.strftime("%d-%m-%Y"),
                        "reason": reason.strip(),
                        "items": [
                            {
                                "product_id": x.get("product_id"),
                                "desc": x.get("desc", ""),
                                "qty": float(x.get("qty", 0) or 0),
                                "rate": float(x.get("rate", 0) or 0),
                            }
                            for x in return_items
                        ],
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                )

                now_ts = datetime.now().timestamp()
                last_signature = st.session_state.get("_last_sales_return_signature")
                last_time = float(
                    st.session_state.get("_last_sales_return_time", 0.0) or 0.0
                )

                if (
                    last_signature == return_signature
                    and (now_ts - last_time) < 5
                ):
                    st.warning(
                        t("return_recently_saved")
                    )
                else:
                    taxable = sum(x["amount"] for x in return_items)

                    intra = bool(
                        selected_invoice.get("is_intra_state", True)
                    )
                    cgst = sgst = igst = 0.0

                    for x in return_items:
                        tax = x["amount"] * x["gst_rate"] / 100.0

                        if intra:
                            cgst += tax / 2.0
                            sgst += tax / 2.0
                        else:
                            igst += tax

                    grand = taxable + cgst + sgst + igst

                    existing_numbers = {
                        str(r.get("return_number", ""))
                        for r in sales_returns
                    }

                    seq = len(sales_returns) + 1

                    while True:
                        return_number = (
                            f"SR-{selected_invoice.get('invoice_number','')}-{seq}"
                        )

                        if return_number not in existing_numbers:
                            break

                        seq += 1

                    try:
                        with engine.begin() as con:
                            result = con.execute(
                                insert(sales_returns_table).values(
                                    user_id=USER_ID,
                                    original_invoice_id=selected_invoice_id,
                                    original_invoice_number=selected_invoice.get(
                                        "invoice_number", ""
                                    ),
                                    return_number=return_number,
                                    return_date=return_date.strftime("%d-%m-%Y"),
                                    customer_name=selected_invoice.get(
                                        "customer_name", ""
                                    ),
                                    reason=reason.strip(),
                                    items_json=json.dumps(
                                        return_items,
                                        ensure_ascii=False,
                                    ),
                                    taxable_value=taxable,
                                    cgst=cgst,
                                    sgst=sgst,
                                    igst=igst,
                                    grand_total=grand,
                                    created_at=now_naive(),
                                )
                            )

                            return_id = int(
                                result.inserted_primary_key[0]
                            )

                            for item in return_items:
                                if (
                                    item.get("product_id")
                                    and item.get("track_stock")
                                ):
                                    change_stock(
                                        con,
                                        USER_ID,
                                        int(item["product_id"]),
                                        float(item["qty"]),
                                        "SALES_RETURN",
                                        "SALES_RETURN",
                                        return_id,
                                        return_number,
                                        f"Sales Return: {item.get('desc','')}",
                                    )

                        st.session_state[
                            "_last_sales_return_signature"
                        ] = return_signature

                        st.session_state[
                            "_last_sales_return_time"
                        ] = datetime.now().timestamp()

                        st.success(
                            f"{t('sales_return_saved')}: {return_number}"
                        )
                        st.rerun()

                    except IntegrityError:
                        st.error(
                            t("sales_return_exists")
                        )

# ============================================================
# PURCHASE RETURN
# ============================================================
elif menu == "purchase_return":
    st.title(f"🔄 {t('purchase_return')}")

    if not purchases:
        st.info(t("no_purchases"))
    else:
        purchase_map = {
            f"{pur.get('bill_number','')} | {pur.get('supplier_name','')} | {money(pur.get('grand_total',0))}": pur
            for pur in purchases
        }

        selected_purchase_label = st.selectbox(
            t("supplier_bill_number"),
            list(purchase_map.keys()),
            key="purchase_return_purchase",
        )

        selected_purchase = purchase_map[selected_purchase_label]
        selected_purchase_id = int(selected_purchase["id"])

        st.write(
            f"**{t('supplier_name')}:** "
            f"{selected_purchase.get('supplier_name','')}"
        )
        st.write(
            f"**{t('purchase_date')}:** "
            f"{selected_purchase.get('purchase_date','')}"
        )
        st.write(
            f"**{t('grand_total')}:** "
            f"{money(selected_purchase.get('grand_total',0))}"
        )

        st.markdown("---")

        return_date = st.date_input(
            t("date"),
            value=date.today(),
            key="purchase_return_date",
        )

        reason = st.text_input(
            t("reason"),
            key="purchase_return_reason",
        )

        previous_purchase_returns = [
            r for r in purchase_returns
            if int(r.get("original_purchase_id", 0) or 0)
            == selected_purchase_id
        ]

        return_items = []

        for idx, item in enumerate(selected_purchase.get("items", [])):
            desc = item.get("desc", "")
            purchased_qty = float(item.get("qty", 0) or 0)
            rate = float(item.get("rate", 0) or 0)
            gst_rate = float(item.get("gst_rate", 0) or 0)
            product_id = item.get("product_id")

            already_returned = 0.0

            for old_return in previous_purchase_returns:
                for old_item in old_return.get("items", []):
                    old_product_id = old_item.get("product_id")
                    old_desc = str(
                        old_item.get("desc", "")
                    ).strip().lower()
                    old_rate = float(
                        old_item.get("rate", 0) or 0
                    )
                    old_gst_rate = float(
                        old_item.get("gst_rate", 0) or 0
                    )

                    same_product = (
                        product_id is not None
                        and old_product_id is not None
                        and str(product_id) == str(old_product_id)
                        and old_desc == str(desc).strip().lower()
                        and abs(old_rate - rate) < 0.0001
                        and abs(old_gst_rate - gst_rate) < 0.0001
                    )

                    same_non_product_item = (
                        product_id is None
                        and old_product_id is None
                        and old_desc == str(desc).strip().lower()
                        and abs(old_rate - rate) < 0.0001
                        and abs(old_gst_rate - gst_rate) < 0.0001
                    )

                    if same_product or same_non_product_item:
                        already_returned += float(
                            old_item.get("qty", 0) or 0
                        )

            remaining_qty = max(
                0.0,
                purchased_qty - already_returned,
            )

            available_stock = remaining_qty

            if product_id is not None:
                try:
                    available_stock = float(
                        INV_MAP.get(
                            int(product_id),
                            {},
                        ).get("current_stock", 0) or 0
                    )
                except Exception:
                    available_stock = 0.0

            max_return_qty = min(
                remaining_qty,
                max(0.0, available_stock),
            )

            st.write(f"**{desc}**")
            st.caption(
                f"{t('quantity')}: {purchased_qty:g}"
                f"  |  ↩ {already_returned:g}"
                f"  |  ✓ {remaining_qty:g}"
                f"  |  📦 {t('current_stock')}: {available_stock:g}"
            )

            qty_return = st.number_input(
                f"{t('quantity')} - {desc}",
                min_value=0.0,
                max_value=float(max_return_qty),
                value=0.0,
                step=1.0,
                key=(
                    f"purchase_return_qty_"
                    f"{selected_purchase['id']}_{idx}"
                ),
                disabled=max_return_qty <= 0,
            )

            if qty_return > 0:
                return_items.append({
                    "product_id": product_id,
                    "desc": desc,
                    "hsn": item.get("hsn", ""),
                    "qty": float(qty_return),
                    "rate": rate,
                    "gst_rate": gst_rate,
                    "amount": float(qty_return) * rate,
                })

        st.markdown("---")

        if st.button(
            t("purchase_return"),
            use_container_width=True,
            type="primary",
            key="save_purchase_return",
        ):
            if not return_items:
                st.warning(t("return_quantity_required"))
            else:
                return_signature = json.dumps(
                    {
                        "purchase_id": selected_purchase_id,
                        "return_date": return_date.strftime(
                            "%d-%m-%Y"
                        ),
                        "reason": reason.strip(),
                        "items": [
                            {
                                "product_id": x.get("product_id"),
                                "desc": x.get("desc", ""),
                                "qty": float(
                                    x.get("qty", 0) or 0
                                ),
                                "rate": float(
                                    x.get("rate", 0) or 0
                                ),
                            }
                            for x in return_items
                        ],
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                )

                now_ts = datetime.now().timestamp()
                last_signature = st.session_state.get(
                    "_last_purchase_return_signature"
                )
                last_time = float(
                    st.session_state.get(
                        "_last_purchase_return_time",
                        0.0,
                    ) or 0.0
                )

                if (
                    last_signature == return_signature
                    and (now_ts - last_time) < 5
                ):
                    st.warning(t("return_recently_saved"))
                else:
                    taxable = sum(
                        x["amount"] for x in return_items
                    )

                    intra = bool(
                        selected_purchase.get(
                            "is_intra_state",
                            True,
                        )
                    )

                    cgst = sgst = igst = 0.0

                    for x in return_items:
                        tax = (
                            x["amount"]
                            * x["gst_rate"]
                            / 100.0
                        )

                        if intra:
                            cgst += tax / 2.0
                            sgst += tax / 2.0
                        else:
                            igst += tax

                    grand = taxable + cgst + sgst + igst

                    existing_numbers = {
                        str(r.get("return_number", ""))
                        for r in purchase_returns
                    }

                    seq = len(purchase_returns) + 1
                    while True:
                        return_number = (
                            f"PR-"
                            f"{selected_purchase.get('bill_number', '')}-"
                            f"{seq}"
                        )

                        if return_number not in existing_numbers:
                            break

                        seq += 1

                    try:
                        with engine.begin() as con:
                            result = con.execute(
                                insert(
                                    purchase_returns_table
                                ).values(
                                    user_id=USER_ID,
                                    original_purchase_id=(
                                        selected_purchase_id
                                    ),
                                    original_bill_number=(
                                        selected_purchase.get(
                                            "bill_number",
                                            "",
                                        )
                                    ),
                                    return_number=return_number,
                                    return_date=(
                                        return_date.strftime(
                                            "%d-%m-%Y"
                                        )
                                    ),
                                    supplier_name=(
                                        selected_purchase.get(
                                            "supplier_name",
                                            "",
                                        )
                                    ),
                                    reason=reason.strip(),
                                    items_json=json.dumps(
                                        return_items,
                                        ensure_ascii=False,
                                    ),
                                    taxable_value=taxable,
                                    cgst=cgst,
                                    sgst=sgst,
                                    igst=igst,
                                    grand_total=grand,
                                    created_at=now_naive(),
                                )
                            )

                            return_id = int(
                                result.inserted_primary_key[0]
                            )

                            for item in return_items:
                                if item.get("product_id"):
                                    change_stock(
                                        con,
                                        USER_ID,
                                        int(item["product_id"]),
                                        -float(item["qty"]),
                                        "PURCHASE_RETURN",
                                        "PURCHASE_RETURN",
                                        return_id,
                                        return_number,
                                        (
                                            f"{t('purchase_return')}: "
                                            f"{item.get('desc','')}"
                                        ),
                                    )

                        st.session_state[
                            "_last_purchase_return_signature"
                        ] = return_signature

                        st.session_state[
                            "_last_purchase_return_time"
                        ] = datetime.now().timestamp()

                        st.success(
                            f"{t('purchase_return_saved')}: "
                            f"{return_number}"
                        )
                        st.rerun()

                    except IntegrityError:
                        st.error(
                            t("purchase_return_exists")
                        )

                    except ValueError as exc:
                        if str(exc) == "INSUFFICIENT_STOCK":
                            st.error(t("insufficient_stock"))
                        else:
                            raise
                        # ============================================================
# EXPENSES - ADD + EDIT + DELETE + HISTORY
# ============================================================
elif menu == "expenses":
    st.title(f"💸 {t('expenses')}")

    expense_date = st.date_input(
        t("expense_date"),
        value=date.today(),
        key="expense_date_input",
    )

    expense_category = st.text_input(
        t("expense_category"),
        key="expense_category_input",
    )

    expense_amount = st.number_input(
        t("expense_amount"),
        min_value=0.0,
        value=0.0,
        step=1.0,
        key="expense_amount_input",
    )

    expense_note = st.text_area(
        t("expense_note"),
        key="expense_note_input",
    )

    if st.button(
        f"💾 {t('save_expense')}",
        type="primary",
        use_container_width=True,
        key="save_expense_button",
    ):
        if float(expense_amount) <= 0:
            st.warning(t("expense_amount_required"))

        else:
            with engine.begin() as con:
                con.execute(
                    insert(expenses_table).values(
                        user_id=USER_ID,
                        expense_date=expense_date.strftime("%d-%m-%Y"),
                        category=expense_category.strip(),
                        amount=float(expense_amount),
                        note=expense_note.strip(),
                        created_at=now_naive(),
                    )
                )

            st.success(t("expense_saved"))
            st.rerun()

    st.markdown("---")
    st.subheader(f"📋 {t('expense_history')}")

    with engine.connect() as con:
        expense_rows = [
            row_dict(r)
            for r in con.execute(
                select(expenses_table)
                .where(
                    expenses_table.c.user_id == USER_ID
                )
                .order_by(
                    expenses_table.c.id.desc()
                )
            ).all()
        ]

    if not expense_rows:
        st.info(t("no_expenses"))

    else:
        for exp in expense_rows:

            exp_id = int(exp["id"])

            category_text = (
                exp.get("category", "")
                or "-"
            )

            note_text = (
                exp.get("note", "")
                or "-"
            )

            amount_value = float(
                exp.get("amount", 0)
                or 0
            )

            with st.expander(
                f"{exp.get('expense_date', '')} | "
                f"{category_text} | "
                f"{money(amount_value)}"
            ):

                st.write(
                    f"**{t('expense_date')}:** "
                    f"{exp.get('expense_date', '')}"
                )

                st.write(
                    f"**{t('expense_category')}:** "
                    f"{category_text}"
                )

                st.write(
                    f"**{t('expense_amount')}:** "
                    f"{money(amount_value)}"
                )

                st.write(
                    f"**{t('expense_note')}:** "
                    f"{note_text}"
                )

                st.markdown("---")

                # --------------------------------------------
                # EDIT EXPENSE
                # --------------------------------------------
                with st.expander(
                    f"✏️ {t('edit_record')}"
                ):
                    old_expense_date = parse_app_date(
                        exp.get("expense_date")
                    )

                    if old_expense_date is None:
                        old_expense_date = date.today()

                    with st.form(
                        f"edit_expense_form_{exp_id}"
                    ):
                        edit_date = st.date_input(
                            t("expense_date"),
                            value=old_expense_date,
                            key=f"edit_expense_date_{exp_id}",
                        )

                        edit_category = st.text_input(
                            t("expense_category"),
                            value=exp.get(
                                "category",
                                "",
                            )
                            or "",
                            key=f"edit_expense_category_{exp_id}",
                        )

                        edit_amount = st.number_input(
                            t("expense_amount"),
                            min_value=0.01,
                            value=float(
                                exp.get(
                                    "amount",
                                    0,
                                )
                                or 0
                            ),
                            step=1.0,
                            key=f"edit_expense_amount_{exp_id}",
                        )

                        edit_note = st.text_area(
                            t("expense_note"),
                            value=exp.get(
                                "note",
                                "",
                            )
                            or "",
                            key=f"edit_expense_note_{exp_id}",
                        )

                        save_edit = st.form_submit_button(
                            f"💾 {t('edit_record')}",
                            use_container_width=True,
                            type="primary",
                        )

                    if save_edit:

                        old_data = {
                            "expense_date": exp.get(
                                "expense_date",
                                "",
                            ),
                            "category": exp.get(
                                "category",
                                "",
                            ),
                            "amount": float(
                                exp.get(
                                    "amount",
                                    0,
                                )
                                or 0
                            ),
                            "note": exp.get(
                                "note",
                                "",
                            ),
                        }

                        new_data = {
                            "expense_date": edit_date.strftime(
                                "%d-%m-%Y"
                            ),
                            "category": edit_category.strip(),
                            "amount": float(
                                edit_amount
                            ),
                            "note": edit_note.strip(),
                        }

                        with engine.begin() as con:

                            con.execute(
                                update(expenses_table)
                                .where(
                                    expenses_table.c.id
                                    == exp_id,
                                    expenses_table.c.user_id
                                    == USER_ID,
                                )
                                .values(
                                    expense_date=new_data[
                                        "expense_date"
                                    ],
                                    category=new_data[
                                        "category"
                                    ],
                                    amount=new_data[
                                        "amount"
                                    ],
                                    note=new_data[
                                        "note"
                                    ],
                                )
                            )

                            log_change(
                                con=con,
                                user_id=USER_ID,
                                record_type="EXPENSE",
                                record_id=exp_id,
                                record_number=(
                                    f"EXP-{exp_id}"
                                ),
                                action="EDIT",
                                old_data=old_data,
                                new_data=new_data,
                            )

                        st.success(
                            t("expense_updated")
                        )

                        st.rerun()

                # --------------------------------------------
                # DELETE EXPENSE
                # --------------------------------------------
                with st.expander(
                    f"🗑️ {t('delete_record')}"
                ):

                    confirm_delete = st.checkbox(
                        t("confirm_delete"),
                        key=(
                            f"confirm_delete_expense_"
                            f"{exp_id}"
                        ),
                    )

                    if st.button(
                        f"🗑️ {t('delete_record')}",
                        key=(
                            f"delete_expense_"
                            f"{exp_id}"
                        ),
                        use_container_width=True,
                    ):

                        if not confirm_delete:
                            st.warning(
                                t("confirm_delete")
                            )

                        else:
                            old_data = {
                                "expense_date": exp.get(
                                    "expense_date",
                                    "",
                                ),
                                "category": exp.get(
                                    "category",
                                    "",
                                ),
                                "amount": float(
                                    exp.get(
                                        "amount",
                                        0,
                                    )
                                    or 0
                                ),
                                "note": exp.get(
                                    "note",
                                    "",
                                ),
                            }

                            with engine.begin() as con:

                                log_change(
                                    con=con,
                                    user_id=USER_ID,
                                    record_type="EXPENSE",
                                    record_id=exp_id,
                                    record_number=(
                                        f"EXP-{exp_id}"
                                    ),
                                    action="DELETE",
                                    old_data=old_data,
                                    new_data={},
                                )

                                con.execute(
                                    delete(
                                        expenses_table
                                    ).where(
                                        expenses_table.c.id
                                        == exp_id,
                                        expenses_table.c.user_id
                                        == USER_ID,
                                    )
                                )

                            st.success(
                                t("expense_deleted")
                            )

                            st.rerun()
                            # ============================================================
# EDIT / DELETE HISTORY
# ============================================================
elif menu == "edit_delete_history":
    st.title(
        f"📝 {t('edit_delete_history')}"
    )

    history_rows = get_change_history(
        USER_ID
    )

    total_changes = len(
        history_rows
    )

    edit_count = sum(
        1
        for row in history_rows
        if row.get("action") == "EDIT"
    )

    delete_count = sum(
        1
        for row in history_rows
        if row.get("action") == "DELETE"
    )

    h1, h2, h3 = st.columns(3)

    h1.metric(
        t("change_history"),
        total_changes,
    )

    h2.metric(
        t("edited"),
        edit_count,
    )

    h3.metric(
        t("deleted"),
        delete_count,
    )

    st.markdown("---")

    if not history_rows:
        st.info(
            t("no_change_history")
        )

    else:
        history_search = st.text_input(
            f"🔎 {t('search')}",
            key="change_history_search",
        ).strip().lower()

        visible_history = []

        for row in history_rows:
            search_value = (
                f"{row.get('record_type', '')} "
                f"{row.get('record_number', '')} "
                f"{row.get('action', '')}"
            ).lower()

            if (
                not history_search
                or history_search
                in search_value
            ):
                visible_history.append(
                    row
                )

        st.caption(
            f"{len(visible_history)} "
            f"{t('found')}"
        )

        for row in visible_history:

            action = str(
                row.get(
                    "action",
                    "",
                )
            )

            action_icon = (
                "✏️"
                if action == "EDIT"
                else "🗑️"
            )

            created_at = row.get(
                "created_at",
                "",
            )

            with st.expander(
                f"{action_icon} "
                f"{row.get('record_type', '')}"
                f" | "
                f"{row.get('record_number', '')}"
                f" | "
                f"{created_at}"
            ):

                st.write(
                    f"**{t('record_type')}:** "
                    f"{row.get('record_type', '')}"
                )

                st.write(
                    f"**{t('action')}:** "
                    f"{action}"
                )

                # ============================================================
                # CLEAN PROFESSIONAL CHANGE DISPLAY
                # ============================================================

                old_data = row.get("old_data") or {}
                new_data = row.get("new_data") or {}

                field_labels = {
                    "invoice_number": "Invoice Number",
                    "invoice_date": "Invoice Date",
                    "customer_name": "Customer Name",
                    "customer_address": "Address",
                    "customer_gstin": "Customer GSTIN",
                    "customer_state": "Customer State",
                    "place_of_supply": "Place of Supply",
                    "taxable_value": "Taxable Value",
                    "cgst": "CGST",
                    "sgst": "SGST",
                    "igst": "IGST",
                    "grand_total": "Grand Total",

                    "expense_date": "Expense Date",
                    "category": "Category",
                    "amount": "Amount",
                    "note": "Note",

                    "supplier_name": "Supplier Name",
                    "supplier_address": "Supplier Address",
                    "supplier_gstin": "Supplier GSTIN",
                    "purchase_date": "Purchase Date",
                    "purchase_number": "Purchase Number",

                    "product_name": "Product Name",
                    "description": "Description",
                    "hsn_sac": "HSN / SAC",
                    "quantity": "Quantity",
                    "rate": "Rate",
                    "gst_percent": "GST %",
                    "items": "Items",
"paid_amount": "Paid Amount",
                }

                money_fields = {
                    "taxable_value",
                    "cgst",
                    "sgst",
                    "igst",
                    "grand_total",
                    "amount",
                    "rate",
                    "paid_amount",
                }

                def clean_field_name(key):
                    return field_labels.get(
                        key,
                        str(key).replace("_", " ").title()
                    )

                def clean_value(key, value):
                    if key == "items" and isinstance(value, list):
                        item_lines = []

                        for index, item in enumerate(value, start=1):
                            if isinstance(item, dict):
                                description = (
    item.get("product_name")
    or item.get("desc")
    or item.get("description")
    or item.get("name")
    or "-"
)

                                qty = item.get("qty", 0)
                                rate = item.get("rate", 0)
                                gst_rate = item.get("gst_rate", 0)
                                amount = item.get("amount", 0)

                                item_lines.append(
                                    f"Item {index}: {description} | "
                                    f"Qty: {qty} | "
                                    f"Rate: ₹ {float(rate):,.2f} | "
                                    f"GST: {gst_rate}% | "
                                    f"Amount: ₹ {float(amount):,.2f}"
                                )

                        return "  \n".join(item_lines)
                    if value is None or value == "":
                        return "-"

                    if key in money_fields:
                        try:
                            return f"₹ {float(value):,.2f}"
                        except (TypeError, ValueError):
                            return str(value)

                    if isinstance(value, float):
                        return f"{value:,.2f}"

                    return str(value)

                action_value = str(
                    row.get("action", "")
                ).upper()

                # ---------------- EDIT HISTORY ----------------
                if action_value == "EDIT":

                    changed_keys = []

                    all_keys = list(
                        dict.fromkeys(
                            list(old_data.keys()) +
                            list(new_data.keys())
                        )
                    )

                    for key in all_keys:
                        old_value = old_data.get(key)
                        new_value = new_data.get(key)

                        if old_value != new_value:
                            changed_keys.append(key)

                    if changed_keys:
                        st.markdown(f"### ✏️ {t('change_history')}")

                        for key in changed_keys:
                            label = clean_field_name(key)

                            old_value = clean_value(
                                key,
                                old_data.get(key)
                            )

                            new_value = clean_value(
                                key,
                                new_data.get(key)
                            )

                            st.markdown(
                                f"**{label}:** "
                                f"`{old_value}` → `{new_value}`"
                            )

                    else:
                        st.info(
                            t("no_visible_changes")
                        )

                # ---------------- DELETE HISTORY ----------------
                elif action_value == "DELETE":

                    st.markdown(
                        f"### 🗑️ {t('delete_record')}"
                    )

                    if old_data:
                        for key, value in old_data.items():
                            label = clean_field_name(key)
                            display_value = clean_value(
                                key,
                                value
                            )

                            st.markdown(
                                f"**{label}:** {display_value}"
                            )

                    else:
                        st.info(
                            t("no_previous_record")
                        )

                # ---------------- OTHER ACTION ----------------
                else:

                    if old_data:
                        st.markdown(
                            f"### {t('old_data')}"
                        )

                        for key, value in old_data.items():
                            label = clean_field_name(key)
                            display_value = clean_value(
                                key,
                                value
                            )

                            st.markdown(
                                f"**{label}:** {display_value}"
                            )

                    if new_data:
                        st.markdown(
                            f"### {t('new_data')}"
                        )

                        for key, value in new_data.items():
                            label = clean_field_name(key)
                            display_value = clean_value(
                                key,
                                value
                            )

                            st.markdown(
                                f"**{label}:** {display_value}"
                            )

# ============================================================
# REPORTS
# ============================================================
elif menu == "reports":
    st.title(f"📈 {t('reports')}")

    r1, r2 = st.columns(2)
    with r1:
        date_from = st.date_input(t("from_date"), value=date.today().replace(day=1), key="report_from")
    with r2:
        date_to = st.date_input(t("to_date"), value=date.today(), key="report_to")

    filtered_invoices = []
    for i in invoices:
        d = parse_app_date(i.get("invoice_date"))
        if d is None or (date_from <= d <= date_to):
            filtered_invoices.append(i)

    filtered_purchases = []
    for p in purchases:
        d = parse_app_date(p.get("purchase_date"))
        if d is None or (date_from <= d <= date_to):
            filtered_purchases.append(p)

    taxable = sum(float(i.get("taxable_value", 0) or 0) for i in filtered_invoices)
    cgst_total = sum(float(i.get("cgst", 0) or 0) for i in filtered_invoices)
    sgst_total = sum(float(i.get("sgst", 0) or 0) for i in filtered_invoices)
    igst_total = sum(float(i.get("igst", 0) or 0) for i in filtered_invoices)
    total = sum(float(i.get("grand_total", 0) or 0) for i in filtered_invoices)

    purchase_taxable = sum(float(p.get("taxable_value", 0) or 0) for p in filtered_purchases)
    purchase_gst = sum(
        float(p.get("cgst", 0) or 0) + float(p.get("sgst", 0) or 0) + float(p.get("igst", 0) or 0)
        for p in filtered_purchases
    )
    purchase_total = sum(float(p.get("grand_total", 0) or 0) for p in filtered_purchases)
    with engine.begin() as con:
        report_expenses = con.execute(
            select(expenses_table)
            .where(expenses_table.c.user_id == USER_ID)
        ).mappings().all()

    filtered_expenses = []
    for e in report_expenses:
        d = parse_app_date(e.get("expense_date"))
        if d is None or (date_from <= d <= date_to):
            filtered_expenses.append(e)

    expense_total = sum(
        float(e.get("amount", 0) or 0)
        for e in filtered_expenses
    )

    filtered_sales_returns = []
    for r in sales_returns:
        d = parse_app_date(r.get("return_date"))
        if d is not None and date_from <= d <= date_to:
            filtered_sales_returns.append(r)

    filtered_purchase_returns = []
    for r in purchase_returns:
        d = parse_app_date(r.get("return_date"))
        if d is not None and date_from <= d <= date_to:
            filtered_purchase_returns.append(r)

    sales_return_taxable = sum(
        float(r.get("taxable_value", 0) or 0)
        for r in filtered_sales_returns
    )

    sales_return_cgst = sum(
        float(r.get("cgst", 0) or 0)
        for r in filtered_sales_returns
    )

    sales_return_sgst = sum(
        float(r.get("sgst", 0) or 0)
        for r in filtered_sales_returns
    )

    sales_return_igst = sum(
        float(r.get("igst", 0) or 0)
        for r in filtered_sales_returns
    )

    sales_return_total = sum(
        float(r.get("grand_total", 0) or 0)
        for r in filtered_sales_returns
    )

    purchase_return_taxable = sum(
        float(r.get("taxable_value", 0) or 0)
        for r in filtered_purchase_returns
    )

    purchase_return_cgst = sum(
        float(r.get("cgst", 0) or 0)
        for r in filtered_purchase_returns
    )

    purchase_return_sgst = sum(
        float(r.get("sgst", 0) or 0)
        for r in filtered_purchase_returns
    )

    purchase_return_igst = sum(
        float(r.get("igst", 0) or 0)
        for r in filtered_purchase_returns
    )

    purchase_return_total = sum(
        float(r.get("grand_total", 0) or 0)
        for r in filtered_purchase_returns
    )

    net_taxable_sales = taxable - sales_return_taxable
    net_cgst = cgst_total - sales_return_cgst
    net_sgst = sgst_total - sales_return_sgst
    net_igst = igst_total - sales_return_igst
    net_total_sales = total - sales_return_total

    net_purchase_taxable = purchase_taxable - purchase_return_taxable
    net_purchase_gst = purchase_gst - (
        purchase_return_cgst
        + purchase_return_sgst
        + purchase_return_igst
    )
    net_purchase_total = purchase_total - purchase_return_total

    estimated_profit_loss = (
        net_total_sales
        - net_purchase_total
        - expense_total
    )

    st.subheader(t("sales_summary"))
    a, b, c = st.columns(3)
    a.metric(t("taxable_sales"), money(net_taxable_sales))
    b.metric(t("total_gst"), money(net_cgst + net_sgst + net_igst))
    c.metric(t("total_sales"), money(net_total_sales))

    d, e, f = st.columns(3)
    d.metric(t("cgst"), money(net_cgst))
    e.metric(t("sgst"), money(net_sgst))
    f.metric(t("igst"), money(net_igst))

    st.subheader(t("purchase_summary"))
    p1, p2, p3 = st.columns(3)
    p1.metric(t("taxable_purchases"), money(net_purchase_taxable))
    p2.metric(t("purchase_gst"), money(net_purchase_gst))
    p3.metric(t("total_purchases"), money(net_purchase_total))

    e1, e2 = st.columns(2)
    e1.metric(t("total_expenses"), money(expense_total))
    e2.metric(t("estimated_profit_loss"), money(estimated_profit_loss))
    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(t("customer_sales"))
        customer_totals = {}

        for inv in filtered_invoices:
            name = inv.get("customer_name", "")
            customer_totals[name] = (
                customer_totals.get(name, 0.0)
                + float(inv.get("grand_total", 0) or 0)
            )

        for r in filtered_sales_returns:
            name = r.get("customer_name", "")
            customer_totals[name] = (
                customer_totals.get(name, 0.0)
                - float(r.get("grand_total", 0) or 0)
            )

        for name, value in sorted(
            customer_totals.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )[:20]:
            st.write(f"{name}: **{money(value)}**")

    with c2:
        st.subheader(t("supplier_purchases"))
        supplier_totals = {}

        for pur in filtered_purchases:
            name = pur.get("supplier_name", "")
            supplier_totals[name] = (
                supplier_totals.get(name, 0.0)
                + float(pur.get("grand_total", 0) or 0)
            )

        for r in filtered_purchase_returns:
            name = r.get("supplier_name", "")
            supplier_totals[name] = (
                supplier_totals.get(name, 0.0)
                - float(r.get("grand_total", 0) or 0)
            )

        for name, value in sorted(
            supplier_totals.items(),
            key=lambda kv: kv[1],
            reverse=True,
        )[:20]:
            st.write(f"{name}: **{money(value)}**")

    st.subheader(t("product_sales"))
    product_totals = {}

    for inv in filtered_invoices:
        for item in inv.get("items", []):
            name = item.get("desc", "")
            product_totals[name] = (
                product_totals.get(name, 0.0)
                + float(item.get("amount", 0) or 0)
            )

    for r in filtered_sales_returns:
        for item in r.get("items", []):
            name = item.get("desc", "")
            product_totals[name] = (
                product_totals.get(name, 0.0)
                - float(item.get("amount", 0) or 0)
            )

    for name, value in sorted(
        product_totals.items(),
        key=lambda kv: kv[1],
        reverse=True,
    )[:30]:
        st.write(f"{name}: **{money(value)}**")
        # ============================================================
    # V5.3 - EXCEL / CSV EXPORT
    # ============================================================
    st.markdown("---")
    st.subheader(f"📤 {t('export_excel_csv')}")

    st.caption(
        f"{t('export_data_from')} "
        f"{date_from.strftime('%d-%m-%Y')} {t('export_to')} "
        f"{date_to.strftime('%d-%m-%Y')}"
    )

    import csv
    import zipfile

    # ------------------------------------------------------------
    # SALES DATA
    # ------------------------------------------------------------
    sales_headers = [
        "Invoice Number",
        "Date",
        "Customer",
        "Customer GSTIN",
        "Place of Supply",
        "Items",
        "Taxable Value",
        "CGST",
        "SGST",
        "IGST",
        "Grand Total",
        "Paid Amount",
        "Balance Amount",
        "Payment Status",
    ]

    sales_rows = []

    for inv in filtered_invoices:
        item_texts = []

        for item in inv.get("items", []):
            item_texts.append(
                f"{item.get('desc', '')} "
                f"x {float(item.get('qty', 0) or 0):g} "
                f"@ {float(item.get('rate', 0) or 0):.2f}"
            )

        paid_amount, balance_amount, status_key = (
            payment_status_for_invoice(
                inv,
                PAID_MAP,
            )
        )

        sales_rows.append([
            inv.get("invoice_number", ""),
            inv.get("invoice_date", ""),
            inv.get("customer_name", ""),
            inv.get("customer_gstin", ""),
            inv.get("place_of_supply", ""),
            "; ".join(item_texts),

            float(
                inv.get(
                    "taxable_value",
                    0,
                )
                or 0
            ),

            float(
                inv.get(
                    "cgst",
                    0,
                )
                or 0
            ),

            float(
                inv.get(
                    "sgst",
                    0,
                )
                or 0
            ),

            float(
                inv.get(
                    "igst",
                    0,
                )
                or 0
            ),

            float(
                inv.get(
                    "grand_total",
                    0,
                )
                or 0
            ),

            float(
                paid_amount
                or 0
            ),

            float(
                balance_amount
                or 0
            ),

            t(status_key),
        ])

    # ------------------------------------------------------------
    # PURCHASE DATA
    # ------------------------------------------------------------
    purchase_headers = [
        "Supplier Bill Number",
        "Date",
        "Supplier",
        "Supplier GSTIN",
        "Items",
        "Taxable Value",
        "CGST",
        "SGST",
        "IGST",
        "Grand Total",
    ]

    purchase_rows = []

    for pur in filtered_purchases:
        item_texts = []

        for item in pur.get("items", []):
            item_texts.append(
                f"{item.get('desc', '')} "
                f"x {float(item.get('qty', 0) or 0):g} "
                f"@ {float(item.get('rate', 0) or 0):.2f}"
            )

        purchase_rows.append([
            pur.get("bill_number", ""),
            pur.get("purchase_date", ""),
            pur.get("supplier_name", ""),
            pur.get("supplier_gstin", ""),
            "; ".join(item_texts),

            float(
                pur.get(
                    "taxable_value",
                    0,
                )
                or 0
            ),

            float(
                pur.get(
                    "cgst",
                    0,
                )
                or 0
            ),

            float(
                pur.get(
                    "sgst",
                    0,
                )
                or 0
            ),

            float(
                pur.get(
                    "igst",
                    0,
                )
                or 0
            ),

            float(
                pur.get(
                    "grand_total",
                    0,
                )
                or 0
            ),
        ])

    # ------------------------------------------------------------
    # EXPENSE DATA
    # ------------------------------------------------------------
    expense_headers = [
        "Date",
        "Category",
        "Amount",
        "Note",
    ]

    expense_rows_export = []

    for exp in filtered_expenses:
        expense_rows_export.append([
            exp.get(
                "expense_date",
                "",
            ),

            exp.get(
                "category",
                "",
            ),

            float(
                exp.get(
                    "amount",
                    0,
                )
                or 0
            ),

            exp.get(
                "note",
                "",
            ),
        ])

    # ------------------------------------------------------------
    # CUSTOMER LEDGER DATA
    # ------------------------------------------------------------
    ledger_headers = [
        "Customer",
        "Invoice Number",
        "Invoice Date",
        "Invoice Total",
        "Paid Amount",
        "Balance Amount",
        "Payment Status",
    ]

    ledger_rows_export = []

    for inv in filtered_invoices:
        paid_amount, balance_amount, status_key = (
            payment_status_for_invoice(
                inv,
                PAID_MAP,
            )
        )

        ledger_rows_export.append([
            inv.get(
                "customer_name",
                "",
            ),

            inv.get(
                "invoice_number",
                "",
            ),

            inv.get(
                "invoice_date",
                "",
            ),

            float(
                inv.get(
                    "grand_total",
                    0,
                )
                or 0
            ),

            float(
                paid_amount
                or 0
            ),

            float(
                balance_amount
                or 0
            ),

            t(status_key),
        ])

    # ------------------------------------------------------------
    # SALES RETURN DATA
    # ------------------------------------------------------------
    sales_return_headers = [
        "Return Number",
        "Return Date",
        "Original Invoice",
        "Customer",
        "Reason",
        "Taxable Value",
        "CGST",
        "SGST",
        "IGST",
        "Grand Total",
    ]

    sales_return_rows_export = []

    for row in filtered_sales_returns:
        sales_return_rows_export.append([
            row.get(
                "return_number",
                "",
            ),

            row.get(
                "return_date",
                "",
            ),

            row.get(
                "original_invoice_number",
                "",
            ),

            row.get(
                "customer_name",
                "",
            ),

            row.get(
                "reason",
                "",
            ),

            float(
                row.get(
                    "taxable_value",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "cgst",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "sgst",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "igst",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "grand_total",
                    0,
                )
                or 0
            ),
        ])

    # ------------------------------------------------------------
    # PURCHASE RETURN DATA
    # ------------------------------------------------------------
    purchase_return_headers = [
        "Return Number",
        "Return Date",
        "Original Bill",
        "Supplier",
        "Reason",
        "Taxable Value",
        "CGST",
        "SGST",
        "IGST",
        "Grand Total",
    ]

    purchase_return_rows_export = []

    for row in filtered_purchase_returns:
        purchase_return_rows_export.append([
            row.get(
                "return_number",
                "",
            ),

            row.get(
                "return_date",
                "",
            ),

            row.get(
                "original_bill_number",
                "",
            ),

            row.get(
                "supplier_name",
                "",
            ),

            row.get(
                "reason",
                "",
            ),

            float(
                row.get(
                    "taxable_value",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "cgst",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "sgst",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "igst",
                    0,
                )
                or 0
            ),

            float(
                row.get(
                    "grand_total",
                    0,
                )
                or 0
            ),
        ])

    # ------------------------------------------------------------
    # REPORT SUMMARY
    # ------------------------------------------------------------
    report_headers = [
        "Report",
        "Value",
    ]

    report_rows_export = [
        [
            "Company",
            current_user.get(
                "company_name",
                "",
            ),
        ],

        [
            "From Date",
            date_from.strftime(
                "%d-%m-%Y"
            ),
        ],

        [
            "To Date",
            date_to.strftime(
                "%d-%m-%Y"
            ),
        ],

        [
            "Taxable Sales",
            float(
                net_taxable_sales
                or 0
            ),
        ],

        [
            "Sales GST",
            float(
                net_cgst
                + net_sgst
                + net_igst
            ),
        ],

        [
            "Net Sales",
            float(
                net_total_sales
                or 0
            ),
        ],

        [
            "Taxable Purchases",
            float(
                net_purchase_taxable
                or 0
            ),
        ],

        [
            "Purchase GST",
            float(
                net_purchase_gst
                or 0
            ),
        ],

        [
            "Net Purchases",
            float(
                net_purchase_total
                or 0
            ),
        ],

        [
            "Sales Returns",
            float(
                sales_return_total
                or 0
            ),
        ],

        [
            "Purchase Returns",
            float(
                purchase_return_total
                or 0
            ),
        ],

        [
            "Total Expenses",
            float(
                expense_total
                or 0
            ),
        ],

        [
            "Estimated Profit / Loss",
            float(
                estimated_profit_loss
                or 0
            ),
        ],
    ]

    # ------------------------------------------------------------
    # CSV FUNCTION
    # ------------------------------------------------------------
    def make_csv_bytes(
        headers,
        rows,
    ):
        text_buffer = io.StringIO()

        writer = csv.writer(
            text_buffer
        )

        writer.writerow(
            headers
        )

        writer.writerows(
            rows
        )

        return (
            text_buffer
            .getvalue()
            .encode(
                "utf-8-sig"
            )
        )

    # ------------------------------------------------------------
    # CREATE CSV ZIP
    # ------------------------------------------------------------
    csv_zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        csv_zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as csv_zip:

        csv_zip.writestr(
            "sales.csv",
            make_csv_bytes(
                sales_headers,
                sales_rows,
            ),
        )

        csv_zip.writestr(
            "purchases.csv",
            make_csv_bytes(
                purchase_headers,
                purchase_rows,
            ),
        )

        csv_zip.writestr(
            "expenses.csv",
            make_csv_bytes(
                expense_headers,
                expense_rows_export,
            ),
        )

        csv_zip.writestr(
            "customer_ledger.csv",
            make_csv_bytes(
                ledger_headers,
                ledger_rows_export,
            ),
        )

        csv_zip.writestr(
            "sales_returns.csv",
            make_csv_bytes(
                sales_return_headers,
                sales_return_rows_export,
            ),
        )

        csv_zip.writestr(
            "purchase_returns.csv",
            make_csv_bytes(
                purchase_return_headers,
                purchase_return_rows_export,
            ),
        )

        csv_zip.writestr(
            "report_summary.csv",
            make_csv_bytes(
                report_headers,
                report_rows_export,
            ),
        )

    csv_zip_buffer.seek(0)

    # ------------------------------------------------------------
    # CREATE EXCEL WORKBOOK
    # ------------------------------------------------------------
    excel_bytes = None
    excel_error = None

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font

        excel_buffer = io.BytesIO()

        workbook = Workbook()

        default_sheet = workbook.active
        workbook.remove(
            default_sheet
        )

        def add_excel_sheet(
            sheet_name,
            headers,
            rows,
        ):
            worksheet = workbook.create_sheet(
                title=sheet_name
            )

            worksheet.append(
                headers
            )

            for cell in worksheet[1]:
                cell.font = Font(
                    bold=True
                )

            for row in rows:
                worksheet.append(
                    row
                )

            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = (
                worksheet.dimensions
            )

            for column_cells in worksheet.columns:
                max_length = 0

                column_letter = (
                    column_cells[0]
                    .column_letter
                )

                for cell in column_cells:
                    try:
                        cell_length = len(
                            str(
                                cell.value
                                if cell.value is not None
                                else ""
                            )
                        )

                        if cell_length > max_length:
                            max_length = (
                                cell_length
                            )

                    except Exception:
                        pass

                worksheet.column_dimensions[
                    column_letter
                ].width = min(
                    max(
                        max_length + 2,
                        12,
                    ),
                    45,
                )

        add_excel_sheet(
            "Report Summary",
            report_headers,
            report_rows_export,
        )

        add_excel_sheet(
            "Sales",
            sales_headers,
            sales_rows,
        )

        add_excel_sheet(
            "Purchases",
            purchase_headers,
            purchase_rows,
        )

        add_excel_sheet(
            "Expenses",
            expense_headers,
            expense_rows_export,
        )

        add_excel_sheet(
            "Customer Ledger",
            ledger_headers,
            ledger_rows_export,
        )

        add_excel_sheet(
            "Sales Returns",
            sales_return_headers,
            sales_return_rows_export,
        )

        add_excel_sheet(
            "Purchase Returns",
            purchase_return_headers,
            purchase_return_rows_export,
        )

        workbook.save(
            excel_buffer
        )

        excel_buffer.seek(0)

        excel_bytes = (
            excel_buffer.getvalue()
        )

    except Exception as exc:
        excel_error = str(exc)

    # ------------------------------------------------------------
    # DOWNLOAD BUTTONS
    # ------------------------------------------------------------
    export_col1, export_col2 = st.columns(2)

    with export_col1:

        if excel_bytes is not None:
            st.download_button(
                f"📊 {t('download_excel')}",
                data=excel_bytes,
                file_name=(
                    "shivpruba_billing_report_"
                    f"{date_from.strftime('%Y%m%d')}_"
                    f"{date_to.strftime('%Y%m%d')}.xlsx"
                ),
                mime=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
                key="download_excel_report",
            )

        else:
            st.warning(
                f"{t('excel_export_failed')}: {excel_error}"
            )

    with export_col2:

        st.download_button(
            f"📁 {t('download_csv_files')}",
            data=csv_zip_buffer.getvalue(),
            file_name=(
                "shivpruba_billing_csv_"
                f"{date_from.strftime('%Y%m%d')}_"
                f"{date_to.strftime('%Y%m%d')}.zip"
            ),
            mime="application/zip",
            use_container_width=True,
            key="download_csv_report",
        )
# ============================================================
# SETTINGS + BACKUP
# ============================================================
elif menu == "settings":
    st.title(f"⚙️ {t('settings')}")
    st.subheader(t("company_profile"))

    with st.form("settings_form"):
        company_name = st.text_input(t("company_name"), value=current_user.get("company_name") or "")
        company_address = st.text_area(t("address"), value=current_user.get("company_address") or "")
        company_gstin = st.text_input(t("gstin"), value=current_user.get("company_gstin") or "")
        company_phone = st.text_input(t("phone"), value=current_user.get("company_phone") or "")
        company_email = st.text_input(t("email"), value=current_user.get("company_email") or "")
        state0 = current_user.get("company_state") if current_user.get("company_state") in STATES else "Maharashtra"
        company_state = st.selectbox(t("state"), STATES, index=STATES.index(state0), format_func=state_label)
        invoice_prefix = st.text_input(t("invoice_prefix"), value=app_settings.get("invoice_prefix") or "INV")
        default_low_stock = st.number_input(
            t("default_low_stock"), min_value=0.0,
            value=float(app_settings.get("default_low_stock", 5.0) or 5.0), step=1.0
        )
        save_settings = st.form_submit_button(t("save_settings"), use_container_width=True, type="primary")

    if save_settings:
        with engine.begin() as con:
            con.execute(update(users).where(users.c.id == USER_ID).values(
                company_name=company_name.strip(), company_address=company_address.strip(),
                company_gstin=company_gstin.strip(), company_phone=company_phone.strip(),
                company_email=company_email.strip(), company_state=company_state,
                preferred_language=selected_lang,
            ))
            con.execute(update(user_settings_table).where(
                user_settings_table.c.user_id == USER_ID
            ).values(
                invoice_prefix=invoice_prefix.strip() or "INV",
                default_low_stock=float(default_low_stock),
                updated_at=now_naive(),
            ))
        st.success(t("settings_saved"))
        st.rerun()

     # ============================================================
    # V5.3 - BACKUP + RESTORE
    # ============================================================
    st.markdown("---")
    st.subheader(f"💾 {t('backup')}")
    st.caption(t("backup_help"))

    # ------------------------------------------------------------
    # LOAD EXPENSES FOR BACKUP
    # ------------------------------------------------------------
    with engine.connect() as con:
        backup_expenses = [
            dict(row)
            for row in con.execute(
                select(expenses_table)
                .where(expenses_table.c.user_id == USER_ID)
                .order_by(expenses_table.c.id)
            ).mappings().all()
        ]

    # ------------------------------------------------------------
    # CREATE COMPLETE BACKUP
    # ------------------------------------------------------------
    backup_data = {
        "backup_format": "SHIVPRUBA_BILLING_V1",
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "generated_at": now_naive().isoformat(),
        "language": selected_lang,

        "business": {
            key: current_user.get(key)
            for key in [
                "company_name",
                "company_address",
                "company_gstin",
                "company_phone",
                "company_email",
                "company_state",
            ]
        },

        "app_settings": {
            "invoice_prefix": app_settings.get("invoice_prefix", "INV"),
            "default_low_stock": float(
                app_settings.get("default_low_stock", 5.0) or 5.0
            ),
        },

        "customers": customers,
        "suppliers": suppliers,
        "products": products,
        "inventory": get_inventory(USER_ID),

        "purchases": purchases,
        "purchase_returns": purchase_returns,

        "invoices": invoices,
        "sales_returns": sales_returns,

        "quotations": quotations,

        "payments": get_payments(USER_ID),
        "expenses": backup_expenses,

        "stock_ledger": get_stock_ledger(USER_ID),
    }

    st.download_button(
        "⬇️ " + t("download_backup"),
        json.dumps(
            backup_data,
            ensure_ascii=False,
            indent=2,
            default=str,
        ).encode("utf-8"),
        f"shivpruba_billing_backup_{date.today().strftime('%Y%m%d')}.json",
        "application/json",
        use_container_width=True,
        key="download_complete_backup",
    )

    st.caption(
        t("backup_keep_safe")
    )

    # ------------------------------------------------------------
    # RESTORE BACKUP
    # ------------------------------------------------------------
    st.markdown("---")
    st.subheader(f"♻️ {t('restore_backup')}")

    st.info(
        t("restore_help")
    )

    uploaded_backup = st.file_uploader(
        t("upload_backup_file"),
        type=["json"],
        key="restore_backup_file",
    )

    restore_data = None
    restore_valid = False

    if uploaded_backup is not None:
        try:
            raw_backup = uploaded_backup.getvalue().decode("utf-8-sig")
            restore_data = json.loads(raw_backup)

            if not isinstance(restore_data, dict):
                raise ValueError("Invalid backup structure.")

            required_sections = [
                "business",
                "customers",
                "products",
                "inventory",
                "purchases",
                "invoices",
            ]

            missing_sections = [
                section
                for section in required_sections
                if section not in restore_data
            ]

            if missing_sections:
                st.error(
                    f"{t('invalid_backup_missing')}: " + ", ".join(missing_sections)
                )
            else:
                restore_valid = True

                st.success(t("backup_valid"))

                r1, r2, r3 = st.columns(3)

                r1.metric(
                    t("customers"),
                    len(restore_data.get("customers", [])),
                )

                r2.metric(
                    t("products"),
                    len(restore_data.get("products", [])),
                )

                r3.metric(
                    t("invoices"),
                    len(restore_data.get("invoices", [])),
                )

                r4, r5, r6 = st.columns(3)

                r4.metric(
                    t("purchases"),
                    len(restore_data.get("purchases", [])),
                )

                r5.metric(
                    t("quotation"),
                    len(restore_data.get("quotations", [])),
                )

                r6.metric(
                    t("expenses"),
                    len(restore_data.get("expenses", [])),
                )

        except Exception as exc:
            restore_valid = False
            st.error(f"{t('backup_read_failed')}: {exc}")

    if restore_valid and restore_data is not None:

        confirm_restore = st.checkbox(
            t("restore_confirm_replace"),
            key="confirm_restore_checkbox",
        )

        restore_word = st.text_input(
            t("restore_type_confirm"),
            key="restore_confirmation_word",
        )

        restore_button = st.button(
            f"♻️ {t('restore_my_backup')}",
            type="primary",
            use_container_width=True,
            key="restore_backup_button",
            disabled=not (
                confirm_restore
                and restore_word.strip().upper() == "RESTORE"
            ),
        )

        if restore_button:

            # ----------------------------------------------------
            # HELPERS
            # ----------------------------------------------------
            def backup_items(row):
                items_value = row.get("items")

                if isinstance(items_value, list):
                    return items_value

                try:
                    return json.loads(
                        row.get("items_json") or "[]"
                    )
                except Exception:
                    return []

            def remap_items(row, product_id_map):
                output = []

                for old_item in backup_items(row):
                    item = dict(old_item)

                    old_pid = item.get("product_id")

                    if old_pid not in (None, "", 0, "0"):
                        try:
                            old_pid_int = int(old_pid)
                            item["product_id"] = (
                                product_id_map.get(old_pid_int)
                            )
                        except Exception:
                            item["product_id"] = None

                    output.append(item)

                return output

            def safe_float(value, default=0.0):
                try:
                    return float(value or 0)
                except Exception:
                    return float(default)

            # ----------------------------------------------------
            # RESTORE TRANSACTION
            # ----------------------------------------------------
            try:
                with engine.begin() as con:

                    # =================================================
                    # 1. DELETE CURRENT USER BUSINESS DATA
                    # =================================================
                    con.execute(
                        delete(payments_table).where(
                            payments_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(sales_returns_table).where(
                            sales_returns_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(purchase_returns_table).where(
                            purchase_returns_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(stock_ledger_table).where(
                            stock_ledger_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(quotations_table).where(
                            quotations_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(invoices_table).where(
                            invoices_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(purchases_table).where(
                            purchases_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(product_inventory_table).where(
                            product_inventory_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(products_table).where(
                            products_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(customers_table).where(
                            customers_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(suppliers_table).where(
                            suppliers_table.c.user_id == USER_ID
                        )
                    )

                    con.execute(
                        delete(expenses_table).where(
                            expenses_table.c.user_id == USER_ID
                        )
                    )

                    # =================================================
                    # 2. RESTORE BUSINESS PROFILE
                    # =================================================
                    business_backup = restore_data.get(
                        "business",
                        {},
                    )

                    restored_state = business_backup.get(
                        "company_state",
                        "Maharashtra",
                    )

                    if restored_state not in STATES:
                        restored_state = "Maharashtra"

                    restored_language = normalize_lang(
                        restore_data.get(
                            "language",
                            selected_lang,
                        )
                    )

                    con.execute(
                        update(users)
                        .where(users.c.id == USER_ID)
                        .values(
                            company_name=str(
                                business_backup.get(
                                    "company_name",
                                    "",
                                )
                                or ""
                            ),
                            company_address=str(
                                business_backup.get(
                                    "company_address",
                                    "",
                                )
                                or ""
                            ),
                            company_gstin=str(
                                business_backup.get(
                                    "company_gstin",
                                    "",
                                )
                                or ""
                            ),
                            company_phone=str(
                                business_backup.get(
                                    "company_phone",
                                    "",
                                )
                                or ""
                            ),
                            company_email=str(
                                business_backup.get(
                                    "company_email",
                                    "",
                                )
                                or ""
                            ),
                            company_state=restored_state,
                            preferred_language=restored_language,
                            setup_complete=True,
                        )
                    )

                    # =================================================
                    # 3. RESTORE APP SETTINGS
                    # =================================================
                    settings_backup = restore_data.get(
                        "app_settings",
                        {},
                    )

                    restored_prefix = str(
                        settings_backup.get(
                            "invoice_prefix",
                            "INV",
                        )
                        or "INV"
                    ).strip()

                    restored_low_stock = safe_float(
                        settings_backup.get(
                            "default_low_stock",
                            5.0,
                        ),
                        5.0,
                    )

                    existing_settings = con.execute(
                        select(user_settings_table).where(
                            user_settings_table.c.user_id
                            == USER_ID
                        )
                    ).first()

                    if existing_settings:
                        con.execute(
                            update(user_settings_table)
                            .where(
                                user_settings_table.c.user_id
                                == USER_ID
                            )
                            .values(
                                invoice_prefix=(
                                    restored_prefix or "INV"
                                ),
                                default_low_stock=(
                                    restored_low_stock
                                ),
                                updated_at=now_naive(),
                            )
                        )
                    else:
                        con.execute(
                            insert(user_settings_table).values(
                                user_id=USER_ID,
                                invoice_prefix=(
                                    restored_prefix or "INV"
                                ),
                                default_low_stock=(
                                    restored_low_stock
                                ),
                                created_at=now_naive(),
                                updated_at=now_naive(),
                            )
                        )

                    # =================================================
                    # 4. RESTORE CUSTOMERS
                    # =================================================
                    for row in restore_data.get(
                        "customers",
                        [],
                    ):
                        con.execute(
                            insert(customers_table).values(
                                user_id=USER_ID,
                                name=str(
                                    row.get("name", "") or ""
                                ),
                                address=str(
                                    row.get("address", "") or ""
                                ),
                                gstin=str(
                                    row.get("gstin", "") or ""
                                ),
                                state=str(
                                    row.get(
                                        "state",
                                        "Maharashtra",
                                    )
                                    or "Maharashtra"
                                ),
                                created_at=now_naive(),
                            )
                        )

                    # =================================================
                    # 5. RESTORE SUPPLIERS
                    # =================================================
                    for row in restore_data.get(
                        "suppliers",
                        [],
                    ):
                        con.execute(
                            insert(suppliers_table).values(
                                user_id=USER_ID,
                                name=str(
                                    row.get("name", "") or ""
                                ),
                                address=str(
                                    row.get("address", "") or ""
                                ),
                                gstin=str(
                                    row.get("gstin", "") or ""
                                ),
                                phone=str(
                                    row.get("phone", "") or ""
                                ),
                                email=str(
                                    row.get("email", "") or ""
                                ),
                                state=str(
                                    row.get(
                                        "state",
                                        "Maharashtra",
                                    )
                                    or "Maharashtra"
                                ),
                                created_at=now_naive(),
                            )
                        )

                    # =================================================
                    # 6. RESTORE PRODUCTS + CREATE ID MAP
                    # =================================================
                    product_id_map = {}

                    for row in restore_data.get(
                        "products",
                        [],
                    ):
                        old_id = int(row.get("id", 0) or 0)

                        result = con.execute(
                            insert(products_table).values(
                                user_id=USER_ID,
                                name=str(
                                    row.get("name", "") or ""
                                ),
                                hsn=str(
                                    row.get("hsn", "") or ""
                                ),
                                rate=safe_float(
                                    row.get("rate", 0)
                                ),
                                gst_rate=safe_float(
                                    row.get("gst_rate", 18),
                                    18,
                                ),
                                created_at=now_naive(),
                            )
                        )

                        new_id = int(
                            result.inserted_primary_key[0]
                        )

                        if old_id:
                            product_id_map[old_id] = new_id

                    # =================================================
                    # 7. RESTORE INVENTORY
                    # =================================================
                    inventory_done = set()

                    for row in restore_data.get(
                        "inventory",
                        [],
                    ):
                        old_pid = int(
                            row.get("product_id", 0) or 0
                        )

                        new_pid = product_id_map.get(old_pid)

                        if not new_pid:
                            continue

                        con.execute(
                            insert(
                                product_inventory_table
                            ).values(
                                user_id=USER_ID,
                                product_id=new_pid,
                                sku=str(
                                    row.get("sku", "") or ""
                                ),
                                unit=str(
                                    row.get("unit", "Pcs")
                                    or "Pcs"
                                ),
                                purchase_rate=safe_float(
                                    row.get(
                                        "purchase_rate",
                                        0,
                                    )
                                ),
                                opening_stock=safe_float(
                                    row.get(
                                        "opening_stock",
                                        0,
                                    )
                                ),
                                low_stock_limit=safe_float(
                                    row.get(
                                        "low_stock_limit",
                                        5,
                                    ),
                                    5,
                                ),
                                current_stock=safe_float(
                                    row.get(
                                        "current_stock",
                                        0,
                                    )
                                ),
                                updated_at=now_naive(),
                            )
                        )

                        inventory_done.add(new_pid)

                    # Create missing inventory rows if necessary
                    for new_pid in product_id_map.values():
                        if new_pid not in inventory_done:
                            con.execute(
                                insert(
                                    product_inventory_table
                                ).values(
                                    user_id=USER_ID,
                                    product_id=new_pid,
                                    sku="",
                                    unit="Pcs",
                                    purchase_rate=0.0,
                                    opening_stock=0.0,
                                    low_stock_limit=(
                                        restored_low_stock
                                    ),
                                    current_stock=0.0,
                                    updated_at=now_naive(),
                                )
                            )

                    # =================================================
                    # 8. RESTORE PURCHASES
                    # =================================================
                    purchase_id_map = {}

                    for row in restore_data.get(
                        "purchases",
                        [],
                    ):
                        old_id = int(row.get("id", 0) or 0)

                        restored_items = remap_items(
                            row,
                            product_id_map,
                        )

                        result = con.execute(
                            insert(purchases_table).values(
                                user_id=USER_ID,
                                bill_number=str(
                                    row.get(
                                        "bill_number",
                                        "",
                                    )
                                    or ""
                                ),
                                purchase_date=str(
                                    row.get(
                                        "purchase_date",
                                        "",
                                    )
                                    or ""
                                ),
                                supplier_name=str(
                                    row.get(
                                        "supplier_name",
                                        "",
                                    )
                                    or ""
                                ),
                                supplier_address=str(
                                    row.get(
                                        "supplier_address",
                                        "",
                                    )
                                    or ""
                                ),
                                supplier_gstin=str(
                                    row.get(
                                        "supplier_gstin",
                                        "",
                                    )
                                    or ""
                                ),
                                supplier_state=str(
                                    row.get(
                                        "supplier_state",
                                        "",
                                    )
                                    or ""
                                ),
                                items_json=json.dumps(
                                    restored_items,
                                    ensure_ascii=False,
                                ),
                                taxable_value=safe_float(
                                    row.get(
                                        "taxable_value",
                                        0,
                                    )
                                ),
                                cgst=safe_float(
                                    row.get("cgst", 0)
                                ),
                                sgst=safe_float(
                                    row.get("sgst", 0)
                                ),
                                igst=safe_float(
                                    row.get("igst", 0)
                                ),
                                grand_total=safe_float(
                                    row.get(
                                        "grand_total",
                                        0,
                                    )
                                ),
                                is_intra_state=bool(
                                    row.get(
                                        "is_intra_state",
                                        True,
                                    )
                                ),
                                created_at=now_naive(),
                            )
                        )

                        new_id = int(
                            result.inserted_primary_key[0]
                        )

                        if old_id:
                            purchase_id_map[old_id] = new_id

                    # =================================================
                    # 9. RESTORE INVOICES
                    # =================================================
                    invoice_id_map = {}

                    for row in restore_data.get(
                        "invoices",
                        [],
                    ):
                        old_id = int(row.get("id", 0) or 0)

                        restored_items = remap_items(
                            row,
                            product_id_map,
                        )

                        result = con.execute(
                            insert(invoices_table).values(
                                user_id=USER_ID,
                                invoice_number=str(
                                    row.get(
                                        "invoice_number",
                                        "",
                                    )
                                    or ""
                                ),
                                invoice_date=str(
                                    row.get(
                                        "invoice_date",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_name=str(
                                    row.get(
                                        "customer_name",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_address=str(
                                    row.get(
                                        "customer_address",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_gstin=str(
                                    row.get(
                                        "customer_gstin",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_state=str(
                                    row.get(
                                        "customer_state",
                                        "",
                                    )
                                    or ""
                                ),
                                place_of_supply=str(
                                    row.get(
                                        "place_of_supply",
                                        "",
                                    )
                                    or ""
                                ),
                                items_json=json.dumps(
                                    restored_items,
                                    ensure_ascii=False,
                                ),
                                taxable_value=safe_float(
                                    row.get(
                                        "taxable_value",
                                        0,
                                    )
                                ),
                                cgst=safe_float(
                                    row.get("cgst", 0)
                                ),
                                sgst=safe_float(
                                    row.get("sgst", 0)
                                ),
                                igst=safe_float(
                                    row.get("igst", 0)
                                ),
                                grand_total=safe_float(
                                    row.get(
                                        "grand_total",
                                        0,
                                    )
                                ),
                                is_intra_state=bool(
                                    row.get(
                                        "is_intra_state",
                                        True,
                                    )
                                ),
                                created_at=now_naive(),
                            )
                        )

                        new_id = int(
                            result.inserted_primary_key[0]
                        )

                        if old_id:
                            invoice_id_map[old_id] = new_id

                    # =================================================
                    # 10. RESTORE QUOTATIONS
                    # =================================================
                    for row in restore_data.get(
                        "quotations",
                        [],
                    ):
                        restored_items = remap_items(
                            row,
                            product_id_map,
                        )

                        con.execute(
                            insert(quotations_table).values(
                                user_id=USER_ID,
                                quotation_number=str(
                                    row.get(
                                        "quotation_number",
                                        "",
                                    )
                                    or ""
                                ),
                                quotation_date=str(
                                    row.get(
                                        "quotation_date",
                                        "",
                                    )
                                    or ""
                                ),
                                valid_until=str(
                                    row.get(
                                        "valid_until",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_name=str(
                                    row.get(
                                        "customer_name",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_address=str(
                                    row.get(
                                        "customer_address",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_gstin=str(
                                    row.get(
                                        "customer_gstin",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_state=str(
                                    row.get(
                                        "customer_state",
                                        "",
                                    )
                                    or ""
                                ),
                                place_of_supply=str(
                                    row.get(
                                        "place_of_supply",
                                        "",
                                    )
                                    or ""
                                ),
                                items_json=json.dumps(
                                    restored_items,
                                    ensure_ascii=False,
                                ),
                                taxable_value=safe_float(
                                    row.get(
                                        "taxable_value",
                                        0,
                                    )
                                ),
                                cgst=safe_float(
                                    row.get("cgst", 0)
                                ),
                                sgst=safe_float(
                                    row.get("sgst", 0)
                                ),
                                igst=safe_float(
                                    row.get("igst", 0)
                                ),
                                grand_total=safe_float(
                                    row.get(
                                        "grand_total",
                                        0,
                                    )
                                ),
                                is_intra_state=bool(
                                    row.get(
                                        "is_intra_state",
                                        True,
                                    )
                                ),
                                created_at=now_naive(),
                            )
                        )

                    # =================================================
                    # 11. RESTORE SALES RETURNS
                    # =================================================
                    sales_return_id_map = {}

                    for row in restore_data.get(
                        "sales_returns",
                        [],
                    ):
                        old_return_id = int(
                            row.get("id", 0) or 0
                        )

                        old_invoice_id = int(
                            row.get(
                                "original_invoice_id",
                                0,
                            )
                            or 0
                        )

                        new_invoice_id = invoice_id_map.get(
                            old_invoice_id
                        )

                        if not new_invoice_id:
                            continue

                        restored_items = remap_items(
                            row,
                            product_id_map,
                        )

                        result = con.execute(
                            insert(
                                sales_returns_table
                            ).values(
                                user_id=USER_ID,
                                original_invoice_id=(
                                    new_invoice_id
                                ),
                                original_invoice_number=str(
                                    row.get(
                                        "original_invoice_number",
                                        "",
                                    )
                                    or ""
                                ),
                                return_number=str(
                                    row.get(
                                        "return_number",
                                        "",
                                    )
                                    or ""
                                ),
                                return_date=str(
                                    row.get(
                                        "return_date",
                                        "",
                                    )
                                    or ""
                                ),
                                customer_name=str(
                                    row.get(
                                        "customer_name",
                                        "",
                                    )
                                    or ""
                                ),
                                reason=str(
                                    row.get("reason", "") or ""
                                ),
                                items_json=json.dumps(
                                    restored_items,
                                    ensure_ascii=False,
                                ),
                                taxable_value=safe_float(
                                    row.get(
                                        "taxable_value",
                                        0,
                                    )
                                ),
                                cgst=safe_float(
                                    row.get("cgst", 0)
                                ),
                                sgst=safe_float(
                                    row.get("sgst", 0)
                                ),
                                igst=safe_float(
                                    row.get("igst", 0)
                                ),
                                grand_total=safe_float(
                                    row.get(
                                        "grand_total",
                                        0,
                                    )
                                ),
                                created_at=now_naive(),
                            )
                        )

                        new_return_id = int(
                            result.inserted_primary_key[0]
                        )

                        if old_return_id:
                            sales_return_id_map[
                                old_return_id
                            ] = new_return_id

                    # =================================================
                    # 12. RESTORE PURCHASE RETURNS
                    # =================================================
                    purchase_return_id_map = {}

                    for row in restore_data.get(
                        "purchase_returns",
                        [],
                    ):
                        old_return_id = int(
                            row.get("id", 0) or 0
                        )

                        old_purchase_id = int(
                            row.get(
                                "original_purchase_id",
                                0,
                            )
                            or 0
                        )

                        new_purchase_id = (
                            purchase_id_map.get(
                                old_purchase_id
                            )
                        )

                        if not new_purchase_id:
                            continue

                        restored_items = remap_items(
                            row,
                            product_id_map,
                        )

                        result = con.execute(
                            insert(
                                purchase_returns_table
                            ).values(
                                user_id=USER_ID,
                                original_purchase_id=(
                                    new_purchase_id
                                ),
                                original_bill_number=str(
                                    row.get(
                                        "original_bill_number",
                                        "",
                                    )
                                    or ""
                                ),
                                return_number=str(
                                    row.get(
                                        "return_number",
                                        "",
                                    )
                                    or ""
                                ),
                                return_date=str(
                                    row.get(
                                        "return_date",
                                        "",
                                    )
                                    or ""
                                ),
                                supplier_name=str(
                                    row.get(
                                        "supplier_name",
                                        "",
                                    )
                                    or ""
                                ),
                                reason=str(
                                    row.get("reason", "") or ""
                                ),
                                items_json=json.dumps(
                                    restored_items,
                                    ensure_ascii=False,
                                ),
                                taxable_value=safe_float(
                                    row.get(
                                        "taxable_value",
                                        0,
                                    )
                                ),
                                cgst=safe_float(
                                    row.get("cgst", 0)
                                ),
                                sgst=safe_float(
                                    row.get("sgst", 0)
                                ),
                                igst=safe_float(
                                    row.get("igst", 0)
                                ),
                                grand_total=safe_float(
                                    row.get(
                                        "grand_total",
                                        0,
                                    )
                                ),
                                created_at=now_naive(),
                            )
                        )

                        new_return_id = int(
                            result.inserted_primary_key[0]
                        )

                        if old_return_id:
                            purchase_return_id_map[
                                old_return_id
                            ] = new_return_id

                    # =================================================
                    # 13. RESTORE PAYMENTS
                    # =================================================
                    for row in restore_data.get(
                        "payments",
                        [],
                    ):
                        old_invoice_id = int(
                            row.get("invoice_id", 0) or 0
                        )

                        new_invoice_id = invoice_id_map.get(
                            old_invoice_id
                        )

                        if not new_invoice_id:
                            continue

                        con.execute(
                            insert(payments_table).values(
                                user_id=USER_ID,
                                invoice_id=new_invoice_id,
                                amount=safe_float(
                                    row.get("amount", 0)
                                ),
                                payment_date=str(
                                    row.get(
                                        "payment_date",
                                        "",
                                    )
                                    or ""
                                ),
                                note=str(
                                    row.get("note", "") or ""
                                ),
                                created_at=now_naive(),
                            )
                        )

                    # =================================================
                    # 14. RESTORE EXPENSES
                    # =================================================
                    for row in restore_data.get(
                        "expenses",
                        [],
                    ):
                        con.execute(
                            insert(expenses_table).values(
                                user_id=USER_ID,
                                expense_date=str(
                                    row.get(
                                        "expense_date",
                                        "",
                                    )
                                    or ""
                                ),
                                category=str(
                                    row.get(
                                        "category",
                                        "",
                                    )
                                    or ""
                                ),
                                amount=safe_float(
                                    row.get("amount", 0)
                                ),
                                note=str(
                                    row.get("note", "") or ""
                                ),
                                created_at=now_naive(),
                            )
                        )

                    # =================================================
                    # 15. RESTORE STOCK LEDGER
                    # =================================================
                    for row in restore_data.get(
                        "stock_ledger",
                        [],
                    ):
                        old_pid = int(
                            row.get("product_id", 0) or 0
                        )

                        new_pid = product_id_map.get(old_pid)

                        if not new_pid:
                            continue

                        reference_type = str(
                            row.get(
                                "reference_type",
                                "",
                            )
                            or ""
                        )

                        old_reference_id = int(
                            row.get(
                                "reference_id",
                                0,
                            )
                            or 0
                        )

                        new_reference_id = 0

                        if reference_type == "INVOICE":
                            new_reference_id = (
                                invoice_id_map.get(
                                    old_reference_id,
                                    0,
                                )
                            )

                        elif reference_type == "PURCHASE":
                            new_reference_id = (
                                purchase_id_map.get(
                                    old_reference_id,
                                    0,
                                )
                            )

                        elif reference_type == "SALES_RETURN":
                            new_reference_id = (
                                sales_return_id_map.get(
                                    old_reference_id,
                                    0,
                                )
                            )

                        elif reference_type == "PURCHASE_RETURN":
                            new_reference_id = (
                                purchase_return_id_map.get(
                                    old_reference_id,
                                    0,
                                )
                            )

                        con.execute(
                            insert(stock_ledger_table).values(
                                user_id=USER_ID,
                                product_id=new_pid,
                                movement_type=str(
                                    row.get(
                                        "movement_type",
                                        "",
                                    )
                                    or ""
                                ),
                                qty_change=safe_float(
                                    row.get(
                                        "qty_change",
                                        0,
                                    )
                                ),
                                balance_after=safe_float(
                                    row.get(
                                        "balance_after",
                                        0,
                                    )
                                ),
                                reference_type=(
                                    reference_type
                                ),
                                reference_id=(
                                    new_reference_id
                                ),
                                reference_number=str(
                                    row.get(
                                        "reference_number",
                                        "",
                                    )
                                    or ""
                                ),
                                note=str(
                                    row.get("note", "") or ""
                                ),
                                created_at=now_naive(),
                            )
                        )

                # ----------------------------------------------------
                # SUCCESS
                # ----------------------------------------------------
                st.session_state.guest_lang = normalize_lang(
                    restore_data.get(
                        "language",
                        selected_lang,
                    )
                )

                st.success(
                    f"✅ {t('backup_restored')}"
                )

                st.rerun()

            except IntegrityError as exc:
                st.error(
                    f"{t('restore_integrity_failed')}: {exc}"
                )

            except Exception as exc:
                st.error(
                    f"{t('restore_failed')}: {exc}"
                )
    

    st.markdown("---")
    st.subheader(f"📱 {t('use_on_phone')}")
    st.info(t("phone_help"))
