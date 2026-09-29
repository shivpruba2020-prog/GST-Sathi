import io
import json
import os
import re
from datetime import date, datetime
from pathlib import Path

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
APP_VERSION = "Version 5.0 | SHIVPRUBA BILLING"


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
    page_icon=APP_ICON,
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
    "invoice_history": "बिल इतिहास", "purchase_history": "खरेदी इतिहास", "reports": "अहवाल", "settings": "सेटिंग्ज",
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
            padding-top: .5rem;
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


def make_invoice_pdf(inv, business):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setTitle(f"{APP_NAME} - {inv['invoice_number']}")
    pdf_text(pdf, 18 * mm, height - 18 * mm, t("create_tax_invoice"), 15, True)
    pdf_text(pdf, 18 * mm, height - 29 * mm, business.get("company_name", ""), 13, True)
    pdf_text(pdf, 18 * mm, height - 36 * mm, business.get("company_address", ""), 9)
    pdf_text(pdf, 18 * mm, height - 43 * mm, f"GSTIN: {business.get('company_gstin','')}", 9)
    pdf_text(pdf, 18 * mm, height - 50 * mm, f"{t('phone')}: {business.get('company_phone','')}", 9)
    pdf_text(pdf, 115 * mm, height - 29 * mm, f"{t('invoice_number')}: {inv['invoice_number']}", 9, True)
    pdf_text(pdf, 115 * mm, height - 37 * mm, f"{t('date')}: {inv['invoice_date']}", 9)
    pdf_text(pdf, 115 * mm, height - 45 * mm, f"{t('place_of_supply')}: {inv.get('place_of_supply','')}", 8)
    y = height - 70 * mm
    pdf.line(18 * mm, y, 192 * mm, y)
    y -= 8 * mm
    pdf_text(pdf, 18 * mm, y, t("customer_info"), 10, True)
    y -= 7 * mm
    pdf_text(pdf, 18 * mm, y, inv.get("customer_name", ""), 10, True)
    y -= 6 * mm
    pdf_text(pdf, 18 * mm, y, inv.get("customer_address", ""), 9)
    y -= 6 * mm
    pdf_text(pdf, 18 * mm, y, f"GSTIN: {inv.get('customer_gstin','')}", 9)
    y -= 10 * mm
    pdf.line(18 * mm, y, 192 * mm, y)
    y -= 7 * mm
    headers = ["#", t("description"), t("hsn_sac"), t("quantity"), t("rate"), "GST%", t("amount")]
    xs = [18, 28, 92, 116, 132, 157, 174]
    for x, header in zip(xs, headers):
        pdf_text(pdf, x * mm, y, header, 8, True)
    y -= 6 * mm
    pdf.line(18 * mm, y, 192 * mm, y)
    y -= 6 * mm
    for index, item in enumerate(inv.get("items", []), 1):
        if y < 45 * mm:
            pdf.showPage()
            y = height - 25 * mm
        pdf_text(pdf, 18 * mm, y, index, 8)
        pdf_text(pdf, 28 * mm, y, str(item.get("desc", ""))[:28], 8)
        pdf_text(pdf, 92 * mm, y, item.get("hsn", ""), 8)
        pdf_text(pdf, 116 * mm, y, f"{float(item.get('qty',0)):g}", 8)
        pdf_text(pdf, 132 * mm, y, f"{float(item.get('rate',0)):,.2f}", 8)
        pdf_text(pdf, 157 * mm, y, f"{float(item.get('gst_rate',0)):g}", 8)
        pdf_text(pdf, 174 * mm, y, f"{float(item.get('amount',0)):,.2f}", 8)
        y -= 7 * mm
    y -= 3 * mm
    pdf.line(112 * mm, y, 192 * mm, y)
    y -= 7 * mm
    pdf_text(pdf, 120 * mm, y, t("taxable_value"), 8)
    pdf_text(pdf, 170 * mm, y, f"{float(inv.get('taxable_value',0)):,.2f}", 8)
    y -= 6 * mm
    if inv.get("is_intra_state"):
        pdf_text(pdf, 120 * mm, y, "CGST", 8); pdf_text(pdf, 170 * mm, y, f"{float(inv.get('cgst',0)):,.2f}", 8)
        y -= 6 * mm
        pdf_text(pdf, 120 * mm, y, "SGST", 8); pdf_text(pdf, 170 * mm, y, f"{float(inv.get('sgst',0)):,.2f}", 8)
    else:
        pdf_text(pdf, 120 * mm, y, "IGST", 8); pdf_text(pdf, 170 * mm, y, f"{float(inv.get('igst',0)):,.2f}", 8)
    y -= 8 * mm
    pdf.line(112 * mm, y, 192 * mm, y)
    y -= 8 * mm
    pdf_text(pdf, 120 * mm, y, t("grand_total"), 10, True)
    pdf_text(pdf, 166 * mm, y, f"Rs. {float(inv.get('grand_total',0)):,.2f}", 10, True)
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

    total_sales = sum(float(i.get("grand_total", 0) or 0) for i in invoices)
    total_tax = sum(
        float(i.get("cgst", 0) or 0) + float(i.get("sgst", 0) or 0) + float(i.get("igst", 0) or 0)
        for i in invoices
    )
    total_purchases = sum(float(p.get("grand_total", 0) or 0) for p in purchases)
    stock_value = sum(
        float(x.get("current_stock", 0) or 0) * float(x.get("purchase_rate", 0) or 0)
        for x in inventory
    )
    today_str = date.today().strftime("%d-%m-%Y")
    today_count = sum(1 for i in invoices if i.get("invoice_date") == today_str)
    today_purchase_count = sum(1 for p in purchases if p.get("purchase_date") == today_str)
    low_items = [
        x for x in inventory
        if x.get("unit") != "Service"
        and float(x.get("low_stock_limit", 0) or 0) > 0
        and float(x.get("current_stock", 0) or 0) <= float(x.get("low_stock_limit", 0) or 0)
    ]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("total_invoices"), len(invoices))
    c2.metric(t("total_sales"), money(total_sales))
    c3.metric(t("today_invoices"), today_count)
    c4.metric(t("total_gst"), money(total_tax))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric(t("total_purchases"), money(total_purchases))
    c6.metric(t("today_purchases"), today_purchase_count)
    c7.metric(t("stock_value"), money(stock_value))
    c8.metric(t("low_stock"), len(low_items))

    if low_items:
        product_by_id = {int(p["id"]): p for p in products}
        names = []
        for x in low_items[:8]:
            p = product_by_id.get(int(x["product_id"]), {})
            names.append(f"{p.get('name', t('product'))}: {float(x.get('current_stock',0)):g} {x.get('unit','')}")
        st.warning("⚠️ " + t("low_stock") + ": " + " | ".join(names))

    st.markdown("---")
    left_recent, right_recent = st.columns(2)
    with left_recent:
        st.subheader(t("recent_invoices"))
        if not invoices:
            st.info(t("no_invoices"))
        for inv in invoices[-5:][::-1]:
            with st.expander(f"{inv['invoice_number']} | {inv['customer_name']} | {money(inv['grand_total'])}"):
                st.write(f"**{t('date')}:** {inv['invoice_date']}")
                st.write(f"**{t('grand_total')}:** {money(inv['grand_total'])}")
                st.download_button(
                    t("download_pdf"),
                    make_invoice_pdf(inv, current_user),
                    f"{clean_filename(inv['invoice_number'])}.pdf",
                    "application/pdf",
                    key=f"dash_pdf_{inv['id']}",
                    use_container_width=True,
                )

    with right_recent:
        st.subheader(t("recent_purchases"))
        if not purchases:
            st.info(t("no_purchases"))
        for pur in purchases[-5:][::-1]:
            with st.expander(f"{pur['bill_number']} | {pur['supplier_name']} | {money(pur['grand_total'])}"):
                st.write(f"**{t('date')}:** {pur['purchase_date']}")
                st.write(f"**{t('grand_total')}:** {money(pur['grand_total'])}")

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
# INVOICE HISTORY + PAYMENTS
# ============================================================
elif menu == "invoice_history":
    st.title(f"🕘 {t('invoice_history')}")
    if not invoices:
        st.info(t("no_invoices"))
    else:
        search_text = st.text_input(f"🔎 {t('search_invoice')}").strip().lower()
        filtered = invoices if not search_text else [
            inv for inv in invoices
            if search_text in inv["invoice_number"].lower()
            or search_text in inv["customer_name"].lower()
        ]
        st.caption(f"{len(filtered)} {t('found')}")

        for inv in filtered[::-1]:
            paid_amount, balance, status_key = payment_status_for_invoice(inv, PAID_MAP)
            with st.expander(
                f"{inv['invoice_number']} | {inv['customer_name']} | {money(inv['grand_total'])} | "
                f"{inv['invoice_date']} | {t(status_key)}"
            ):
                st.write(f"**{t('address')}:** {inv.get('customer_address','')}")
                st.write(f"**GSTIN:** {inv.get('customer_gstin','')}")
                st.write(f"**{t('taxable_value')}:** {money(inv.get('taxable_value',0))}")
                st.write(f"**{t('grand_total')}:** {money(inv.get('grand_total',0))}")

                p1, p2, p3 = st.columns(3)
                p1.metric(t("payment_status"), t(status_key))
                p2.metric(t("paid_amount"), money(paid_amount))
                p3.metric(t("balance_amount"), money(balance))

                inv_payments = [
                    p for p in payments
                    if int(p.get("invoice_id", 0) or 0) == int(inv["id"])
                ]
                if inv_payments:
                    st.markdown(f"**{t('payment_history')}**")
                    for payment in inv_payments[::-1]:
                        pay_col, delete_col = st.columns([5, 1])
                        with pay_col:
                            note_text = f" | {payment.get('note','')}" if str(payment.get("note", "")).strip() else ""
                            st.write(
                                f"{payment.get('payment_date','')} | **{money(payment.get('amount',0))}**{note_text}"
                            )
                        with delete_col:
                            if st.button(
                                f"🗑️ {t('delete')}",
                                key=f"delete_payment_{inv['id']}_{payment['id']}",
                                use_container_width=True,
                            ):
                                with engine.begin() as con:
                                    con.execute(delete(payments_table).where(
                                        payments_table.c.id == int(payment["id"]),
                                        payments_table.c.user_id == USER_ID,
                                        payments_table.c.invoice_id == int(inv["id"]),
                                    ))
                                st.success(t("payment_deleted"))
                                st.rerun()
                else:
                    st.caption(t("no_payments"))

                if balance > 0.005:
                    with st.form(f"payment_form_{inv['id']}"):
                        st.markdown(f"**💳 {t('record_payment')}**")
                        payment_amount = st.number_input(
                            t("payment_amount"), min_value=0.01, max_value=float(balance),
                            value=float(balance), step=1.0, key=f"pay_amount_{inv['id']}"
                        )
                        payment_date_value = st.date_input(
                            t("payment_date"), value=date.today(), key=f"pay_date_{inv['id']}"
                        )
                        payment_note = st.text_input(t("payment_note"), key=f"pay_note_{inv['id']}")
                        save_payment = st.form_submit_button(
                            t("record_payment"), use_container_width=True, type="primary"
                        )

                    if save_payment:
                        amount_value = float(payment_amount)
                        date_value = payment_date_value.strftime("%d-%m-%Y")
                        note_value = payment_note.strip()
                        signature = f"{inv['id']}|{amount_value:.2f}|{date_value}|{note_value}"
                        now_ts = datetime.now().timestamp()
                        last_sig = st.session_state.get("_last_payment_signature", "")
                        last_ts = float(st.session_state.get("_last_payment_time", 0.0) or 0.0)

                        if amount_value > balance + 0.005:
                            st.error(t("payment_too_high"))
                        elif signature == last_sig and (now_ts - last_ts) < 5:
                            st.warning(t("payment_duplicate"))
                        else:
                            with engine.begin() as con:
                                con.execute(insert(payments_table).values(
                                    user_id=USER_ID, invoice_id=int(inv["id"]), amount=amount_value,
                                    payment_date=date_value, note=note_value, created_at=now_naive()
                                ))
                            st.session_state["_last_payment_signature"] = signature
                            st.session_state["_last_payment_time"] = now_ts
                            st.success(t("payment_saved"))
                            st.rerun()

                st.download_button(
                    t("download_pdf"), make_invoice_pdf(inv, current_user),
                    f"{clean_filename(inv['invoice_number'])}.pdf", "application/pdf",
                    key=f"hist_{inv['id']}", use_container_width=True,
                )

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

    st.subheader(t("sales_summary"))
    a, b, c = st.columns(3)
    a.metric(t("taxable_sales"), money(taxable))
    b.metric(t("total_gst"), money(cgst_total + sgst_total + igst_total))
    c.metric(t("total_sales"), money(total))

    d, e, f = st.columns(3)
    d.metric(t("cgst"), money(cgst_total))
    e.metric(t("sgst"), money(sgst_total))
    f.metric(t("igst"), money(igst_total))

    st.subheader(t("purchase_summary"))
    p1, p2, p3 = st.columns(3)
    p1.metric(t("taxable_purchases"), money(purchase_taxable))
    p2.metric(t("purchase_gst"), money(purchase_gst))
    p3.metric(t("total_purchases"), money(purchase_total))

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(t("customer_sales"))
        customer_totals = {}
        for inv in filtered_invoices:
            name = inv.get("customer_name", "")
            customer_totals[name] = customer_totals.get(name, 0.0) + float(inv.get("grand_total", 0) or 0)
        for name, value in sorted(customer_totals.items(), key=lambda kv: kv[1], reverse=True)[:20]:
            st.write(f"{name}: **{money(value)}**")

    with c2:
        st.subheader(t("supplier_purchases"))
        supplier_totals = {}
        for pur in filtered_purchases:
            name = pur.get("supplier_name", "")
            supplier_totals[name] = supplier_totals.get(name, 0.0) + float(pur.get("grand_total", 0) or 0)
        for name, value in sorted(supplier_totals.items(), key=lambda kv: kv[1], reverse=True)[:20]:
            st.write(f"{name}: **{money(value)}**")

    st.subheader(t("product_sales"))
    product_totals = {}
    for inv in filtered_invoices:
        for item in inv.get("items", []):
            name = item.get("desc", "")
            product_totals[name] = product_totals.get(name, 0.0) + float(item.get("amount", 0) or 0)
    for name, value in sorted(product_totals.items(), key=lambda kv: kv[1], reverse=True)[:30]:
        st.write(f"{name}: **{money(value)}**")

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

    st.markdown("---")
    st.subheader(f"💾 {t('backup')}")
    st.caption(t("backup_help"))

    backup_data = {
        "generated_at": now_naive().isoformat(),
        "language": selected_lang,
        "business": {
            key: current_user.get(key)
            for key in [
                "company_name", "company_address", "company_gstin",
                "company_phone", "company_email", "company_state"
            ]
        },
        "customers": customers,
        "suppliers": suppliers,
        "products": products,
        "inventory": get_inventory(USER_ID),
        "purchases": purchases,
        "stock_ledger": get_stock_ledger(USER_ID),
        "invoices": invoices,
        "payments": get_payments(USER_ID),
    }

    st.download_button(
        t("download_backup"),
        json.dumps(backup_data, ensure_ascii=False, indent=2, default=str).encode("utf-8"),
        "shivpruba_billing_backup.json",
        "application/json",
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader(f"📱 {t('use_on_phone')}")
    st.info(t("phone_help"))
