"""Deterministic scholarship matching, independent of the Streamlit UI."""
import re
import pandas as pd

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

            if re.search(r"\b" + re.escape(keyword) + r"\b", field_text):
                matched_groups.add(group_name)

    return matched_groups


def field_match_type(scholarship_field, user_field):

    scholarship_field = normalize_field(
        scholarship_field
    )

    user_field = normalize_field(
        user_field
    )

    if not user_field or not scholarship_field:
        return "none"

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

    if re.search(r"\b" + re.escape(user_field) + r"\b", scholarship_field):
        return "exact"

    if re.search(r"\b" + re.escape(scholarship_field) + r"\b", user_field):
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


def deadline_status(date, today=None):

    if pd.isna(date):
        return "Deadline varies"

    days_left = (pd.Timestamp(date).normalize() - pd.Timestamp(today if today is not None else pd.Timestamp.today()).normalize()).days

    if days_left < 0:
        return "Deadline passed"

    if days_left <= 7:
        return f"Urgent — {days_left} days left"

    if days_left <= 30:
        return f"Coming soon — {days_left} days left"

    if days_left <= 90:
        return f"Upcoming — {days_left} days left"

    return f"Future deadline — {days_left} days left"


def deadline_score(date, today=None):

    if pd.isna(date):
        return 0

    days_left = (pd.Timestamp(date).normalize() - pd.Timestamp(today if today is not None else pd.Timestamp.today()).normalize()).days

    if days_left < 0:
        return 0

    if days_left <= 7:
        return 10

    if days_left <= 30:
        return 8

    if days_left <= 90:
        return 6

    return 4



def find_scholarships(catalog, *, countries, degree, field, cgpa, funding="Any", today=None, include_expired=False):
    """Return ranked rows and filter counts without mutating the catalog.

    Unknown deadlines remain visible; known expired deadlines are omitted by
    default. CGPA is on a 0-10 scale; scores are heuristic, not probabilities.
    """
    if not 0 <= float(cgpa) <= 10:
        raise ValueError("CGPA must be between 0 and 10")
    if not str(field).strip():
        raise ValueError("Field of study cannot be empty")
    df = catalog.copy(deep=True)
    df["country_normalized"] = df["country"].apply(normalize_country)
    df["degree_normalized"] = df["degree_level"].apply(normalize_degree)
    df["field"] = df["field"].fillna("")
    df["funding_tags"] = df["funding_tags"].fillna("")
    df["min_cgpa_num"] = pd.to_numeric(df["min_cgpa_10"], errors="coerce")
    df["deadline_date"] = pd.to_datetime(df["deadline"], errors="coerce")
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

    if not include_expired:
        cutoff = pd.Timestamp(today if today is not None else pd.Timestamp.today()).normalize()
        final_results = final_results[final_results["deadline_date"].isna() | (final_results["deadline_date"] >= cutoff)].copy()
    counts = dict(country=country_count, degree=degree_count, field=field_count, cgpa=cgpa_count, funding=funding_count, available=len(final_results))
    if final_results.empty:
        final_results["match_score"] = pd.Series(dtype=int)
        return final_results, counts
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
            row["deadline_date"], today=today
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

    return final_results, counts
