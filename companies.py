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
    {"name": "Toast",           "board_token": "toast",         "category": "food"},
    {"name": "Afresh",          "board_token": "afresh",        "category": "food"},
    {"name": "Flipdish",        "board_token": "flipdish",      "category": "food"},
    {"name": "Sweetgreen",      "board_token": "sweetgreen",    "category": "food"},
    {"name": "DoorDash",        "board_token": "doordashusa",   "category": "food"},
    {"name": "Too Good To Go",  "board_token": "toogoodtogo",   "category": "food"},
    {"name": "Zerocater",       "board_token": "zerocater",     "category": "food"},

    # --- CPG / Food Manufacturing ---
    {"name": "Daily Harvest",   "board_token": "dailyharvest",  "category": "food"},
    {"name": "Misfits Market",  "board_token": "misfitsmarket", "category": "food"},
    {"name": "Vega",            "board_token": "vega",          "category": "food"},

    # --- Grocery Tech ---
    {"name": "Instacart",       "board_token": "instacart",     "category": "food"},

    # --- Bay Area Mid-Size Tech ---
    {"name": "Samsara",         "board_token": "samsara",       "category": "analytics"},
    {"name": "Webflow",         "board_token": "webflow",       "category": "analytics"},
    {"name": "Taskrabbit",      "board_token": "taskrabbit",    "category": "analytics"},
    {"name": "Moloco",          "board_token": "moloco",        "category": "analytics"},
    {"name": "HoneyBook",       "board_token": "honeybook",     "category": "analytics"},
    {"name": "Domino Data Lab", "board_token": "dominodatalab", "category": "analytics"},
    {"name": "Doximity",        "board_token": "doximity",      "category": "analytics"},
    {"name": "Babylist",        "board_token": "babylist",      "category": "analytics"},
    {"name": "Moveworks",       "board_token": "moveworks",     "category": "analytics"},
    {"name": "Calm",            "board_token": "calm",          "category": "analytics"},
    {"name": "Liftoff",         "board_token": "liftoff",       "category": "analytics"},
    {"name": "NextRoll",        "board_token": "nextroll",      "category": "analytics"},
    {"name": "Marqeta",         "board_token": "marqeta",       "category": "analytics"},

    # --- Analytics / BI (broader targets) ---
    {"name": "Amplitude",       "board_token": "amplitude",      "category": "analytics"},
    {"name": "Mixpanel",        "board_token": "mixpanel",       "category": "analytics"},
    {"name": "Fivetran",        "board_token": "fivetran",       "category": "analytics"},
    {"name": "Hightouch",       "board_token": "hightouch",      "category": "analytics"},
    {"name": "dbt Labs",        "board_token": "dbtlabsinc",     "category": "analytics"},
]


# ─────────────────────────────────────────────
# LEVER COMPANIES
# API endpoint: https://api.lever.co/v0/postings/{company_id}?mode=json
# ─────────────────────────────────────────────

LEVER_COMPANIES = [
    # --- Food Tech / Restaurant Tech ---
    {"name": "Olo",              "company_id": "olo",            "category": "food"},
    {"name": "ChowNow",          "company_id": "chownow",        "category": "food"},
    {"name": "Restaurant365",    "company_id": "restaurant365",  "category": "food"},
    {"name": "Chef Robotics",    "company_id": "ChefRobotics",   "category": "food"},
    {"name": "Foodsmart",        "company_id": "foodsmart",      "category": "food"},
    {"name": "Thistle",          "company_id": "thistle.co",     "category": "food"},
    {"name": "Brightseed",       "company_id": "brightseedbio",  "category": "food"},
    {"name": "Bowery Farming",   "company_id": "boweryfarming",  "category": "food"},
    {"name": "Mom's Meals",      "company_id": "momsmeals",      "category": "food"},

    # --- Grocery / Delivery ---
    {"name": "Gopuff",           "company_id": "gopuff",         "category": "food"},

    # --- Analytics / BI (broader targets) ---
    {"name": "Metabase",         "company_id": "metabase",       "category": "analytics"},
]


