import requests
import pandas as pd


def kitoltottseg(token, url="https://redcap.onkobank.com/redcap/api/"):

    data = {
        "token": token,
        "content": "metadata",
        "format": "json",
        "returnFormat": "json"
    }

    metadata = pd.DataFrame(
        requests.post(url, data=data).json()
    )

    required_by_form = (metadata[(metadata["required_field"] == "y")].groupby("form_name")["field_name"].apply(list).to_dict())

    records_request = {
        "token": token,
        "content": "record",
        "format": "json",
        "returnFormat": "json",
        "exportDataAccessGroups": "true"
    }

    records = pd.DataFrame(requests.post(url, data=records_request).json())

    all_required_fields = [field for fields in required_by_form.values() for field in fields]

    for field in all_required_fields:
        if field not in records.columns:
            records[field] = None

    completed_forms = {
        "krhzi_elbocstst_kvet_adatok",
        "ito_elbocsts_utni_adatok",
        "felvteli_adatok"
    }

    results = []


    for form, fields in required_by_form.items():
        
        temp = records.copy()
        
        complete_col = f"{form}_complete"
        
        if complete_col in temp.columns:
            temp = temp[temp[complete_col].astype(str) == "2"]

        values = temp[fields].apply(lambda col: col.str.strip() if col.dtype == "object" else col)

        temp["filled_required"] = (values.notna() & (values != "")).sum(axis=1)

        temp["total_required"] = len(fields)
        temp["form_name"] = form

        results.append(temp[["record_id", "redcap_data_access_group", "form_name", "filled_required", "total_required"]])

    completion = pd.concat(results, ignore_index=True)

    summary = (completion.groupby(["redcap_data_access_group", "form_name"])
    .agg(records=("record_id", "count"), filled_required=("filled_required", "sum"), total_required=("total_required", "sum"))
    .reset_index()
    )


    summary["completion_pct"] = (summary["filled_required"] / summary["total_required"] * 100).round(1)

    return summary
