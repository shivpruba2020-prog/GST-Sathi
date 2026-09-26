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
# GST SATHI - COMPLETE SINGLE FILE APP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_FILE = BASE_DIR / "gst_sathi.db"


# ============================================================
# APP ICON
# ============================================================

def make_icon_bytes():

    img = Image.new(
        "RGB",
        (512, 512),
        "white"
    )

    d = ImageDraw.Draw(img)

    d.rounded_rectangle(
        (32, 32, 480, 480),
        radius=92,
        fill=(15, 88, 190)
    )

    d.rounded_rectangle(
        (78, 78, 434, 434),
        radius=62,
        fill="white"
    )

    d.text(
        (160, 165),
        "GST",
        fill=(15, 88, 190)
    )

    d.text(
        (155, 260),
        "SATHI",
        fill=(15, 88, 190)
    )

    buf = io.BytesIO()

    img.save(
        buf,
        format="PNG"
    )

    return buf.getvalue()


ICON_BYTES = make_icon_bytes()

APP_ICON = Image.open(
    io.BytesIO(
        ICON_BYTES
    )
)


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="GST Sathi",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# MOBILE / HOME SCREEN ICON
# ============================================================

def inject_mobile_icon():

    try:

        icon_b64 = base64.b64encode(
            ICON_BYTES
        ).decode("ascii")

        components.html(
            f"""
            <script>

            const head =
            window.parent.document.head;

            const icon =
            'data:image/png;base64,{icon_b64}';

            function ensure(rel) {{

                let el =
                head.querySelector(
                    `link[rel='${{rel}}']`
                );

                if (!el) {{

                    el =
                    window.parent.document.createElement(
                        'link'
                    );

                    el.rel = rel;

                    head.appendChild(
                        el
                    );
                }}

                el.href = icon;
            }}

            ensure('icon');
            ensure('apple-touch-icon');

            window.parent.document.title =
            'GST Sathi';

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
# ALL WHITE / BLANK METRIC CARDS FIXED HERE
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


    /* =====================================================
       ALL SUMMARY CARDS
       Dashboard + Reports + Invoice Result
       ===================================================== */

    [data-testid="stMetric"] {

        background:
        linear-gradient(
            135deg,
            #17345f 0%,
            #245a9f 100%
        ) !important;

        border:
        1px solid
        rgba(255,255,255,.14)
        !important;

        border-radius:
        18px !important;

        padding:
        16px 18px !important;

        min-height:
        112px !important;

        box-shadow:
        0 8px 24px
        rgba(0,0,0,.16)
        !important;
    }


    [data-testid="stMetric"] * {

        color:
        #ffffff !important;
    }


    [data-testid="stMetricLabel"] {

        color:
        #ffffff !important;

        font-size:
        .95rem !important;

        font-weight:
        700 !important;

        opacity:
        .95 !important;
    }


    [data-testid="stMetricValue"] {

        color:
        #ffffff !important;

        font-size:
        1.65rem !important;

        font-weight:
        800 !important;
    }


    /* Card 1 - Blue */

    div[data-testid="stHorizontalBlock"]
    > div:nth-child(1)
    [data-testid="stMetric"] {

        background:
        linear-gradient(
            135deg,
            #123c74 0%,
            #1976d2 100%
        ) !important;
    }


    /* Card 2 - Green */

    div[data-testid="stHorizontalBlock"]
    > div:nth-child(2)
    [data-testid="stMetric"] {

        background:
        linear-gradient(
            135deg,
            #145a46 0%,
            #16a085 100%
        ) !important;
    }


    /* Card 3 - Orange */

    div[data-testid="stHorizontalBlock"]
    > div:nth-child(3)
    [data-testid="stMetric"] {

        background:
        linear-gradient(
            135deg,
            #8a4b08 0%,
            #f39c12 100%
        ) !important;
    }


    /* Card 4 - Purple */

    div[data-testid="stHorizontalBlock"]
    > div:nth-child(4)
    [data-testid="stMetric"] {

        background:
        linear-gradient(
            135deg,
            #56348c 0%,
            #8e44ad 100%
        ) !important;
    }


    div.stButton > button,
    div.stDownloadButton > button {

        min-height:
        3rem;

        border-radius:
        12px;

        font-weight:
        700;
    }


    @media (max-width: 768px) {

        .block-container {

            padding-left:
            .75rem;

            padding-right:
            .75rem;

            padding-top:
            .6rem;
        }


        h1 {

            font-size:
            1.6rem !important;
        }


        h2 {

            font-size:
            1.3rem !important;
        }


        [data-testid="column"] {

            min-width:
            100% !important;

            width:
            100% !important;
        }


        [data-testid="stMetric"] {

            min-height:
            96px !important;
        }


        div.stButton > button,
        div.stDownloadButton > button {

            width:
            100%;

            min-height:
            3.2rem;
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

    "English":
        ["english"],

    "অসমীয়া - Assamese":
        ["assamese"],

    "বাংলা - Bengali":
        ["bengali"],

    "बड़ो - Bodo":
        ["bodo"],

    "डोगरी - Dogri":
        ["dogri"],

    "ગુજરાતી - Gujarati":
        ["gujarati"],

    "हिन्दी - Hindi":
        ["hindi"],

    "ಕನ್ನಡ - Kannada":
        ["kannada"],

    "کٲشُر - Kashmiri":
        ["kashmiri"],

    "कोंकणी - Konkani":
        ["konkani"],

    "मैथिली - Maithili":
        ["maithili"],

    "മലയാളം - Malayalam":
        ["malayalam"],

    "Manipuri / Meitei":
        [
            "manipuri",
            "meitei",
            "meiteilon"
        ],

    "मराठी - Marathi":
        ["marathi"],

    "नेपाली - Nepali":
        ["nepali"],

    "ଓଡ଼ିଆ - Odia":
        [
            "odia",
            "oriya"
        ],

    "ਪੰਜਾਬੀ - Punjabi":
        ["punjabi"],

    "संस्कृत - Sanskrit":
        ["sanskrit"],

    "ᱥᱟᱱᱛᱟᱲᱤ - Santali":
        ["santali"],

    "سنڌي - Sindhi":
        ["sindhi"],

    "தமிழ் - Tamil":
        ["tamil"],

    "తెలుగు - Telugu":
        ["telugu"],

    "اردو - Urdu":
        ["urdu"],
}


# ============================================================
# ENGLISH MASTER TEXT
# ============================================================

EN = {

    "menu":
        "Menu",

    "login":
        "Login",

    "signup":
        "Create Account",

    "logout":
        "Logout",

    "username":
        "Mobile / Email / Username",

    "password":
        "Password",

    "confirm_password":
        "Confirm Password",

    "invalid_login":
        "Incorrect username or password.",

    "account_exists":
        "This username already exists.",

    "password_short":
        "Password must be at least 6 characters.",

    "password_mismatch":
        "Passwords do not match.",

    "account_created":
        "Account created successfully.",

    "welcome":
        "Welcome to GST Sathi",

    "business_setup":
        "Business Setup",

    "business_setup_help":
        "Enter your business details once. You can change them later in Settings.",

    "get_started":
        "Save & Get Started",

    "dashboard":
        "Dashboard",

    "new_invoice":
        "New Invoice",

    "customers":
        "Customers",

    "products":
        "Products",

    "invoice_history":
        "Invoice History",

    "reports":
        "Reports",

    "settings":
        "Settings",

    "backup":
        "Backup",

    "total_invoices":
        "Total Invoices",

    "total_sales":
        "Total Sales",

    "today_invoices":
        "Today's Invoices",

    "total_gst":
        "Total GST",

    "recent_invoices":
        "Recent Invoices",

    "no_invoices":
        "No invoices yet.",

    "create_invoice":
        "Create Tax Invoice",

    "customer_info":
        "Customer Information",

    "saved_customer":
        "Saved Customer",

    "manual_customer":
        "New / Manual Customer",

    "customer_name":
        "Customer Name",

    "customer_address":
        "Customer Address",

    "customer_gstin":
        "Customer GSTIN (Optional)",

    "customer_state":
        "Customer State",

    "invoice_details":
        "Invoice Details",

    "invoice_number":
        "Invoice Number",

    "invoice_date":
        "Invoice Date",

    "place_of_supply":
        "Place of Supply",

    "items":
        "Goods / Services",

    "number_of_items":
        "Number of items",

    "item":
        "Item",

    "saved_product":
        "Saved Product",

    "custom_item":
        "Custom Item",

    "description":
        "Description",

    "hsn":
        "HSN / SAC",

    "quantity":
        "Quantity",

    "rate":
        "Rate",

    "gst_rate":
        "GST %",

    "save_invoice":
        "Calculate & Save Invoice",

    "customer_required":
        "Please enter the customer name.",

    "invoice_saved":
        "Invoice saved successfully.",

    "invoice_duplicate":
        "This invoice number already exists.",

    "taxable_value":
        "Taxable Value",

    "grand_total":
        "Grand Total",

    "download_pdf":
        "Download PDF",

    "search":
        "Search invoice number or customer name",

    "found":
        "invoices found",

    "date":
        "Date",

    "amount":
        "Amount",

    "address":
        "Address",

    "add_customer":
        "Add Customer",

    "save_customer":
        "Save Customer",

    "customer_saved":
        "Customer saved.",

    "no_customers":
        "No saved customers yet.",

    "delete":
        "Delete",

    "add_product":
        "Add Product / Service",

    "product_name":
        "Product / Service Name",

    "save_product":
        "Save Product",

    "product_saved":
        "Product saved.",

    "no_products":
        "No saved products yet.",

    "company_profile":
        "Company Profile",

    "company_name":
        "Company Name",

    "gstin":
        "GSTIN",

    "phone":
        "Phone",

    "email":
        "Email",

    "state":
        "State",

    "save_settings":
        "Save Settings",

    "settings_saved":
        "Settings saved.",

    "sales_summary":
        "Sales Summary",

    "taxable_sales":
        "Taxable Sales",

    "cgst":
        "CGST",

    "sgst":
        "SGST",

    "igst":
        "IGST",

    "phone_install":
        "Use on Phone",

    "phone_install_help":
        "Open the public GST Sathi link in Chrome or Safari, then choose Add to Home Screen.",

    "download_backup":
        "Download My Backup",

    "backup_help":
        "Download a copy of your business profile, customers, products and invoices.",

    "translation_note":
        "This language could not be translated right now, so English is being shown.",

    "version":
        "Version 3.2 | GST Sathi",
}


# ============================================================
# INDIAN STATES
# ============================================================

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
    "Other"
]


# ============================================================
# TRANSLATION
# ============================================================

@st.cache_data(show_spinner=False)
def build_language_pack(
    language_name
):

    if language_name == "English":

        return (
            EN.copy(),
            {s: s for s in STATES},
            True
        )


    try:

        probe = GoogleTranslator(
            source="en",
            target="hi"
        )


        supported = (
            probe.get_supported_languages(
                as_dict=True
            )
        )


        target_code = None


        for alias in [

            a.lower()

            for a
            in LANGUAGES.get(
                language_name,
                []
            )
        ]:

            for supported_name, code in supported.items():

                name = (
                    supported_name.lower()
                )


                if (
                    name == alias
                    or
                    alias in name
                ):

                    target_code = code

                    break


            if target_code:

                break


        if not target_code:

            return (
                EN.copy(),
                {s: s for s in STATES},
                False
            )


        all_text = (
            list(
                EN.values()
            )
            +
            STATES
        )


        translator = GoogleTranslator(
            source="en",
            target=target_code
        )


        out = []


        for i in range(
            0,
            len(all_text),
            25
        ):

            batch = (
                all_text[
                    i:i+25
                ]
            )


            translated = (
                translator.translate_batch(
                    batch
                )
            )


            if (
                not translated
                or
                len(translated)
                !=
                len(batch)
            ):

                raise ValueError(
                    "Translation failed"
                )


            out.extend(
                translated
            )


        ui_n = len(
            EN
        )


        return (

            dict(
                zip(
                    EN.keys(),
                    out[:ui_n]
                )
            ),

            dict(
                zip(
                    STATES,
                    out[ui_n:]
                )
            ),

            True
        )


    except Exception:

        return (
            EN.copy(),
            {s: s for s in STATES},
            False
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
        autoincrement=True
    ),

    Column(
        "username",
        String(255),
        nullable=False,
        unique=True
    ),

    Column(
        "password_hash",
        String(500),
        nullable=False
    ),

    Column(
        "preferred_language",
        String(120),
        nullable=False,
        default="English"
    ),

    Column(
        "setup_complete",
        Boolean,
        nullable=False,
        default=False
    ),

    Column(
        "company_name",
        String(300),
        default=""
    ),

    Column(
        "company_address",
        Text,
        default=""
    ),

    Column(
        "company_gstin",
        String(40),
        default=""
    ),

    Column(
        "company_phone",
        String(80),
        default=""
    ),

    Column(
        "company_email",
        String(255),
        default=""
    ),

    Column(
        "company_state",
        String(120),
        default="Maharashtra"
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow
    ),
)


customers_table = Table(

    "customers",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    ),

    Column(
        "name",
        String(300),
        nullable=False
    ),

    Column(
        "address",
        Text,
        default=""
    ),

    Column(
        "gstin",
        String(40),
        default=""
    ),

    Column(
        "state",
        String(120),
        default="Maharashtra"
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow
    ),
)


products_table = Table(

    "products",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    ),

    Column(
        "name",
        String(300),
        nullable=False
    ),

    Column(
        "hsn",
        String(80),
        default=""
    ),

    Column(
        "rate",
        Float,
        nullable=False,
        default=0.0
    ),

    Column(
        "gst_rate",
        Float,
        nullable=False,
        default=18.0
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow
    ),
)


invoices_table = Table(

    "invoices",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True
    ),

    Column(
        "user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    ),

    Column(
        "invoice_number",
        String(120),
        nullable=False
    ),

    Column(
        "invoice_date",
        String(20),
        nullable=False
    ),

    Column(
        "customer_name",
        String(300),
        nullable=False
    ),

    Column(
        "customer_address",
        Text,
        default=""
    ),

    Column(
        "customer_gstin",
        String(40),
        default=""
    ),

    Column(
        "customer_state",
        String(120),
        default=""
    ),

    Column(
        "place_of_supply",
        String(120),
        default=""
    ),

    Column(
        "items_json",
        Text,
        nullable=False
    ),

    Column(
        "taxable_value",
        Float,
        nullable=False,
        default=0.0
    ),

    Column(
        "cgst",
        Float,
        nullable=False,
        default=0.0
    ),

    Column(
        "sgst",
        Float,
        nullable=False,
        default=0.0
    ),

    Column(
        "igst",
        Float,
        nullable=False,
        default=0.0
    ),

    Column(
        "grand_total",
        Float,
        nullable=False,
        default=0.0
    ),

    Column(
        "is_intra_state",
        Boolean,
        nullable=False,
        default=True
    ),

    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow
    ),

    UniqueConstraint(
        "user_id",
        "invoice_number",
        name="uq_invoice_user_number"
    ),
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_secret(
    name,
    default=""
):

    try:

        return st.secrets.get(
            name,
            default
        )

    except Exception:

        return default


@st.cache_resource
def get_engine():

    db_url = (

        get_secret(
            "DATABASE_URL",
            ""
        )

        or

        os.environ.get(
            "DATABASE_URL",
            ""
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
            +
            db_url[
                len("postgres://"):
            ]
        )


    elif db_url.startswith(
        "postgresql://"
    ):

        db_url = (
            "postgresql+psycopg2://"
            +
            db_url[
                len("postgresql://"):
            ]
        )


    kwargs = {
        "pool_pre_ping": True
    }


    if db_url.startswith(
        "sqlite:"
    ):

        kwargs[
            "connect_args"
        ] = {
            "check_same_thread":
                False
        }


    eng = create_engine(
        db_url,
        **kwargs
    )


    metadata.create_all(
        eng
    )


    return eng


engine = get_engine()


# ============================================================
# DATABASE HELPERS
# ============================================================

def row_dict(
    row
):

    return (

        dict(
            row._mapping
        )

        if row is not None

        else None
    )


def get_user(
    user_id
):

    with engine.connect() as con:

        return row_dict(

            con.execute(

                select(users)

                .where(
                    users.c.id
                    ==
                    user_id
                )

            ).first()
        )


def get_user_by_username(
    username
):

    username = (
        username
        .strip()
        .lower()
    )


    with engine.connect() as con:

        return row_dict(

            con.execute(

                select(users)

                .where(
                    users.c.username
                    ==
                    username
                )

            ).first()
        )


def get_customers(
    user_id
):

    with engine.connect() as con:

        rows = con.execute(

            select(
                customers_table
            )

            .where(
                customers_table.c.user_id
                ==
                user_id
            )

            .order_by(
                customers_table.c.name
            )

        ).all()


    return [

        row_dict(r)

        for r
        in rows
    ]


def get_products(
    user_id
):

    with engine.connect() as con:

        rows = con.execute(

            select(
                products_table
            )

            .where(
                products_table.c.user_id
                ==
                user_id
            )

            .order_by(
                products_table.c.name
            )

        ).all()


    return [

        row_dict(r)

        for r
        in rows
    ]


def get_invoices(
    user_id
):

    with engine.connect() as con:

        rows = con.execute(

            select(
                invoices_table
            )

            .where(
                invoices_table.c.user_id
                ==
                user_id
            )

            .order_by(
                invoices_table.c.id
            )

        ).all()


    out = []


    for r in rows:

        d = row_dict(
            r
        )


        try:

            d["items"] = json.loads(

                d.pop(
                    "items_json"
                )
            )


        except Exception:

            d["items"] = []


        out.append(
            d
        )


    return out


def money(
    value
):

    return (
        f"₹ "
        f"{float(value or 0):,.2f}"
    )


def clean_filename(
    value
):

    return (

        re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            str(value)
        )

        .strip("_")

        or

        "invoice"
    )


# ============================================================
# SESSION
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
        "English"
    )

    if current_user

    else "English"
)


if saved_lang not in LANGUAGES:

    saved_lang = "English"


# ============================================================
# LANGUAGE SELECTOR
# ============================================================

selected_language = (

    st.sidebar.selectbox(

        "🌐 भाषा / Language",

        list(
            LANGUAGES.keys()
        ),

        index=
        list(
            LANGUAGES.keys()
        ).index(
            saved_lang
        ),
    )
)


TEXT, STATE_LABELS, TRANSLATION_OK = (

    build_language_pack(
        selected_language
    )
)


def t(
    key
):

    return TEXT.get(
        key,
        EN.get(
            key,
            key
        )
    )


if (
    selected_language
    !=
    "English"

    and

    not TRANSLATION_OK
):

    st.sidebar.warning(
        EN[
            "translation_note"
        ]
    )


st.sidebar.title(
    "🧾 GST Sathi"
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
            t("signup")
        ]
    )


    with tab1:

        with st.form(
            "login_form"
        ):

            login_username = (
                st.text_input(
                    t("username")
                )
            )


            login_password = (
                st.text_input(
                    t("password"),
                    type="password"
                )
            )


            login_submit = (
                st.form_submit_button(

                    t("login"),

                    use_container_width=True,

                    type="primary"
                )
            )


        if login_submit:

            found = (
                get_user_by_username(
                    login_username
                )
            )


            if (
                found

                and

                check_password_hash(
                    found[
                        "password_hash"
                    ],
                    login_password
                )
            ):

                st.session_state.user_id = (
                    found["id"]
                )


                st.rerun()


            else:

                st.error(
                    t(
                        "invalid_login"
                    )
                )


    with tab2:

        with st.form(
            "signup_form"
        ):

            new_username = (
                st.text_input(
                    t("username"),
                    key="signup_username"
                )
            )


            new_password = (
                st.text_input(
                    t("password"),
                    type="password",
                    key="signup_password"
                )
            )


            confirm_password = (
                st.text_input(
                    t(
                        "confirm_password"
                    ),
                    type="password"
                )
            )


            signup_submit = (
                st.form_submit_button(

                    t("signup"),

                    use_container_width=True,

                    type="primary"
                )
            )


        if signup_submit:

            uname = (
                new_username
                .strip()
                .lower()
            )


            if len(
                uname
            ) < 3:

                st.error(
                    "Username is required."
                )


            elif len(
                new_password
            ) < 6:

                st.error(
                    t(
                        "password_short"
                    )
                )


            elif (
                new_password
                !=
                confirm_password
            ):

                st.error(
                    t(
                        "password_mismatch"
                    )
                )


            else:

                try:

                    with engine.begin() as con:

                        result = con.execute(

                            insert(users)

                            .values(

                                username=
                                    uname,

                                password_hash=
                                    generate_password_hash(
                                        new_password
                                    ),

                                preferred_language=
                                    selected_language,

                                setup_complete=
                                    False,

                                company_state=
                                    "Maharashtra",

                                created_at=
                                    datetime.utcnow(),
                            )
                        )


                        new_id = (
                            result
                            .inserted_primary_key[0]
                        )


                    st.session_state.user_id = (
                        int(new_id)
                    )


                    st.success(
                        t(
                            "account_created"
                        )
                    )


                    st.rerun()


                except IntegrityError:

                    st.error(
                        t(
                            "account_exists"
                        )
                    )


    st.stop()


# ============================================================
# LOGGED USER
# ============================================================

current_user = get_user(
    st.session_state.user_id
)


USER_ID = current_user[
    "id"
]


if (
    selected_language
    !=
    current_user.get(
        "preferred_language"
    )
):

    with engine.begin() as con:

        con.execute(

            update(users)

            .where(
                users.c.id
                ==
                USER_ID
            )

            .values(
                preferred_language=
                    selected_language
            )
        )


# ============================================================
# FIRST BUSINESS SETUP
# ============================================================

if not current_user.get(
    "setup_complete",
    False
):

    st.title(
        f"🏪 {t('business_setup')}"
    )


    st.caption(
        t(
            "business_setup_help"
        )
    )


    with st.form(
        "business_setup_form"
    ):

        company_name = (
            st.text_input(

                t(
                    "company_name"
                ),

                value=
                current_user.get(
                    "company_name"
                )
                or ""
            )
        )


        company_address = (
            st.text_area(

                t(
                    "address"
                ),

                value=
                current_user.get(
                    "company_address"
                )
                or ""
            )
        )


        company_gstin = (
            st.text_input(

                t(
                    "gstin"
                ),

                value=
                current_user.get(
                    "company_gstin"
                )
                or ""
            )
        )


        company_phone = (
            st.text_input(

                t(
                    "phone"
                ),

                value=
                current_user.get(
                    "company_phone"
                )
                or ""
            )
        )


        company_email = (
            st.text_input(

                t(
                    "email"
                ),

                value=
                current_user.get(
                    "company_email"
                )
                or ""
            )
        )


        state0 = (

            current_user.get(
                "company_state"
            )

            if
            current_user.get(
                "company_state"
            )
            in STATES

            else
            "Maharashtra"
        )


        company_state = (
            st.selectbox(

                t(
                    "state"
                ),

                STATES,

                index=
                STATES.index(
                    state0
                ),

                format_func=
                lambda s:
                STATE_LABELS.get(
                    s,
                    s
                )
            )
        )


        setup_submit = (
            st.form_submit_button(

                t(
                    "get_started"
                ),

                use_container_width=True,

                type="primary"
            )
        )


    if setup_submit:

        if not company_name.strip():

            st.error(
                "Company name is required."
            )


        else:

            with engine.begin() as con:

                con.execute(

                    update(users)

                    .where(
                        users.c.id
                        ==
                        USER_ID
                    )

                    .values(

                        setup_complete=
                            True,

                        company_name=
                            company_name.strip(),

                        company_address=
                            company_address.strip(),

                        company_gstin=
                            company_gstin.strip(),

                        company_phone=
                            company_phone.strip(),

                        company_email=
                            company_email.strip(),

                        company_state=
                            company_state,
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
                        path
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
    bold=False
):

    font = PDF_FONT


    if (
        PDF_FONT
        ==
        "Helvetica"

        and

        bold
    ):

        font = (
            "Helvetica-Bold"
        )


    pdf.setFont(
        font,
        size
    )


    pdf.drawString(
        x,
        y,
        str(
            text
            or
            ""
        )
    )


# ============================================================
# CREATE PDF
# ============================================================

def make_invoice_pdf(
    inv,
    business
):

    buffer = io.BytesIO()


    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )


    width, height = A4


    pdf.setTitle(
        f"GST Sathi - "
        f"{inv['invoice_number']}"
    )


    pdf_text(
        pdf,
        18*mm,
        height-18*mm,
        "TAX INVOICE",
        16,
        True
    )


    pdf_text(
        pdf,
        18*mm,
        height-29*mm,
        business.get(
            "company_name",
            ""
        ),
        13,
        True
    )


    pdf_text(
        pdf,
        18*mm,
        height-36*mm,
        business.get(
            "company_address",
            ""
        ),
        9
    )


    pdf_text(
        pdf,
        18*mm,
        height-43*mm,
        f"GSTIN: "
        f"{business.get('company_gstin','')}",
        9
    )


    pdf_text(
        pdf,
        18*mm,
        height-50*mm,
        f"Phone: "
        f"{business.get('company_phone','')}",
        9
    )


    pdf_text(
        pdf,
        18*mm,
        height-57*mm,
        f"Email: "
        f"{business.get('company_email','')}",
        9
    )


    pdf_text(
        pdf,
        118*mm,
        height-29*mm,
        f"Invoice No: "
        f"{inv['invoice_number']}",
        9,
        True
    )


    pdf_text(
        pdf,
        118*mm,
        height-37*mm,
        f"Date: "
        f"{inv['invoice_date']}",
        9
    )


    pdf_text(
        pdf,
        118*mm,
        height-45*mm,
        f"Place of Supply: "
        f"{inv.get('place_of_supply','')}",
        9
    )


    y = (
        height
        -
        75*mm
    )


    pdf.line(
        18*mm,
        y,
        192*mm,
        y
    )


    y -= 8*mm


    pdf_text(
        pdf,
        18*mm,
        y,
        "Bill To:",
        10,
        True
    )


    y -= 7*mm


    pdf_text(
        pdf,
        18*mm,
        y,
        inv.get(
            "customer_name",
            ""
        ),
        10,
        True
    )


    y -= 6*mm


    pdf_text(
        pdf,
        18*mm,
        y,
        inv.get(
            "customer_address",
            ""
        ),
        9
    )


    y -= 6*mm


    pdf_text(
        pdf,
        18*mm,
        y,
        f"GSTIN: "
        f"{inv.get('customer_gstin','')}",
        9
    )


    y -= 6*mm


    pdf_text(
        pdf,
        18*mm,
        y,
        f"State: "
        f"{inv.get('customer_state','')}",
        9
    )


    y -= 10*mm


    pdf.line(
        18*mm,
        y,
        192*mm,
        y
    )


    y -= 7*mm


    headers = [

        "#",
        "Description",
        "HSN",
        "Qty",
        "Rate",
        "GST%",
        "Amount"
    ]


    xs = [

        18,
        28,
        92,
        116,
        132,
        157,
        174
    ]


    for x, header in zip(
        xs,
        headers
    ):

        pdf_text(
            pdf,
            x*mm,
            y,
            header,
            8,
            True
        )


    y -= 6*mm


    pdf.line(
        18*mm,
        y,
        192*mm,
        y
    )


    y -= 6*mm


    for index, item in enumerate(
        inv.get(
            "items",
            []
        ),
        1
    ):

        if y < 45*mm:

            pdf.showPage()

            y = (
                height
                -
                25*mm
            )


        pdf_text(
            pdf,
            18*mm,
            y,
            index,
            8
        )


        pdf_text(
            pdf,
            28*mm,
            y,
            str(
                item.get(
                    "desc",
                    ""
                )
            )[:30],
            8
        )


        pdf_text(
            pdf,
            92*mm,
            y,
            item.get(
                "hsn",
                ""
            ),
            8
        )


        pdf_text(
            pdf,
            116*mm,
            y,
            f"{float(item.get('qty',0)):g}",
            8
        )


        pdf_text(
            pdf,
            132*mm,
            y,
            f"{float(item.get('rate',0)):,.2f}",
            8
        )


        pdf_text(
            pdf,
            157*mm,
            y,
            f"{float(item.get('gst_rate',0)):g}",
            8
        )


        pdf_text(
            pdf,
            174*mm,
            y,
            f"{float(item.get('amount',0)):,.2f}",
            8
        )


        y -= 7*mm


    y -= 4*mm


    pdf.line(
        112*mm,
        y,
        192*mm,
        y
    )


    y -= 7*mm


    pdf_text(
        pdf,
        120*mm,
        y,
        "Taxable Value",
        9
    )


    pdf_text(
        pdf,
        170*mm,
        y,
        f"{inv.get('taxable_value',0):,.2f}",
        9
    )


    y -= 6*mm


    if inv.get(
        "is_intra_state"
    ):

        pdf_text(
            pdf,
            120*mm,
            y,
            "CGST",
            9
        )


        pdf_text(
            pdf,
            170*mm,
            y,
            f"{inv.get('cgst',0):,.2f}",
            9
        )


        y -= 6*mm


        pdf_text(
            pdf,
            120*mm,
            y,
            "SGST",
            9
        )


        pdf_text(
            pdf,
            170*mm,
            y,
            f"{inv.get('sgst',0):,.2f}",
            9
        )


    else:

        pdf_text(
            pdf,
            120*mm,
            y,
            "IGST",
            9
        )


        pdf_text(
            pdf,
            170*mm,
            y,
            f"{inv.get('igst',0):,.2f}",
            9
        )


    y -= 8*mm


    pdf.line(
        112*mm,
        y,
        192*mm,
        y
    )


    y -= 8*mm


    pdf_text(
        pdf,
        120*mm,
        y,
        "GRAND TOTAL",
        11,
        True
    )


    pdf_text(
        pdf,
        166*mm,
        y,
        f"Rs. "
        f"{inv.get('grand_total',0):,.2f}",
        11,
        True
    )


    pdf_text(
        pdf,
        18*mm,
        18*mm,
        "Generated with GST Sathi",
        8
    )


    pdf.save()


    buffer.seek(
        0
    )


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


invoices = get_invoices(
    USER_ID
)


# ============================================================
# MENU
# ============================================================

MENU_ICONS = {

    "dashboard":
        "🏠",

    "new_invoice":
        "🧾",

    "customers":
        "👥",

    "products":
        "📦",

    "invoice_history":
        "🕘",

    "reports":
        "📊",

    "settings":
        "⚙️",
}


menu = st.sidebar.radio(

    t(
        "menu"
    ),

    list(
        MENU_ICONS.keys()
    ),

    format_func=
    lambda x:
    f"{MENU_ICONS[x]} {t(x)}"
)


st.sidebar.markdown(
    "---"
)


st.sidebar.caption(
    current_user.get(
        "company_name",
        ""
    )
)


st.sidebar.caption(
    t(
        "version"
    )
)


if st.sidebar.button(

    f"🚪 {t('logout')}",

    use_container_width=True
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
                0
            )
        )

        for i
        in invoices
    )


    total_tax = sum(

        float(
            i.get(
                "cgst",
                0
            )
        )

        +

        float(
            i.get(
                "sgst",
                0
            )
        )

        +

        float(
            i.get(
                "igst",
                0
            )
        )

        for i
        in invoices
    )


    today_str = (
        date.today()
        .strftime(
            "%d-%m-%Y"
        )
    )


    today_count = sum(

        1

        for i
        in invoices

        if i.get(
            "invoice_date"
        )
        ==
        today_str
    )


    c1, c2, c3, c4 = (
        st.columns(4)
    )


    c1.metric(
        t(
            "total_invoices"
        ),
        len(
            invoices
        )
    )


    c2.metric(
        t(
            "total_sales"
        ),
        money(
            total_sales
        )
    )


    c3.metric(
        t(
            "today_invoices"
        ),
        today_count
    )


    c4.metric(
        t(
            "total_gst"
        ),
        money(
            total_tax
        )
    )


    st.markdown(
        "---"
    )


    st.subheader(
        t(
            "recent_invoices"
        )
    )


    if not invoices:

        st.info(
            t(
                "no_invoices"
            )
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

                t(
                    "download_pdf"
                ),

                make_invoice_pdf(
                    inv,
                    current_user
                ),

                f"{clean_filename(inv['invoice_number'])}.pdf",

                "application/pdf",

                key=
                f"dash_pdf_{inv['id']}"
            )


# ============================================================
# NEW INVOICE
# ============================================================

elif menu == "new_invoice":

    st.title(
        f"🧾 {t('create_invoice')}"
    )


    left, right = (
        st.columns(2)
    )


    customer_map = {

        c["name"]:
        c

        for c
        in customers
    }


    with left:

        st.subheader(
            t(
                "customer_info"
            )
        )


        choice = (
            st.selectbox(

                t(
                    "saved_customer"
                ),

                [
                    t(
                        "manual_customer"
                    )
                ]

                +

                list(
                    customer_map.keys()
                )
            )
        )


        cdata = (
            customer_map.get(
                choice,
                {}
            )
        )


        customer_name = (
            st.text_input(

                t(
                    "customer_name"
                ),

                value=
                cdata.get(
                    "name",
                    ""
                ),

                key=
                f"cn_{choice}"
            )
        )


        customer_address = (
            st.text_area(

                t(
                    "customer_address"
                ),

                value=
                cdata.get(
                    "address",
                    ""
                ),

                key=
                f"ca_{choice}"
            )
        )


        customer_gstin = (
            st.text_input(

                t(
                    "customer_gstin"
                ),

                value=
                cdata.get(
                    "gstin",
                    ""
                ),

                key=
                f"cg_{choice}"
            )
        )


        cstate = (

            cdata.get(
                "state",
                "Maharashtra"
            )

            if
            cdata.get(
                "state",
                "Maharashtra"
            )
            in STATES

            else
            "Maharashtra"
        )


        customer_state = (
            st.selectbox(

                t(
                    "customer_state"
                ),

                STATES,

                index=
                STATES.index(
                    cstate
                ),

                format_func=
                lambda s:
                STATE_LABELS.get(
                    s,
                    s
                ),

                key=
                f"cs_{choice}"
            )
        )


    with right:

        st.subheader(
            t(
                "invoice_details"
            )
        )


        suggested = (

            f"INV-"
            f"{datetime.now().strftime('%Y%m%d')}-"
            f"{len(invoices)+1:03d}"
        )


        invoice_number = (
            st.text_input(

                t(
                    "invoice_number"
                ),

                value=
                suggested
            )
        )


        inv_date = (
            st.date_input(

                t(
                    "invoice_date"
                ),

                value=
                date.today()
            )
        )


        place_supply = (
            st.selectbox(

                t(
                    "place_of_supply"
                ),

                STATES,

                index=
                STATES.index(
                    customer_state
                ),

                format_func=
                lambda s:
                STATE_LABELS.get(
                    s,
                    s
                )
            )
        )


    st.markdown(
        "---"
    )


    st.subheader(
        f"📦 {t('items')}"
    )


    nitems = int(

        st.number_input(

            t(
                "number_of_items"
            ),

            min_value=1,

            max_value=20,

            value=1,

            step=1
        )
    )


    pmap = {

        p["name"]:
        p

        for p
        in products
    }


    invoice_items = []


    for i in range(
        nitems
    ):

        st.markdown(
            f"**{t('item')} {i+1}**"
        )


        pchoice = (
            st.selectbox(

                t(
                    "saved_product"
                ),

                [
                    t(
                        "custom_item"
                    )
                ]

                +

                list(
                    pmap.keys()
                ),

                key=
                f"pc_{i}"
            )
        )


        pdata = (
            pmap.get(
                pchoice,
                {}
            )
        )


        a, b, c, d, e = (
            st.columns(
                [
                    3,
                    1.2,
                    1,
                    1.3,
                    1.1
                ]
            )
        )


        with a:

            desc = (
                st.text_input(

                    t(
                        "description"
                    ),

                    value=
                    pdata.get(
                        "name",
                        ""
                    ),

                    key=
                    f"desc_{i}_{pchoice}"
                )
            )


        with b:

            hsn = (
                st.text_input(

                    t(
                        "hsn"
                    ),

                    value=
                    pdata.get(
                        "hsn",
                        ""
                    ),

                    key=
                    f"hsn_{i}_{pchoice}"
                )
            )


        with c:

            qty = (
                st.number_input(

                    t(
                        "quantity"
                    ),

                    min_value=
                        0.01,

                    value=
                        1.0,

                    step=
                        1.0,

                    key=
                        f"qty_{i}"
                )
            )


        with d:

            rate = (
                st.number_input(

                    t(
                        "rate"
                    ),

                    min_value=
                        0.0,

                    value=
                        float(
                            pdata.get(
                                "rate",
                                0.0
                            )
                        ),

                    step=
                        10.0,

                    key=
                        f"rate_{i}_{pchoice}"
                )
            )


        with e:

            opts = [
                0,
                5,
                12,
                18,
                28
            ]


            default_gst = int(
                pdata.get(
                    "gst_rate",
                    18
                )
            )


            if default_gst not in opts:

                default_gst = 18


            gst = st.selectbox(

                t(
                    "gst_rate"
                ),

                opts,

                index=
                opts.index(
                    default_gst
                ),

                key=
                f"gst_{i}_{pchoice}"
            )


        invoice_items.append(

            {

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
                    *
                    float(rate)
            }
        )


        st.markdown(
            "---"
        )


    if st.button(

        t(
            "save_invoice"
        ),

        use_container_width=True,

        type="primary"
    ):

        if not customer_name.strip():

            st.error(
                t(
                    "customer_required"
                )
            )


        elif any(

            i[
                "invoice_number"
            ]
            ==
            invoice_number.strip()

            for i
            in invoices
        ):

            st.error(
                t(
                    "invoice_duplicate"
                )
            )


        else:

            taxable = sum(

                x[
                    "amount"
                ]

                for x
                in invoice_items
            )


            intra = (

                current_user.get(
                    "company_state"
                )

                ==

                place_supply
            )


            cgst = 0.0
            sgst = 0.0
            igst = 0.0


            for x in invoice_items:

                tax = (

                    x[
                        "amount"
                    ]

                    *

                    x[
                        "gst_rate"
                    ]

                    /

                    100
                )


                if intra:

                    cgst += (
                        tax / 2
                    )

                    sgst += (
                        tax / 2
                    )


                else:

                    igst += (
                        tax
                    )


            grand = (

                taxable
                +
                cgst
                +
                sgst
                +
                igst
            )


            try:

                with engine.begin() as con:

                    result = con.execute(

                        insert(
                            invoices_table
                        )

                        .values(

                            user_id=
                                USER_ID,

                            invoice_number=
                                invoice_number.strip(),

                            invoice_date=
                                inv_date.strftime(
                                    "%d-%m-%Y"
                                ),

                            customer_name=
                                customer_name.strip(),

                            customer_address=
                                customer_address.strip(),

                            customer_gstin=
                                customer_gstin.strip(),

                            customer_state=
                                customer_state,

                            place_of_supply=
                                place_supply,

                            items_json=
                                json.dumps(
                                    invoice_items,
                                    ensure_ascii=False
                                ),

                            taxable_value=
                                taxable,

                            cgst=
                                cgst,

                            sgst=
                                sgst,

                            igst=
                                igst,

                            grand_total=
                                grand,

                            is_intra_state=
                                intra,

                            created_at=
                                datetime.utcnow(),
                        )
                    )


                    inv_id = (
                        result
                        .inserted_primary_key[0]
                    )


            except IntegrityError:

                st.error(
                    t(
                        "invoice_duplicate"
                    )
                )

                st.stop()


            if (

                customer_name.strip()

                and

                not any(

                    c["name"]
                    .strip()
                    .lower()

                    ==

                    customer_name
                    .strip()
                    .lower()

                    for c
                    in customers
                )
            ):

                with engine.begin() as con:

                    con.execute(

                        insert(
                            customers_table
                        )

                        .values(

                            user_id=
                                USER_ID,

                            name=
                                customer_name.strip(),

                            address=
                                customer_address.strip(),

                            gstin=
                                customer_gstin.strip(),

                            state=
                                customer_state,

                            created_at=
                                datetime.utcnow()
                        )
                    )


            new_inv = {

                "id":
                    inv_id,

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
                t(
                    "invoice_saved"
                )
            )


            x, y, z = (
                st.columns(3)
            )


            x.metric(
                t(
                    "taxable_value"
                ),

                money(
                    taxable
                )
            )


            y.metric(

                "CGST + SGST"

                if intra

                else

                "IGST",

                money(

                    cgst
                    +
                    sgst

                    if intra

                    else

                    igst
                )
            )


            z.metric(
                t(
                    "grand_total"
                ),

                money(
                    grand
                )
            )


            st.download_button(

                t(
                    "download_pdf"
                ),

                make_invoice_pdf(
                    new_inv,
                    current_user
                ),

                f"{clean_filename(invoice_number)}.pdf",

                "application/pdf",

                use_container_width=True,
            )


# ============================================================
# CUSTOMERS
# ============================================================

elif menu == "customers":

    st.title(
        f"👥 {t('customers')}"
    )


    with st.expander(

        f"➕ {t('add_customer')}",

        expanded=
        not customers
    ):

        with st.form(
            "customer_form",
            clear_on_submit=True
        ):

            name = (
                st.text_input(
                    t(
                        "customer_name"
                    )
                )
            )


            address = (
                st.text_area(
                    t(
                        "customer_address"
                    )
                )
            )


            gstin = (
                st.text_input(
                    t(
                        "customer_gstin"
                    )
                )
            )


            state_value = (
                st.selectbox(

                    t(
                        "customer_state"
                    ),

                    STATES,

                    index=
                    STATES.index(
                        "Maharashtra"
                    ),

                    format_func=
                    lambda s:
                    STATE_LABELS.get(
                        s,
                        s
                    )
                )
            )


            add_customer = (
                st.form_submit_button(

                    t(
                        "save_customer"
                    ),

                    use_container_width=True
                )
            )


        if (
            add_customer
            and
            name.strip()
        ):

            with engine.begin() as con:

                con.execute(

                    insert(
                        customers_table
                    )

                    .values(

                        user_id=
                            USER_ID,

                        name=
                            name.strip(),

                        address=
                            address.strip(),

                        gstin=
                            gstin.strip(),

                        state=
                            state_value,

                        created_at=
                            datetime.utcnow()
                    )
                )


            st.success(
                t(
                    "customer_saved"
                )
            )


            st.rerun()


    if not customers:

        st.info(
            t(
                "no_customers"
            )
        )


    for customer in customers:

        with st.expander(
            customer[
                "name"
            ]
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

                key=
                f"delc_{customer['id']}"
            ):

                with engine.begin() as con:

                    con.execute(

                        delete(
                            customers_table
                        )

                        .where(

                            customers_table.c.id
                            ==
                            customer["id"],

                            customers_table.c.user_id
                            ==
                            USER_ID
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

        expanded=
        not products
    ):

        with st.form(
            "product_form",
            clear_on_submit=True
        ):

            name = (
                st.text_input(
                    t(
                        "product_name"
                    )
                )
            )


            hsn = (
                st.text_input(
                    t(
                        "hsn"
                    )
                )
            )


            rate = (
                st.number_input(

                    t(
                        "rate"
                    ),

                    min_value=
                        0.0,

                    value=
                        0.0,

                    step=
                        10.0
                )
            )


            gst = (
                st.selectbox(

                    t(
                        "gst_rate"
                    ),

                    [
                        0,
                        5,
                        12,
                        18,
                        28
                    ],

                    index=3
                )
            )


            add_product = (
                st.form_submit_button(

                    t(
                        "save_product"
                    ),

                    use_container_width=True
                )
            )


        if (
            add_product
            and
            name.strip()
        ):

            with engine.begin() as con:

                con.execute(

                    insert(
                        products_table
                    )

                    .values(

                        user_id=
                            USER_ID,

                        name=
                            name.strip(),

                        hsn=
                            hsn.strip(),

                        rate=
                            float(rate),

                        gst_rate=
                            float(gst),

                        created_at=
                            datetime.utcnow()
                    )
                )


            st.success(
                t(
                    "product_saved"
                )
            )


            st.rerun()


    if not products:

        st.info(
            t(
                "no_products"
            )
        )


    for product in products:

        with st.expander(
            product[
                "name"
            ]
        ):

            st.write(

                f"HSN/SAC: "
                f"{product.get('hsn','')} | "

                f"{money(product.get('rate',0))} | "

                f"GST "
                f"{float(product.get('gst_rate',0)):g}%"
            )


            if st.button(

                f"🗑️ {t('delete')}",

                key=
                f"delp_{product['id']}"
            ):

                with engine.begin() as con:

                    con.execute(

                        delete(
                            products_table
                        )

                        .where(

                            products_table.c.id
                            ==
                            product["id"],

                            products_table.c.user_id
                            ==
                            USER_ID
                        )
                    )


                st.rerun()


# ============================================================
# INVOICE HISTORY
# ============================================================

elif menu == "invoice_history":

    st.title(
        f"🕘 {t('invoice_history')}"
    )


    if not invoices:

        st.info(
            t(
                "no_invoices"
            )
        )


    else:

        search = (

            st.text_input(
                f"🔎 {t('search')}"
            )

            .strip()

            .lower()
        )


        filtered = (

            invoices

            if not search

            else [

                inv

                for inv
                in invoices

                if
                search
                in
                inv[
                    "invoice_number"
                ].lower()

                or

                search
                in
                inv[
                    "customer_name"
                ].lower()
            ]
        )


        st.caption(
            f"{len(filtered)} "
            f"{t('found')}"
        )


        for inv in filtered[::-1]:

            with st.expander(

                f"{inv['invoice_number']} | "
                f"{inv['customer_name']} | "
                f"{money(inv['grand_total'])} | "
                f"{inv['invoice_date']}"

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


                st.download_button(

                    t(
                        "download_pdf"
                    ),

                    make_invoice_pdf(
                        inv,
                        current_user
                    ),

                    f"{clean_filename(inv['invoice_number'])}.pdf",

                    "application/pdf",

                    key=
                    f"hist_{inv['id']}"
                )


# ============================================================
# REPORTS
# ============================================================

elif menu == "reports":

    st.title(
        f"📊 {t('reports')}"
    )


    taxable = sum(

        float(
            i.get(
                "taxable_value",
                0
            )
        )

        for i
        in invoices
    )


    cgst_total = sum(

        float(
            i.get(
                "cgst",
                0
            )
        )

        for i
        in invoices
    )


    sgst_total = sum(

        float(
            i.get(
                "sgst",
                0
            )
        )

        for i
        in invoices
    )


    igst_total = sum(

        float(
            i.get(
                "igst",
                0
            )
        )

        for i
        in invoices
    )


    total = sum(

        float(
            i.get(
                "grand_total",
                0
            )
        )

        for i
        in invoices
    )


    st.subheader(
        t(
            "sales_summary"
        )
    )


    a, b, c = (
        st.columns(3)
    )


    a.metric(
        t(
            "taxable_sales"
        ),

        money(
            taxable
        )
    )


    b.metric(
        t(
            "total_gst"
        ),

        money(

            cgst_total
            +
            sgst_total
            +
            igst_total
        )
    )


    c.metric(
        t(
            "total_sales"
        ),

        money(
            total
        )
    )


    d, e, f = (
        st.columns(3)
    )


    d.metric(
        t(
            "cgst"
        ),

        money(
            cgst_total
        )
    )


    e.metric(
        t(
            "sgst"
        ),

        money(
            sgst_total
        )
    )


    f.metric(
        t(
            "igst"
        ),

        money(
            igst_total
        )
    )


# ============================================================
# SETTINGS
# ============================================================

elif menu == "settings":

    st.title(
        f"⚙️ {t('settings')}"
    )


    st.subheader(
        t(
            "company_profile"
        )
    )


    with st.form(
        "settings_form"
    ):

        company_name = (
            st.text_input(

                t(
                    "company_name"
                ),

                value=
                current_user.get(
                    "company_name"
                )
                or ""
            )
        )


        company_address = (
            st.text_area(

                t(
                    "address"
                ),

                value=
                current_user.get(
                    "company_address"
                )
                or ""
            )
        )


        company_gstin = (
            st.text_input(

                t(
                    "gstin"
                ),

                value=
                current_user.get(
                    "company_gstin"
                )
                or ""
            )
        )


        company_phone = (
            st.text_input(

                t(
                    "phone"
                ),

                value=
                current_user.get(
                    "company_phone"
                )
                or ""
            )
        )


        company_email = (
            st.text_input(

                t(
                    "email"
                ),

                value=
                current_user.get(
                    "company_email"
                )
                or ""
            )
        )


        state0 = (

            current_user.get(
                "company_state"
            )

            if
            current_user.get(
                "company_state"
            )
            in STATES

            else
            "Maharashtra"
        )


        company_state = (
            st.selectbox(

                t(
                    "state"
                ),

                STATES,

                index=
                STATES.index(
                    state0
                ),

                format_func=
                lambda s:
                STATE_LABELS.get(
                    s,
                    s
                )
            )
        )


        save_settings = (
            st.form_submit_button(

                t(
                    "save_settings"
                ),

                use_container_width=True,

                type="primary"
            )
        )


    if save_settings:

        with engine.begin() as con:

            con.execute(

                update(users)

                .where(
                    users.c.id
                    ==
                    USER_ID
                )

                .values(

                    company_name=
                        company_name.strip(),

                    company_address=
                        company_address.strip(),

                    company_gstin=
                        company_gstin.strip(),

                    company_phone=
                        company_phone.strip(),

                    company_email=
                        company_email.strip(),

                    company_state=
                        company_state,
                )
            )


        st.success(
            t(
                "settings_saved"
            )
        )


        st.rerun()


    # ========================================================
    # BACKUP
    # ========================================================

    st.markdown(
        "---"
    )


    st.subheader(
        f"💾 {t('backup')}"
    )


    st.caption(
        t(
            "backup_help"
        )
    )


    backup_data = {

        "generated_at":
            datetime.utcnow()
            .isoformat(),

        "business": {

            key:
            current_user.get(
                key
            )

            for key in [

                "company_name",
                "company_address",
                "company_gstin",
                "company_phone",
                "company_email",
                "company_state"
            ]
        },

        "customers":
            customers,

        "products":
            products,

        "invoices":
            invoices,
    }


    st.download_button(

        t(
            "download_backup"
        ),

        json.dumps(
            backup_data,
            ensure_ascii=False,
            indent=2,
            default=str
        ).encode(
            "utf-8"
        ),

        "gst_sathi_backup.json",

        "application/json",

        use_container_width=True,
    )


    # ========================================================
    # MOBILE
    # ========================================================

    st.markdown(
        "---"
    )


    st.subheader(
        f"📱 {t('phone_install')}"
    )


    st.info(
        t(
            "phone_install_help"
        )
    )
