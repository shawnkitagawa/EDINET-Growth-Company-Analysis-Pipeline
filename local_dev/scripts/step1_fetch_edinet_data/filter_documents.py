
def filter_documents(date_str : str, results: list[dict], ordinance_code: str = "010", form_code: str = "030000", doc_type_code: str = "120") -> tuple[list[dict], list[dict]]: 

    filtered_documents: list[dict] = []
    updated_documents: list[dict] = []

    if len(results) == 0 : 
        return [],[]

    try: 
        for result in results:

            if result["ordinanceCode"] == ordinance_code and result["formCode"] == "030001" and result["docTypeCode"] == "130":
                updated_documents.append({
                    "docID": result["docID"],
                    "edinetCode": result["edinetCode"],
                    "filerName": result["filerName"],
                    "docDescription": result["docDescription"],
                    "periodStart": result["periodStart"],
                    "periodEnd": result["periodEnd"],
                    "submitDateTime": result["submitDateTime"],
                    "formCode": result["formCode"],
                    "docTypeCode": result["docTypeCode"],
                    "fetchDate": date_str
                })


            if result["ordinanceCode"] == ordinance_code and result["formCode"] == form_code and result["docTypeCode"] == doc_type_code and result["csvFlag"] == "1":
                filtered_documents.append({
                    "docID": result["docID"],
                    "edinetCode": result["edinetCode"],
                    "filerName": result["filerName"],
                    "docDescription": result["docDescription"],
                    "periodStart": result["periodStart"],
                    "periodEnd": result["periodEnd"],
                    "submitDateTime": result["submitDateTime"],
                    "formCode": result["formCode"],
                    "docTypeCode": result["docTypeCode"],
                    "fetchDate": date_str
                })

        return filtered_documents, updated_documents

    except KeyError as e :
        raise KeyError(f"Missing expected key in EDINET document:{e}")
    


def get_unique_documents_by_company(documents: list[dict],correction_docs: list[dict]) -> list[dict]:

    latest_docs = {}

    all_docs = documents + correction_docs

    for doc in all_docs:
        key = (
            doc["edinetCode"],
            doc["periodStart"],
            doc["periodEnd"],
        )

        if key not in latest_docs:
            latest_docs[key] = doc
            continue

        if doc["submitDateTime"] > latest_docs[key]["submitDateTime"]:
            latest_docs[key] = doc

    return list(latest_docs.values())
    