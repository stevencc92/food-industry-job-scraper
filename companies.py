"""
companies.py — Master company list for job scraper
Organized by ATS platform: Greenhouse → Lever → Workday
Targeting: Food Tech, Restaurant Tech, Contract Food Service, CPG/Food Manufacturing
"""

# ─────────────────────────────────────────────
# GREENHOUSE COMPANIES
# API endpoint: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
# Board token is typically the slug shown below
# ─────────────────────────────────────────────

GREENHOUSE_COMPANIES = [
    # --- Food Tech / Restaurant Tech ---
    {"name": "Toast",           "board_token": "toastinc"},
    {"name": "Olo",             "board_token": "olo"},
    {"name": "Chowly",          "board_token": "chowly"},
    {"name": "Incentivio",      "board_token": "incentivio"},
    {"name": "Flipdish",        "board_token": "flipdish"},
    {"name": "Deliverect",      "board_token": "deliverect"},
    {"name": "Lunchbox",        "board_token": "lunchbox"},
    {"name": "Ovation",         "board_token": "ovation"},
    {"name": "Popmenu",         "board_token": "popmenu"},
    {"name": "Restaurant365",   "board_token": "restaurant365"},
    {"name": "Slingshot",       "board_token": "slingshotinsights"},
    {"name": "Tastewise",       "board_token": "tastewise"},
    {"name": "Afresh",          "board_token": "afresh"},
    {"name": "Galley Solutions","board_token": "galleysolutions"},
    {"name": "Meez",            "board_token": "meez"},
    {"name": "Kitchenary",      "board_token": "kitchenary"},

    # --- Contract Food Service ---
    {"name": "Aramark",         "board_token": "aramark"},
    {"name": "Compass Group",   "board_token": "compassgroupusa"},
    {"name": "Eurest",          "board_token": "eurest"},          # Compass sub-brand
    {"name": "Canteen",         "board_token": "canteen"},         # Compass sub-brand

    # --- CPG / Food Manufacturing ---
    {"name": "Impossible Foods","board_token": "impossiblefoods"},
    {"name": "Oatly",           "board_token": "oatly"},
    {"name": "Chobani",         "board_token": "chobani"},
    {"name": "Daily Harvest",   "board_token": "dailyharvest"},
    {"name": "Bright Farms",    "board_token": "brightfarms"},
    {"name": "Gotham Greens",   "board_token": "gothamgreens"},
    {"name": "Apeel Sciences",  "board_token": "apeelsciences"},
    {"name": "Miyoko's Creamery","board_token": "miyokos"},
    {"name": "Ripple Foods",    "board_token": "ripplefoods"},
    {"name": "Vega",            "board_token": "vega"},

    # --- Grocery Tech / Food Delivery ---
    {"name": "Instacart",       "board_token": "instacart"},
    {"name": "Good Food Institute", "board_token": "gfi"},
    {"name": "Foodshed",        "board_token": "foodshed"},
    {"name": "Misfits Market",  "board_token": "misfitsmarket"},
    {"name": "Imperfect Foods", "board_token": "imperfectfoods"},
]


# ─────────────────────────────────────────────
# LEVER COMPANIES
# API endpoint: https://api.lever.co/v0/postings/{company_id}?mode=json
# ─────────────────────────────────────────────

LEVER_COMPANIES = [
    # --- Food Tech / Restaurant Tech ---
    {"name": "SevenRooms",      "company_id": "sevenrooms"},
    {"name": "Revel Systems",   "company_id": "revelsystems"},
    {"name": "SpotOn",          "company_id": "spoton"},
    {"name": "Eataly",          "company_id": "eataly"},
    {"name": "Tock",            "company_id": "tock"},
    {"name": "Resy",            "company_id": "resy"},
    {"name": "Notch",           "company_id": "notchfinancial"},
    {"name": "Spoiler Alert",   "company_id": "spoileralert"},
    {"name": "Shelf Engine",    "company_id": "shelfengine"},

    # --- Contract Food Service ---
    {"name": "Sodexo",          "company_id": "sodexo"},
    {"name": "Elior North America", "company_id": "elior"},
    {"name": "Flik Hospitality","company_id": "flikhospitality"},  # Compass sub-brand

    # --- CPG / Food Manufacturing ---
    {"name": "Perfect Day",     "company_id": "perfectday"},
    {"name": "Eat Just",        "company_id": "eatjust"},
    {"name": "Nature's Fynd",   "company_id": "naturesfynd"},
    {"name": "Tender Food",     "company_id": "tenderfood"},
    {"name": "Motif FoodWorks", "company_id": "motiffoodworks"},

    # --- Grocery Tech / Supply Chain ---
    {"name": "Crisp",           "company_id": "crisp"},
    {"name": "KeHE Distributors","company_id": "kehe"},
    {"name": "Produce Pay",     "company_id": "producepay"},
    {"name": "AgriForce",       "company_id": "agriforce"},
]