# ─────────────────────────────────────────────
# WORKDAY COMPANIES
# Workday doesn't have a public REST API — scraping requires
# hitting their search endpoint with HTTP requests.
# URL pattern: https://{subdomain}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/jobs
# These will need per-company verification; placeholders provided.
# ─────────────────────────────────────────────

WORKDAY_COMPANIES = [
    # --- Food & Hospitality ---
    {
        "name": "Sysco",
        "url": "https://sysco.wd5.myworkdayjobs.com/wday/cxs/sysco/syscocareers/jobs",
        "category": "food",
    },
    {
        "name": "Kraft Heinz",
        "url": "https://heinz.wd1.myworkdayjobs.com/wday/cxs/heinz/KraftHeinz_Careers/jobs",
        "category": "food",
    },
    {
        "name": "Conagra Brands",
        "url": "https://conagrabrands.wd1.myworkdayjobs.com/wday/cxs/conagrabrands/Careers_US/jobs",
        "category": "food",
    },
    # --- Analytics / BI ---
    {
        "name": "Leidos",
        "url": "https://leidos.wd5.myworkdayjobs.com/wday/cxs/leidos/External/jobs",
        "category": "analytics",
    },
    {
        "name": "Analog Devices",
        "url": "https://analogdevices.wd1.myworkdayjobs.com/wday/cxs/analogdevices/External/jobs",
        "category": "analytics",
    },
    {
        "name": "BeOne Medicines",
        "url": "https://beigene.wd5.myworkdayjobs.com/wday/cxs/beigene/BeiGene/jobs",
        "category": "analytics",
    },
    {
        "name": "Rosendin",
        "url": "https://rosendin.wd1.myworkdayjobs.com/wday/cxs/rosendin/Careers/jobs",
        "category": "analytics",
    },
]


# ─────────────────────────────────────────────
# ASHBY COMPANIES
# API endpoint: https://jobs.ashbyhq.com/api/non-user-graphql
# company_id is the slug from jobs.ashbyhq.com/{slug}
# ─────────────────────────────────────────────

ASHBY_COMPANIES = [
    # --- Analytics / BI --- (confirmed on Ashby)
    {"name": "Monte Carlo",     "company_id": "montecarlodata", "category": "analytics"},
    {"name": "Lightdash",       "company_id": "lightdash",      "category": "analytics"},
    {"name": "Cube Dev",        "company_id": "cube",           "category": "analytics"},
    {"name": "Airbyte",         "company_id": "airbyte",        "category": "analytics"},

    # --- Bay Area Mid-Size Tech (confirmed on Ashby) ---
    {"name": "Notion",          "company_id": "notion",         "category": "analytics"},
    {"name": "BetterUp",        "company_id": "betterup",       "category": "analytics"},
    {"name": "TRM Labs",        "company_id": "trm-labs",       "category": "analytics"},
]



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

    # Internships
    "data intern",
    "analytics intern",
    "analyst intern",
    "business intelligence intern",
    "BI intern",
    "data engineering intern",
    "reporting intern",
    "insights intern",
]


# ─────────────────────────────────────────────
# QUICK STATS (for README / logging)
# ─────────────────────────────────────────────

ALL_COMPANIES = GREENHOUSE_COMPANIES + LEVER_COMPANIES + WORKDAY_COMPANIES + ASHBY_COMPANIES

if __name__ == "__main__":
    print(f"Total companies: {len(ALL_COMPANIES)}")
    print(f"  Greenhouse: {len(GREENHOUSE_COMPANIES)}")
    print(f"  Lever:      {len(LEVER_COMPANIES)}")
    print(f"  Workday:    {len(WORKDAY_COMPANIES)}")
    print(f"Search keywords: {len(SEARCH_KEYWORDS)}")