FEATURE_EXPLANATION_MAP = {

    # FINANCIAL FEATURES

    "billed_amount":
        "The billed claim amount influenced the denial risk assessment.",

    "amount_to_expected_ratio":
        "The billed amount and the expected amount significantly vary from each other",

    "amount_to_average_ratio":
        "The billed amount and the historical average significantly vary from each other.",

    "high_cost_flag":
        "The billed amount is unusually high for this claim type.",

    # PROVIDER FEATURES

    "provider_claim_count":
        "The provider has a significant historical claim submission volume.",

    "provider_denial_rate":
        "The provider historically has a high insurance denial rate.",

    "provider_high_risk":
        "The provider is categorized as high-risk based on historical claims.",

    # DIAGNOSIS FEATURES

    "severity_score":
        "The clinical severity level of the diagnosis is high.",

    "diagnosis_claim_count":
        "The diagnosis pattern has historical claim frequency significance.",

    "rare_diagnosis_flag":
        "The diagnosis code is uncommon and may require additional review.",

    # MISSING VALUE FLAGS

    "is_diagnosis_missing":
        "Diagnosis information is missing or incomplete.",

    "is_procedure_missing":
        "Procedure coding information is missing.",

    "is_amount_missing":
        "Claim billing amount information is unavailable.",

    "diag_proc_both_missing":
        "Both diagnosis and procedure details are incomplete.",

    # TEMPORAL FEATURES

    "claim_year":
        "Claim submission year patterns contributed to the risk assessment.",

    "claim_month":
        "Seasonal or monthly claim submission trends impacted the review.",

    "claim_weekday":
        "The timing of the claim submission may impact review patterns.",

    "is_weekend_claim":
        "Weekend claims historically show elevated denial probability.",

    # SPECIALTY FEATURES

    "specialty_cardiology":
        "The claim is associated with cardiology specialty services.",

    "specialty_neurology":
        "The claim is associated with neurology specialty services.",

    "specialty_orthopedic":
        "The claim is associated with orthopedic specialty services.",

    "specialty_general":
        "The claim falls under general medical specialty services.",

    "specialty_unknown":
        "Provider specialty information is unavailable.",

    # DIAGNOSIS CATEGORY FEATURES

    "category_heart":
        "The diagnosis is related to cardiac or heart-related conditions.",

    "category_bone":
        "The diagnosis is related to bone or orthopedic conditions.",

    "category_fever":
        "The diagnosis involves fever-related clinical conditions.",

    "category_skin":
        "The diagnosis is associated with dermatological or skin conditions.",

    "category_diabetes":
        "The diagnosis is associated with diabetic conditions.",

    "category_cold":
        "The diagnosis is related to cold or respiratory conditions.",

    # LOCATION FEATURES

    "location_encoded":
        "Claim location patterns contributed to elevated denial risk."
}