# ─────────────────────────────────────────────
# WORKDAY COMPANIES
# Workday doesn't have a public REST API — scraping requires
# hitting their search endpoint with HTTP requests.
# URL pattern: https://{subdomain}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/jobs
# These will need per-company verification; placeholders provided.
# ─────────────────────────────────────────────

WORKDAY_COMPANIES = [
    # --- Contract Food Service ---
    {
        "name": "Aramark (Workday fallback)",
        "url": "https://aramark.wd5.myworkdayjobs.com/wday/cxs/aramark/Aramark_Careers/jobs",
    },
    {
        "name": "Sodexo (Workday fallback)",
        "url": "https://sodexo.wd3.myworkdayjobs.com/wday/cxs/sodexo/SodexoUSA/jobs",
    },
    {
        "name": "Sysco",
        "url": "https://sysco.wd5.myworkdayjobs.com/wday/cxs/sysco/Sysco_External/jobs",
    },
    {
        "name": "US Foods",
        "url": "https://usfoods.wd1.myworkdayjobs.com/wday/cxs/usfoods/USFoods/jobs",
    },

    # --- CPG / Food Manufacturing ---
    {
        "name": "Kraft Heinz",
        "url": "https://kraftheinz.wd5.myworkdayjobs.com/wday/cxs/kraftheinz/KraftHeinzCareers/jobs",
    },
    {
        "name": "Conagra Brands",
        "url": "https://conagra.wd5.myworkdayjobs.com/wday/cxs/conagra/Conagra/jobs",
    },
    {
        "name": "Post Holdings",
        "url": "https://post.wd1.myworkdayjobs.com/wday/cxs/post/PostHoldings/jobs",
    },
    {
        "name": "Hershey",
        "url": "https://hershey.wd5.myworkdayjobs.com/wday/cxs/hershey/HersheyCareers/jobs",
    },
    {
        "name": "McCormick",
        "url": "https://mccormick.wd5.myworkdayjobs.com/wday/cxs/mccormick/McCormick/jobs",
    },
    {
        "name": "TreeHouse Foods",
        "url": "https://treehousefoods.wd1.myworkdayjobs.com/wday/cxs/treehousefoods/TreeHouseFoods/jobs",
    },
]


# ─────────────────────────────────────────────
# SEARCH KEYWORDS
# Used to filter jobs across all platforms
# ─────────────────────────────────────────────

SEARCH_KEYWORDS = [
    # Core analytics titles
    "data analyst",
    "analytics analyst",
    "business analyst",
    "analytics engineer",
    "data engineer",
    "reporting analyst",
    "BI analyst",
    "business intelligence",

    # Domain-specific
    "food analyst",
    "operations analyst",
    "supply chain analyst",
    "menu analyst",
    "pricing analyst",
    "revenue analyst",
    "insights analyst",

    # Entry-friendly
    "junior analyst",
    "associate analyst",
    "analyst I",
    "data associate",
]


# ─────────────────────────────────────────────
# QUICK STATS (for README / logging)
# ─────────────────────────────────────────────

ALL_COMPANIES = GREENHOUSE_COMPANIES + LEVER_COMPANIES + WORKDAY_COMPANIES

if __name__ == "__main__":
    print(f"Total companies: {len(ALL_COMPANIES)}")
    print(f"  Greenhouse: {len(GREENHOUSE_COMPANIES)}")
    print(f"  Lever:      {len(LEVER_COMPANIES)}")
    print(f"  Workday:    {len(WORKDAY_COMPANIES)}")
    print(f"Search keywords: {len(SEARCH_KEYWORDS)}")