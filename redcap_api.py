import requests
import pandas as pd


def kitoltottseg(token, url="https://redcap.onkobank.com/redcap/api/"):

    data = {
        "token": token,
        "content": "metadata",
        "format": "json",
        "returnFormat": "json"
    }

    metadata = pd.DataFrame(requests.post(url, data=data).json())

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


def kitoltottseg_havi(token, url="https://redcap.onkobank.com/redcap/api/"):

    data = {
        "token": token,
        "content": "metadata",
        "format": "json",
        "returnFormat": "json"
    }

    metadata = pd.DataFrame(requests.post(url, data=data).json())

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

    data = {
        "token": token,
        "content": "log",
        "format": "json",
        "returnFormat": "json"
    }

    response = requests.post(url, data=data)

    response.raise_for_status()

    log = pd.DataFrame(response.json())

    completed_felv = log[log["details"].str.contains("felvteli_adatok_complete = '2'", na=False)]
    completed_ito_elbocs = log[log["details"].str.contains("ito_elbocsts_utni_adatok_complete = '2'", na=False)]
    completed_krhzi_elbocs = log[log["details"].str.contains("krhzi_elbocstst_kvet_adatok_complete = '2'", na=False)]

    # dátum konvertálása
    for df in [completed_felv, completed_ito_elbocs, completed_krhzi_elbocs]:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # form azonosító hozzáadása
    completed_felv["form_name"] = "felvteli_adatok"
    completed_ito_elbocs["form_name"] = "ito_elbocsts_utni_adatok"
    completed_krhzi_elbocs["form_name"] = "krhzi_elbocstst_kvet_adatok"

    # összefűzés
    completed_all = pd.concat([completed_felv, completed_ito_elbocs, completed_krhzi_elbocs], ignore_index=True)

    completed_all = completed_all.rename(columns={"record": "record_id"})

    # legelső completion esemény rekord + form szerint
    first_completion = (completed_all.groupby(["record_id", "form_name"], as_index=False)["timestamp"].min())

    first_completion["completion_month"] = (first_completion["timestamp"].dt.to_period("M").astype(str))

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

    completion = completion.merge(first_completion[["record_id", "form_name", "completion_month"]], on=["record_id", "form_name"], how="left")

    summary = (completion.groupby(["redcap_data_access_group", "completion_month", "form_name"])
    .agg(records=("record_id", "count"), filled_required=("filled_required", "sum"), total_required=("total_required", "sum"))
    .reset_index()
    )

    summary["completion_pct"] = (summary["filled_required"] / summary["total_required"] * 100).round(1)

    return summary
