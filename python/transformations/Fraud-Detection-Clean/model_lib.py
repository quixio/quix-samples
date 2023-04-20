import pandas as pd


def clean_function(row):

    cols_needed = [
        "timestamp",
        "AMT_ANNUITY",
        "AMT_CREDIT",
        "AMT_GOODS_PRICE",
        "BASEMENTAREA_MEDI",
        "CODE_GENDER",
        "DAYS_BIRTH",
        "DAYS_EMPLOYED",
        "DAYS_LAST_PHONE_CHANGE",
        "FLAG_PHONE",
        "FLAG_WORK_PHONE",
        "LANDAREA_MEDI",
        "LIVINGAPARTMENTS_MEDI",
        "LIVINGAREA_MEDI",
        "NAME_CONTRACT_TYPE",
        "NAME_EDUCATION_TYPE",
        "NAME_FAMILY_STATUS",
        "NAME_INCOME_TYPE",
        "NONLIVINGAREA_MEDI",
        "OWN_CAR_AGE",
        "REGION_RATING_CLIENT",
        "REGION_RATING_CLIENT_W_CITY",
        "REG_CITY_NOT_LIVE_CITY",
        "YEARS_BUILD_MEDI",
    ]

    # Error if cols are not present
    if len(set(cols_needed) - set(row.index)) != 0:
        print("ERROR")
        print("Missing cols: ", sorted(set(cols_needed) - set(row.index)))

    else:
        # Cols needed output
        cols_needed_output = [
            "timestamp",
            "AMT_ANNUITY",
            "AMT_CREDIT",
            "AMT_GOODS_PRICE",
            "BASEMENTAREA_MEDI",
            "DAYS_BIRTH",
            "DAYS_EMPLOYED",
            "DAYS_LAST_PHONE_CHANGE",
            "FLAG_PHONE",
            "FLAG_WORK_PHONE",
            "LANDAREA_MEDI",
            "LIVINGAPARTMENTS_MEDI",
            "LIVINGAREA_MEDI",
            "NONLIVINGAREA_MEDI",
            "OWN_CAR_AGE",
            "REGION_RATING_CLIENT",
            "REGION_RATING_CLIENT_W_CITY",
            "REG_CITY_NOT_LIVE_CITY",
            "YEARS_BUILD_MEDI",
            "CODE_GENDER__M",
            "CODE_GENDER__XNA",
            "NAME_CONTRACT_TYPE__Revolving loans",
            "NAME_EDUCATION_TYPE__Higher education",
            "NAME_EDUCATION_TYPE__Incomplete higher",
            "NAME_EDUCATION_TYPE__Lower secondary",
            "NAME_EDUCATION_TYPE__Secondary / secondary special",
            "NAME_FAMILY_STATUS__Married",
            "NAME_FAMILY_STATUS__Separated",
            "NAME_FAMILY_STATUS__Single / not married",
            "NAME_FAMILY_STATUS__Widow",
            "NAME_INCOME_TYPE__Commercial associate",
            "NAME_INCOME_TYPE__Maternity leave",
            "NAME_INCOME_TYPE__Pensioner",
            "NAME_INCOME_TYPE__State servant",
            "NAME_INCOME_TYPE__Student",
            "NAME_INCOME_TYPE__Unemployed",
            "NAME_INCOME_TYPE__Working",
        ]

        df_predict = pd.DataFrame()

        # map input columns to output columns
        # split columns with '__' to boolean representations
        for col in cols_needed_output:
            if "__" not in col:
                df_predict[col] = [row[col]]
            elif "__" in col:
                col_root = col.split("__")[0]
                if row[col_root] == col.split("__")[1]:
                    df_predict[col] = 1
                else:
                    df_predict[col] = 0

        if df_predict.shape[1] != len(cols_needed_output):
            print("ERROR")
            print(df_predict)

        return df_predict
