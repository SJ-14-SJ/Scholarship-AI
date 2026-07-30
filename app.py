import os
import html
import pandas as pd
import streamlit as st
from dotenv import load_dotenv


# ------------------------------------------------------------
# App configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="ScholarMatch AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ------------------------------------------------------------
# File paths
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(
    BASE_DIR,
    "scholarships_database_v2.csv"
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_PATH, override=True)


# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f8fafc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 38px 42px;
        border-radius: 24px;
        margin-bottom: 30px;
        background: linear-gradient(
            135deg,
            #eef2ff 0%,
            #f8fafc 55%,
            #eff6ff 100%
        );
        border: 1px solid #dbe4f0;
        box-shadow: 0 8px 30px rgba(15, 23, 42, 0.05);
    }

    .hero h1 {
        font-size: 42px;
        line-height: 1.15;
        margin: 0 0 10px 0;
        color: #172554;
        font-weight: 750;
    }

    .hero p {
        font-size: 17px;
        line-height: 1.7;
        margin: 0;
        color: #475569;
        max-width: 780px;
    }

    .section-title {
        color: #172554;
        font-size: 25px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 20px;
    }

    .profile-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 6px;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
    }

    .result-title {
        color: #172554;
        font-size: 25px;
        font-weight: 700;
        margin-top: 15px;
    }

    .match-score {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: #eef2ff;
        color: #3730a3;
        font-weight: 700;
        font-size: 15px;
        margin: 4px 0 14px 0;
    }

    .field-tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 8px;
        background: #f1f5f9;
        color: #475569;
        font-size: 13px;
        margin-bottom: 12px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        padding: 10px 0 20px 0;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 12px 15px;
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
    }

    div[data-testid="stMetricValue"] {
        color: #172554;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Load scholarship database
# ------------------------------------------------------------

if not os.path.exists(CSV_PATH):

    st.error("Scholarship database not found.")

    st.write(
        "Make sure these files are in the same folder as app.py:"
    )

    st.code(
        """
app.py
scholarships_database_v2.csv
.env
"""
    )

    st.stop()


try:
    df = pd.read_csv(CSV_PATH)

except Exception as e:

    st.error("Could not read the scholarship database.")
    st.code(str(e))
    st.stop()


# ------------------------------------------------------------
# Required database fields
# ------------------------------------------------------------

required_columns = [
    "scholarship_name",
    "provider",
    "country",
    "degree_level",
    "field",
    "min_cgpa_10",
    "funding_type",
    "funding_tags",
    "funding_details",
    "deadline",
    "required_documents",
    "official_url",
    "eligibility_notes"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error("Some required columns are missing from the CSV.")

    st.write("Missing columns:")
    st.write(missing_columns)

    st.write("Available columns:")
    st.write(list(df.columns))

    st.stop()


# ------------------------------------------------------------
# Clean database
# ------------------------------------------------------------

for column in required_columns:

    df[column] = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


df["min_cgpa_num"] = pd.to_numeric(
    df["min_cgpa_10"],
    errors="coerce"
)

df["deadline_date"] = pd.to_datetime(
    df["deadline"],
    errors="coerce"
)

TODAY = pd.Timestamp.today().normalize()


# ------------------------------------------------------------
# Country normalization
# ------------------------------------------------------------

def normalize_country(value):

    value = str(value).strip().lower()

    mapping = {
        "usa": "usa",
        "us": "usa",
        "u.s.": "usa",
        "u.s.a.": "usa",
        "united states": "usa",
        "united states of america": "usa",

        "uk": "uk",
        "united kingdom": "uk",
        "england": "uk",
        "great britain": "uk",

        "germany": "germany",
        "deutschland": "germany",

        "south korea": "south korea",
        "korea": "south korea",
        "republic of korea": "south korea",

        "australia": "australia",
        "canada": "canada",
        "france": "france",
        "netherlands": "netherlands",
        "japan": "japan",
        "sweden": "sweden",
        "switzerland": "switzerland",
        "ireland": "ireland",
        "new zealand": "new zealand",
        "austria": "austria",
        "india": "india"
    }

    return mapping.get(value, value)


# ------------------------------------------------------------
# Degree normalization
# ------------------------------------------------------------

def normalize_degree(value):

    value = str(value).strip().lower()

    mapping = {
        "bachelor": "bachelors",
        "bachelors": "bachelors",
        "bachelor's": "bachelors",
        "undergraduate": "bachelors",
        "undergraduate degree": "bachelors",

        "master": "masters",
        "masters": "masters",
        "master's": "masters",
        "postgraduate": "masters",
        "postgraduate degree": "masters",

        "phd": "phd",
        "ph.d": "phd",
        "ph.d.": "phd",
        "doctorate": "phd",
        "doctoral": "phd",
        "doctoral degree": "phd"
    }

    return mapping.get(value, value)


df["country_normalized"] = df["country"].apply(
    normalize_country
)

df["degree_normalized"] = df["degree_level"].apply(
    normalize_degree
)


# ------------------------------------------------------------
# Field normalization
# ------------------------------------------------------------

def normalize_field(text):

    text = str(text).lower().strip()

    replacements = {
        "&": " and ",
        "/": " ",
        "-": " ",
        "_": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())


# ------------------------------------------------------------
# Related field groups
# ------------------------------------------------------------

FIELD_GROUPS = {

    "computer": {
        "computer science",
        "data science",
        "artificial intelligence",
        "ai",
        "machine learning",
        "deep learning",
        "information technology",
        "information systems",
        "software engineering",
        "cyber security",
        "cybersecurity",
        "computer engineering",
        "informatics",
        "data analytics",
        "analytics",
        "digital sciences",
        "technology"
    },

    "engineering": {
        "engineering",
        "engineering sciences",
        "mechanical engineering",
        "electrical engineering",
        "electronics engineering",
        "electronics",
        "civil engineering",
        "chemical engineering",
        "industrial engineering",
        "aerospace engineering",
        "automotive engineering",
        "environmental engineering",
        "biomedical engineering",
        "materials engineering",
        "technology"
    },

    "business": {
        "business",
        "business administration",
        "management",
        "economics",
        "finance",
        "accounting",
        "marketing",
        "entrepreneurship",
        "commerce",
        "business analytics"
    },

    "science": {
        "science",
        "natural sciences",
        "physics",
        "chemistry",
        "mathematics",
        "statistics",
        "astronomy",
        "earth science",
        "environmental science"
    },

    "life_science": {
        "biology",
        "biotechnology",
        "biochemistry",
        "life sciences",
        "genetics",
        "microbiology",
        "neuroscience",
        "molecular biology"
    },

    "health": {
        "medicine",
        "medical",
        "health",
        "health sciences",
        "public health",
        "nursing",
        "pharmacy",
        "dentistry",
        "physiotherapy",
        "clinical sciences"
    },

    "social_science": {
        "social sciences",
        "sociology",
        "psychology",
        "political science",
        "international relations",
        "social work",
        "development studies",
        "anthropology"
    },

    "humanities": {
        "humanities",
        "history",
        "philosophy",
        "literature",
        "languages",
        "linguistics",
        "cultural studies",
        "arts"
    },

    "law": {
        "law",
        "legal studies",
        "international law"
    },

    "architecture": {
        "architecture",
        "urban planning",
        "design",
        "interior design",
        "landscape architecture"
    },

    "education": {
        "education",
        "teaching",
        "educational studies"
    }
}


def get_field_groups(field_text):

    field_text = normalize_field(field_text)

    matched_groups = set()

    for group_name, keywords in FIELD_GROUPS.items():

        for keyword in keywords:

            keyword = normalize_field(keyword)

            if keyword in field_text:
                matched_groups.add(group_name)

    return matched_groups


# ------------------------------------------------------------
# Field matching
# ------------------------------------------------------------

def field_match_type(scholarship_field, user_field):

    scholarship_field = normalize_field(
        scholarship_field
    )

    user_field = normalize_field(
        user_field
    )

    if not user_field:
        return "broad"

    broad_terms = [
        "all fields",
        "all field",
        "all postgraduate fields",
        "all postgraduate",
        "all disciplines",
        "all discipline",
        "any field",
        "any discipline"
    ]

    for term in broad_terms:

        if term in scholarship_field:
            return "broad"

    if user_field == scholarship_field:
        return "exact"

    if user_field in scholarship_field:
        return "exact"

    if scholarship_field in user_field:
        return "exact"

    user_groups = get_field_groups(user_field)
    scholarship_groups = get_field_groups(scholarship_field)

    if user_groups.intersection(scholarship_groups):
        return "related"

    user_words = set(user_field.split())
    scholarship_words = set(scholarship_field.split())

    important_words = {
        "computer",
        "science",
        "data",
        "artificial",
        "intelligence",
        "machine",
        "learning",
        "engineering",
        "business",
        "management",
        "economics",
        "finance",
        "biology",
        "health",
        "medicine",
        "mathematics",
        "physics",
        "chemistry",
        "law",
        "education",
        "architecture",
        "design",
        "psychology",
        "history",
        "political",
        "social"
    }

    meaningful_user_words = user_words.intersection(
        important_words
    )

    meaningful_scholarship_words = scholarship_words.intersection(
        important_words
    )

    if meaningful_user_words.intersection(
        meaningful_scholarship_words
    ):
        return "related"

    return "none"


# ------------------------------------------------------------
# Funding matching
# ------------------------------------------------------------

def funding_matches(tags, funding_preference):

    if funding_preference == "Any":
        return True

    tags = normalize_field(tags)

    tag_list = [
        item.strip()
        for item in tags.split(",")
    ]

    if funding_preference == "Full Funding":
        return "full" in tag_list

    if funding_preference == "Partial Funding":
        return "partial" in tag_list

    if funding_preference == "Tuition":
        return "tuition" in tag_list

    if funding_preference == "Living Expenses":
        return "living" in tag_list

    return False


# ------------------------------------------------------------
# Deadline helpers
# ------------------------------------------------------------

def deadline_status(date):

    if pd.isna(date):
        return "Deadline varies"

    days_left = (date - TODAY).days

    if days_left < 0:
        return "Deadline passed"

    if days_left <= 7:
        return f"Urgent — {days_left} days left"

    if days_left <= 30:
        return f"Coming soon — {days_left} days left"

    if days_left <= 90:
        return f"Upcoming — {days_left} days left"

    return f"Future deadline — {days_left} days left"


def deadline_score(date):

    if pd.isna(date):
        return 0

    days_left = (date - TODAY).days

    if days_left < 0:
        return 0

    if days_left <= 7:
        return 10

    if days_left <= 30:
        return 8

    if days_left <= 90:
        return 6

    return 4


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>ScholarMatch AI</h1>
        <p>
            Find scholarships that fit your academic profile,
            preferred destinations and funding requirements.
            Enter your details below to see the most relevant
            opportunities from the database.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Database information
# ------------------------------------------------------------

with st.expander("Database information"):

    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.metric(
            "Scholarships",
            len(df)
        )

    with info_col2:
        st.metric(
            "Countries",
            df["country"].nunique()
        )

    with info_col3:
        st.metric(
            "Degree categories",
            df["degree_level"].nunique()
        )

    coverage = (
        df.groupby(
            [
                "country",
                "degree_level"
            ]
        )
        .size()
        .reset_index(
            name="Scholarships"
        )
        .sort_values(
            [
                "country",
                "degree_level"
            ]
        )
    )

    st.dataframe(
        coverage,
        use_container_width=True,
        hide_index=True
    )


# ------------------------------------------------------------
# Student profile
# ------------------------------------------------------------

st.markdown(
    '<div class="section-title">Build your profile</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Tell us what you are looking for and we will filter the database accordingly.'
    '</div>',
    unsafe_allow_html=True
)

profile_col1, profile_col2 = st.columns(2)

with profile_col1:

    field = st.text_input(
        "Field of study",
        value="",
        placeholder="e.g. Computer Science, Business, Biology"
    )

    degree = st.selectbox(
        "Degree level",
        [
            "Bachelor's",
            "Master's",
            "PhD"
        ]
    )

    cgpa = st.number_input(
        "CGPA",
        min_value=0.0,
        max_value=10.0,
        value=8.5,
        step=0.1
    )


with profile_col2:

    available_countries = sorted(
        df["country"].unique().tolist()
    )

    countries = st.multiselect(
        "Target countries",
        available_countries,
        default=[]
    )

    funding = st.selectbox(
        "Funding preference",
        [
            "Any",
            "Full Funding",
            "Partial Funding",
            "Tuition",
            "Living Expenses"
        ]
    )

    email = st.text_input(
        "Email address",
        placeholder="your@email.com"
    )


st.write("")

search_clicked = st.button(
    "Find Scholarships",
    type="primary",
    use_container_width=True
)


# ------------------------------------------------------------
# Matching engine
# ------------------------------------------------------------

if search_clicked:

    if not countries:

        st.warning(
            "Please select at least one target country."
        )

        st.stop()

    if not field.strip():

        st.warning(
            "Please enter your field of study."
        )

        st.stop()

    selected_countries = [
        normalize_country(country)
        for country in countries
    ]

    selected_degree = normalize_degree(
        degree
    )

    # Country filter
    country_results = df[
        df["country_normalized"].isin(
            selected_countries
        )
    ].copy()

    country_count = len(country_results)

    # Degree filter
    degree_results = country_results[
        country_results["degree_normalized"]
        == selected_degree
    ].copy()

    degree_count = len(degree_results)

    # Field matching
    degree_results["field_match_type"] = (
        degree_results["field"].apply(
            lambda value: field_match_type(
                value,
                field
            )
        )
    )

    exact_results = degree_results[
        degree_results["field_match_type"] == "exact"
    ].copy()

    related_results = degree_results[
        degree_results["field_match_type"] == "related"
    ].copy()

    broad_results = degree_results[
        degree_results["field_match_type"] == "broad"
    ].copy()

    specific_results = pd.concat(
        [
            exact_results,
            related_results
        ],
        ignore_index=True
    )

    if len(specific_results) > 0:

        field_results = pd.concat(
            [
                specific_results,
                broad_results
            ],
            ignore_index=True
        )

    else:

        field_results = broad_results.copy()

    field_results = field_results.drop_duplicates(
        subset=[
            "scholarship_name",
            "provider",
            "country",
            "degree_level"
        ]
    ).copy()

    field_count = len(field_results)

    # CGPA filter
    field_results["cgpa_match"] = (
        field_results["min_cgpa_num"].isna()
        |
        (
            cgpa >= field_results["min_cgpa_num"]
        )
    )

    cgpa_results = field_results[
        field_results["cgpa_match"]
    ].copy()

    cgpa_count = len(cgpa_results)

    # Funding filter
    cgpa_results["funding_match"] = (
        cgpa_results["funding_tags"].apply(
            lambda value: funding_matches(
                value,
                funding
            )
        )
    )

    final_results = cgpa_results[
        cgpa_results["funding_match"]
    ].copy()

    funding_count = len(final_results)

    # No results
    if final_results.empty:

        st.error(
            "No scholarships match all of your current filters."
        )

        count_col1, count_col2, count_col3, count_col4, count_col5 = (
            st.columns(5)
        )

        with count_col1:
            st.metric("Country", country_count)

        with count_col2:
            st.metric("Degree", degree_count)

        with count_col3:
            st.metric("Field", field_count)

        with count_col4:
            st.metric("CGPA", cgpa_count)

        with count_col5:
            st.metric("Funding", funding_count)

        st.info(
            "Try relaxing one filter at a time. "
            "For example, select another country, choose "
            "Any under funding, or try a broader field."
        )

        st.session_state["results"] = final_results

        st.session_state["profile"] = {
            "field": field,
            "degree": degree,
            "cgpa": cgpa,
            "countries": countries,
            "funding": funding,
            "email": email,
            "country_count": country_count,
            "degree_count": degree_count,
            "field_count": field_count,
            "cgpa_count": cgpa_count,
            "funding_count": funding_count
        }

    else:

        def calculate_score(row):

            score = 60

            if row["field_match_type"] == "exact":
                score += 25

            elif row["field_match_type"] == "related":
                score += 18

            elif row["field_match_type"] == "broad":
                score += 10

            if pd.isna(row["min_cgpa_num"]):

                score += 2

            else:

                margin = (
                    cgpa
                    - float(row["min_cgpa_num"])
                )

                if margin >= 1.5:
                    score += 8

                elif margin >= 1.0:
                    score += 6

                elif margin >= 0.5:
                    score += 4

                else:
                    score += 2

            score += deadline_score(
                row["deadline_date"]
            )

            return min(100, int(score))

        final_results["match_score"] = (
            final_results.apply(
                calculate_score,
                axis=1
            )
        )

        final_results = final_results.sort_values(
            by=[
                "match_score",
                "deadline_date"
            ],
            ascending=[
                False,
                True
            ],
            na_position="last"
        ).reset_index(drop=True)

        st.session_state["results"] = final_results

        st.session_state["profile"] = {
            "field": field,
            "degree": degree,
            "cgpa": cgpa,
            "countries": countries,
            "funding": funding,
            "email": email,
            "country_count": country_count,
            "degree_count": degree_count,
            "field_count": field_count,
            "cgpa_count": cgpa_count,
            "funding_count": funding_count
        }


# ------------------------------------------------------------
# Results
# ------------------------------------------------------------

if "results" in st.session_state:

    results = st.session_state["results"]

    profile = st.session_state.get(
        "profile",
        {}
    )

    if results.empty:
        st.stop()

    st.success(
        f"{len(results)} scholarships match your profile."
    )

    st.markdown(
        '<div class="section-title">Your search</div>',
        unsafe_allow_html=True
    )

    summary1, summary2, summary3, summary4, summary5 = st.columns(5)

    with summary1:
        st.metric(
            "Degree",
            profile.get("degree", "-")
        )

    with summary2:
        st.metric(
            "CGPA",
            profile.get("cgpa", "-")
        )

    with summary3:
        st.metric(
            "Countries",
            len(
                profile.get(
                    "countries",
                    []
                )
            )
        )

    with summary4:
        st.metric(
            "Funding",
            profile.get("funding", "-")
        )

    with summary5:
        st.metric(
            "Matches",
            len(results)
        )

    st.write("")

    # Field summary
    specific_count = len(
        results[
            results["field_match_type"].isin(
                [
                    "exact",
                    "related"
                ]
            )
        ]
    )

    broad_count = len(
        results[
            results["field_match_type"] == "broad"
        ]
    )

    if specific_count > 0:

        st.info(
            f"{specific_count} result(s) specifically match or "
            f"relate to {profile['field']}. "
            f"{broad_count} additional result(s) accept students "
            f"from a broad range of fields."
        )

    else:

        st.info(
            f"No field-specific scholarships were found for "
            f"{profile['field']} in your selected country and "
            f"degree combination. The results shown are open "
            f"to a broad range of fields."
        )

    st.markdown(
        '<div class="section-title">Recommended scholarships</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Results are ranked using field relevance, CGPA fit and deadline timing.'
        '</div>',
        unsafe_allow_html=True
    )

    # Scholarship cards
    for index, row in results.iterrows():

        rank = index + 1
        score = int(row["match_score"])

        if score >= 90:
            badge = "Excellent match"

        elif score >= 80:
            badge = "Strong match"

        else:
            badge = "Good match"

        with st.container(border=True):

            st.markdown(
                f'<div class="result-title">'
                f'#{rank} — {html.escape(str(row["scholarship_name"]))}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="match-score">'
                f'{score}% match · {badge}'
                f'</div>',
                unsafe_allow_html=True
            )

            if row["field_match_type"] == "exact":

                st.success(
                    f"Field match: {profile['field']}"
                )

            elif row["field_match_type"] == "related":

                st.info(
                    f"Related field: {profile['field']}"
                )

            else:

                st.info(
                    "Open to a broad range of fields"
                )

            detail_col1, detail_col2 = st.columns(2)

            with detail_col1:

                st.write(
                    f"**Provider:** {row['provider']}"
                )

                st.write(
                    f"**Country:** {row['country']}"
                )

                st.write(
                    f"**Degree:** {row['degree_level']}"
                )

                st.write(
                    f"**Field:** {row['field']}"
                )

            with detail_col2:

                st.write(
                    f"**Funding:** {row['funding_details']}"
                )

                minimum_cgpa = row["min_cgpa_num"]

                if pd.isna(minimum_cgpa):

                    st.write(
                        "**Minimum CGPA:** No published cutoff"
                    )

                else:

                    st.write(
                        f"**Minimum CGPA:** {minimum_cgpa}/10"
                    )

                st.write(
                    f"**Deadline:** {row['deadline']}"
                )

                deadline_text = deadline_status(
                    row["deadline_date"]
                )

                st.write(
                    f"**Status:** {deadline_text}"
                )

            with st.expander("Why this scholarship?"):

                st.success(
                    "Country matches your selection."
                )

                st.success(
                    "Degree level matches your selection."
                )

                if row["field_match_type"] == "exact":

                    st.success(
                        f"The scholarship field directly matches "
                        f"your field: {profile['field']}."
                    )

                elif row["field_match_type"] == "related":

                    st.info(
                        f"The scholarship field is related to "
                        f"your field: {profile['field']}."
                    )

                else:

                    st.info(
                        "The scholarship is open to students "
                        "from a broad range of fields."
                    )

                if pd.isna(row["min_cgpa_num"]):

                    st.info(
                        "No published numeric CGPA cutoff is listed."
                    )

                else:

                    st.success(
                        f"Your CGPA ({profile['cgpa']}) meets "
                        f"the published minimum "
                        f"({row['min_cgpa_num']})."
                    )

                st.success(
                    f"Funding matches your preference: "
                    f"{profile['funding']}."
                )

                if row["eligibility_notes"]:

                    st.warning(
                        row["eligibility_notes"]
                    )

            st.write("**Required documents**")

            st.write(
                row["required_documents"]
            )

            if row["official_url"]:

                st.link_button(
                    "View official scholarship",
                    row["official_url"]
                )


    # --------------------------------------------------------
    # Email digest
    # --------------------------------------------------------

    st.write("")
    st.markdown(
        '<div class="section-title">Email your results</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Send a copy of your scholarship results to the email address provided above.'
        '</div>',
        unsafe_allow_html=True
    )

    current_email = profile.get(
        "email",
        ""
    ).strip()

    if current_email:

        st.write(
            f"Results will be sent to **{current_email}**."
        )

        send_email = st.button(
            "Send Scholarship Digest",
            type="primary",
            use_container_width=True
        )

        if send_email:

            resend_key = os.getenv(
                "RESEND_API_KEY",
                ""
            ).strip()

            from_email = "onboarding@resend.dev"

            if not resend_key:

                st.error(
                    "RESEND_API_KEY was not found."
                )

                st.info(
                    """
Add your Resend API key to the .env file:

RESEND_API_KEY=your_resend_api_key
"""
                )

            else:

                try:

                    import resend

                    resend.api_key = resend_key

                    email_html = f"""
                    <html>
                    <body style="
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #1e293b;
                        background: #f8fafc;
                        padding: 25px;
                    ">

                    <div style="
                        max-width: 700px;
                        margin: auto;
                        background: white;
                        padding: 30px;
                        border-radius: 14px;
                        border: 1px solid #e2e8f0;
                    ">

                    <h1 style="color:#172554;">
                        ScholarMatch AI
                    </h1>

                    <p>
                        Here are the scholarship opportunities
                        matched to your profile.
                    </p>

                    <hr>

                    <p>
                        <b>Field:</b>
                        {html.escape(str(profile.get("field", "-")))}<br>

                        <b>Degree:</b>
                        {html.escape(str(profile.get("degree", "-")))}<br>

                        <b>CGPA:</b>
                        {html.escape(str(profile.get("cgpa", "-")))}<br>

                        <b>Funding preference:</b>
                        {html.escape(str(profile.get("funding", "-")))}
                    </p>

                    <hr>
                    """

                    for i, (_, row) in enumerate(
                        results.head(15).iterrows(),
                        start=1
                    ):

                        minimum_cgpa_text = (
                            "No published cutoff"
                            if pd.isna(row["min_cgpa_num"])
                            else f"{row['min_cgpa_num']}/10"
                        )

                        email_html += f"""
                        <div style="
                            border:1px solid #e2e8f0;
                            border-radius:12px;
                            padding:18px;
                            margin-bottom:18px;
                        ">

                        <h2 style="color:#172554;">
                            #{i} — {html.escape(str(row['scholarship_name']))}
                        </h2>

                        <p>
                            <b>Match:</b>
                            {int(row['match_score'])}%
                        </p>

                        <p>
                            <b>Provider:</b>
                            {html.escape(str(row['provider']))}<br>

                            <b>Country:</b>
                            {html.escape(str(row['country']))}<br>

                            <b>Degree:</b>
                            {html.escape(str(row['degree_level']))}<br>

                            <b>Field:</b>
                            {html.escape(str(row['field']))}<br>

                            <b>Funding:</b>
                            {html.escape(str(row['funding_details']))}<br>

                            <b>Minimum CGPA:</b>
                            {minimum_cgpa_text}<br>

                            <b>Deadline:</b>
                            {html.escape(str(row['deadline']))}
                        </p>

                        <p>
                            <a href="{row['official_url']}">
                                View official scholarship
                            </a>
                        </p>

                        </div>
                        """

                    email_html += """
                    <hr>

                    <p style="color:#64748b;">
                        Please verify eligibility, deadlines,
                        funding details and application requirements
                        on the official scholarship website before applying.
                    </p>

                    </div>

                    </body>
                    </html>
                    """

                    resend.Emails.send(
                        {
                            "from": from_email,
                            "to": [current_email],
                            "subject": "Your Scholarship Results",
                            "html": email_html
                        }
                    )

                    st.success(
                        "Scholarship digest sent successfully."
                    )

                    st.write(
                        "Check your inbox and spam/junk folder."
                    )

                except ImportError:

                    st.error(
                        "The Resend package is not installed."
                    )

                    st.code(
                        "pip install resend"
                    )

                except Exception as e:

                    error_text = str(e)

                    st.error(
                        "The email could not be sent."
                    )

                    st.code(
                        error_text
                    )

                    if (
                        "onboarding@resend.dev"
                        in error_text.lower()
                        or "verify"
                        in error_text.lower()
                        or "domain"
                        in error_text.lower()
                        or "sender"
                        in error_text.lower()
                    ):

                        st.warning(
                            """
The current Resend testing sender may be restricted
for your account.

If Resend asks you to verify a sender, verify an email
address or domain in your Resend account and then use
that verified address as the sender.
"""
                        )

    else:

        st.info(
            "Enter an email address above if you would like "
            "to receive your scholarship results by email."
        )


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.divider()

st.markdown(
    """
    <div class="footer">
        Scholarship information should be verified on the
        official provider website before applying.
    </div>
    """,
    unsafe_allow_html=True
)