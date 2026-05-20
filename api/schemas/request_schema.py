from pydantic import BaseModel


class ClaimRequest(BaseModel):

    claim_id: str

    provider_id: str

    diagnosis_code: str

    procedure_code: str

    billed_amount: float

    date: str